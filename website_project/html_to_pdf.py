import pdfkit

def convert_html_to_pdf(input_html_path, output_pdf_path):
    # Configuration for wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf='../../installers/wkhtmltox_0.12.6.1-2.jammy_amd64.deb')  # Adjust path to wkhtmltopdf binary
    
    # Convert HTML to PDF
    try:
        pdfkit.from_file(input_html_path, output_pdf_path, configuration=config)
        print(f"PDF successfully created: {output_pdf_path}")
    except Exception as e:
        print(f"Error during PDF generation: {e}")

if __name__ == "__main__":
    # Input HTML file path
    input_html = "index.html"  # Replace with your HTML file path
    
    # Output PDF file path
    output_pdf = "output_file.pdf"  # Replace with desired output PDF path
    
    # Convert HTML to PDF
    convert_html_to_pdf(input_html, output_pdf)
