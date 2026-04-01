import streamlit as st
import google.generativeai as genai
import pysrt
import time

st.set_page_config(page_title="AI Subtitle Translator", layout="centered")
st.title("🇲🇲 Myanmar AI Sub Translator")

# Load API Key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets ထဲမှာ API Key ထည့်ပေးပါ!")
    st.stop()

uploaded_file = st.file_uploader("SRT ဖိုင် တင်ပေးပါ", type=["srt"])

if uploaded_file:
    subs = pysrt.from_string(uploaded_file.getvalue().decode("utf-8", errors='ignore'))
    st.write(f"စုစုပေါင်း စာကြောင်းရေ: {len(subs)}")
    
    if st.button("ဘာသာပြန်စမယ်"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # စာကြောင်း ၁၅ ကြောင်းစီ Batch ခွဲပြီး ဘာသာပြန်မယ် (ပိုမြန်ပြီး Error နည်းစေတယ်)
        batch_size = 15
        for i in range(0, len(subs), batch_size):
            batch = subs[i:i + batch_size]
            original_texts = "\n".join([f"{j+1}. {s.text}" for j, s in enumerate(batch)])
            
            prompt = f"Translate these movie subtitles to natural Burmese. Keep the numbering and return ONLY the translated text:\n{original_texts}"
            
            try:
                response = model.generate_content(prompt)
                translated_lines = response.text.strip().split('\n')
                
                # ဘာသာပြန်ရလာတဲ့စာတွေကို မူရင်းနေရာမှာ ပြန်ထည့်မယ်
                for j, line in enumerate(translated_lines):
                    if j < len(batch):
                        # နံပါတ်စဉ်တွေ ပါလာရင် ဖယ်ထုတ်မယ်
                        clean_text = line.split('. ', 1)[-1] if '. ' in line else line
                        batch[j].text = clean_text
                
                # API Limit မမိအောင် ခဏနားမယ်
                time.sleep(1) 
                
            except Exception as e:
                status_text.text(f"Error တက်လို့ ခဏနားနေပါတယ်... (Batch {i})")
                time.sleep(5) # Error တက်ရင် ၅ စက္ကန့် နားမယ်
            
            # Progress ပြမယ်
            progress = min((i + batch_size) / len(subs), 1.0)
            progress_bar.progress(progress)
            status_text.text(f"ဘာသာပြန်နေသည်... {min(i + batch_size, len(subs))} / {len(subs)}")

        st.success("ဘာသာပြန်ပြီးပါပြီ!")
        st.download_button("Download Translated SRT", data=subs.to_string(), file_name="translated.srt")
        
