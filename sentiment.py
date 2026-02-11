import pandas as pd

# Load dataset
df = pd.read_csv("Task1_BestBuy_Reviews.csv")

# Define custom sentiment function
def classify_sentiment(rating):
    if rating <= 2:
        return "Negative"
    elif rating == 3:
        return "Neutral"
    else:
        return "Positive"

# Apply classification
df["Sentiment"] = df["Rating"].apply(classify_sentiment)

# Save updated dataset
df.to_csv("Task1_BestBuy_Reviews_Updated.csv", index=False)

print("Script executed successfully.")
print(df.head())