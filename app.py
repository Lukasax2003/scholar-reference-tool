import streamlit as st
from scholarly import scholarly
import pandas as pd
import re
import time

# === Reference Formatting Function ===
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

# === Streamlit UI Config ===
st.set_page_config(page_title="Scholar Reference Tool", page_icon="📚")
st.image("logo.png", width=150)
st.title("📚 Google Scholar Reference Exporter")
st.markdown("Extract and download the **most recent publications** from any Google Scholar profile in your chosen reference style.")

# === User Inputs ===
url = st.text_input("🔗 Paste Google Scholar profile URL")
top_n = st.slider("📄 Number of Most Recent Publications", 1, 20, 5)
style = st.selectbox("🎓 Choose Referencing Style", ["APA", "MLA", "Chicago", "Harvard", "Vancouver"])

# === Generate Button ===
if st.button("📥 Generate References"):
    with st.spinner("🔄 Fetching publications... This might take 10–20 seconds."):
        # Validate URL
        match = re.search(r'user=([\w-]+)', url)
        if not match:
            st.error("❌ Invalid Google Scholar URL.")
            st.stop()

        user_id = match.group(1)

        # Attempt to load author profile
        try:
            author = scholarly.search_author_id(user_id)
            author = scholarly.fill(author)
        except Exception as e:
            st.error(f"❌ Failed to load author profile: {e}")
            st.stop()

        # Fill publications and sort by year
        filled_pubs = []
        for pub in author.get('publications', []):
            try:
                full_pub = scholarly.fill(pub)
                pub_year = full_pub['bib'].get('pub_year')
                if pub_year:  # Only include if year is present
                    filled_pubs.append(full_pub)
                if len(filled_pubs) >= top_n * 2:  # Fetch more to account for skips
                    break
            except:
                continue

        if not filled_pubs:
            st.error("❌ No publications with a publication year were found.")
            st.stop()

        # Sort and slice
        sorted_pubs = sorted(filled_pubs, key=lambda p: int(p['bib']['pub_year']), reverse=True)
        publications = sorted_pubs[:top_n]

        # Format and export
        ref_list = []
        for pub in publications:
            try:
                bib = pub['bib']
                formatted = format_reference(bib, style)
                ref_list.append({"Reference": formatted})
            except:
                continue

        if not ref_list:
            st.error("❌ Could not format any references. Try again or use a different profile.")
            st.stop()

        # Export to Excel
        df = pd.DataFrame(ref_list)
        file_name = f"Scholar_References_{style}.xlsx"
        df.to_excel(file_name, index=False)
        with open(file_name, "rb") as f:
            st.download_button(
                label="⬇️ Download Excel File",
                data=f,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.success("✅ References generated and ready to download!")