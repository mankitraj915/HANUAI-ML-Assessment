import pandas as pd
import os
import re
import sys
from bs4 import BeautifulSoup
from textblob import TextBlob

def smart_parse():
    print("--- DIAGNOSTIC PARSER STARTING ---")
    html_file = "bestbuy_real.html"
    
    # 1. Check File Existence
    if not os.path.exists(html_file):
        print(f"❌ ERROR: '{html_file}' not found.")
        return

    # 2. Load HTML (Try UTF-8, then others)
    try:
        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except UnicodeDecodeError:
        print("⚠️ UTF-8 failed, trying default encoding...")
        with open(html_file, "r") as f:
            soup = BeautifulSoup(f, "html.parser")

    # 3. STRATEGY: Find by "Star Rating" (The most reliable anchor)
    # BestBuy ratings always have a title like "5 out of 5 stars" or similar.
    print("🔍 Scanning for star ratings...")
    
    # regex to find "digit out of digit" or "stars"
    star_elements = soup.find_all(attrs={"title": re.compile(r"\d\s?out of\s?\d|stars", re.IGNORECASE)})
    
    if not star_elements:
        # Fallback: Search for class names containing "rating"
        star_elements = soup.find_all(class_=re.compile(r"rating", re.IGNORECASE))

    print(f"   Found {len(star_elements)} potential review anchors.")

    data = []
    for star in star_elements:
        try:
            # The star element is usually INSIDE the review container.
            # We climb up the tree to find the "Review Item" container.
            # Usually it's an 'li' or a 'div' about 3-5 levels up.
            
            container = star.find_parent("li")
            if not container:
                # If not in an 'li', try finding the closest main 'div' wrapper
                container = star.find_parent("div", class_=re.compile(r"item|content|review", re.IGNORECASE))
            
            if not container: continue

            # --- EXTRACTION ---
            
            # 1. Rating
            rating_text = star.get("title", "0")
            # Extract the first number
            rating = rating_text.split()[0] if rating_text[0].isdigit() else "0"

            # 2. Review Text (Look for the longest text block in the container)
            # This avoids capturing buttons or labels.
            all_text_elements = container.find_all(["p", "span", "div"])
            review_text = ""
            max_len = 0
            
            for t in all_text_elements:
                txt = t.get_text(strip=True)
                # Filter out garbage (dates, names, generic labels)
                if len(txt) > max_len and "out of 5" not in txt and "Verified" not in txt:
                    review_text = txt
                    max_len = len(txt)
            
            # 3. Name (Look for text that is short and usually bold or near the top)
            # Heuristic: Name is often in a span/div with 'name' or 'author' class
            name_tag = container.find(class_=re.compile(r"name|author", re.IGNORECASE))
            name = name_tag.get_text(strip=True) if name_tag else "Anonymous"

            # 4. Sentiment
            blob = TextBlob(review_text)
            sent = "Positive" if blob.sentiment.polarity > 0.1 else "Negative" if blob.sentiment.polarity < -0.1 else "Neutral"

            # Deduplication Check (Avoid adding the same review twice)
            if not any(d['Review Text'] == review_text for d in data):
                data.append({
                    "Reviewer": name,
                    "Rating": rating,
                    "Review Text": review_text,
                    "Sentiment": sent
                })

        except Exception as e:
            continue

    # 4. Save
    if len(data) > 0:
        df = pd.DataFrame(data)
        df.to_csv("Task1_BestBuy_Reviews.csv", index=False)
        print(f"✅ SUCCESS! Extracted {len(df)} reviews.")
        print("📁 Saved to: Task1_BestBuy_Reviews.csv")
        print("📊 Sample:")
        print(df[['Reviewer', 'Rating', 'Sentiment']].head())
    else:
        print("❌ STILL EMPTY. Possible reasons:")
        print("   1. The HTML file doesn't actually contain reviews (Open it in Chrome to check).")
        print("   2. BestBuy changed their code drastically.")

if __name__ == "__main__":
    smart_parse()