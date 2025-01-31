from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import io
import os
import boto3
from dotenv import load_dotenv
import requests
import base64

from azurePdfScraping import extract_pdf_data, save_markdown_data
from openSourcePdf import extract_data, save_to_md
from seleniumScraping import selenium_scraping
from scrapingBee import scrape_page

# Load environment variables
load_dotenv(override=True)

# S3 client configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION")
SCRAPINGBEE_API_KEY = os.getenv("SCRAPING_BEE_KEY")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION,
)

def upload_to_s3(file_content: bytes, folder: str, filename: str, content_type: str) -> None:
    s3_path = f"{folder}/{filename}"
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_path,
            Body=file_content,
            ContentType=content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 Upload Failed: {str(e)}")

app = FastAPI(title="PDF and Web Scraping API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WebScrapingRequest(BaseModel):
    url: str
    method: str
    api_key: str = None



@app.post("/pdf/enterprise-scrape")
async def enterprise_pdf_scrape(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        # Upload the original PDF to S3
        upload_to_s3(contents, "pdf_extraction/enterprise", file.filename, "application/pdf")
        
        pdf_file_io = io.BytesIO(contents)
        extracted_data = extract_pdf_data(pdf_file_io)
        
        if extracted_data:
            markdown_content = save_markdown_data(extracted_data)
            
            md_filename = file.filename.replace(".pdf", ".md")
            upload_to_s3(markdown_content.encode(), "pdf_extraction/enterprise/markdown", md_filename, "text/markdown")
            
            for image_data in extracted_data.get("images", []):
                image_filename = image_data['filename']
                image_content = base64.b64decode(image_data['base64'])
                upload_to_s3(image_content, "pdf_extraction/enterprise/images", image_filename, "image/png")
            
            return {
                "message": "Successfully processed the PDF and saved to S3.",
                "markdown_content": markdown_content
            }
        else:
            raise HTTPException(status_code=400, detail="No Data Extracted From the PDF")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/pdf/opensource-scrape")
async def opensource_pdf_scrape(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        upload_to_s3(contents, "pdf_extraction/opensource", file.filename, "application/pdf")
        
        pdf_file_io = io.BytesIO(contents)
        extracted_data = extract_data(pdf_file_io)
        
        if extracted_data:
            markdown_content = save_to_md(extracted_data)
            
            md_filename = file.filename.replace(".pdf", ".md")
            upload_to_s3(markdown_content.encode(), "pdf_extraction/opensource/markdown", md_filename, "text/markdown")
            
            for image_data in extracted_data.get("images", []):
                image_filename = image_data['filename']
                image_content = base64.b64decode(image_data['base64'])
                upload_to_s3(image_content, "pdf_extraction/opensource/images", image_filename, "image/png")
            
            return {
                "message": "Successfully processed the PDF and saved to S3.",
                "markdown_content": markdown_content
            }
        else:
            raise HTTPException(status_code=400, detail="No Data Extracted From the PDF")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))











@app.post("/web/scrape")
async def web_scrape(request: WebScrapingRequest):
    try:
        if request.method == "Selenium":
            # Call selenium scraping
            markdown_content, images = selenium_scraping(request.url)
            folder = "web_scraping/selenium"
        elif request.method == "ScrapingBee":
            if not SCRAPINGBEE_API_KEY:
                raise HTTPException(status_code=400, detail="ScrapingBee API key not configured")
            # Call scrapingbee scraping
            markdown_content, images = scrape_page(request.url, SCRAPINGBEE_API_KEY)
            folder = "web_scraping/scrapingbee"
        else:
            raise HTTPException(status_code=400, detail="Invalid Scraping Method")
        
        if markdown_content.startswith("Error"):
            raise HTTPException(status_code=500, detail=markdown_content)
        
        # Upload the URL to S3
        url_filename = "scraped_url.txt"
        upload_to_s3(request.url.encode(), folder, url_filename, "text/plain")
        
        # Upload the markdown content to S3
        md_filename = "scraped_data.md"
        upload_to_s3(markdown_content.encode(), folder, md_filename, "text/markdown")
        
        # Now upload the images to S3 (separate folder for images)
        image_urls = []
        for index, img in enumerate(images):
            img_data = requests.get(img).content  # Download the image
            image_filename = f"image_{index + 1}.jpg"

            if request.method == "Selenium":
                image_url = upload_to_s3(img_data, "web_scraping/selenium/images", image_filename, "image/jpeg")
            elif request.method == "ScrapingBee":
                image_url = upload_to_s3(img_data, "web_scraping/scrapingbee/images", image_filename, "image/jpeg")

            image_urls.append(image_url)
        
        return {
            "message": "Scraping completed and saved to S3.",
            "markdown_content": markdown_content,
            "image_urls": image_urls  # Return the URLs of the uploaded images
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
