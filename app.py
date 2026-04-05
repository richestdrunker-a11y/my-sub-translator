import streamlit as st
import google.generativeai as genai
import pysrt
import time

st.set_page_config(page_title="Burmese Subtitle Pro", layout="centered")
st.title("🇲🇲 Myanmar AI Sub Translator")

# Secrets ထဲက Key ကို လှမ်းဖတ်ခြင်း
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Error: Streamlit Secrets ထဲမှာ API Key ထည့်ပေးဖို့ လိုပါတယ်။")
    st.stop()

uploaded_file = st.file_uploader("SRT ဖိုင် တင်ပေးပါ", type=["srt"])

if uploaded_file:
    original_name = uploaded_file.name
    new_filename = original_name.replace(".srt", " (Burmese).srt")
    
    content = uploaded_file.getvalue().decode("utf-8", errors='ignore')
    subs = pysrt.from_string(content)
    st.write(f"ဖိုင်အမည်: {original_name}")
    
    if st.button("ဘာသာပြန်စမယ်"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        batch_size = 5 # Quota အတွက် batch ကို ထပ်လျှော့ထားပါတယ်
        for i in range(0, len(subs), batch_size):
            batch = subs[i:i + batch_size]
            original_texts = ""
            for j, s in enumerate(batch):
                original_texts += f"ID-{j+1}: {s.text}\n"
            
            # မြန်မာလိုပဲ ပြန်ပေးဖို့ AI ကို အမိန့်ပေးခြင်း
            prompt = f"""Translate the following subtitles into natural Burmese language. 
            Return ONLY the Burmese lines. Do not include original English or IDs.
            Subtitles:
            {original_texts}"""
            
            try:
                response = model.generate_content(prompt)
                translated_lines = [l.strip() for l in response.text.strip().split('\n') if l.strip()]
                
                for j, line in enumerate(translated_lines):
                    if j < len(batch):
                        batch[j].text = line
                
                time.sleep(6) # Quota limit အတွက် ၆ စက္ကန့် နားခြင်း
                
            except Exception:
                status_text.text("Quota ပြည့်သွားလို့ ၁ မိနစ် ခေတ္တနားနေပါတယ်...")
                time.sleep(65)
            
            progress = min((i + batch_size) / len(subs), 1.0)
            progress_bar.progress(progress)
            status_text.text(f"ဘာသာပြန်နေသည်... {min(i + batch_size, len(subs))} / {len(subs)}")

        st.success("ဘာသာပြန်ပြီးပါပြီ!")
        
        # SRT Manual Format (AttributeError မတက်စေရန်)
        final_srt = ""
        for s in subs:
            final_srt += f"{s.index}\n{s.start} --> {s.end}\n{s.text}\n\n"
        
        st.download_button(
            label="Download Translated SRT",
            data=final_srt,
            file_name=new_filename,
            mime="text/plain"
            )
        
