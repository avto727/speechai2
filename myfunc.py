import requests, bs4, re, webbrowser
import os, sys, subprocess
from urllib import request
from urllib.parse import quote
import urllib.request
import html2text

# Чистит фразу от ключевых слов
def cleanphrase(statement, spisok):
    for x in spisok:
        statement=statement.replace(x, '')
    statement=statement.strip()
    return statement

# Функция дающая случайный анекдот
def anekdot():
    s=requests.get('http://anekdotme.ru/random')
    b=bs4.BeautifulSoup(s.text, "html.parser")
    p=b.select('.anekdot_text')
    s=(p[0].getText().strip())
    reg = re.compile('[^0-9a-zA-Zа-яА-я .,!?-]')
    s=reg.sub('', s)
    return(s)

# Открыть сайт во внешнем браузере
def openurl(url):
    webbrowser.open(url)

# Запускает внешнюю команду ОС
def osrun(cmd):
    PIPE = subprocess.PIPE
    p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)

def zapusti(statement):
    ot='Такой команды я пока не знаю'
    statement=cleanphrase(statement,['запусти', 'запустить'])
    if((statement.find("калькулятор")!=-1) or (statement.find("calculator")!=-1)):
        osrun('calc')
        ot='Калькулятор запущен'
    if((statement.find("блокнот")!=-1) or (statement.find("notepad")!=-1)):
        osrun('notepad')
        ot='Блокнот запущен'
    if((statement.find("paint")!=-1) or (statement.find("паинт")!=-1)):
        osrun('mspaint')
        ot='Графический редактор запущен'
    if((statement.find("browser")!=-1) or (statement.find("браузер")!=-1)):
        openurl('http://google.ru')
        ot='Запускаю браузер'
    if((statement.find("проводник")!=-1) or (statement.find("файловый менеджер")!=-1)):
        osrun('explorer')
        ot='Проводник запущен'
    return ot

# Даёт iframe код ютуб ролика по любому поисковому запросу    
def findyoutube(x):
    x=cleanphrase(x, ['хочу', 'на ютубе', 'на ютюбе', 'на ютуб', 'ютюб', 'на youtube', 'на you tube', 'на youtub', 'youtube', 'ютуб', 'ютубе', 'посмотреть', 'смотреть'])
    zz=[]
    sq='http://www.youtube.com/results?search_query='+quote(x)
    doc = urllib.request.urlopen(sq).read().decode('cp1251',errors='ignore')
    match = re.findall("\?v\=(.+?)\"", doc)
    if not(match is None):
        for ii in match:
            if(len(ii)<25):
                zz.append(ii)
    zz2=dict(zip(zz,zz)).values()
    zz3=[]
    for qq in zz2: zz3.append(qq)
    s=zz3[0]
    s='''<iframe width="900" height="550" src="https://www.youtube.com/embed/'''+s+'''?autoplay=1" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'''
    return s

def mysearch(z):
    doc = urllib.request.urlopen('http://go.mail.ru/search?fm=1&q='+quote(z)).read().decode('unicode-escape',errors='ignore')
    sp=re.compile('title":"(.*?)orig').findall(doc)
    mas1=[]
    mas2=[]
    for x in sp:
        if((x.rfind('wikihow')==-1) and (x.rfind('an.yandex')==-1) and (x.rfind('wikipedia')==-1) and (x.rfind('otvet.mail.ru')==-1) and (x.rfind('youtube')==-1) and(x.rfind('.jpg')==-1) and (x.rfind('.png')==-1) and (x.rfind('.gif')==-1)):  
            a=x.replace(',','')
            a=a.replace('"','')
            a=a.replace('<b>','')
            a=a.replace('</b>','')
            a=a.split('url:')
            if(len(a)>1):
                z=a[0].split('}')
                mas1.append(z[0])
                z=a[1].split('}')
                z=z[0].split('title')
                mas2.append(z[0])
    return mas2

def gettext(url):
    s=url
    txt=''
    try:
        doc = urllib.request.urlopen(s).read().decode('utf-8',errors='ignore')
    except:
        response = requests.get(s)
        doc=response.content.decode('utf-8',errors='ignore')
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.body_width = False
    h.ignore_images = True
    doc = h.handle(doc)
    summa=""       
    ss=doc.split("\n")
    for xx in ss:
        xx=xx.strip()
        if((len(xx)>50) and (xx.startswith('&')==False) and not('то стабильная версия' in xx) and (xx.startswith('>')==False) and (xx.startswith('*')==False) and (xx.startswith('\\')==False) and (xx.startswith('<')==False) and (xx.startswith('(')==False) and (xx.startswith('#')==False) and (xx.endswith('.') or xx.endswith('?') or xx.endswith('!') or xx.endswith(';'))):
            summa = summa + xx + "\n \n"  
    if(len(summa)>200):
        txt=summa
    return txt





