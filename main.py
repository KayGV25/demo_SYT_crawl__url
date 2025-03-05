import streamlit as st

pages = {
    "Trích Xuất Từ Ngữ Vi Phạm": [
        st.Page("syt_extract.py", title = "File PDF"),
        st.Page("url_extract.py", title = "Url")
    ]
}

pg = st.navigation(pages)
pg.run()