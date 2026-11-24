import pandas as pd

excel_path = r"D:\SafeGuard-AI-Professional\data\mumbai places safety full.xlsx"
df = pd.read_excel(excel_path, sheet_name="Mumbai Places Safety")
print("Total rows:", len(df))
print("\nUnique Zones:\n", df["Zone"].value_counts(dropna=False))
print("\nUnique Categories:\n", df["Category"].value_counts(dropna=False))
print("\nUnique Lighting:\n", df["Street Lighting"].value_counts(dropna=False))
print("\nSafety Score stats:\n", df["Safety Score (1-10, est.)"].describe())
