import os
import PyPDF2

def get_pdf_content(file_path):
    """Extracts text content from a PDF file."""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        text = []
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                lines = page_text.split('\n')
                text += lines

        return text

def get_all_pdfs_content(directory):
    """Gets content of all PDF files in the directory and subdirectories."""
    pdf_contents = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(root, file)
                try:
                    pdf_contents[file_path] = get_pdf_content(file_path)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return pdf_contents

def write_content_to_txt(output_dir, pdf_path, content):
    """Writes the extracted PDF content to a .txt file with the same name in the output directory."""
    txt_file_name = os.path.basename(pdf_path).replace('.pdf', '.txt')
    txt_path = os.path.join(output_dir, txt_file_name)
    with open(txt_path, 'w', encoding='utf-8', errors='ignore') as txt_file:
        txt_file.write('\n'.join(content))

def main():
    input_folder = "input"
    output_folder = "output"

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get the content of all PDFs
    pdf_contents = get_all_pdfs_content(input_folder)

    # Write each PDF content to a .txt file in the output folder
    for path, content in pdf_contents.items():
        write_content_to_txt(output_folder, path, content)
        #print(f"Content of {path} written to {os.path.join(output_folder, os.path.basename(path).replace('.pdf', '.txt'))}\n{'-' * 40}\n")

if __name__ == "__main__":
    main()
