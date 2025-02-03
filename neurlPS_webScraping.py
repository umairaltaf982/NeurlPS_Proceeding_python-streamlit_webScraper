import ssl
import os
import aiohttp
import asyncio
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm

BASE_URL = "https://papers.nips.cc"
DOWNLOAD_DIR = "downloads"
INFO_DIR = "info"
PAPERS_DIR = "papers"
MAX_CONCURRENT_REQUESTS = 10
CSV_FILE = "download_log.csv"

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def menu():
    print("1. Enter the Years to Download")
    print("2. Download all Years Data")
    print("3. Enter the HTML link to Download")
    print("4. Enter the HTML Link for Info")
    print("5. Exit")

def save_to_csv(data):
    """Save download details to a CSV file."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Year", "File Name", "URL", "Type"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

async def fetch_papers_from_year(year_url, year):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(year_url) as response:
                text = await response.text()
                soup = BeautifulSoup(text, "html.parser")
                paper_links = soup.select("ul > li > a[title]")

                tasks = []
                for paper_link in paper_links:
                    paper_page_url = urljoin(BASE_URL, paper_link["href"])
                    tasks.append(download_pdf_from_paper_page(session, paper_page_url, year))

                await asyncio.gather(*tasks)
    except Exception as e:
        print(f"Error fetching papers from {year_url}: {e}")

async def fetch_paper_from_link(url):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url) as response:
                text = await response.text()
                soup = BeautifulSoup(text, "html.parser")
                paper_link = soup.find("a", text="Paper")

                if paper_link:
                    pdf_url = urljoin(BASE_URL, paper_link["href"])
                    file_name = pdf_url.split("/")[-1]
                    file_path = os.path.join(DOWNLOAD_DIR, file_name)
                    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
                    print(f"Downloading PDF from: {pdf_url}")
                    await download_file_with_progress_bar(session, pdf_url, file_path)
                    print(f"\nDownload complete: {file_path} ✅")
                    save_to_csv({
                        "Year": "N/A",
                        "File Name": file_name,
                        "URL": pdf_url,
                        "Type": "Paper"
                    })
                else:
                    print("No 'Paper' link found on the page.")
    except Exception as e:
        print(f"Error fetching paper from {url}: {e}")

async def fetch_info_from_link(url):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url) as response:
                text = await response.text()
                soup = BeautifulSoup(text, "html.parser")
                bibtex_link = soup.find("a", text="Bibtex")

                if bibtex_link:
                    bibtex_url = urljoin(BASE_URL, bibtex_link["href"])
                    file_name = bibtex_url.split("/")[-1]
                    file_path = os.path.join(INFO_DIR, file_name)
                    os.makedirs(INFO_DIR, exist_ok=True)
                    print(f"Downloading Bibtex file from: {bibtex_url}")
                    await download_file_with_progress_bar(session, bibtex_url, file_path)
                    print(f"\nDownload complete: {file_path} ✅")
                    save_to_csv({
                        "Year": "N/A",
                        "File Name": file_name,
                        "URL": bibtex_url,
                        "Type": "Bibtex"
                    })
                    with open(file_path, "r") as file:
                        bibtex_content = file.read()
                        print(f"\nBibtex Content:\n{bibtex_content}")
                else:
                    print("No 'Bibtex' link found on the page.")
    except Exception as e:
        print(f"Error fetching info from {url}: {e}")

async def download_pdf_from_paper_page(session, paper_page_url, year):
    try:
        async with session.get(paper_page_url) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            pdf_link = soup.find("a", text="Paper")

            if pdf_link:
                pdf_url = urljoin(BASE_URL, pdf_link["href"])
                file_name = pdf_url.split("/")[-1]
                dir_path = os.path.join(PAPERS_DIR, str(year))
                os.makedirs(dir_path, exist_ok=True)
                file_path = os.path.join(dir_path, file_name)
                print(f"\nDownloading: {file_name}")
                await download_file_with_progress_bar(session, pdf_url, file_path)
                print(f"\nDownload complete: {file_path} ✅")
                save_to_csv({
                    "Year": year,
                    "File Name": file_name,
                    "URL": pdf_url,
                    "Type": "Paper"
                })
    except Exception as e:
        print(f"Error downloading PDF from {paper_page_url}: {e}")

async def download_file_with_progress_bar(session, url, file_path):
    try:
        async with session.get(url) as response:
            file_size = int(response.headers.get("content-length", 0))
            progress_bar = tqdm(total=file_size, unit="B", unit_scale=True, desc=file_path.split("/")[-1])

            with open(file_path, "wb") as file:
                async for chunk in response.content.iter_chunked(1024):
                    file.write(chunk)
                    progress_bar.update(len(chunk))
            progress_bar.close()
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")

async def main():
    while True:
        menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            start_year = int(input("Enter the Starting Year (Min : 1987): "))
            end_year = int(input("Enter the Ending Year (Max : 2023): "))

            tasks = []
            for year in range(start_year, end_year + 1):
                year_url = f"{BASE_URL}/paper_files/paper/{year}"
                tasks.append(fetch_papers_from_year(year_url, year))

            await asyncio.gather(*tasks)

        elif choice == "2":
            tasks = []
            for year in range(1987, 2024):
                year_url = f"{BASE_URL}/paper_files/paper/{year}"
                tasks.append(fetch_papers_from_year(year_url, year))

            await asyncio.gather(*tasks)

        elif choice == "3":
            url = input("Enter the URL: ")
            await fetch_paper_from_link(url)

        elif choice == "4":
            url = input("Enter the URL: ")
            await fetch_info_from_link(url)

        elif choice == "5":
            break

        else:
            print("Invalid Choice, Try again please.")

if __name__ == "__main__":
    asyncio.run(main())
