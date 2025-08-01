# app.py
import streamlit as st
import pandas as pd
import os

os.makedirs("results", exist_ok=True)
os.makedirs("data/raw_html", exist_ok=True)
os.makedirs("data/text", exist_ok=True)

from datetime import datetime

from scraper import scrape_and_save_all
from llm_parser import extract_events_from_texts

st.title("🔍 Pittsburgh Event Scraper & Extractor")

# Step 1: Upload Excel
uploaded_file = st.file_uploader("Upload your Events.xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("File uploaded. Previewing first 5 rows:")
    st.dataframe(df.head())

    # Option to skip scraping if files exist
    skip_scraping = st.checkbox("Skip scraping if text files already exist", value=True)

    # Step 2: Scrape Pages
    if st.button("Scrape and Save Webpages"):
        os.makedirs("data/raw_html", exist_ok=True)
        os.makedirs("data/text", exist_ok=True)
        scrape_and_save_all(df, skip_existing=skip_scraping)
        st.success("Scraping complete. Text files saved.")

    # Step 3: Ask for date input
    date_str = st.text_input("What is today's date? (YYYY-MM-DD)")

    # Step 4: OpenAI API Key
    openai_key = st.text_input("Enter your OpenAI API Key", type="password")

    if date_str and openai_key and st.button("Extract Events using LLM"):
        try:
            user_date = datetime.strptime(date_str, "%Y-%m-%d")
            output_df = extract_events_from_texts(df, user_date, openai_key)
            st.success("Extraction complete. Previewing data:")
            st.dataframe(output_df)

            # Export to CSV
            output_df.to_csv("results/events_extracted.csv", index=False)
            with open("results/events_extracted.csv", "rb") as f:
                st.download_button("Download CSV", f, file_name="events_extracted.csv")
        except Exception as e:
            st.error(f"Error during processing: {str(e)}")
