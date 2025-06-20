import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from io import BytesIO

def get_page(page=1):
    url = "https://apps.hkma.gov.hk/eng/index.php?c=search&m=search_by_name"
    payload = {
        'search': '',
        'per_page': 100,
        'page': page
    }
    response = requests.post(url, data=payload)
    return response.text

def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    rows = table.find_all("tr")[1:]
    data = []
    for row in rows:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if cols:
            data.append({
                "Name": cols[0],
                "CE Number": cols[1],
                "AI Name": cols[2],
                "Position": cols[3],
                "Type 1 RA": cols[4],
                "Type 4 RA": cols[5],
                "Type 6 RA": cols[6],
                "Status": cols[7]
            })
    return data

def run_scraper():
    all_data = []
    page = 1
    while True:
        html = get_page(page)
        data = parse_page(html)
        if not data:
            break
        all_data.extend(data)
        page += 1
        time.sleep(1)
    return pd.DataFrame(all_data)

st.title("HKMA Securities Staff Scraper")

if st.button("Run Scraper"):
    with st.spinner("Scraping... Please wait."):
        df = run_scraper()
        st.success(f"Done! Retrieved {len(df)} records.")
        st.dataframe(df)

        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button(
            label="Download as Excel",
            data=buffer,
            file_name="HKMA_Securities_Register.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
