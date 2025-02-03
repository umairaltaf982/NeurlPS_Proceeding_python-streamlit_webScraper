import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from tqdm import tqdm

BASE_URL = "https://papers.nips.cc"
DOWNLOAD_DIR = "downloads"
INFO_DIR = "info"
PAPERS_DIR = "papers"
MAX_THREADS = 10

def menu():
    print("1. Enter the Years to Download")
    print("2. Download all Years Data")
    print("3. Enter the HTML link to Download")
    print("4. Enter the HTML Link for Info")
    print("5. Exit")

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
        print(f"Error fetching papers from {year_url}: {e}")

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
            print(f"Downloading PDF from: {pdf_url}")
            download_file_with_progress_bar(pdf_url, file_path)
            print(f"\nDownload complete: {file_path} ✅")
        else:
            print("No 'Paper' link found on the page.")
    except Exception as e:
        print(f"Error fetching paper from {url}: {e}")

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
            print(f"Downloading Bibtex file from: {bibtex_url}")
            download_file_with_progress_bar(bibtex_url, file_path)
            print(f"\nDownload complete: {file_path} ✅")
            with open(file_path, "r") as file:
                bibtex_content = file.read()
                print(f"\nBibtex Content:\n{bibtex_content}")
        else:
            print("No 'Bibtex' link found on the page.")
    except Exception as e:
        print(f"Error fetching info from {url}: {e}")

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
            print(f"\nDownloading: {file_name}")
            download_file_with_progress_bar(pdf_url, file_path)
            print(f"\nDownload complete: {file_path} ✅")
    except Exception as e:
        print(f"Error downloading PDF from {paper_page_url}: {e}")

def download_file_with_progress_bar(url, file_path):
    try:
        response = requests.get(url, stream=True)
        file_size = int(response.headers.get("content-length", 0))
        progress_bar = tqdm(total=file_size, unit="B", unit_scale=True, desc=file_path.split("/")[-1])

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))
        progress_bar.close()
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")

def main():
    while True:
        menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            start_year = int(input("Enter the Starting Year (Min : 1987): "))
            end_year = int(input("Enter the Ending Year (Max : 2023): "))

            for year in range(start_year, end_year + 1):
                year_url = f"{BASE_URL}/paper_files/paper/{year}"
                fetch_papers_from_year(year_url, year)

        elif choice == "2":
            for year in range(1987, 2024):
                year_url = f"{BASE_URL}/paper_files/paper/{year}"
                fetch_papers_from_year(year_url, year)

        elif choice == "3":
            url = input("Enter the URL: ")
            fetch_paper_from_link(url)

        elif choice == "4":
            url = input("Enter the URL: ")
            fetch_info_from_link(url)

        elif choice == "5":
            break

        else:
            print("Invalid Choice, Try again please.")

if __name__ == "__main__":
    main()