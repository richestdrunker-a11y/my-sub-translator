import streamlit as st
import google.generativeai as genai
import pysrt
import time

st.set_page_config(page_title="Burmese Subtitle Pro", layout="centered")
st.title("🇲🇲 Myanmar AI Sub Translator")

# Secrets မှ API Key ကို ခေါ်ယူခြင်း
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets ထဲမှာ API Key ထည့်ရန် လိုအပ်ပါသည်။")
    st.stop()

uploaded_file = st.file_uploader("SRT ဖိုင် တင်ပေးပါ", type=["srt"])

if uploaded_file:
    # ဖိုင်နာမည်ကို (Burmese).srt ဟု ပြောင်းလဲသတ်မှတ်ခြင်း
    original_name = uploaded_file.name
    new_filename = original_name.replace(".srt", " (Burmese).srt")
    
    content = uploaded_file.getvalue().decode("utf-8", errors='ignore')
    subs = pysrt.from_string(content)
    st.write(f"ဖိုင်အမည်: {original_name}")
    st.write(f"စုစုပေါင်း: {len(subs)} ကြောင်း")
    
    if st.button("ဘာသာပြန်စမယ်"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        batch_size = 10
        for i in range(0, len(subs), batch_size):
            batch = subs[i:i + batch_size]
            original_texts = "\n".join([f"{j+1}. {s.text}" for j, s in enumerate(batch)])
            
            prompt = f"Translate these movie subtitles to natural Burmese. Return ONLY the translated lines:\n{original_texts}"
            
            try:
                response = model.generate_content(prompt)
                translated_lines = [l.strip() for l in response.text.split('\n') if l.strip()]
                
                for j, line in enumerate(translated_lines):
                    if j < len(batch):
                        clean_text = line.split('. ', 1)[-1] if '. ' in line else line
                        batch[j].text = clean_text
                
                # Quota limit မမိစေရန် ၃ စက္ကန့်စီ နားခြင်း
                time.sleep(3) 
                
            except Exception as e:
                # Quota ပြည့်သွားပါက ၁ မိနစ် စောင့်ဆိုင်းခြင်း
                status_text.text("Quota ပြည့်သွားသဖြင့် ၁ မိနစ် ခေတ္တနားနေပါသည်။ မပိတ်လိုက်ပါနဲ့...")
                time.sleep(60)
            
            progress = min((i + batch_size) / len(subs), 1.0)
            progress_bar.progress(progress)
            status_text.text(f"ဘာသာပြန်နေသည်... {min(i + batch_size, len(subs))} / {len(subs)}")

        st.success("ဘာသာပြန်ခြင်း ပြီးဆုံးပါပြီ!")
        
        # SRT Format ပြန်လည်ဖွဲ့စည်းခြင်း
        final_srt = ""
        for s in subs:
            final_srt += f"{s.index}\n{s.start} --> {s.end}\n{s.text}\n\n"
        
        st.download_button(
            label="Download Translated SRT",
            data=final_srt,
            file_name=new_filename,
            mime="text/plain"
                    )
            
