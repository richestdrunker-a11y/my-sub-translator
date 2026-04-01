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
        
        batch_size = 15
        for i in range(0, len(subs), batch_size):
            batch = subs[i:i + batch_size]
            original_texts = "\n".join([f"{j+1}. {s.text}" for j, s in enumerate(batch)])
            
            prompt = f"Translate these movie subtitles to natural Burmese. Keep the numbering and return ONLY the translated text:\n{original_texts}"
            
            try:
                response = model.generate_content(prompt)
                translated_lines = response.text.strip().split('\n')
                
                for j, line in enumerate(translated_lines):
                    if j < len(batch):
                        clean_text = line.split('. ', 1)[-1] if '. ' in line else line
                        batch[j].text = clean_text
                
                time.sleep(1) 
                
            except Exception:
                time.sleep(5) 
            
            progress = min((i + batch_size) / len(subs), 1.0)
            progress_bar.progress(progress)
            status_text.text(f"ဘာသာပြန်နေသည်... {min(i + batch_size, len(subs))} / {len(subs)}")

        st.success("ဘာသာပြန်ပြီးပါပြီ!")
        
        # --- ပြင်ဆင်ချက်- စိတ်ချရဆုံး နည်းလမ်းဖြင့် SRT စာသားပြန်ထုတ်ခြင်း ---
        # pysrt object ကို manual loop ပတ်ပြီး string ပြန်ဖွဲ့တာက အသေချာဆုံးပါ
        final_srt = ""
        for s in subs:
            final_srt += f"{s.index}\n{s.start} --> {s.end}\n{s.text}\n\n"
        
        st.download_button(
            label="Download Translated SRT",
            data=final_srt,
            file_name="translated_myanmar.srt",
            mime="text/plain"
        )

