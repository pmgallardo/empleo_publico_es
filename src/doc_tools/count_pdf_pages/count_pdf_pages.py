import os
from PyPDF2 import PdfReader

def list_pdf_files(folder_path):
    # List all files in the given folder
    files = os.listdir(folder_path)
    # Filter out only PDF files
    pdf_files = [file for file in files if file.lower().endswith('.pdf')]
    return pdf_files

def get_pdf_page_count(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        # Get the number of pages
        num_pages = len(reader.pages)
    return num_pages

def main(folder_path):
    # Get all PDF files in the folder
    pdf_files = list_pdf_files(folder_path)
    # Obtain the number of pages for each PDF file
    pages = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        try:
            num_pages = get_pdf_page_count(pdf_path)
            pages.append((pdf_file, num_pages))
        except Exception as e:
            print(f"Could not read {pdf_file}: {e}")

    # Sort by filename
    sorted_pages = sorted(pages, key=lambda x: x[0])
    for pdf_file, num_pages in sorted_pages:
        print(f"{pdf_file},{num_pages}")

# Replace 'your/folder/path' with the path to the folder containing the PDF files
if __name__ == "__main__":
    folder_path = "/home/pablo/Documents/inap/programa/pdf/Temario-ASTIC-2023-Temas-Especificos-6e7wxd/Temario Especifico 2023/Temario Especifico 2023/vol4"
    main(folder_path)