from bs4 import BeautifulSoup
import re
import requests
import random
from datetime import datetime

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
    start_page = random.randrange(1500, start_page - 20)
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
                            i['img'] = str.replace(str.replace(rsoup.select_one('a[href*=".jpg"]')['href'], 'https', 'http'), 'http', 'https')
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


def search_video(key):
    head='http://www.58b.tv'
    header = {
        'Host': 'www.58b.tv',
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64;rv: 58.0) Gecko / 20100101Firefox / 58.0',
        'Upgrade-Insecure-Requests': '1'
    }
    payload={'s':'home-Vod-innersearch-q-'+key+'-order-undefined'}
    rs=requests.get('http://www.58b.tv/index.php',params=payload,headers=header)
    soup=BeautifulSoup(rs.text,'lxml')
    ary=[]
    for item in soup.findAll("table",attrs={'style':'width:100%;'}):
        i=dict()
        i['img']=str.replace(str.replace(item.select_one("img[src]")['src'], 'https', 'http'), 'http', 'https')
        i['url']=head+item.select_one('a')['href']
        i['name']=item.select_one('td h3 a').text
        print(i)
        ary.append(i)
    return ary


def search_video_detail(url):
    result=dict()
    header={
        'Host': 'www.58b.tv',
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64;rv: 58.0) Gecko / 20100101Firefox / 58.0',
        'Upgrade-Insecure-Requests':'1'
    }
    rs = requests.get(url,headers=header);
    soup= BeautifulSoup(rs.text,'lxml')
    time_string=soup.find('div',{'class':'vshow'}).find('p',{'style':"margin-bottom:10px"}).text
    m = re.search(r"：(\S+) (\S+)",time_string)
    fmt='%Y-%m-%d %H:%M:%S'
    d=datetime.strptime(m.group(1)+" "+m.group(2), fmt)
    film= soup.find('h2')
    ep_string=soup.find('div', {'class': 'vshow'}).find(string=re.compile(r"連載")).find_parent().text
    m = re.search(r"連載：(\S+)", ep_string)
    ep=m.group(1)
    result['film']=film.string
    result['update_time']=d
    result['episode']=ep
    result['url']=url
    return result


def test_connect():
    head = 'http://www.58b.tv'
    header={
        'Host': 'www.58b.tv',
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64;rv: 58.0) Gecko / 20100101Firefox / 58.0',
        'Upgrade-Insecure-Requests':'1'
    }
    payload = {'s': 'home-Vod-innersearch-q-' + '閃電俠' + '-order-undefined'}
    rs = requests.get('http://www.58b.tv/index.php', params=payload,headers=header)
    return str(rs)
