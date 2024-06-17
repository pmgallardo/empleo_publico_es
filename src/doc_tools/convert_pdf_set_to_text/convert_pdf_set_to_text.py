import os
from PyPDF2 import PdfReader

folder_path = '/home/username/Documents/example_folder'
output_file_path = 'example.txt'


# Commented out other folder paths and output files for brevity
def remove_leading_zeroes(s):
    stripped_string = s.lstrip('0')
    return stripped_string if stripped_string else '0'

def custom_sort(filename):
    parts = filename.split(" ", 1)
    num_part = parts[0].split(".")[0]
    return (int(num_part), parts[1]) if len(parts) > 1 else (int(num_part), "")

def convert_pdfs_to_text(folder_path, output_file_path):
    # Get list of all files in the directory
    files = os.listdir(folder_path)

    # Filter out only PDF files and sort them using custom_sort function
    pdf_files = sorted([f for f in files if f.lower().endswith('.pdf')], key=custom_sort)

    combined_text_content = ""

    # Loop through each PDF file
    for pdf_file in pdf_files:
        print(f"Reading file {pdf_file.title()}")

        # Extract the number from the filename (assuming the filename is purely numerical before .pdf)
        filenumber = remove_leading_zeroes(os.path.splitext(pdf_file)[0])

        pdf_path = os.path.join(folder_path, pdf_file)

        # Open the PDF file
        reader = PdfReader(pdf_path)
        text_content = ""

        # Extract text from each page
        for page in reader.pages:
            text_content += page.extract_text() + "\n"

        # Prepend the "h2. %" line
        text_content = f"h2. Tema {filenumber}\n" + text_content

        # Append the text content to the combined content
        combined_text_content += text_content

    # Write the combined text content to a single output file
    with open(output_file_path, 'w', encoding='utf-8', errors='ignore') as output_file:
        output_file.write(combined_text_content)


# Example usage:
convert_pdfs_to_text(folder_path, output_file_path)