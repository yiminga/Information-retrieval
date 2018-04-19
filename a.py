import re
import urllib
from urllib import request
import sys
import jieba
import sqlite3
from  collections import deque
from bs4 import BeautifulSoup

url='http://gongyi.qq.com'

queue=deque()
visited=set()
queue.append(url)

conn=sqlite3.connect('viewsdu.db')
c=conn.cursor()
c.execute('drop table doc')
c.execute('create table doc (id int primary key,link text)')
c.execute('drop table word')
c.execute('create table word (term varchar(25) primary key,list text)')
conn.commit()
conn.close()

print('-----start------')

cnt=0

while queue:
    url=queue.popleft()
    visited.add(url)
    cnt+=1
    print(cnt,':',url)

    try:
        response=request.urlopen(url)
        content=response.read().decode('gb18030')
    except:
        continue
#    print(content)

    soup=BeautifulSoup(content,'html.parser')
    for link in soup.find_all('a'):
        x=link.get('href')
        if not re.match(r'\/a\/.+',str(x)):
            continue
        else:
            x='http://gongyi.qq.com'+x
            print(x)
        if (x not in visited)and(x not in queue):
            queue.append(x)


    soup=BeautifulSoup(content,'lxml')
    para=soup.find('div',id="Cnt-Main-Article-QQ",class_="Cnt-Main-Article-QQ")
    dd=re.compile(r'<[^>]+>',re.S)
    para=dd.sub('',str(para))
    print(para)
    if para==None:
        print('there is nothing')
        continue

    seggen=jieba.cut_for_search(para)
    seglist=list(seggen)
    
    print('fenci chenggong')

    conn=sqlite3.connect('viewsdu.db')
    c=conn.cursor()
    c.execute('insert into doc values (?,?)',(cnt,url))

    for word in seglist:
        print(word)
        c.execute('select list from word where term=?',(word,))
        result=c.fetchall()
        if len(result)==0:
            docliststr=str(cnt)
            c.execute('insert into word values (?,?)',(word,docliststr))
        else:
            docliststr=result[0][0]
            docliststr+=' '+str(cnt)
            c.execute('update word set list=? where term=?',(docliststr,word))
    conn.commit()
    conn.close()
    print('end')
conn=sqlite3.connect('viewsdu.db')
c=conn.cursor()
c.execute('select * from word')
result=c.fetchall()
print(type(result),result)
conn.commit()
conn.close()














