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
        st.error("Invalid Google Scholar URL.")
    else:
        user_id = match.group(1)
        author = scholarly.search_author_id(user_id)
        author = scholarly.fill(author)
        publications = author['publications'][:top_n]

        ref_list = []
        for pub in publications:
            pub_filled = scholarly.fill(pub)
            bib = pub_filled['bib']
            formatted = format_reference(bib, style)
            ref_list.append({"Reference": formatted})

        df = pd.DataFrame(ref_list)
        file_name = f"Scholar_References_{style}.xlsx"
        df.to_excel(file_name, index=False)
        with open(file_name, "rb") as f:
            st.download_button(label="📥 Download Excel File", data=f, file_name=file_name)

        st.success("✅ References generated!")