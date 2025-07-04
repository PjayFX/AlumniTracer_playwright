import os
import pandas as pd
from playwright.sync_api import sync_playwright, Page
import time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
from typing import List, Dict
import logging

def get_credentials_from_terminal() -> Dict[str, str]:
    """
    Prompts the user to input login credentials via the terminal.

    Returns:
        Dict[str, str]: A dictionary with 'username' and 'password'.
    """
    username = input("Enter your LinkedIn username: ")
    password = input("Enter your LinkedIn password: ")
    return {'username': username, 'password': password}

def get_recent_csv(directory: str) -> str:
    """
    Finds the most recent CSV file in the specified directory.

    Args:
        directory (str): Path to the directory containing CSV files.

    Returns:
        str: Path to the most recent CSV file.
    """
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]
    if not files:
        raise FileNotFoundError("No CSV files found in the specified directory.")
    return max(files, key=os.path.getctime)

def get_names_from_csv(file_path: str) -> List[str]:
    """
    Reads names from a CSV file.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        List[str]: List of names from the CSV file.
    """
    data = pd.read_csv(file_path)
    if 'names' in data.columns:
        return data['names'].tolist()
    else:
        raise ValueError("CSV file must contain a 'names' column.")

def linkedin_login(page: Page, credentials: Dict[str, str]) -> None:
    """
    Logs into LinkedIn using the provided credentials.

    Args:
        page (Page): Playwright page object.
        credentials (Dict[str, str]): Dictionary containing 'username' and 'password'.
    """
    print("Opening LinkedIn login page...")
    page.goto("https://www.linkedin.com/login", timeout=60000)

    page.wait_for_selector("#username", timeout=60000)
    print("LinkedIn login page loaded successfully.")

    print("Entering login credentials...")
    page.fill("#username", credentials['username'])
    page.fill("#password", credentials['password'])

    page.click("button[type='submit']")
    print("Login submitted successfully.")

    # Check for verification prompt
    try:
        verification_header = page.query_selector("h1.content__header")
        if verification_header and "Let’s do a quick verification" in verification_header.inner_text():
            print("Verification required. Returning to input credentials.")
            return
    except Exception as e:
        print(f"Error checking for verification prompt: {e}")

    # Wait for LinkedIn homepage to load
    page.wait_for_selector("input[placeholder='Search']", timeout=60000)
    print("LinkedIn homepage loaded successfully.")

def extract_profile_data(page: Page) -> Dict[str, str]:
    """
    Extracts relevant data from a LinkedIn profile page, including experiences, education, and skills.

    Args:
        page (Page): Playwright page object.

    Returns:
        Dict[str, str]: A dictionary containing extracted profile data.
    """
    print("Extracting profile data...")
    profile_data = {}

    # Extract basic profile information
    try:
        name_element = page.query_selector("h1")
        profile_data['name'] = name_element.inner_text().strip() if name_element else "N/A"

        headline_element = page.query_selector("div.text-body-medium")
        profile_data['headline'] = headline_element.inner_text().strip() if headline_element else "N/A"

        location_element = page.query_selector("span.text-body-small")
        profile_data['location'] = location_element.inner_text().strip() if location_element else "N/A"
    except Exception as e:
        print(f"Error extracting basic profile information: {e}")

    # Extract education
    print("Extracting education...")
    education_items = []
    try:
        education_section = page.query_selector("section.artdeco-card:has(h2:has-text('Education'))")
        if education_section:
            education_entries = education_section.query_selector_all("li.artdeco-list__item")
            for entry in education_entries:
                school_element = entry.query_selector("div.hoverable-link-text span[aria-hidden='true']")
                duration_element = entry.query_selector("span.t-14.t-normal.t-black--light span[aria-hidden='true']")

                education_items.append({
                    "school": school_element.inner_text().strip() if school_element else "N/A",
                    "duration": duration_element.inner_text().strip() if duration_element else "N/A"
                })
    except Exception as e:
        print(f"Error extracting education: {e}")
    profile_data['education'] = education_items

    # Extract experiences
    print("Extracting experiences...")
    experiences = []
    try:
        experience_section = page.query_selector("section:has(h2:has-text('Experience'))")
        if experience_section:
            experience_items = experience_section.query_selector_all("li")
            for item in experience_items:
                title_element = item.query_selector("span[aria-hidden='true']")
                company_element = item.query_selector("span.t-14.t-normal")
                duration_element = item.query_selector("span.t-14.t-black--light")
                location_element = item.query_selector("span.t-14.t-black--light:nth-child(2)")

                experiences.append({
                    "title": title_element.inner_text().strip() if title_element else "N/A",
                    "company": company_element.inner_text().strip() if company_element else "N/A",
                    "duration": duration_element.inner_text().strip() if duration_element else "N/A",
                    "location": location_element.inner_text().strip() if location_element else "N/A"
                })
    except Exception as e:
        print(f"Error extracting experiences: {e}")
    profile_data['experiences'] = experiences

    # Extract skills
    print("Extracting skills...")
    skills = []
    try:
        skills_section = page.query_selector("section:has(h2:has-text('Skills'))")
        if skills_section:
            skill_items = skills_section.query_selector_all("li")
            for skill in skill_items:
                skill_element = skill.query_selector("span[aria-hidden='true']")
                skills.append(skill_element.inner_text().strip() if skill_element else "N/A")
    except Exception as e:
        print(f"Error extracting skills: {e}")
    profile_data['skills'] = skills

    print("Profile data extracted successfully.")
    return profile_data

def save_profile_data_to_csv(profile_data: List[Dict[str, str]], output_directory: str) -> None:
    """
    Saves extracted profile data to a CSV file.

    Args:
        profile_data (List[Dict[str, str]]): List of dictionaries containing profile data.
        output_directory (str): Directory where the CSV file will be saved.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_file = os.path.join(output_directory, 'ExtractedProfiles.csv')
    print(f"Saving extracted profiles to {output_file}...")

    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'headline', 'location', 'current_company', 'education', 'notice', 'duplicate'])
            writer.writeheader()
            writer.writerows(profile_data)
        print(f"Extracted profiles saved to {output_file}")
    except PermissionError:
        print(f"Permission denied for {output_file}. Attempting to save with a different filename...")
        alternative_file = os.path.join(output_directory, 'ExtractedProfiles_Alt.csv')
        with open(alternative_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'headline', 'location', 'current_company', 'education', 'notice', 'duplicate'])
            writer.writeheader()
            writer.writerows(profile_data)
        print(f"Extracted profiles saved to {alternative_file}")

def save_data_incrementally(data_type: str, data: List[Dict[str, str]], file_path: str) -> None:
    """
    Saves data incrementally to a CSV file.

    Args:
        data_type (str): Type of data being saved (e.g., 'profiles', 'experiences', 'skills', 'education').
        data (List[Dict[str, str]]): List of dictionaries containing data to be saved.
        file_path (str): Path to the CSV file where data will be saved.
    """
    if not data:
        print(f"No {data_type} data to save.")
        return

    file_exists = os.path.isfile(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerows(data)

    print(f"{data_type.capitalize()} data saved incrementally to {file_path}.")

def search_and_handle_profiles(page: Page, names: List[str], output_directory: str) -> None:
    """
    Searches for names on LinkedIn, extracts profile data, and saves data incrementally.

    Args:
        page (Page): Playwright page object.
        names (List[str]): List of names to search for.
        output_directory (str): Directory where extracted data will be saved.
    """
    extracted_profiles = []  # Define extracted_profiles to track processed profiles
    extracted_education = []  # Define extracted_education to store education data
    extracted_experiences = []  # Define extracted_experiences to store experiences data
    extracted_skills = []  # Define extracted_skills to store skills data

    for name in names:
        print(f"Searching for {name}...")
        attempt = 0
        matched_profiles = []

        while attempt < 2:
            try:
                # Perform search
                page.fill("input[placeholder='Search']", name)
                page.press("input[placeholder='Search']", "Enter")
                page.wait_for_timeout(5000)  # Wait for search results to load

                profile_containers = page.query_selector_all("div[data-chameleon-result-urn]")
                if not profile_containers:
                    print(f"No profiles found for {name}. Skipping...")
                    break

                for container in profile_containers:
                    profile_name_element = container.query_selector("a span[aria-hidden='true']")
                    if profile_name_element:
                        profile_name = profile_name_element.inner_text().strip()
                        print(f"Extracted profile name: {profile_name}")

                        match_score = fuzz.ratio(name.lower(), profile_name.lower())
                        print(f"Match score: {match_score}")

                        if match_score >= 90:
                            matched_profiles.append({
                                "container": container,
                                "name": profile_name
                            })

                if matched_profiles:
                    print(f"Found {len(matched_profiles)} matching profiles for {name}. Checking for duplicates...")
                    
                    # Count duplicates across all previously extracted profiles
                    duplicate_count = sum(
                        fuzz.ratio(existing_profile['name'].lower(), matched['name'].lower()) >= 90
                        for existing_profile in extracted_profiles
                        for matched in matched_profiles
                    )

                    # Proceed with the first matched profile
                    first_match = matched_profiles[0]["container"]
                    profile_link = first_match.query_selector("a[href]")
                    if profile_link:
                        profile_link.click()
                        page.wait_for_timeout(5000)  # Wait for profile page to load

                        profile_data = extract_profile_data(page)
                        print(f"Extracted profile data: {profile_data}")

                        # Log duplicate count
                        profile_data['duplicate_count'] = duplicate_count

                        extracted_profiles.append({
                            'name': profile_data['name'],
                            'headline': profile_data['headline'],
                            'location': profile_data['location'],
                            'duplicate_count': profile_data['duplicate_count']
                        })

                        # Add education, experiences, and skills to their respective lists
                        for education in profile_data['education']:
                            extracted_education.append({'name': profile_data['name'], **education})
                        for experience in profile_data['experiences']:
                            extracted_experiences.append({'name': profile_data['name'], **experience})
                        for skill in profile_data['skills']:
                            extracted_skills.append({'name': profile_data['name'], 'skill': skill})

                        break  # Proceed with the first matched profile
                else:
                    print(f"No matching profiles found for {name}. Retrying...")
                    attempt += 1
            except Exception as e:
                print(f"Error processing profile {name}: {e}")
                attempt += 1

        if attempt == 2 and not matched_profiles:
            print(f"No matching profiles found for {name} after 2 attempts. Adding notice to CSV...")
            extracted_profiles.append({
                'name': name,
                'headline': "N/A",
                'location': "N/A",
                'duplicate_count': 0
            })

    # Save extracted data to separate CSV files
    save_data_incrementally('profiles', extracted_profiles, os.path.join(output_directory, 'ExtractedProfiles.csv'))
    save_data_incrementally('education', extracted_education, os.path.join(output_directory, 'Education.csv'))
    save_data_incrementally('experiences', extracted_experiences, os.path.join(output_directory, 'Experiences.csv'))
    save_data_incrementally('skills', extracted_skills, os.path.join(output_directory, 'Skills.csv'))

def open_linkedin_login_and_search(credentials: Dict[str, str], names: List[str], output_directory: str) -> None:
    """
    Logs into LinkedIn, searches for names, and handles profiles.

    Args:
        credentials (Dict[str, str]): Dictionary containing 'username' and 'password'.
        names (List[str]): List of names to search for.
        output_directory (str): Directory where extracted data will be saved.
    """
    last_processed_index = 0
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()

                linkedin_login(page, credentials)

                # Resume from the last processed name
                for index in range(last_processed_index, len(names)):
                    name = names[index]
                    print(f"Processing profile: {name} (Index: {index})")
                    try:
                        search_and_handle_profiles(page, [name], output_directory)
                        last_processed_index = index + 1  # Update the last processed index
                    except Exception as profile_error:
                        print(f"Error processing profile {name}: {profile_error}")
                        raise profile_error

                browser.close()
                print("Browser closed successfully.")
                return
        except Exception as e:
            retry_count += 1
            print(f"An error occurred: {e}. Retrying... ({retry_count}/{max_retries})")

    print("Max retries exceeded. Ending process.")

if __name__ == "__main__":
    print("Script started.")
    credentials = get_credentials_from_terminal()
    alumni_directory = 'C:/Users/pagbilaf/linkedincrawler/data/AlumniLists'
    recent_csv = get_recent_csv(alumni_directory)
    names = get_names_from_csv(recent_csv)
    output_directory = 'C:/Users/pagbilaf/linkedincrawler/data/ExtractedData'
    open_linkedin_login_and_search(credentials, names, output_directory)
    print("Script finished.")