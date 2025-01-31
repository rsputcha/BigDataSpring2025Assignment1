from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests

def selenium_scraping(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        # Set up the Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)

        # Wait for the page to load completely
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        markdown_content = f"# Extracted Content from {url}\n\n"
        image_urls = []

        # Extract and save text content (headings and paragraphs)
        markdown_content += "## Text Content\n\n"
        elements = driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //p")
        for element in elements:
            markdown_content += f"{element.text.strip()}\n\n"

        # Extract and save tables
        markdown_content += "## Tables\n\n"
        tables = driver.find_elements(By.TAG_NAME, "table")
        for table_index, table in enumerate(tables, start=1):
            markdown_content += f"### Table {table_index}\n\n"
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                columns = row.find_elements(By.TAG_NAME, "td")
                row_data = [col.text.strip() for col in columns]
                markdown_content += "| " + " | ".join(row_data) + " |\n"
            markdown_content += "\n"

        # Extract and save links
        markdown_content += "## Links\n\n"
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            if href:
                markdown_content += f"- [{link.text}]({href})\n"
        markdown_content += "\n"

        # Extract and save images
        markdown_content += "## Images\n\n"
        images = driver.find_elements(By.TAG_NAME, "img")
        for index, image in enumerate(images, start=1):
            img_url = image.get_attribute("src")
            if img_url:
                image_urls.append(img_url)
                markdown_content += f"![Image {index}]({img_url})\n"

        return markdown_content, image_urls

    except Exception as e:
        return f"Error during scraping: {str(e)}", []

    finally:
        if 'driver' in locals():
            driver.quit()
