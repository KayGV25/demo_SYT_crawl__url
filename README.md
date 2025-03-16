# Demo trích xuất từ hóa vi phạm từ file, từ trang web quảng cáo thông qua đường dẫn
## File
- `article_crawl.py`: Trích xuật nội dung của trang web thông qua url được cho.
- `url_extract.py`: Giao diện để người dùng nhập vào đường dẫn và hiển kết quả trích xuất.
- `syt_extract.py`: Giao diện để người dùng đăng tải file dưới định dạng pdf và hiển kết quả trích xuất.
- `medical_bases_datacrawler.py`: Cào dữ liệu từ trang web ủa Sở Y Tế TPHCM để lấy thông tin của các bệnh viện, cơ sở y tế.
## Cách chạy demo
```bash
pip install -r requirements.txt
streamlit run main.py
```

- Deploy testing link: https://kaygv25-demo-syt-crawl--url-main-myttoy.streamlit.app/
- URL to test filtering: https://thammyviensline.com/tham-vien-sline-su-lua-chon-hoan-hao-cua-ban/