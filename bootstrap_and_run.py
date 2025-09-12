import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.aboulahia.com/"

# --------------------------------------
# تعريف جميع السلاسل والكتب
# --------------------------------------
series_books = {
    "حقائق ورقائق": [
        "c01.html","c02.html","c03.html","c04.html","c05.html","c06.html","c07.html",
        "c08.html","c09.html","c10.html","c11.html","c12.html","c13.html","c54.html",
        "c40.html","c66.html"
    ],
    "رسائل السلام": [
        "c21.html","c22.html","c20.html","c23.html","c14.html","c15.html","c17.html",
        "c18.html","c67.html","c76.html","c56.html","c92.html","c85.html","c57.html"
    ],
    "التزكية والترقية": ["c59.html","c60.html","c61.html","c62.html","c64.html"],
    "الإلحاد والدجل": ["c77.html","c78.html","c79.html","c80.html","c88.html","c134.html","c135.html","c136.html"],
    "الدين.. والدجل": [
        "c24.html","c25.html","c26.html","c27.html","c28.html","c16.html","c19.html",
        "c29.html","c45.html","c33.html","c34.html","c33.html","c35.html","c41.html",
        "c37.html","c39.html","c74.html","c46.html","c89.html","c84.html"
    ],
    "دين الله.. ودين البشر": ["c94.html","c95.html","c99.html","c70.html","c71.html","c103.html"],
    "هذه إيران وهذا مشروعها": ["c87.html","c90.html","c47.html","c100.html","c112.html"],
    "أبحاث ودراسات": ["c48.html","c49.html","c50.html","c51.html","c69.html","c101.html"],
    "فقه الأسرة برؤية مقاصدية": ["c31.html","c32.html","c36.html","c38.html","c42.html","c43.html","c44.html"],
    "رسائل شوق وحنين": ["c53.html","c58.html","c73.html","c63.html","c52.html"],
    "التنزيل والتأويل": [
        "c114.html","c115.html","c116.html","c117.html","c118.html","c119.html","c120.html",
        "c121.html","c122.html","c123.html","c124.html","c125.html","c137.html","c138.html",
        "c140.html","c141.html","c142.html","c143.html","c144.html","c145.html","c146.html","c147.html"
    ],
    "كلمات ومقالات": [
        "c102.html","c113.html","c126.html","c127.html","c128.html","c129.html","c130.html",
        "c131.html","c132.html","c133.html","c86.html","c93.html","c139.html"
    ],
    "مسيرة وقيم": ["c152.html","c153.html","c154.html","c155.html","c156.html","c157.html","c158.html"],
}

# --------------------------------------
# دوال المساعدة
# --------------------------------------
def fetch_soup(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.encoding = "utf-8"
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "lxml")
    except Exception as e:
        print(f"⚠️ خطأ في تحميل {url}: {e}")
    return None

def get_book_title(url):
    soup = fetch_soup(url)
    if not soup:
        return url
    meta = soup.find("meta", attrs={"name": "title"})
    if meta and meta.get("content"):
        return meta["content"].strip()
    return url

def get_internal_headings(url):
    soup = fetch_soup(url)
    if not soup:
        return []
    headings = []
    current_h1 = None
    for p in soup.find_all("p"):
        classes = p.get("class", [])
        if "aaa1" in classes:  # مستوى 3
            current_h1 = {
                "id": p.get("id", ""),
                "text": p.get_text(strip=True),
                "subs": []
            }
            headings.append(current_h1)
        elif "a2" in classes and current_h1:  # مستوى 4
            current_h1["subs"].append({
                "id": p.get("id", ""),
                "text": p.get_text(strip=True)
            })
    return headings

# --------------------------------------
# إنشاء sitemap.html
# --------------------------------------
output_file = "sitemap.html"

html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>خريطة الموقع</title>
  <style>
    body { font-family: "Traditional Arabic", serif; background: #f9f9f9; line-height: 1.8; padding: 20px; }
    h1 { text-align: center; color: #004d40; }
    .controls { text-align: center; margin-bottom: 20px; }
    button { margin: 0 5px; padding: 6px 12px; font-size: 14px; cursor: pointer; border-radius: 5px; border: 1px solid #00796b; background: #b2dfdb; }
    details { margin: 6px 0; border: 1px solid #ddd; border-radius: 8px; padding: 6px 10px; background: #fff; }
    summary { font-size: 20px; font-weight: bold; cursor: pointer; color: #00695c; outline: none; }
    .level2 summary { font-size: 18px; color: #00796b; }
    .level3 summary { font-size: 16px; color: #444; }
    .level4 { margin-right: 25px; font-size: 15px; color: #222; padding: 3px 6px; background: #eef7ff; border-radius: 6px; }
    .level4::before { content: "📌 "; color: #1565c0; }
    ul { list-style: none; padding-right: 25px; margin: 0; }
    li { margin: 4px 0; }
    a { text-decoration: none; color: #1565c0; }
    a:hover { text-decoration: underline; font-weight: bold; }
  </style>
  <script>
    function openAll() { document.querySelectorAll('details').forEach(d => d.open = true); }
    function closeAll() { document.querySelectorAll('details').forEach(d => d.open = false); }

    // التحكم في سلوك الروابط/العناوين
    function toggleOrOpen(event, detailsId, url) {
      event.preventDefault();
      const details = document.getElementById(detailsId);
      if (!details.open) {
        details.open = true;
      } else {
        window.open(url, "_blank");
      }
    }
  </script>
</head>
<body>
  <h1>خريطة الموقع</h1>
  <div class="controls">
    <button onclick="openAll()">فتح الكل</button>
    <button onclick="closeAll()">إغلاق الكل</button>
  </div>
"""

# --------------------------------------
# بناء الفهرس
# --------------------------------------
counter = 0
for series, books in series_books.items():
    counter += 1
    series_id = f"series_{counter}"
    html_content += f"<details id='{series_id}'>\n<summary>📚 سلسلة [{series}]</summary>\n"
    for book in books:
        counter += 1
        book_id = f"book_{counter}"
        url = BASE_URL + book.replace(" ", "")
        book_title = get_book_title(url)
        html_content += f'<details id="{book_id}" class="level2">\n'
        html_content += f'<summary><a href="#" onclick="toggleOrOpen(event, \'{book_id}\', \'{url}\')">📖 {book_title}</a></summary>\n'
        headings = get_internal_headings(url)
        for h1 in headings:
            counter += 1
            h1_id = f"h1_{counter}"
            h1_url = f"{url}#{h1['id']}"
            html_content += f'  <details id="{h1_id}" class="level3">\n'
            html_content += f'  <summary><a href="#" onclick="toggleOrOpen(event, \'{h1_id}\', \'{h1_url}\')">{h1["text"]}</a></summary>\n'
            if h1["subs"]:
                html_content += "    <ul>\n"
                for h2 in h1["subs"]:
                    h2_url = f'{url}#{h2["id"]}'
                    html_content += f'      <li class="level4"><a href="{h2_url}" target="_blank">{h2["text"]}</a></li>\n'
                html_content += "    </ul>\n"
            html_content += "  </details>\n"
        html_content += "</details>\n"
    html_content += "</details>\n"

html_content += """
</body>
</html>
"""

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ تم إنشاء خريطة الموقع مع الروابط التفاعلية: {output_file}")
