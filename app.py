
import streamlit as st
import google.generativeai as genai
import pysrt
import time

st.set_page_config(page_title="AI Subtitle Translator", layout="centered")
st.title("🇲🇲 Myanmar AI Sub Translator")

# Load API Key from Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Please add GEMINI_API_KEY to Streamlit Secrets!")
    st.stop()

uploaded_file = st.file_uploader("SRT ဖိုင် တင်ပေးပါ", type=["srt"])

if uploaded_file:
    subs = pysrt.from_string(uploaded_file.getvalue().decode("utf-8"))
    st.write(f"စုစုပေါင်းစာကြောင်းရေ: {len(subs)}")
    
    if st.button("ဘာသာပြန်စမယ်"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        progress_bar = st.progress(0)
        
        for i, sub in enumerate(subs):
            prompt = f"Translate this movie subtitle to natural Burmese: {sub.text}"
            response = model.generate_content(prompt)
            sub.text = response.text
            progress_bar.progress((i + 1) / len(subs))
            
        st.success("ဘာသာပြန်ပြီးပါပြီ!")
        st.download_button("Download SRT", data=subs.to_string(), file_name="translated.srt")
      
