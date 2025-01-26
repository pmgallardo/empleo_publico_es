from fpdf import FPDF

def text_to_pdf(text):
    # save FPDF() class into a
    # variable pdf
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf
    pdf.set_font("helvetica", style="", size=12)

    # insert the texts in pdf
    # not using line breaks
    #for line in text.splitlines():
    #    pdf.cell(200, 10, text=line, new_x="LMARGIN", new_y="NEXT", align='L')

    # using line breaks
    pdf.multi_cell(0, 5, text)

    # save the pdf with name .pdf
    pdf.output("exam.pdf")

# read text from file
file = open("input_file.txt", "r")
text = file.read()
file.close()

text_to_pdf(text)