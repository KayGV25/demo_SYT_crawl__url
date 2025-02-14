import yake
import streamlit as st
import article_crawl as ac
from flashtext import KeywordProcessor
from collections import Counter

DEFAULT_KEYWORDS = ["mới nhất", "hiện đại nhất", "độc quyền", "duy nhất", "hoàn toàn", "nhất", "hoàn toàn 100%"]

def main(): 
    st.set_page_config(page_title="Demo Lọc Từ khóa Vi phạm", page_icon="🔍")
    st.title("Demo Lọc từ khóa vi phạm từ url")

    url = st.text_input("Nhập URL", placeholder="https://www.example.com")
    keywords = st.text_area("Nhập các từ khóa cần lọc", placeholder="violation, spam, malware")
    
    left_column, mid_column, right_column = st.columns(3, vertical_alignment="center", gap="medium")
    length_keywords_list = left_column.number_input("Nhập độ dài danh sách kết quả", min_value=1, max_value=50, value=10)
    filtered_options = mid_column.checkbox("Lọc các từ khóa theo cơ sở dữ liệu", value=True)
    filter_btn = right_column.button(label="Lọc", on_click=show_result(url=url, keywords=keywords, length_keywords_list=length_keywords_list, filtered_options=filtered_options), use_container_width=True)

def extract_keywords(article: str, keywords: list[str]) -> dict[str, int]:
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_list(keywords)
    extracted_keywords = keyword_processor.extract_keywords(article)
    
    # Count the frequency of each keyword
    keyword_frequency = dict(Counter(extracted_keywords))
    
    return keyword_frequency

def show_result(url:str, keywords:str, length_keywords_list:str, filtered_options:bool):
    # Kiểm tra nếu URL và từ khóa không được nhập
    if not url:
        st.error("Vui lòng nhập đầy đủ thông tin.")
    else:
        if(not keywords):
            keywords = DEFAULT_KEYWORDS
        else:
            # Should be calling from database
            keywords = keywords.split(", ")

        article = ac.crawl_and_clean_article(url=url)

        filtered_keywords = extract_keywords(article["title"] + " " + article["content"], keywords)

        st.success("Kết quả lọc <từ khóa>: <số lần xuất hiện>:\n- " + "\n- ".join([f"{kw}: {f}" for kw, f in filtered_keywords.items()]))

        # st.success(f"Từ khóa khác trong bài viết - Yake: \n- " + "\n- ".join(topYake(article, DEFAULT_KEYWORDS.lower().split(", "), filtered=filtered_options, length=length_keywords_list)))

# def topYake(article, word_list:list[str], length:int=10, filtered:bool=False):
#     kw_extractor = yake.KeywordExtractor(lan="vi", top=100)
#     article_keywords = kw_extractor.extract_keywords(article["content"] + ". " + article["title"])
#     sorted_article_keywords = sorted(article_keywords, key=lambda x: x[1], reverse=False)

#     if not filtered:
#         top = [kw for kw, score in sorted_article_keywords]
#         return top[:length]
#     filtered_keywords = [kw for kw, score in sorted_article_keywords if any(word.lower() in kw.lower() for word in word_list)]
#     return filtered_keywords[:length]

# def top10KeyBert(article):
#     kw_extractor = KeyBERT()
#     article_keywords = kw_extractor.extract_keywords((article["title"] + " " + article["content"]).lower(), keyphrase_ngram_range=(1, 3), stop_words='vietnamese', top_n=10)
#     top10 = [kw for kw, score in article_keywords]
#     return top10


if __name__ == "__main__": 
    main()
