# NeurIPS Proceedings Web Scraping

This project scrapes research papers and metadata from the NeurIPS (Neural Information Processing Systems) conference website. It provides two implementations: **Python** and **Java**. The Python version includes a Streamlit-based interactive web app for easy use.

## Features

- **Download Papers**: Download PDFs of NeurIPS papers by year or specific URLs.
- **Extract Metadata**: Fetch metadata such as paper titles, authors, and Bibtex information.
- **Interactive Interface**: A Streamlit app for Python to interactively download papers and view metadata.

## Prerequisites

### Python
- Python 3.8+
- Required libraries: `requests`, `beautifulsoup4`, `tqdm`, `streamlit`

Install dependencies:
```bash
pip install requests beautifulsoup4 tqdm streamlit
```
## How to Run

### Python Implementation

1. Clone the repository:
```bash
git clone https://github.com/umairaltaf982/NeuralPS_Proceedings_dataset_Web_Scrapping.git
cd NeuralPS_Proceedings_dataset_Web_Scrapping
```
2. Run the Streamlit app:
```bash
streamlit run neurlPS_webScraping_streamlit.py
```
3. Open the app in your browser (usually at http://localhost:8501).
4. Use the sidebar menu to:
    - Download papers by year range.
    - Download all papers (1987–2023).
    - Download a specific paper by URL.
    - Fetch Bibtex information for a paper.
  
## Extracted MetaData

The scraped metadata is saved in the following formats:
- CSV: output.csv (contains paper titles, authors, year, and download links).
- JSON: output.json (structured metadata for easy parsing).

```csv
title,authors,year,url
"Deep Reinforcement Learning","Fox D.Harvy, Nelson E.Smith",2020,"https://papers.nips.cc/paper/2020/hash/2020"
"Generative Adversarial Networks","Brickson Bard, Johnith Green Harley",2019,"https://papers.nips.cc/paper/2019/hash/2021"
```

```json
[
  {
    "title": "Deep Reinforcement Learning",
    "authors": ["Fox D.Harvy", "Nelson E.Smith"],
    "year": 2020,
    "url": "https://papers.nips.cc/paper/2020/hash/2020"
  },
  {
    "title": "Generative Adversarial Networks",
    "authors": ["Brickson Bard", "Johnith Green Harley"],
    "year": 2019,
    "url": "https://papers.nips.cc/paper/2019/hash/2021"
  }
]
```
## Responsible Web Scrapping

- Respect the website’s robots.txt file.
- Add delays between requests to avoid overloading the server.
- Use the data ethically and in compliance with copyright laws.
  
Contact

For questions or feedback, contact umairaltaf982@gmail.com.

Let me know if you need further assistance! 🚀
