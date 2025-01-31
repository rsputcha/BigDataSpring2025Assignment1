import streamlit as st
import requests
import io
 
def dashboard_page():
    # Set page config for the dashboard
    st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="collapsed")
 
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("<h1>Dashboard</h1>", unsafe_allow_html=True)
    
    
    # Create main content area
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("<h2>Select Scraping Method</h2>", unsafe_allow_html=True)
        
        scraping_option = st.selectbox(
            'Select Scraping Type',
            ('Select Option', 'PDF Scraping', 'Web Scraping'),
            index=0
        )
 
        if scraping_option == 'PDF Scraping':
            st.markdown("<h3>Select PDF Scraping Method</h3>", unsafe_allow_html=True)
            
            pdf_scraping_option = st.selectbox(
                'Select PDF Scraping Option',
                ('Select Option', 'OpenSource', 'Enterprise'),
                index=0
            )
 
            if pdf_scraping_option != 'Select Option':
                st.write(f"Upload your PDF for {pdf_scraping_option}.")
                pdf_file = st.file_uploader("Choose a PDF", type="pdf", key=f"{pdf_scraping_option.lower()}_pdf")
                
                if pdf_file:
                    with st.spinner(f"Scraping '{pdf_file.name}' in progress..."):
                        files = {"file": pdf_file.getvalue()}
                        endpoint = f"https://bigdataspring2025assignment1.onrender.com/pdf/{pdf_scraping_option.lower()}-scrape"
                        ##endpoint = f"http://localhost:8000/pdf/{pdf_scraping_option.lower()}-scrape"
                       
                        response = requests.post(endpoint, files=files)
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.success(data["message"])
                            st.markdown(data["markdown_content"])
                            
                            st.download_button(
                                label="Download Markdown File",
                                data=data["markdown_content"],
                                file_name="extracted_data.md",
                                mime="text/markdown"
                            )
                        else:
                            st.error(f"Error: {response.json()['detail']}")
 
 
        elif scraping_option == 'Web Scraping':
            st.markdown("<h3>Select Web Scraping Method</h3>", unsafe_allow_html=True)
 
            web_scraping_option = st.selectbox(
                'Select Web Scraping Option',
                ('Select Option', 'Selenium', 'ScrapingBee'),
                index=0
            )
            
            # Only show URL input and start button when a valid option is selected
            if web_scraping_option != 'Select Option':
                # Text input for the URL
                url = st.text_input(f"Enter URL For {web_scraping_option} Scraping:")
                
                # Show the "Start Scraping" button only when the URL is provided
                if url:
                    if st.button("Start Scraping"):
                        with st.spinner("Scraping in Progress..."):
                            request_data = {
                                "url": url,
                                "method": web_scraping_option
                            }
                            
                            # Make the POST request to the FastAPI server
                            response = requests.post("https://bigdataspring2025assignment1.onrender.com/web/scrape", json=request_data)
                            ##response = requests.post("http://localhost:8000/web/scrape", json=request_data)

                            # Handle the response from FastAPI
                            if response.status_code == 200:
                                data = response.json()
                                st.success(data["message"])
                                st.markdown(data["markdown_content"])
                                
                                st.download_button(
                                    label="Download Markdown File",
                                    data=data["markdown_content"],
                                    file_name="scraped_content.md",
                                    mime="text/markdown"
                                )
                            else:
                                st.error(f"Error: {response.json()['detail']}")
                else:
                    st.warning("Please Enter a Valid URL to Start Scraping.")
 
 
 
if __name__ == '__main__':
    dashboard_page()
 