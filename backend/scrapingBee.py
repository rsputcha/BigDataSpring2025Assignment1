import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv(override=True)

# ScrapingBee API endpoint
SCRAPING_BEE_ENDPOINT = os.getenv("SCRAPING_BEE_EP")

def scrape_page(url, api_key):
    # Parameters for the request
    params = {
        'api_key': api_key,
        'url': url,
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Make the GET request to ScrapingBee API
        response = requests.get(SCRAPING_BEE_ENDPOINT, params=params, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            markdown_content = "# Webpage Content\n\n"
            images = []  # List to hold image URLs

            # Scrape headings
            for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                markdown_content += f"## {header.get_text(strip=True)}\n\n"

            # Scrape paragraphs
            for para in soup.find_all('p'):
                markdown_content += f"{para.get_text(strip=True)}\n\n"

            # Scrape images
            for img in soup.find_all('img', src=True):
                img_url = img['src']
                if img_url.startswith('http'):
                    markdown_content += f"![Image]({img_url})\n\n"
                    images.append(img_url)

            # Scrape links
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True)
                link_url = link['href']
                markdown_content += f"[{link_text}]({link_url})\n"

            return markdown_content, images

        else:
            return f"Error: Failed to scrape the page. Status code: {response.status_code}", []

    except requests.exceptions.RequestException as e:
        return f"Error: An error occurred: {str(e)}", []
