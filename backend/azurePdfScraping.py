import io
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Replace these with your Azure Form Recognizer credentials
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT_URL")
AZURE_KEY = os.getenv("AZURE_KEY_API")


# Initialize the Azure Form Recognizer client
client = DocumentAnalysisClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_KEY)
)

# Function to extract data (text and tables) from the PDF using Azure Form Recognizer
def extract_pdf_data(pdf_file_io):
    try:
        poller = client.begin_analyze_document("prebuilt-layout", pdf_file_io)
        result = poller.result()

        extracted_data = {
            "text": "",
            "tables": [],
            "pages": []
        }

        # Extract text from each page
        for page in result.pages:
            page_text = ""
            for line in page.lines:
                page_text += line.content + "\n"
            extracted_data["pages"].append({"page_number": page.page_number, "text": page_text})
            extracted_data["text"] += page_text

        # Extract tables
        for table in result.tables:
            table_data = []
            for cell in table.cells:
                table_data.append({
                    "row": cell.row_index,
                    "column": cell.column_index,
                    "text": cell.content
                })
            extracted_data["tables"].append(table_data)

        return extracted_data

    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        return None

# Function to store extracted data in a markdown file
def save_markdown_data(extracted_data):
    try:
        if extracted_data is None:
            raise ValueError("No data extracted from PDF.")

        markdown_content = f"# Extracted PDF Data\n\n"

        # Add extracted text
        markdown_content += f"## Text Data\n\n{extracted_data['text']}\n\n"

        # Add extracted tables
        if extracted_data['tables']:
            markdown_content += f"## Tables\n\n"
            for table in extracted_data['tables']:
                markdown_content += f"### Table\n\n"
                for cell in table:
                    markdown_content += f"Row: {cell['row']}, Column: {cell['column']} - {cell['text']}\n"
                markdown_content += "\n"

        # Check if the file path is valid
        output_file_path = "extracted_data.md"
        if os.path.isdir(output_file_path):
            raise ValueError(f"The path '{output_file_path}' is a directory, not a file.")

        # Store the markdown content in a file
        with open(output_file_path, "w") as md_file:
            md_file.write(markdown_content)

        return markdown_content

    except Exception as e:
        print(f"Error during markdown saving: {str(e)}")
        return None  # Ensure that if it fails, it returns None


# Example function usage
def main(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            pdf_file_io = io.BytesIO(file.read())
            
            # Extract data from the PDF
            extracted_data = extract_pdf_data(pdf_file_io)
            
            # If data is extracted, save it to markdown
            if extracted_data:
                markdown_content = save_markdown_data(extracted_data)
                print(f"Successfully processed the PDF. Markdown content saved to 'extracted_data.md'.")
                print(f"Markdown content preview:\n{markdown_content[:300]}...")  # Print preview of markdown content
            else:
                print("No data was extracted from the PDF.")
    
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    pdf_path = "file.pdf"  # Replace with your actual PDF file path
    main(pdf_path)


