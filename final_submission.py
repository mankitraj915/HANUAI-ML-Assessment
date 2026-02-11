import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from bs4 import BeautifulSoup

# ==========================================
# CONFIGURATION
# ==========================================
HTML_FILENAME = "bestbuyrealdata.html" 
CSV_FILENAME = "Hanuai task2 assignment.csv"

# ==========================================
# TASK 1: OPTIMIZED "WEBPAGE COMPLETE" PARSER
# ==========================================
def run_task1():
    print(f"\n--- TASK 1: PARSING '{HTML_FILENAME}' ---")
    
    if not os.path.exists(HTML_FILENAME):
        print(f"❌ ERROR: '{HTML_FILENAME}' not found.")
        return

    # 1. Load the file (Handling encoding issues common with Saved Webpages)
    try:
        with open(HTML_FILENAME, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except UnicodeDecodeError:
        print("⚠️ Formatting warning: Retrying with standard encoding...")
        with open(HTML_FILENAME, "r") as f: # Default system encoding
            soup = BeautifulSoup(f, "html.parser")

    # 2. THE LOGIC: Find List Items (<li>) containing ratings
    # Reviews are always in a list. We find every list item that mentions a star rating.
    print("   Scanning list items...")
    
    # Find all <li> tags
    all_list_items = soup.find_all("li")
    
    data = []
    
    for item in all_list_items:
        try:
            item_text = item.get_text(" ", strip=True)
            
            # CHECK: Is this a review? 
            # It must have "out of 5" OR "stars" AND be long enough to be a review.
            if ("out of 5" in item_text.lower() or "stars" in item_text.lower()) and len(item_text) > 50:
                
                # A. Extract Rating
                # Look for "X out of 5"
                rating_match = re.search(r"(\d)\s?out of\s?5", item_text)
                rating = rating_match.group(1) if rating_match else "0"

                # B. Extract Name
                # BestBuy names are usually at the start or marked by 'Reviewed by'
                if "Reviewed by" in item_text:
                    start_index = item_text.find("Reviewed by") + 11
                    end_index = item_text.find(" ", start_index + 15) # Grab next few words
                    name = item_text[start_index:end_index].strip()
                else:
                    # Fallback: Just take the first few words if they look like a name
                    name = "BestBuy Customer"

                # C. Extract Review Body
                # We simply use the full text of the list item, cleaning up the rating header
                review_body = item_text
                
                # D. Sentiment
                blob = TextBlob(review_body)
                sent = "Positive" if blob.sentiment.polarity > 0.1 else "Negative" if blob.sentiment.polarity < -0.1 else "Neutral"

                data.append({
                    "Reviewer Name": name,
                    "Rating": rating,
                    "Review Text": review_body, # Storing full text ensures we don't miss context
                    "Sentiment": sent
                })
        except:
            continue

    # 3. Save
    if data:
        df = pd.DataFrame(data)
        # Drop duplicates (Saved webpages sometimes duplicate header/footer content)
        df = df.drop_duplicates(subset=["Review Text"])
        df.to_csv("Task1_BestBuy_Reviews.csv", index=False)
        print(f"✅ SUCCESS: Extracted {len(df)} reviews to 'Task1_BestBuy_Reviews.csv'")
    else:
        print("❌ FAILED: Zero reviews found.")
        print("   -> Tip: Open the HTML file in Chrome. If you don't see reviews there, you saved it before they loaded.")

# ==========================================
# TASK 2: DATA MINING (Standard)
# ==========================================
def run_task2():
    print(f"\n--- TASK 2: MINING '{CSV_FILENAME}' ---")
    
    if not os.path.exists(CSV_FILENAME):
        print(f"❌ ERROR: '{CSV_FILENAME}' not found.")
        return

    try:
        df = pd.read_csv(CSV_FILENAME)
        print(f"   Loaded {len(df)} rows.")
    except: return

    # Regex Logic
    REGEX_COMPONENTS = {
        "Radio Unit": re.compile(r"radio|audio|stereo|tuner", re.IGNORECASE),
        "Display Screen": re.compile(r"screen|display|monitor|touch|lcd", re.IGNORECASE),
        "Camera System": re.compile(r"camera|lens|image|video", re.IGNORECASE),
        "Battery/Power": re.compile(r"battery|voltage|power|charge", re.IGNORECASE),
        "Bluetooth": re.compile(r"bluetooth|phone|pair|connect", re.IGNORECASE)
    }
    
    REGEX_FAILURES = {
        "Blank Screen": re.compile(r"blank|black|dark|off", re.IGNORECASE),
        "Electrical Short": re.compile(r"short|fuse|circuit|wire|burn", re.IGNORECASE),
        "System Freeze": re.compile(r"freeze|frozen|lock|hang|stuck", re.IGNORECASE),
        "Audio Noise": re.compile(r"noise|static|hum|buzz|sound", re.IGNORECASE)
    }

    def mine_attributes(row):
        text = str(row.get('CAUSAL_VERBATIM', '')) + " " + str(row.get('CUSTOMER_VERBATIM', ''))
        text = text.lower()
        
        comp = "Other"
        for k, v in REGEX_COMPONENTS.items():
            if v.search(text): comp = k; break
            
        issue = "Unknown"
        for k, v in REGEX_FAILURES.items():
            if v.search(text): issue = k; break
            
        return pd.Series([comp, issue])

    df[['Mined_Component', 'Mined_Failure']] = df.apply(mine_attributes, axis=1)

    df.to_csv("Task2_Mined_Analysis.csv", index=False)
    print("✅ SUCCESS: Saved 'Task2_Mined_Analysis.csv'")

    plt.figure(figsize=(10,6))
    order = df['Mined_Component'].value_counts().index
    sns.countplot(y='Mined_Component', data=df, order=order, palette='viridis')
    plt.title("Frequency of Failure by Component")
    plt.tight_layout()
    plt.savefig("Task2_Failure_Chart.png")
    print("✅ SUCCESS: Saved 'Task2_Failure_Chart.png'")

if __name__ == "__main__":
    run_task1()
    run_task2()