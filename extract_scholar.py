from scholarly import scholarly
import pandas as pd
import re

# === FUNCTION: FORMATTING ===
def format_reference(bib, style):
    authors = bib.get('author', 'Unknown Author')
    year = bib.get('pub_year', 'n.d.')
    title = bib.get('title', 'No Title')
    journal = bib.get('journal', '')
    volume = bib.get('volume', '')
    pages = bib.get('pages', '')
    
    if style == "APA":
        return f"{authors} ({year}). {title}. {journal}."
    
    elif style == "MLA":
        return f"{authors}. \"{title}.\" {journal}, {year}."
    
    elif style == "Chicago":
        return f"{authors}. \"{title}.\" {journal} ({year})."
    
    elif style == "Harvard":
        return f"{authors} ({year}) '{title}', {journal}."
    
    elif style == "Vancouver":
        return f"{authors}. {title}. {journal}. {year};{volume}:{pages}"
    
    else:
        return f"{authors} ({year}). {title}. {journal}."

# === STEP 1: INPUTS ===
url = input("Paste the Google Scholar profile URL: ")
top_n = int(input("How many top publications do you want? (e.g. 5): "))

print("\nChoose referencing style:")
print("1. APA")
print("2. MLA")
print("3. Chicago")
print("4. Harvard")
print("5. Vancouver")

style_choice = input("Enter 1–5: ").strip()
styles = {"1": "APA", "2": "MLA", "3": "Chicago", "4": "Harvard", "5": "Vancouver"}
style = styles.get(style_choice, "APA")

# === STEP 2: GET USER ID FROM URL ===
match = re.search(r'user=([\w-]+)', url)
if not match:
    print("❌ Invalid Google Scholar URL.")
    exit()
user_id = match.group(1)

# === STEP 3: GET AUTHOR + PUBLICATIONS ===
author = scholarly.search_author_id(user_id)
author = scholarly.fill(author)

publications = author['publications'][:top_n]
ref_list = []

for pub in publications:
    pub_filled = scholarly.fill(pub)
    bib = pub_filled['bib']
    formatted = format_reference(bib, style)
    ref_list.append({f"Reference ({style} Style)": formatted})

# === STEP 4: EXPORT TO EXCEL ===
df = pd.DataFrame(ref_list)
file_name = f"Scholar_References_{style}.xlsx"
df.to_excel(file_name, index=False)

print(f"\n✅ Done! File saved as {file_name}")