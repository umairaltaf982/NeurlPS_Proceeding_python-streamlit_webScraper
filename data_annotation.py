import pandas as pd
import google.generativeai as genai
import concurrent.futures
import time

dataset_path = "research_papers.csv"
df = pd.read_csv(dataset_path)

print("Columns in the dataset:", df.columns.tolist())

GEMINI_API_KEY = "AIzaSyCKfMYDKB4j9mpYp6SFLPC02fdQCxD7wss"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

LABELS = [
    "Deep Learning/Machine Learning",
    "Computer Vision",
    "Reinforcement Learning",
    "Natural Language Processing (NLP)",
    "Optimization Algorithms"
]

def classify_paper(title, abstract, max_retries=3, initial_delay=10):
    delay = initial_delay
    for retry_count in range(max_retries):
        try:
            prompt = f"""
            Classify the following research paper into one of these categories: {', '.join(LABELS)}.
            Title: {title}
            Abstract: {abstract}
            Return only the category name.
            """
            response = model.generate_content(prompt)
            predicted_label = response.text.strip()

            if predicted_label not in LABELS:
                predicted_label = "Unknown"

            return predicted_label

        except Exception as e:
            if "ResourceExhausted" in str(e) or "429" in str(e):
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"Error classifying paper '{title}': {e}")
                return "Error"

    print(f"Max retries exceeded for '{title}'.")
    return "Error"

title_column = 'Title'
abstract_column = 'Abstract'
df['Category'] = ""

MAX_WORKERS = 5

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    future_to_index = {
        executor.submit(classify_paper, row[title_column], row[abstract_column]): index
        for index, row in df.iterrows()
    }

    for future in concurrent.futures.as_completed(future_to_index):
        index = future_to_index[future]
        try:
            df.at[index, 'Category'] = future.result()
            print(f"Processed Paper {index + 1}/{len(df)} -> {df.at[index, 'Category']}")
        except Exception as e:
            print(f"Error processing Paper {index + 1}: {e}")

output_path = "annotated_research_papers.csv"
df.to_csv(output_path, index=False)
print(f"Annotation complete! Annotated dataset saved to {output_path}")
