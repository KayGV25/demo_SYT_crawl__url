import streamlit as st
import pdfplumber
import re

banned_words = ["hoàn toàn", "100%", "mới nhất", "hiện đại nhất", "duy nhất", "độc quyền"]
name_keywords = ["tên", "trung tâm", "bệnh viện", "cơ sở", "phòng khám", "hệ thống", "thẩm mỹ", "thẩm mĩ", "nha khoa"]
location_keywords = ["địa chỉ", "trụ sở", "chi nhánh", "cơ sở", "khu vực", "addr", "add", "đ.c", "đc", "đ/c"]

st.title("Demo Kiểm Tra Quảng Cáo Y Tế")
st.write("Tải lên file PDF chứa nội dung quảng cáo để kiểm tra các vi phạm về luật quảng cáo y tế.")

uploaded_file = st.file_uploader("Chọn file PDF", type=["pdf"])

def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.error(f"Đã xảy ra lỗi khi đọc file PDF: {e}")
    return text

def find_banned_words(text, banned_words):
    violations = {}
    text_lower = text.lower()
    for word in banned_words:
        pattern = re.compile(re.escape(word.lower()))
        matches = pattern.findall(text_lower)
        if matches:
            violations[word] = len(matches)
    return violations

def check_required_info(text):
    violations = {}
    text_lower = text.lower()
    if not any(re.search(keyword.lower(), text_lower) for keyword in name_keywords):
        violations["Điều 9, Ý 2a: Tên của cơ sở"] = "Chưa có thông tin tên của cơ sở khám bệnh, chữa bệnh."
        
    if not any(re.search(keyword.lower(), text_lower) for keyword in location_keywords):
        violations["Điều 9, Ý 2a: Thông tin địa chỉ"] = "Chưa có thông tin địa chỉ, trụ sở hoặc chi nhánh của cơ sở khám bệnh, chữa bệnh."
    return violations

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    
    if not text: st.error("Không thể trích xuất văn bản từ file PDF này.")
    else:
        st.subheader("Nội dung trích xuất:")
        st.text_area("Nội dung file PDF", text, height=300)
        
        banned_violations = find_banned_words(text, banned_words)
        required_info_violations = check_required_info(text)
        
        st.subheader("Kết quả kiểm tra:")
        violations_exist = False
        
        if banned_violations:
            violations_exist = True
            st.write("**Vi phạm Điều 8, Ý 11:** Sử dụng từ ngữ cấm hoặc có ý nghĩa tương tự")
            for word, count in banned_violations.items():
                st.write(f" - **'{word}'** xuất hiện **{count}** lần.")
        else:
            st.write("Không phát hiện vi phạm về từ ngữ cấm (Điều 8, Ý 11).")
            
        if required_info_violations:
            violations_exist = True
            st.write("**Vi phạm Điều 9, Ý 2a:** Thiếu thông tin bắt buộc của cơ sở khám bệnh, chữa bệnh")
            for violation, message in required_info_violations.items():
                st.write(f" - {violation}: {message}")
        else:
            st.write("Đã có đầy đủ thông tin bắt buộc (Điều 9, Ý 2a).")
        
        st.subheader("Kết quả phân loại:")
        if violations_exist:
            st.error("Sai luật")
        else:
            st.success("Đúng luật")