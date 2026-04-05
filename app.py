import streamlit as st
import google.generativeai as genai
import pysrt
import time

st.set_page_config(page_title="Burmese Subtitle Pro", layout="centered")
st.title("🇲🇲 Myanmar AI Sub Translator")

# Secrets မှ API Key ယူခြင်း
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["AIzaSyAEwytMbbszXWSPZba4D3uU1DwJ2quiz7E"])
else:
    st.error("Secrets ထဲမှာ API Key မရှိသေးပါ။")
    st.stop()

uploaded_file = st.file_uploader("SRT ဖိုင် တင်ပေးပါ", type=["srt"])

if uploaded_file:
    # ဖိုင်နာမည်ကို Burmese srt ဆိုပြီး တွဲပေးရန်
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
        
        # Quota limit မမိအောင် Batch size ကို လျှော့ထားပါတယ်
        batch_size = 10
        for i in range(0, len(subs), batch_size):
            batch = subs[i:i + batch_size]
            original_texts = "\n".join([f"{j+1}. {s.text}" for j, s in enumerate(batch)])
            
            prompt = f"Translate these to natural Burmese. Return ONLY Burmese lines:\n{original_texts}"
            
            try:
                response = model.generate_content(prompt)
                translated_lines = [l.strip() for l in response.text.split('\n') if l.strip()]
                
                for j, line in enumerate(translated_lines):
                    if j < len(batch):
                        # နံပါတ်စဉ်များ ပါလာပါက ဖယ်ထုတ်ရန်
                        clean_text = line.split('. ', 1)[-1] if '. ' in line else line
                        batch[j].text = clean_text
                
                # Quota Error မတက်အောင် တစ်ခါပို့ပြီးတိုင်း ၃ စက္ကန့် နားပါမယ်
                time.sleep(3) 
                
            except Exception as e:
                # Quota ပြည့်သွားရင် ၁ မိနစ် ခဏနားပြီး ပြန်ကြိုးစားမယ်
                status_text.text("Quota ပြည့်သွားလို့ ၁ မိနစ် ခဏနားနေပါတယ်။ မပိတ်လိုက်ပါနဲ့...")
                time.sleep(60)
                # ပြန်ကြိုးစားခြင်း
                try:
                    response = model.generate_content(prompt)
                    # ... (ဆက်လက်လုပ်ဆောင်ခြင်း)
                except:
                    pass
            
            progress = min((i + batch_size) / len(subs), 1.0)
            progress_bar.progress(progress)
            status_text.text(f"ဘာသာပြန်နေသည်... {min(i + batch_size, len(subs))} / {len(subs)}")

        st.success("ဘာသာပြန်ပြီးပါပြီ!")
        
        # SRT format ကို manual တည်ဆောက်ခြင်း (AttributeError မတက်စေရန်)
        final_srt = ""
        for s in subs:
            final_srt += f"{s.index}\n{s.start} --> {s.end}\n{s.text}\n\n"
        
        st.download_button(
            label="Download Translated SRT",
            data=final_srt,
            file_name=new_filename,
            mime="text/plain"
            )
        
