import subprocess
import sys
import time
import os

# --- PART 1: AUTO-INSTALL LIBRARIES ---
def install(package):
    print(f"[SETUP] Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = ['selenium', 'webdriver-manager', 'pandas', 'textblob', 'nltk', 'scikit-learn', 'matplotlib', 'seaborn']
print("--- CHECKING LIBRARIES ---")
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        install(package)

# --- PART 2: DOWNLOAD NLTK DATA ---
import nltk
print("[SETUP] Downloading NLTK language data...")
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')

# --- PART 3: TASK 1 (WEB SCRAPER) ---
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from textblob import TextBlob

def run_task1():
    print("\n--- STARTING TASK 1: WEB SCRAPING ---")
    url = "https://www.bestbuy.ca/en-ca/product/sony-wh-1000xm5-over-ear-noise-cancelling-bluetooth-headphones-black/16163673"
    
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Initialize Driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)
    
    # Pagination Loop
    print("Collecting reviews (Clicking 'Show More')...")
    reviews_collected = 0
    while reviews_collected < 60:
        try:
            reviews = driver.find_elements(By.CLASS_NAME, "reviewItem_2k5V5")
            reviews_collected = len(reviews)
            print(f"Reviews found so far: {reviews_collected}")
            
            if reviews_collected >= 60: break

            btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CLASS_NAME, "loadMore_3TiIu")))
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(2)
        except:
            print("No more 'Show More' buttons or limit reached.")
            break

    # Data Extraction
    data = []
    reviews = driver.find_elements(By.CLASS_NAME, "reviewItem_2k5V5")
    for r in reviews:
        try:
            txt = r.find_element(By.CLASS_NAME, "reviewContent_09w65").text
            try: name = r.find_element(By.CLASS_NAME, "name_1aa6i").text
            except: name = "Anonymous"
            try: rating = r.find_element(By.CLASS_NAME, "rating_3pA0I").get_attribute("title").split()[0]
            except: rating = "0"
            
            # Sentiment
            pol = TextBlob(txt).sentiment.polarity
            sent = "Positive" if pol > 0.1 else "Negative" if pol < -0.1 else "Neutral"
            
            data.append({"Reviewer": name, "Review": txt, "Rating": rating, "Sentiment": sent})
        except: continue
        
    driver.quit()
    pd.DataFrame(data).to_csv("Task1_Reviews.csv", index=False)
    print("Task 1 Done! Saved 'Task1_Reviews.csv'")

# --- PART 4: TASK 2 (DATA ANALYSIS) ---
import matplotlib.pyplot as plt
import seaborn as sns

def run_task2():
    print("\n--- STARTING TASK 2: DATA ANALYSIS ---")
    file_name = "Hanuai task2 assignment.csv"
    
    if not os.path.exists(file_name):
        print(f"ERROR: '{file_name}' not found. Please ensure it is in the folder.")
        return

    df = pd.read_csv(file_name)

    # Text Mining Logic
    def extract_component(text):
        text = str(text).lower()
        if 'radio' in text: return 'Radio'
        if 'screen' in text or 'display' in text: return 'Screen'
        if 'camera' in text: return 'Camera'
        if 'battery' in text: return 'Battery'
        return 'Other'

    df['Combined_Text'] = df['CAUSAL_VERBATIM'].fillna('') + " " + df['CUSTOMER_VERBATIM'].fillna('')
    df['Extracted_Component'] = df['Combined_Text'].apply(extract_component)

    # Save Output
    df.to_csv("Task2_Analyzed.csv", index=False)
    print("Task 2 Data Saved 'Task2_Analyzed.csv'")

    # Generate Chart
    plt.figure(figsize=(10,6))
    sns.countplot(y='Extracted_Component', data=df, order=df['Extracted_Component'].value_counts().index)
    plt.title("Top Failed Components")
    plt.savefig("Task2_Chart.png")
    print("Task 2 Chart Saved 'Task2_Chart.png'")

if __name__ == "__main__":
    run_task1()
    run_task2()