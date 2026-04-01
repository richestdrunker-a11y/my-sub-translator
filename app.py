import streamlit as st
import google.generativeai as genai
import pysrt
import time

st.set_page_config(page_title="AI Subtitle Translator", layout="centered")
st.title("🇲🇲 Myanmar AI Sub Translator")

# Secrets ထဲက Key ကိုယူမယ်
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Please add GEMINI_API_KEY to Streamlit Secrets!")
    st.stop()

uploaded_file = st.file_uploader("SRT ဖိုင် တင်ပေးပါ", type=["srt"])

if uploaded_file:
    # SRT ဖိုင်ကို ဖတ်မယ်
    subs = pysrt.from_string(uploaded_file.getvalue().decode("utf-8"))
    st.write(f"စုစုပေါင်း စာကြောင်းရေ: {len(subs)}")
    
    if st.button("ဘာသာပြန်စမယ်"):
        # Model နာမည်ကို အမှန်ပြင်ထားပါတယ်
        model = genai.GenerativeModel('gemini-1.5-flash')
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, sub in enumerate(subs):
            # AI ကို ခိုင်းမယ့် စာသား (Prompt)
            prompt = f"Translate this movie subtitle to natural and informal Burmese. Return ONLY the translated text: {sub.text}"
            
            try:
                response = model.generate_content(prompt)
                sub.text = response.text
            except Exception as e:
                # Error တက်ရင် ခဏနားပြီး ပြန်ကြိုးစားမယ်
                time.sleep(2)
                continue
            
            # Progress ပြပေးမယ်
            progress = (i + 1) / len(subs)
            progress_bar.progress(progress)
            status_text.text(f"ဘာသာပြန်နေသည်... {i+1} / {len(subs)}")

        st.success("ဘာသာပြန်ပြီးပါပြီ!")
        # ဘာသာပြန်ပြီးသားဖိုင်ကို ပြန်ထုတ်ပေးမယ်
        st.download_button("Download Translated SRT", data=subs.to_string(), file_name="translated.srt")
        
