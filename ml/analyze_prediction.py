import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ✅ Load CSV
csv_path = "model/reports/predictions.csv"
df = pd.read_csv(csv_path)

# --- 1. Class Distribution ---
plt.figure(figsize=(10,6))
sns.countplot(x="predicted_class", data=df, order=df["predicted_class"].value_counts().index)
plt.title("Number of Predictions per Class")
plt.xlabel("Predicted Class")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("model/reports/class_distribution.png")
plt.close()

# --- 2. Confidence Histogram ---
plt.figure(figsize=(10,6))
sns.histplot(df["confidence"], bins=20, kde=True)
plt.title("Confidence Score Distribution")
plt.xlabel("Confidence")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("model/reports/confidence_histogram.png")
plt.close()

print("✅ Analysis complete: class_distribution.png and confidence_histogram.png saved in model/reports/")
