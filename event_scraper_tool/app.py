import streamlit as st
import pandas as pd
import openai
import os

st.set_page_config(layout="wide")
st.title("🔍 Pittsburgh Event Scraper & Extractor")

# Tabs
tab1, tab2 = st.tabs(["📁 Upload & Extract", "💬 Chat with Events"])

with tab1:
    uploaded_file = st.file_uploader("Upload your Events.xlsx file", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.success("File uploaded. Previewing first 5 rows:")
        st.dataframe(df.head())

        # Optional: Save uploaded data for chat
        st.session_state['event_data'] = df

with tab2:
    st.subheader("Ask questions about your events")

    if 'event_data' not in st.session_state:
        st.warning("Please upload and extract event data in the first tab before chatting.")
    else:
        df = st.session_state['event_data']
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        user_input = st.text_input("Ask something like 'Show me all events in August'", key="chat_input")

        if user_input:
            df_sample = df.to_csv(index=False)[:6000]  # Limit for token size
            prompt = f"""
You are an assistant that helps a user analyze a CSV of upcoming events.

Here is the data:
{df_sample}

Now answer this question:
{user_input}
"""
            openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                answer = response['choices'][0]['message']['content']
            except Exception as e:
                answer = f"❌ Error from OpenAI: {str(e)}"

            st.session_state.chat_history.append((user_input, answer))

        # Display chat
        for question, response in reversed(st.session_state.chat_history):
            st.markdown(f"**You:** {question}")
            st.markdown(f"**Assistant:** {response}")
