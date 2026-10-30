#!/usr/bin/env python3
"""Fetch Geoawesome feed, preserve summaries, optionally translate with OpenAI API.
No full-text scraping or republication. Feed may be inaccessible; exit safely without deleting cached items.
"""
import os, re, json, hashlib, html, datetime
from pathlib import Path
from urllib.parse import urlparse
import requests
import feedparser
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data.json'
FEEDS = ['https://geoawesome.com/feed/', 'https://geoawesome.com/category/news/feed/']
HEADERS = {'User-Agent': 'GeoSpatialVietDigest/1.0 (+independent Vietnamese link aggregator)'}
CATEGORIES = {
    'geoai':'GeoAI', 'ai':'GeoAI', 'earth observation':'Viễn thám & EO',
    'remote sensing':'Viễn thám & EO', 'satellite':'Vệ tinh & Không gian',
    'space':'Vệ tinh & Không gian', 'gis':'Công nghệ GIS', 'geodev':'Công nghệ GIS',
    'maps':'Bản đồ số', 'mapping':'Bản đồ số', 'smart city':'Đô thị thông minh',
}

def clean(s):
    return re.sub(r'\s+', ' ', BeautifulSoup(html.unescape(s or ''), 'html.parser').get_text(' ', strip=True)).strip()

def classify(tags, title):
    hay=' '.join(tags+[title]).lower()
    for term, category in CATEGORIES.items():
        if term in hay: return category
    return 'Khác'

def translate(title, excerpt):
    key=os.environ.get('OPENAI_API_KEY')
    if not key: return None
    payload={
       'model':os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini'),
       'messages':[{'role':'system','content':
           'Bạn là biên tập viên bản tin công nghệ địa không gian. Dựa CHỈ vào tiêu đề và phần trích dẫn được cung cấp, hãy viết JSON với keys title_vi, summary_vi, keywords. '
           'title_vi là tiêu đề tiếng Việt chính xác. summary_vi 1-2 câu, tối đa 60 từ; keywords là mảng tối đa 3 cụm ngắn bằng tiếng Việt. '
           'Thêm geo_perspective gồm science_value, vietnam_application, tools (mảng tên công cụ hoặc phương pháp, tối đa 4), research_prompt, evidence_limit. Đây là GỢI Ý phân tích của người làm địa lý, không phải nội dung hay kết luận từ bài nguồn. Giải thích ứng dụng ở Việt Nam bằng ngôn ngữ có điều kiện (có thể, cần kiểm chứng); không tuyên bố nghiên cứu đã làm hay gán các công cụ cho tác giả nếu nguồn không nói. evidence_limit nêu rõ chỉ dựa vào tiêu đề/trích đoạn RSS, phải đọc bài gốc để xác nhận. Độ dài mỗi trường tối đa 45 từ. Không dịch nguyên văn toàn bộ bài. Không thêm dấu markdown.'},
           {'role':'user','content':json.dumps({'title':title, 'excerpt':excerpt},ensure_ascii=False)}],
       'response_format':{'type':'json_object'},'temperature':0.2
    }
    try:
        resp=requests.post('https://api.openai.com/v1/chat/completions',headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},json=payload,timeout=35)
        resp.raise_for_status()
        parsed=json.loads(resp.json()['choices'][0]['message']['content'])
        if parsed.get('title_vi') and parsed.get('summary_vi'):
            return parsed
    except Exception as exc:
        print('Translation unavailable:',str(exc)[:180])
    return None

def main():
    existing=json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else {'articles':[]}
    items={row['url']:row for row in existing.get('articles', []) if row.get('url')}
    changed=False; retrieved=0
    for feed_url in FEEDS:
        try:
            response=requests.get(feed_url,headers=HEADERS,timeout=22)
            response.raise_for_status()
            parsed=feedparser.parse(response.content)
            if not parsed.entries: raise ValueError('Feed returned zero articles')
            for entry in parsed.entries[:35]:
                url=entry.get('link','').split('#')[0]
                host=urlparse(url).hostname or ''
                if host not in ('geoawesome.com','www.geoawesome.com'): continue
                retrieved += 1
                if url in items: continue
                title=clean(entry.get('title',''))
                excerpt=clean(entry.get('summary',''))[:850]
                if not title: continue
                pub=entry.get('published_parsed') or entry.get('updated_parsed')
                date=datetime.date(*pub[:3]).isoformat() if pub else datetime.date.today().isoformat()
                tags=[x.get('term','') for x in entry.get('tags',[])]
                translated=translate(title,excerpt)
                article={
                    'id':hashlib.sha1(url.encode()).hexdigest()[:14],
                    'title_original':title,
                    'title_vi':translated['title_vi'] if translated else title,
                    'summary_vi':translated['summary_vi'] if translated else 'Chưa có tóm tắt tiếng Việt; xem nội dung nguyên bản tại nguồn Geoawesome.',
                    'published':date,'author':clean(entry.get('author','Geoawesome')),
                    'category':classify(tags,title),'url':url,
                    'keywords':translated.get('keywords',[])[:3] if translated else tags[:3],
                    'geo_perspective':translated.get('geo_perspective') if translated and isinstance(translated.get('geo_perspective'),dict) else None
                }
                items[url]=article;changed=True
        except Exception as e:
            print('Feed not available:',feed_url,str(e)[:200])
    if not retrieved:
        print('No feeds accessible; preserving existing data without changing update timestamp.')
        return
    entries=sorted(items.values(),key=lambda x:x.get('published',''),reverse=True)[:150]
    status='translated' if os.environ.get('OPENAI_API_KEY') else 'untranslated'
    result={'updated_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec='seconds'),'status':status,'articles':entries}
    DATA.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Feed items:',retrieved,'new:',changed,'stored:',len(entries))

if __name__=='__main__':main()
