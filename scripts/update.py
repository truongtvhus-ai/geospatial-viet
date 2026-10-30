#!/usr/bin/env python3
"""GeoSpatial Viet 3.0: full-article reading for original Vietnamese analysis.
Never republishes original full text or translation without permission.
"""
import os, re, json, hashlib, html, datetime, time
from pathlib import Path
from urllib.parse import urlparse
import requests, feedparser, trafilatura
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data.json'
FEEDS=['https://geoawesome.com/feed/','https://geoawesome.com/category/news/feed/']
HEADERS={'User-Agent':'GeoSpatialViet/3.0 (independent research digest; contact site owner)'}
CATEGORIES={'geoai':'GeoAI','earth observation':'Viễn thám & EO','remote sensing':'Viễn thám & EO','satellite':'Vệ tinh & Không gian','space':'Vệ tinh & Không gian','gis':'Công nghệ GIS','geodev':'Công nghệ GIS','maps':'Bản đồ số','mapping':'Bản đồ số','smart city':'Đô thị thông minh','ai':'GeoAI'}
MAX_NEW=int(os.getenv('MAX_NEW_ARTICLES','8'))
MAX_WORDS=int(os.getenv('MAX_SOURCE_WORDS','8500'))

def clean(s):return re.sub(r'\s+',' ',BeautifulSoup(html.unescape(s or ''),'html.parser').get_text(' ',strip=True)).strip()
def classify(tags,title):
    hay=' '.join(tags+[title]).lower()
    return next((v for k,v in CATEGORIES.items() if k in hay),'Khác')
def extract(url):
    """Read original text in memory only; do not store or publish the extracted text."""
    try:
        r=requests.get(url,headers=HEADERS,timeout=30)
        r.raise_for_status()
        text=trafilatura.extract(r.text,include_comments=False,include_tables=True,include_links=False,favor_precision=True)
        return ' '.join((text or '').split()[:MAX_WORDS])
    except Exception as e:
        print('Source extraction failed:',url,str(e)[:150]);return ''

def generate(title,excerpt,source_text):
    key=os.getenv('OPENAI_API_KEY')
    if not key:return None
    source_status='full_article' if len(source_text.split())>=180 else 'rss_only'
    evidence=(source_text if source_status=='full_article' else excerpt)[:37000]
    system='''Bạn là biên tập viên học thuật về địa không gian. Hãy trả về một đối tượng JSON với: title_vi, summary_vi, keywords (mảng tối đa 5), analysis (đối tượng gồm lead, scientific_context, methods_and_data, findings_and_implications, limitations, vietnam_applications, learning_activity, editorial_note), geo_perspective (science_value, vietnam_application, tools là mảng, research_prompt, evidence_limit). Viết bằng tiếng Việt rõ ràng, giàu thông tin, tổng 700–1100 từ NẾU tư liệu đủ; nếu thiếu thì viết ngắn và nói rõ. Bài phân tích phải là sản phẩm viết mới, cấu trúc và cách diễn đạt độc lập; TUYỆT ĐỐI không dịch nguyên văn, không tái tạo hoặc bám sát bố cục bài gốc, không trích đoạn dài, không sao chép bảng. Không bịa số liệu, tác giả, trích dẫn, DOI, công cụ hoặc kết quả. Phân biệt nội dung bài viết với gợi ý ứng dụng. scientific_context: nền tảng khoa học; methods_and_data: dữ liệu/phương pháp thật sự được nguồn đề cập, hoặc nêu không rõ; findings_and_implications: các luận điểm chính dưới dạng tổng hợp; limitations: mức độ chắc chắn và giới hạn; vietnam_applications: các ví dụ khả thi (đề xuất, không được gán cho tác giả); learning_activity: bài tập cho sinh viên; editorial_note: lưu ý độc lập và xác minh nguồn. summary_vi tối đa 85 từ. evidence_limit nói rõ dữ liệu căn cứ toàn bài hay trích đoạn RSS. Trả JSON thuần.'''
    try:
        r=requests.post('https://api.openai.com/v1/chat/completions',headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},json={'model':os.getenv('OPENAI_MODEL','gpt-4.1-mini'),'temperature':0.25,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':system},{'role':'user','content':json.dumps({'title':title,'excerpt':excerpt,'source_basis':source_status,'article_content_for_analysis_only':evidence},ensure_ascii=False)}]},timeout=115)
        r.raise_for_status(); obj=json.loads(r.json()['choices'][0]['message']['content'])
        if not obj.get('title_vi') or not isinstance(obj.get('analysis'),dict):raise ValueError('Malformed output')
        return obj,source_status
    except Exception as e:
        print('AI analysis failed:',str(e)[:250]);return None

def main():
    existing=json.loads(DATA.read_text('utf-8')) if DATA.exists() else {'articles':[]}
    items={a['url']:a for a in existing.get('articles',[]) if a.get('url')}
    seen=0;new=0;analyzed=0
    for feed in FEEDS:
        try:
            r=requests.get(feed,headers=HEADERS,timeout=25);r.raise_for_status()
            parsed=feedparser.parse(r.content)
            if not parsed.entries:raise ValueError('No entries')
            for ent in parsed.entries[:40]:
                url=ent.get('link','').split('#')[0]
                if urlparse(url).hostname not in ('geoawesome.com','www.geoawesome.com'):continue
                seen+=1
                if url in items or new>=MAX_NEW:continue
                title=clean(ent.get('title',''))
                if not title:continue
                excerpt=clean(ent.get('summary',''))[:1500]
                pub=ent.get('published_parsed') or ent.get('updated_parsed')
                published=datetime.date(*pub[:3]).isoformat() if pub else datetime.date.today().isoformat()
                tags=[x.get('term','') for x in ent.get('tags',[])]
                full=extract(url)
                result=generate(title,excerpt,full)
                translated,basis=result if result else ({},'rss_only')
                article={'id':hashlib.sha1(url.encode()).hexdigest()[:14], 'title_original':title,'title_vi':translated.get('title_vi',title),'summary_vi':translated.get('summary_vi','Chưa có bản phân tích tiếng Việt; xem bài gốc.'),'published':published,'author':clean(ent.get('author','Geoawesome')),'category':classify(tags,title),'url':url,'keywords':translated.get('keywords',tags[:3]),'analysis':translated.get('analysis') if translated else None,'source_basis':basis if translated else 'unprocessed','content_rights':'analysis_only','geo_perspective':translated.get('geo_perspective') if translated else None}
                items[url]=article;new+=1;analyzed+=bool(translated)
                print('Added:',title[:65],'basis:',article['source_basis'])
        except Exception as e:print('Feed unavailable:',feed,str(e)[:200])
    if not seen:
        print('No accessible feed: previous data preserved');return
    rows=sorted(items.values(),key=lambda x:x.get('published',''),reverse=True)[:200]
    output={'updated_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec='seconds'),'status':'translated' if os.getenv('OPENAI_API_KEY') else 'untranslated','version':'3.0','articles':rows}
    DATA.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(f'Seen {seen}; new {new}; AI analyzed {analyzed}; stored {len(rows)}')
if __name__=='__main__':main()
