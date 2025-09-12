# indexsit.py
# الزاحف: يجمع meta title و <p class="aaa1"> و <p class="a2"> من صفحات داخل الدومين
import sys
from urllib.parse import urljoin, urlparse
import os
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import urllib.robotparser as robotparser

BASE_URL = "https://www.aboulahia.com/"
DOMAIN = urlparse(BASE_URL).netloc
MAX_PAGES = 1000  # عدل هذا حسب حاجتك
OUTPUT_FILE = "sitemap.html"

# User-Agent: حاول استخدام fake_useragent إن أمكن، وإلا استخدم واحد ثابت
try:
    from fake_useragent import UserAgent
    UA = UserAgent()
    HEADERS = {"User-Agent": UA.random}
except Exception:
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}

session = requests.Session()
session.headers.update(HEADERS)
session.max_redirects = 5
session.timeout = 10

def is_internal(url):
    parsed = urlparse(url)
    return (parsed.netloc == "" or parsed.netloc == DOMAIN) and parsed.scheme in ("", "http", "https")

def obeys_robots(url):
    try:
        rp = robotparser.RobotFileParser()
        robots_url = urljoin(url, "/robots.txt")
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(HEADERS.get("User-Agent","*"), url)
    except Exception:
        return True  # إن تعذر الفحص، نفترض سماحًا (يمكن تعديل هذا السلوك)

def safe_get(url):
    try:
        r = session.get(url, timeout=10)
        if r.status_code == 200 and "text/html" in r.headers.get("Content-Type",""):
            return r.text
    except Exception as e:
        # طباعة الأخطاء لكن لا ينهار البرنامج
        print(f"Error fetching {url}: {e}")
    return None

def parse_page(url, html):
    soup = BeautifulSoup(html, "lxml")
    meta = soup.find("meta", attrs={"name":"title"})
    title = meta["content"].strip() if meta and meta.get("content") else url

    # اجمع جميع aaa1
    aaa1_nodes = []
    for p in soup.find_all("p", class_="aaa1"):
        text = p.get_text(strip=True)
        pid = p.get("id","")
        link = f"{url}#{pid}" if pid else url
        aaa1_nodes.append({"text": text, "link": link, "node": p, "a2": []})

    # اجمع جميع a2
    a2_nodes = []
    for p in soup.find_all("p", class_="a2"):
        text = p.get_text(strip=True)
        pid = p.get("id","")
        link = f"{url}#{pid}" if pid else url
        a2_nodes.append({"text": text, "link": link, "node": p})

    # ربط a2 بأقرب aaa1 سابق (داخل نفس الصفحة)
    if aaa1_nodes and a2_nodes:
        # نستخدم موقع العناصر في الشجرة: نبحث لكل a2 عن اقرب aaa1 يسبقها
        for a2 in a2_nodes:
            node = a2["node"]
            prev = node.find_previous("p", class_="aaa1")
            if prev:
                # نوجد أي aaa1 في القايمة هي نفس الـ prev (عن طريق النص أو id)
                assigned = False
                for aaa1 in aaa1_nodes:
                    if (prev is aaa1["node"]) or (aaa1["node"].get("id") and aaa1["node"]["id"] == prev.get("id")) or (aaa1["text"] == prev.get_text(strip=True)):
                        aaa1["a2"].append({"text": a2["text"], "link": a2["link"]})
                        assigned = True
                        break
                if not assigned:
                    # إن لم نربطه فندعه في قسم منفصل (أو أسفل أول aaa1)
                    aaa1_nodes[0]["a2"].append({"text": a2["text"], "link": a2["link"]})
    else:
        # إن لم توجد aaa1 لكن يوجد a2، نضعها في "غير مصنفة"
        pass

    return {"url": url, "title": title, "aaa1": [{"text":n["text"], "link":n["link"], "a2":[{"text":x["text"], "link":x["link"]} for x in n["a2"]]} for n in aaa1_nodes]}

def crawl(seed, max_pages=MAX_PAGES):
    visited = set()
    to_visit = [seed]
    pages = []
    pbar = tqdm(total=max_pages, desc="Crawling", unit="page")
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        url = url.split("#")[0]
        if url in visited:
            continue
        # robots
        if not obeys_robots(url):
            print(f"Blocked by robots.txt: {url}")
            visited.add(url)
            pbar.update(1)
            continue
        visited.add(url)
        html = safe_get(url)
        if not html:
            pbar.update(1)
            continue
        page_data = parse_page(url, html)
        pages.append(page_data)
        # استخراج الروابط الداخلية
        soup = BeautifulSoup(html, "lxml")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full = urljoin(url, href).split("#")[0]
            if is_internal(full) and full not in visited and full not in to_visit:
                to_visit.append(full)
        pbar.update(1)
    pbar.close()
    return pages

def generate_html(pages, output=OUTPUT_FILE):
    template_head = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>خارطة الموقع</title>
<style>
:root { --bg:#f7fbfb; --card:#ffffff; --accent:#00695c; --muted:#4b6b66; }
body{font-family:"Traditional Arabic", serif;background:var(--bg);margin:0;padding:24px;color:#222}
.container{max-width:1100px;margin:0 auto}
.header{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
h1{margin:0;color:var(--accent)}
.tree{background:var(--card);padding:18px;border-radius:12px;box-shadow:0 6px 18px rgba(0,0,0,0.06)}
.tree ul{list-style:none;padding-right:18px;margin:0;border-right:1px solid #eee}
.tree li{position:relative;margin:8px 0;padding:8px;border-radius:8px;cursor:pointer;transition:background .18s}
.tree li:hover{background:#f0f7f6}
.tree li::before{content:"▸";position:absolute;right:-20px;top:12px;color:var(--accent);transition:transform .18s}
.tree li.open::before{transform:rotate(90deg)}
.tree ul ul{display:none}
.tree li.open>ul{display:block}
.level1{font-size:18px;font-weight:700;color:var(--accent);padding-left:6px}
.level2{font-size:16px;font-weight:600;color:var(--muted);padding-left:6px}
.level3{font-size:15px;color:#333;padding-left:6px}
a{color:inherit;text-decoration:none}
a:hover{text-decoration:underline}
.meta-note{font-size:13px;color:#666;margin-bottom:12px}
.small{font-size:13px;color:#777}
.controls{display:flex;gap:8px;align-items:center}
.btn{background:var(--accent);color:#fff;padding:8px 12px;border-radius:8px;border:none;cursor:pointer}
.input{padding:8px;border-radius:8px;border:1px solid #ddd}
@media (max-width:600px){.header{flex-direction:column;align-items:flex-start;gap:12px}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>خارطة الموقع</h1>
<div class="controls">
<span class="small">تم توليد الخريطة آليًا</span>
</div>
</div>
<div class="tree">
<ul>
"""
    template_tail = """
</ul>
</div>
</div>
<script>
// تفعيل الفتح/الغلق عند النقر
document.querySelectorAll(".tree li").forEach(function(li){
  li.addEventListener("click", function(e){
    e.stopPropagation();
    li.classList.toggle("open");
  });
});
</script>
</body></html>
"""
    parts = [template_head]
    for page in pages:
        safe_title = page["title"].replace("<","&lt;").replace(">","&gt;")
        parts.append(f'<li class="level1"><a href="{page["url"]}" target="_blank">{safe_title}</a>')
        if page.get("aaa1"):
            parts.append("<ul>")
            for a1 in page["aaa1"]:
                parts.append(f'<li class="level2"><a href="{a1["link"]}" target="_blank">{a1["text"]}</a>')
                if a1.get("a2"):
                    parts.append("<ul>")
                    for a2 in a1["a2"]:
                        parts.append(f'<li class="level3"><a href="{a2["link"]}" target="_blank">{a2["text"]}</a></li>')
                    parts.append("</ul>")
                parts.append("</li>")
            parts.append("</ul>")
        parts.append("</li>")
    parts.append(template_tail)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"✅ sitemap generated: {OUTPUT_FILE}")

def main():
    print("Crawling starting from:", BASE_URL)
    pages = crawl(BASE_URL, max_pages=500)  # غيّر max_pages إن أردت
    generate_html(pages)

if __name__ == "__main__":
    main()