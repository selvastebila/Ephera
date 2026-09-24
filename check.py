import re

# Read app.js
with open(r"c:\Users\user\Desktop\project AI\src\app.js", "r", encoding="utf-8") as f:
    code = f.read()

print("File size:", len(code))
