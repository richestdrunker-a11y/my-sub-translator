import streamlit as st
import google.generativeai as genai
import pysrt
import time

st.set_page_config(page_title="Burmese Subtitle Pro", layout="centered")
st.title("🇲🇲 Myanmar AI Sub Translator")

# Secrets မှ Key ကို ယူခြင်း
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets ထဲမှာ GEMINI_API_KEY မရှိသေးပါ။")
    st.stop()

uploaded_file = st.file_uploader("SRT ဖိုင် တင်ပေးပါ", type=["srt"])

if uploaded_file:
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
        
        batch_size = 5 # Quota အတွက် နည်းနည်းစီပဲ လုပ်မယ်
        for i in range(0, len(subs), batch_size):
            batch = subs[i:i + batch_size]
            
            # AI ကို ပို့မယ့် စာသားပုံစံ
            to_translate = "\n".join([f"[{j}] {s.text}" for j, s in enumerate(batch)])
            
            # ပိုမိုပြတ်သားတဲ့ Prompt
            prompt = f"""You are a movie subtitle translator. 
            Translate the following English lines into natural Burmese language.
            IMPORTANT: Return ONLY the Burmese text, line by line. 
            Keep the [number] tag at the start of each line.
            Do not speak English in your response.
            
            Lines:
            {to_translate}"""
            
            try:
                response = model.generate_content(prompt)
                lines = response.text.strip().split('\n')
                
                # ရလာတဲ့ မြန်မာစာသားတွေကို မူရင်းနေရာမှာ အစားထိုးမယ်
                for l in lines:
                    if "[" in l and "]" in l:
                        try:
                            idx_str = l.split(']')[0].replace('[', '')
                            idx = int(idx_str)
                            translated_text = l.split(']', 1)[1].strip()
                            if idx < len(batch):
                                batch[idx].text = translated_text
                        except:
                            continue
                
                time.sleep(7) # Quota protection
                
            except Exception:
                status_text.text("Quota ပြည့်သွားလို့ ခဏနားနေပါတယ်။")
                time.sleep(65)
            
            progress = min((i + batch_size) / len(subs), 1.0)
            progress_bar.progress(progress)
            status_text.text(f"ဘာသာပြန်နေသည်... {min(i + batch_size, len(subs))} / {len(subs)}")

        st.success("ဘာသာပြန်ပြီးပါပြီ!")
        
        # SRT ပြန်ဖွဲ့ခြင်း (AttributeError ကင်းစေရန်)
        final_srt = ""
        for s in subs:
            final_srt += f"{s.index}\n{s.start} --> {s.end}\n{s.text}\n\n"
        
        st.download_button(
            label="Download Translated SRT",
            data=final_srt,
            file_name=new_filename,
            mime="text/plain"
                        )
                        
