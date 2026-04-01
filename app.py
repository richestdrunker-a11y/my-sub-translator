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
    content = uploaded_file.getvalue().decode("utf-8", errors='ignore')
    subs = pysrt.from_string(content)
    st.write(f"စုစုပေါင်း စာကြောင်းရေ: {len(subs)}")
    
    if st.button("ဘာသာပြန်စမယ်"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Batch size ကို ၁၀ ကြောင်းပဲ ထားပါမယ် (ပိုသေချာအောင်)
        batch_size = 10
        for i in range(0, len(subs), batch_size):
            batch = subs[i:i + batch_size]
            original_texts = ""
            for j, s in enumerate(batch):
                original_texts += f"Line {j+1}: {s.text}\n"
            
            # AI ကို ခိုင်းတဲ့ စာသားကို ပိုမိုတိကျအောင် ပြင်ဆင်ထားပါတယ်
            prompt = f"""You are a professional movie translator. 
            Translate the following English subtitle lines into natural Burmese.
            Provide ONLY the Burmese translation, line by line.
            Do not include the English text or 'Line X:' prefix.
            
            Subtitles to translate:
            {original_texts}"""
            
            try:
                response = model.generate_content(prompt)
                translated_lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
                
                for j, translated_text in enumerate(translated_lines):
                    if j < len(batch):
                        batch[j].text = translated_text
                
                time.sleep(1) # API Limit မမိအောင်
                
            except Exception:
                time.sleep(5) 
            
            progress = min((i + batch_size) / len(subs), 1.0)
            progress_bar.progress(progress)
            status_text.text(f"ဘာသာပြန်နေသည်... {min(i + batch_size, len(subs))} / {len(subs)}")

        st.success("ဘာသာပြန်ပြီးပါပြီ!")
        
        # SRT Format အမှန်အတိုင်း ပြန်ဖွဲ့ခြင်း
        final_srt = ""
        for s in subs:
            final_srt += f"{s.index}\n{s.start} --> {s.end}\n{s.text}\n\n"
        
        st.download_button(
            label="Download Translated SRT",
            data=final_srt,
            file_name="translated_myanmar.srt",
            mime="text/plain"
        )
            
