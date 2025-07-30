import streamlit as st
from scholarly import scholarly
import pandas as pd
import re

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

st.title("Google Scholar Reference Exporter")

url = st.text_input("Paste Google Scholar profile URL")
top_n = st.slider("Number of Top Publications", 1, 20, 5)
style = st.selectbox("Choose Referencing Style", ["APA", "MLA", "Chicago", "Harvard", "Vancouver"])

if st.button("Generate References"):
    match = re.search(r'user=([\w-]+)', url)
    if not match:
        st.error("❌ Invalid Google Scholar URL.")
    else:
        user_id = match.group(1)
        try:
            author = scholarly.search_author_id(user_id)
            author = scholarly.fill(author)

            # Get most recent publications
            filled_pubs = [scholarly.fill(pub) for pub in author['publications'] if 'pub_year' in scholarly.fill(pub)['bib']]
            sorted_pubs = sorted(filled_pubs, key=lambda p: int(p['bib']['pub_year']), reverse=True)
            publications = sorted_pubs[:top_n]

        except Exception as e:
            st.error(f"❌ Error loading profile: {e}")
            st.stop()

        ref_list = []
        for pub in publications:
            bib = pub['bib']
            formatted = format_reference(bib, style)
            ref_list.append({"Reference": formatted})

        df = pd.DataFrame(ref_list)
        file_name = f"Scholar_References_{style}.xlsx"
        df.to_excel(file_name, index=False)
        with open(file_name, "rb") as f:
            st.download_button(label="📥 Download Excel File", data=f, file_name=file_name)

        st.success("✅ References generated!")