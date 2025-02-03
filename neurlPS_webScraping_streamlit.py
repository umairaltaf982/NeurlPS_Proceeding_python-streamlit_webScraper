import os
import requests
import streamlit as st
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from tqdm import tqdm

BASE_URL = "https://papers.nips.cc"
DOWNLOAD_DIR = "downloads"
INFO_DIR = "info"
PAPERS_DIR = "papers"
MAX_THREADS = 10

st.title("NIPS Paper Downloader 🚀")
st.write("Download research papers from the NeurIPS conference website.")

def fetch_papers_from_year(year_url, year):
    try:
        response = requests.get(year_url)
        soup = BeautifulSoup(response.text, "html.parser")
        paper_links = soup.select("ul > li > a[title]")

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            for paper_link in paper_links:
                paper_page_url = urljoin(BASE_URL, paper_link["href"])
                executor.submit(download_pdf_from_paper_page, paper_page_url, year)
    except Exception as e:
        st.error(f"Error fetching papers from {year_url}: {e}")

def fetch_paper_from_link(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        paper_link = soup.find("a", text="Paper")

        if paper_link:
            pdf_url = urljoin(BASE_URL, paper_link["href"])
            file_name = pdf_url.split("/")[-1]
            file_path = os.path.join(DOWNLOAD_DIR, file_name)
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            st.info(f"Downloading PDF from: {pdf_url}")
            download_file_with_progress_bar(pdf_url, file_path)
            st.success(f"Download complete: {file_path} ✅")
        else:
            st.warning("No 'Paper' link found on the page.")
    except Exception as e:
        st.error(f"Error fetching paper from {url}: {e}")

def fetch_info_from_link(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        bibtex_link = soup.find("a", text="Bibtex")

        if bibtex_link:
            bibtex_url = urljoin(BASE_URL, bibtex_link["href"])
            file_name = bibtex_url.split("/")[-1]
            file_path = os.path.join(INFO_DIR, file_name)
            os.makedirs(INFO_DIR, exist_ok=True)
            st.info(f"Downloading Bibtex file from: {bibtex_url}")
            download_file_with_progress_bar(bibtex_url, file_path)
            st.success(f"Download complete: {file_path} ✅")
            with open(file_path, "r") as file:
                bibtex_content = file.read()
                st.code(bibtex_content, language="bibtex")
        else:
            st.warning("No 'Bibtex' link found on the page.")
    except Exception as e:
        st.error(f"Error fetching info from {url}: {e}")

def download_pdf_from_paper_page(paper_page_url, year):
    try:
        response = requests.get(paper_page_url)
        soup = BeautifulSoup(response.text, "html.parser")
        pdf_link = soup.find("a", text="Paper")

        if pdf_link:
            pdf_url = urljoin(BASE_URL, pdf_link["href"])
            file_name = pdf_url.split("/")[-1]
            dir_path = os.path.join(PAPERS_DIR, str(year))
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, file_name)
            st.info(f"Downloading: {file_name}")
            download_file_with_progress_bar(pdf_url, file_path)
            st.success(f"Download complete: {file_path} ✅")
    except Exception as e:
        st.error(f"Error downloading PDF from {paper_page_url}: {e}")

# Function to download a file with a progress bar
def download_file_with_progress_bar(url, file_path):
    try:
        response = requests.get(url, stream=True)
        file_size = int(response.headers.get("content-length", 0))
        progress_bar = st.progress(0)
        status_text = st.empty()

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    progress = file.tell() / file_size
                    progress_bar.progress(progress)
                    status_text.text(f"Progress: {int(progress * 100)}%")
        st.success("Download complete! ✅")
    except Exception as e:
        st.error(f"Error downloading file from {url}: {e}")

st.sidebar.title("Menu")
choice = st.sidebar.radio(
    "Choose an option:",
    [
        "Download Papers by Year Range",
        "Download All Papers (1987-2023)",
        "Download Specific Paper",
        "Fetch Bibtex Information",
    ],
)

if choice == "Download Papers by Year Range":
    st.header("Download Papers by Year Range")
    start_year = st.number_input("Enter the Starting Year (Min: 1987)", 1987, 2023, 2020)
    end_year = st.number_input("Enter the Ending Year (Max: 2023)", 1987, 2023, 2023)

    if st.button("Start Download"):
        for year in range(start_year, end_year + 1):
            year_url = f"{BASE_URL}/paper_files/paper/{year}"
            fetch_papers_from_year(year_url, year)

elif choice == "Download All Papers (1987-2023)":
    st.header("Download All Papers (1987-2023)")
    if st.button("Start Download"):
        for year in range(1987, 2024):
            year_url = f"{BASE_URL}/paper_files/paper/{year}"
            fetch_papers_from_year(year_url, year)

elif choice == "Download Specific Paper":
    st.header("Download Specific Paper")
    url = st.text_input("Enter the URL of the paper:")
    if st.button("Download"):
        fetch_paper_from_link(url)

elif choice == "Fetch Bibtex Information":
    st.header("Fetch Bibtex Information")
    url = st.text_input("Enter the URL of the paper:")
    if st.button("Fetch Bibtex"):
        fetch_info_from_link(url)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Built with ❤️ using Streamlit")