import os
import csv
from newspaper import Article
from bs4 import BeautifulSoup
import requests
import re

ADDRESS_KEYWORDS = ["địa chỉ", "trụ sở", "chi nhánh", "cơ sở", "khu vực", "addr", "add", "đ.c", "đc", "đ/c"]
VIETNAM_CITIES = [
    "Hà Nội", "HN", "Hồ Chí Minh", "TPHCM", "HCM", "Đà Nẵng", "DN", "ĐN",
    "Hải Phòng", "HP", "Cần Thơ", "CT", "Nha Trang", "NT", "Vũng Tàu", "VT"
]
NAME_KEYWORDS = ["tên", "trung tâm", "bệnh viện", "cơ sở", "phòng khám", "hệ thống", "thẩm mỹ", "thẩm mĩ", "nha khoa"]

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
class _article:
    def __init__(self, title: str, content: str, footer: str):
        self.title = title
        self.content = content
        self.footer = footer
        self.address = None
        self.place_name = None

def crawl_article(url) -> _article:
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        # Use BeautifulSoup to extract the footer
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        footer = soup.find('footer')
        footer_text = footer.get_text(separator='. ') if footer else ""
        
        return {"title": article.title, "content": article.text, "footer": footer_text}
    except Exception as e:
        print(f"Error crawling article: {e}")
        return None

def clean_content(text: str) -> str:
    text = text.replace('\n\n', '. ').replace('\n', ' ').replace('\t', ' ').replace('- ', ' ').replace('..', '.')
    return ' '.join(text.split())

def extract_address(text: str) -> str:
    lines = text.split(". ")  # Split by sentences
    for line in lines:
        if line != "":
            for keyword in ADDRESS_KEYWORDS:
                if keyword.lower() in line.lower():
                    return line.strip()
    
    for line in lines:
        if line != "":
            for city in VIETNAM_CITIES:
                if city.lower() in line.lower():
                    return line.strip()
    
    return None
def extract_place_name(text: str) -> str:
    lines = re.split(r"[\-.*\n]", text)  # Split using multiple separators
    for line in lines:
        for keyword in NAME_KEYWORDS:
            if keyword.lower() in line.lower():
                return line.strip()
    return None
def crawl_and_clean_article(url: str) -> _article:
    article = crawl_article(url)
    if not article:
        return None
    
    article["content"] = clean_content(article["content"])
    article["footer"] = clean_content(article["footer"])
    address = extract_address(article["footer"])
    place_name = extract_place_name(article["content"])
    if place_name == None:
        place_name = extract_place_name(article["footer"])
    article["address"] = address
    article["place_name"] = place_name
    return article

def crawl_and_clean_articles(url_list: list) -> list[_article]:
    articles = []
    for url in url_list:
        article = crawl_and_clean_article(url)
        if article:
            articles.append(article)
    return articles

def output(articles: list, title_as_filename: bool = True, csv_output: bool = False):
    if not csv_output:
        __output_file(articles, title_as_filename=title_as_filename)
    else:
        __output_csv(articles)

def __output_file(articles: list, title_as_filename: bool = True):
    if not articles:
        print("Error: No articles found.")
        return
    
    out_path = "res"
    os.makedirs(out_path, exist_ok=True)
    
    for article in articles:
        filename = f"{article['title']}.txt" if title_as_filename else f"{articles.index(article) + 1}.txt"
        with open(os.path.join(out_path, filename), "w") as f:
            f.write(f"Title: {article['title']}\n\n")
            f.write(f"Content:\n{article['content']}\n\n")
            f.write(f"Footer:\n{article['footer']}\n\n")
            f.write(f"Extracted Address: {article['address']}\n\n")
            f.write(f"Extracted Place Name: {article['place_name']}")
        print(f"Article {article['title']} saved to {out_path}")

def __output_csv(articles: list):
    with open('res.csv', 'w', newline='') as csvfile:
        fieldnames = ['title', 'content', 'footer', 'address']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(articles)
    print("CSV file created successfully")

if __name__ == "__main__":
    urls = [
        "https://thammyviensline.com/tham-vien-sline-su-lua-chon-hoan-hao-cua-ban/",
        "https://nhakhoakim.com/"
        # "https://plo.vn/csgt-thong-tin-ban-dau-vu-o-to-khach-bi-lat-o-phu-yen-post833337.html",
        # "https://tapchigiaothong.vn/rao-ban-vinfast-vf3-sau-10-km-nguoi-dung-noi-thang-mot-dieu-183250207203953709.htm",
        # "https://vov.vn/the-gioi/toretsk-ruc-lua-ukraine-tuyen-bo-day-lui-moi-cuoc-tan-cong-cua-nga-tai-day-post1153466.vov"
    ]
    output(crawl_and_clean_articles(urls), title_as_filename=False, csv_output=False)
