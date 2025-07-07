import os
import csv

def save_names_to_csv():
    """
    Saves predefined names to a CSV file in the AlumniLists directory.
    """
    # Predefined names
    names = [
        "Fernando Pagbilao Jr.",
        "Rosel Mina",
        "Jhon Carlo Santillan",
        "Mark Cernan Gutay",
        "Jay Dane Mendoza",
        "Ronalyn Cadelina",
        "Czar Erson Isla",
        "Samira Aubrey Manzano",
        "Angeline Casabar",
        "Angelyn Dela Cruz",
        "Reighn Gumpal",
        "Mark Christian E. Labuanan",
        "Carl Rainier M. Manalili",
        "Jay - ar Santos",
        "Roland Andrei Ventura",
        "Macario Jr. Alejandro",
        "Christian Utleg Calpito",
        "Reymark Oliquino",
        "Caezar Stanly P. Tomas",
        "Daniel Loreto D. Andres",
        "Jan Aisonlei C. Bañagale",
        "Noriel Caban",
        "Iresh Bueno",
        "Harry Miranda",
        "Sean Vennon Acosta",
        "James Caraui",
        "Edmar Jan Gumtang",
        "Adrian Agustin"
    ]

    # Define the output file path
    alumni_directory = 'c:/Users/HP/AlumniTracer_playwright/data/AlumniLists'
    print(f"Checking if directory exists: {alumni_directory}")
    if not os.path.exists(alumni_directory):
        print(f"Directory does not exist. Creating: {alumni_directory}")
        os.makedirs(alumni_directory)  # Create the directory if it doesn't exist

    output_file = os.path.join(alumni_directory, 'InputNames.csv')
    print(f"Output file path: {output_file}")

    # Write names to the CSV file
    print("Writing names to the CSV file...")
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['names'])  # Write the header
        for name in names:
            writer.writerow([name])  # Write each name

    print(f"Names saved to {output_file}")

if __name__ == "__main__":
    print("Starting script...")
    save_names_to_csv()
    print("Script finished.")