import os
import sys
import subprocess

# حيلة برمجية ذكية لتثبيت المكتبات إجبارياً داخل السيرفر
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from pypdf import PdfReader
except ImportError:
    install("pypdf")
    from pypdf import PdfReader

try:
    from google import genai
except ImportError:
    install("google-genai")
    from google import genai

try:
    import edge_tts
except ImportError:
    install("edge-tts")
    import edge_tts

import streamlit as st
import asyncio

st.set_page_config(page_title="منصة الشرح الذكي", layout="centered")

st.title("🎓 منصة الشرح الآلي الذكي للطلاب")
st.write("ارفع ملف المادة الخاص بك، وسيقوم الذكاء الاصطناعي بصناعة سيناريو شرح مسموع لك!")

subject_name = st.text_input("📚 اسم المادة الدراسية:", placeholder="مثال: علم الأحياء، تاريخ...")
uploaded_file = st.file_uploader("📂 ارفع ملف الدرس (صيغة PDF فقط):", type=["pdf"])

def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content: text += content + "\n"
    return text

async def generate_voice(text, output_path):
    communicate = edge_tts.Communicate(text, "ar-EG-ShakirNeural")
    await communicate.save(output_path)

if st.button("🚀 ابدأ توليد الشرح الآن"):
    if not subject_name or not uploaded_file:
        st.error("الرجاء إدخال اسم المادة ورفع ملف الـ PDF أولاً.")
    else:
        with st.spinner("⏳ جاري قراءة الملف وتحليله عبر Gemini..."):
            try:
                file_text = extract_text(uploaded_file)
                client = genai.Client(api_key=st.secrets.get("GEMINI_API_KEY", "YOUR_API_KEY"))
                
                prompt = f"أنت أستاذ جامعي متمكن تشرح للطلاب بأسلوب مبسط وشيق جداً ومباشر للامتحان. المادة: {subject_name}. المحتوى المرفق: {file_text[:3000]}. اكتب نصاً مسترسلاً باللغة العربية يشرح هذا المحتوى بالكامل."
                
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt,
                )
                
                explanation_text = response.text
                st.success("✅ تم توليد سيناريو الشرح بنجاح!")
                st.subheader("📝 النص الشارح المتولد:")
                st.write(explanation_text)
                
                with st.spinner("🔊 جاري تحويل الشرح إلى صوت مسموع..."):
                    audio_file = "explanation.mp3"
                    asyncio.run(generate_voice(explanation_text[:800], audio_file))
                    
                    st.subheader("🎧 استمع إلى الشرح الصوتي للمادة:")
                    st.audio(audio_file, format="audio/mp3")
                    st.balloons()
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {str(e)}")
