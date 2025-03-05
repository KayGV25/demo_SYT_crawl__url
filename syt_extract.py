import streamlit as st
import PyPDF2
import re

banned_words = ["hoàn toàn", "100%", "mới nhất", "hiện đại nhất", "độc quyền", "duy nhất"]

st.title("Demo Trích Xuất Từ Ngữ Vi Phạm từ File PDF")
st.write("Tải lên file PDF chứa nội dung quảng cáo để kiểm tra các từ ngữ vi phạm.")

uploaded_file = st.file_uploader("quang_cao_y_te_sai_su_that.pdf", type=["pdf"])

def extract_text_from_pdf(file):
    """Trích xuất toàn bộ văn bản từ file PDF."""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        st.error(f"Đã xảy ra lỗi khi đọc file PDF: {e}")
    return text

def find_banned_words(text, banned_words):
    violations = {}
    for word in banned_words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        matches = pattern.findall(text)
        if matches:
            violations[word] = len(matches)
    return violations

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    
    if not text:
        st.error("Không thể trích xuất văn bản từ file PDF này.")
    else:
        st.subheader("Nội dung trích xuất:")
        st.text_area("Nội dung file PDF", text, height=300)

        violations = find_banned_words(text, banned_words)
        
        st.subheader("Kết quả kiểm tra từ ngữ vi phạm:")
        if violations:
            for word, count in violations.items():
                st.write(f" - **'{word}'** xuất hiện **{count}** lần.")
        else:
            st.success("Không tìm thấy từ ngữ vi phạm nào trong file PDF.")