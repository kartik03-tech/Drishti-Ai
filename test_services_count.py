import app
from collections import Counter

s = app.service_rows(None)
print("Total services count:", len(s))
counts = Counter([x["type"] for x in s])
for k, v in counts.items():
    print(f"  {k:15}: {v}")
