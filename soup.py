from bs4 import BeautifulSoup
import re
import json
import requests
import random

domain = 'https://www.ptt.cc'


def gossip():
    ans = {'from': '/bbs/Gossiping/index.html', 'yes': 'yes'}
    rs = requests.session()
    rs.post('https://www.ptt.cc/ask/over18', data=ans)
    html = rs.get('https://www.ptt.cc/bbs/Gossiping/index.html')
    soup = BeautifulSoup(html.text, 'lxml')
    content = ""
    for tag in soup.find_all('div', {'class': 'r-ent'}, limit=5):
        if tag:
            title = tag.find('a').text
            link = 'https://www.ptt.cc' + tag.find('a').get('href')
            content += '{}\n{}\n\n'.format(title, link)
    return content


def beauty():
    rs = requests.get('https://www.ptt.cc/bbs/Beauty/index.html')
    soup = BeautifulSoup(rs.text, 'lxml')
    start_page = get_Current_Page(soup)
    start_page= random.randrange(1000,start_page-20)
    count = 0
    htmls = []
    ary=[]
    for page in range(start_page - 10, start_page):
        htmls.append('https://www.ptt.cc/bbs/Beauty/index{}.html'.format(page))

    while htmls:
        html = htmls.pop(0)
        rs = requests.get(html)
        soup = BeautifulSoup(rs.text, 'lxml')
        for item in soup.select(".r-ent"):
            if count >9:
                return ary.copy()
            if item:
                rate = item.select('.nrec')[0].string
                if rate:
                    rate = '100' if rate.startswith('爆') else rate
                    rate = '0' if rate.startswith('X') else rate
                else:
                    rate = 0

                if int(rate) > 50:
                    if item.select_one('a'):
                        r=requests.get(domain + item.select_one('a')['href'])
                        rsoup=BeautifulSoup(r.text,'lxml')
                        if rsoup.select_one('a[href*=".jpg"]'):
                            i=dict()
                            i['target']=domain + item.select_one('a')['href']
                            i['img'] =str.replace(rsoup.select_one('a[href*=".jpg"]')['href'], 'https', 'http')
                            i['img']=str.replace(i['img'],'http','https')
                            ary.append(i)
                            count += 1
    return ary.copy()


def draw_beauty():
    rs = requests.get('https://www.ptt.cc/bbs/Beauty/index.html')
    soup = BeautifulSoup(rs.text, 'lxml')
    start_page = get_Current_Page(soup)
    start_page = random.randrange(1000, start_page - 20)
    count = 0
    htmls = []
    ary = []
    for page in range(start_page - 10, start_page):
        htmls.append('https://www.ptt.cc/bbs/Beauty/index{}.html'.format(page))

    while htmls:
        html = htmls.pop(0)
        rs = requests.get(html)
        soup = BeautifulSoup(rs.text, 'lxml')
        for item in soup.select(".r-ent"):
            if count > 0:
                return ary.copy()
            if item:
                rate = item.select('.nrec')[0].string
                if rate:
                    rate = '100' if rate.startswith('爆') else rate
                    rate = '0' if rate.startswith('X') else rate
                else:
                    rate = 0

                if int(rate) > 50:
                    if item.select_one('a'):
                        r = requests.get(domain + item.select_one('a')['href'])
                        rsoup = BeautifulSoup(r.text, 'lxml')
                        if rsoup.select_one('a[href*=".jpg"]'):
                            i = dict()
                            i['target'] = domain + item.select_one('a')['href']
                            i['img'] = str.replace(rsoup.select_one('a[href*=".jpg"]')['href'], 'https', 'http')
                            i['img'] = str.replace(i['img'], 'http', 'https')
                            ary.append(i)
                            count += 1
    return ary.copy()


def get_Current_Page(content):
    pattern = re.compile(r'index(\d*)')
    currentpage = pattern.search(content.select('.btn.wide')[1]['href'])
    return int(currentpage.group(1))+1


def lol():
    rs = requests.get('https://www.ptt.cc/bbs/LoL/index.html')
    soup = BeautifulSoup(rs.text, 'lxml')
    start_page = get_Current_Page(soup)
    count = 0
    htmls=[]
    content = ""
    for page in range(start_page-5,start_page):
        htmls.append('https://www.ptt.cc/bbs/LoL/index{}.html'.format(page))

    while htmls and count < 20:
        html=htmls.pop(0)
        rs = requests.get(html)
        soup=BeautifulSoup(rs.text,'lxml')
        for item in soup.select(".r-ent"):
            if item:
                rate = item.select('.nrec')[0].string
                if rate:
                    rate = '100' if rate.startswith('爆') else rate
                    rate = '0' if rate.startswith('X') else rate
                else:
                    rate = 0

                if int(rate) > 50:
                    title = item.select('.title')[0].text
                    link = domain + item.select('a')[0]['href']
                    content += '{}\n{}\n'.format(title, link)
                    count += 1
    return content


def search_keyword_pchome(key):
    print('-------search keyword from pchome------')
    head='https://a.ecimg.tw/'
    payloads={
        'page': 1,
        'sort': 'rnk/dc'
    }
    payloads['q']=key
    response=requests.get('https://ecshweb.pchome.com.tw/search/v3.3/all/results',payloads)
    m=BeautifulSoup(response.text,'lxml')
    print('-------parse data------')
    result=json.loads(m.text)
    pl=[]
    total=len(result['prods'])
    for id,p in enumerate(result['prods']):
        item={}
        item['Id']=p['Id']
        item['name'] = p['name']
        item['image'] = head+p['picS']
        item['describe']=p['describe']
        item['price'] = p['price']
        item['originPrice'] = p['originPrice']
        pl.append(item)
        print('{0:.0f}%'.format((id+1)/total*100))
    print('-------parse complete------')
    print('-------return data--------')
    return pl


def search_product_ruten():
    pass


if __name__ == '__main__':
    print(draw_beauty())
