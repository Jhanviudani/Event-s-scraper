# llm_parser.py
import os
import openai
import pandas as pd
import json
from datetime import datetime
from dateutil import parser as dateparser

def extract_events_from_texts(df, start_date, openai_key):
    openai.api_key = openai_key
    results = []

    for idx, row in df.iterrows():
        org_name = str(row.get("Organisation Name", f"org_{idx}")).strip()
        org_link = row.get("Org Link")

        for label in ["org", "linkedin"]:
            filename = f"data/text/{org_name.replace(' ', '_').lower()}_{label}.txt"
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()

                prompt = build_prompt(content, start_date)

                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                    )
                    answer = response['choices'][0]['message']['content']
                    parsed = parse_llm_output(answer, org_name, org_link)
                    results.extend(parsed)
                except Exception as e:
                    print(f"❌ OpenAI API error for {org_name}: {e}")

    return pd.DataFrame(results)

def build_prompt(text, start_date):
    return f"""
You are an assistant that extracts upcoming events from messy text.

Today's reference date is: {start_date.strftime('%Y-%m-%d')}

From the text below, extract **only events happening on or after that date**. 
For each event, extract:
- Event Name
- Event Date
- Event Location (if available)
- Event URL (if available)
- A one-line Event Summary

Return the output as strict JSON:
[
  {{
    "Event Name": "...",
    "Event Date": "...",
    "Event Location": "...",
    "Event URL": "...",
    "Event Summary": "..."
  }}
]

Here is the text to analyze:
{text[:12000]}
"""

def parse_llm_output(answer, org_name, org_link):
    try:
        parsed = json.loads(answer)
        if not isinstance(parsed, list):
            raise ValueError("Parsed output is not a list of dictionaries")
        for item in parsed:
            item["Org Name"] = org_name
            item["Org Website"] = org_link
        return parsed
    except Exception as e:
        print("❌ Failed to parse LLM output:")
        print("------ RAW OUTPUT ------")
        print(answer[:1000])
        print("------ END ------")
        print(f"Error: {e}")
        return []
