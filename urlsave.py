#!/usr/bin/env python
# coding=utf-8
import pymysql
import requests
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool 
from urllib.parse import urlparse

def format_url(url):
        if urlparse(url)[2] == '':
            url += '/'

        url_structure = urlparse(url)
        netloc = url_structure[1]
        path = url_structure[2]
        query = url_structure[4]

        temp = (netloc,tuple([len(i) for i in path.split('/')]),tuple(sorted([i.split('=')[0] for i in query.split('&')])))
        return temp



def get_urls(keyword):
    page = 0
    base_url = "https://www.baidu.com/s?wd={}&pn={}&rn=50" 
    SIMILAR_SET = set()
    urls = set()
    headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
               'Accept-Language':'zh-CN,en-US;q=0.7,en;q=0.3', 
               'Connection':'keep-alive', 
               'User-Agent':'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.14) Gecko/20110221 Ubuntu/10.10 (maverick) Firefox/3.6.14'}

    def url_similar_control(url):
        t = format_url(url)
        if t not in SIMILAR_SET:
            return True
        return False

    def get_real_url(url):
        try:
            r = requests.get(url,headers=headers,timeout=6)
        except:
            pass 
        else:
            real_url = str(r.url)
            if url_similar_control(real_url):
                SIMILAR_SET.add(format_url(real_url))
                urls.add(real_url)
                print(real_url)

    
   
    while 1:
        print("正在获得第{}页".format(page+1))
        url = base_url.format(keyword,page*50)
        r = requests.get(url,headers=headers) 
        soup = BeautifulSoup(r.text,'lxml')
        h3s = soup.find_all('h3')
        hrefs = [ i.a.get('href') for i in h3s ]
        pool = Pool(10) 
        results = pool.map(get_real_url,hrefs)
        pool.close()
        pool.join()
        if  len(h3s) < 50:
            return urls 
        else:
            page += 1


def save2txt(urls):
    with open('urls.txt','w') as f:
        for url in urls:
            f.write(url+'\n')

def save2mysql(keyword,urls):
    conn = pymysql.connect(host='127.0.0.1',user='root',passwd=None,db='spider') 
    cur = conn.cursor()
    for url in urls:
        try:
            k = '"' + keyword +'"'
            u = '"' + url + '"'
            sql = "insert into injection_point values ({},{})".format(k,u)
            cur.execute(sql)
            conn.commit()
        except:
            print("插入{}失败".format(url))
    cur.close()
    conn.close()



def main():
    keyword = 'inurl:tw%2bphp?item_id'
    urls = get_urls(keyword)
    save2txt(urls)
    save2mysql(keyword,urls)
    print('已保存{}个urls'.format(len(urls)))



if __name__ == '__main__':
    main()
