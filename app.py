# ===============================
# OCR Web App - Streamlit
# ===============================

import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
from docx import Document
import arabic_reshaper
from bidi.algorithm import get_display

# ===============================
# إعداد الصفحة
# ===============================
st.set_page_config(
    page_title="OCR App",
    page_icon="📷",
    layout="centered"
)

st.title("📷 OCR Text Recognition App")
st.write("Upload an image and extract text (English / Arabic)")

# ===============================
# اختيار اللغة
# ===============================
st.subheader("🌍 Select OCR Language")

lang_option = st.radio(
    "Language",
    ["English", "Arabic", "English + Arabic"],
    horizontal=True
)

lang_map = {
    "English": ['en'],
    "Arabic": ['ar'],
    "English + Arabic": ['en', 'ar']
}

selected_lang = lang_map[lang_option]

# ===============================
# تحميل EasyOCR
# ===============================
@st.cache_resource
def load_reader(lang_list):
    return easyocr.Reader(lang_list, gpu=False)

reader = load_reader(selected_lang)

# ===============================
# رفع الصورة
# ===============================
uploaded_file = st.file_uploader(
    "📤 Upload Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # تحويل الصورة لـ OpenCV
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ===============================
    # OCR
    # ===============================
    st.write("🔍 Extracting text...")
    results = reader.readtext(gray, detail=1, paragraph=False)

    if len(results) == 0:
        st.warning("⚠️ No text detected. Try a clearer image.")
    else:
        texts = []

        for bbox, text, prob in results:
            if prob > 0.5:
                # معالجة العربي
                if 'ar' in selected_lang:
                    text = get_display(arabic_reshaper.reshape(text))
                texts.append(text)

        if len(texts) == 0:
            st.warning("⚠️ Text confidence too low.")
        else:
            full_text = "\n".join(texts)

            # ===============================
            # عرض النص بشكل واضح
            # ===============================
            st.subheader("📝 Extracted Text")

            max_len = max(len(line) for line in full_text.split("\n"))
            border = "*" * (max_len + 4)

            output_box = border + "\n"
            for line in full_text.split("\n"):
                output_box += f"* {line.ljust(max_len)} *\n"
            output_box += border

            st.code(output_box)

            # ===============================
            # حفظ في Word
            # ===============================
            doc = Document()
            doc.add_paragraph(full_text)
            doc.save("OCR_result.docx")

            with open("OCR_result.docx", "rb") as f:
                st.download_button(
                    label="⬇️ Download Word File",
                    data=f,
                    file_name="OCR_result.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
