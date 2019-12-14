from PyQt5 import QtCore , QtGui
from PyQt5.QtWidgets import QLabel,QApplication,QMainWindow,QSizePolicy
from PyQt5.QtWebEngineWidgets import *
import subprocess, re, os, bs4, requests, sys
import threading
import speech_recognition as sr
import signal
import pyttsx3
import apiai, json
import myfunc


# Инициализируем SAPI5
engine = pyttsx3.init()
# Получаем список голосов
voices = engine.getProperty('voices')
# Устанавливаем русский язык
engine.setProperty('voice', 'ru')
# Ищем голос Elena от RHVoice
# Его нужно заранее скачать тут, пролистав вниз до раздела SAPI 5:
# https://github.com/Olga-Yakovleva/RHVoice/wiki/Latest-version-%28Russian%29
for voice in voices:
    if voice.name == 'Elena':
        engine.setProperty('voice', voice.id)
# Скорость чтения
engine.setProperty('rate', 110)

# Получаем html шаблон для сообщений в окне чата
htmlcode='<div class="robot">Чем я могу помочь?</div>';
f=open('index.html','r',encoding='UTF-8')
htmltemplate=f.read()
f.close()

# Получаем html шаблон help
f=open('help.html','r',encoding='UTF-8')
htmlcode2=f.read()
f.close()

# Функция, которая обращается к Dialogflow и получает ответ
def AiMessage(s):
    # Токен API к Dialogflow (оставьте этот или натренируйте свою модель)
    request = apiai.ApiAI('7f01246612e64e3f89264a85a965ddd3').text_request()
    # На каком языке будет послан запрос
    request.lang = 'ru'
    # ID Сессии диалога (нужно, чтобы потом учить бота)
    request.session_id = '3301megabot'
    # Посылаем запрос к ИИ с сообщением от юзера
    request.query = s 
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    # Разбираем JSON и вытаскиваем ответ
    response=''
    response = responseJson['result']['fulfillment']['speech'] 
    # Если есть ответ от бота - выдаём его,
    # если нет - бот его не понял
    if response:
        return response
    else:
        return 'Я Вас не совсем поняла!'

otvet=''
listen=''
vopros=''
dontlisten=''
ispeak=''

# Объявляем распознавалку речи от Google
r = sr.Recognizer()

# Отдельный поток 
def thread(my_func):
    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=my_func, args=args, kwargs=kwargs)
        my_thread.start()
    return wrapper

# Функции для сигналов между потоками
def signal_handler(signal, frame):
    global interrupted
    interrupted = True    
def interrupt_callback():
    global interrupted
    return interrupted

# Функция активизирует Google Speech Recognition для распознавания команд
@thread
def listencommand():
    global listen
    global vopros
    global dontlisten
    # Следим за состоянием ассистента - слушает она или говорит
    listen.emit([1])
    # Слушаем микрофон
    with sr.Microphone() as source:
        #r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
    try:
        # Отправляем запись с микрофона гуглу, получаем распознанную фразу
        f=r.recognize_google(audio, language="ru-RU").lower()
        # Меняем состояние ассистента со слушания на ответ
        listen.emit([2])
        # Отправляем распознанную фразу на обработку в функцию myvopros
        vopros.emit([f])
    # В случае ошибки меняем состояние ассистента на "не расслышал"
    except sr.UnknownValueError:
        print("Робот не расслышал фразу")
        dontlisten.emit(['00'])
    except sr.RequestError as e:
        print("Ошибка сервиса; {0}".format(e))
signal.signal(signal.SIGINT, signal_handler)

# Графический интерфейс PyQt 
class W(QMainWindow):
    # Объявляем сигналы, которые приходят от асинхронных функций
    my_signal = QtCore.pyqtSignal(list, name='my_signal')
    my_listen = QtCore.pyqtSignal(list, name='my_listen')
    my_vopros = QtCore.pyqtSignal(list, name='my_vopros')
    my_dontlisten = QtCore.pyqtSignal(list, name='my_dontlisten')
    def __init__(self, *args):
        super().__init__()
        self.setAnimated(False)
        self.flag = True
        self.centralwidget = QMainWindow()
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        # Label в который мы загрузим картинку с девушкой
        self.label = QLabel(self.centralwidget)
        # Прикрепляем к Label функцию обработки клика
        self.label.installEventFilter(self)
        # Настраиваем вид курсора на картинке
        self.label.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # Позиционируем Label внутри окна
        self.label.setGeometry(QtCore.QRect(2, 2, 400, 300))
        # Объявляем элемент QWebEngineView для отображения html странички с чатом
        self.browser = QWebEngineView(self.centralwidget)
        # Объявляем элемент QWebEngineView для отображения видео с ютуба, текстов и веб страниц
        self.browser2 = QWebEngineView(self.centralwidget)
        # Позиционируем QWebEngineView внутри окна
        self.browser.setGeometry(QtCore.QRect(2, 305, 400, 300))
        self.browser2.setGeometry(QtCore.QRect(405, 2, 930, 603))
        # Загружаем в QWebEngineView html документ с чатом
        global htmltemplate
        global htmlcode
        global htmlcode2
        htmlresult=htmltemplate.replace('%code%',htmlcode)
        self.browser.setHtml(htmlresult, QtCore.QUrl("file://"));
        self.browser.show()
        self.browser2.setHtml(htmlcode2, QtCore.QUrl("file://"));
        self.browser2.show()  
        self.label.setText("<center><img src='file:///"+os.getcwd()+"/img/1.jpg'></center>")
        # Соединяем сигналы и функции класса
        global otvet
        otvet=self.my_signal
        global listen
        listen=self.my_listen
        global dontlisten
        dontlisten=self.my_dontlisten
        global vopros
        vopros=self.my_vopros
        self.my_listen.connect(self.mylisten, QtCore.Qt.QueuedConnection)
        self.my_vopros.connect(self.myvopros, QtCore.Qt.QueuedConnection)
        self.my_dontlisten.connect(self.mydontlisten, QtCore.Qt.QueuedConnection)

    # Обработка клика по картинке с девушкой    
    def eventFilter(self,obj,e):
        if e.type() == 2:
            btn = e.button()
            if btn == 1:
                listencommand()
            elif btn == 2: self.label.setText("<center><img src='file:///"+os.getcwd()+"/img/1.jpg'></center>")
        return super(QMainWindow,self).eventFilter(obj,e)
    
    # Смена картинки девушки в зависимости от того слушает она или говорит
    def mylisten(self, data):
        if(data[0]==1):
            self.label.setText("<center><img src='file:///"+os.getcwd()+"/img/2.jpg'></center>")
        if(data[0]==2):
             self.label.setText("<center><img src='file:///"+os.getcwd()+"/img/1.jpg'></center>")

    # Добавление в html чат фразы ассистента
    def addrobotphrasetohtml(self, phrase):
        global htmltemplate
        global htmlcode
        htmlcode='<div class="robot">'+phrase+'</div>'+htmlcode
        htmlresult=htmltemplate.replace('%code%',htmlcode)
        self.browser.setHtml(htmlresult, QtCore.QUrl("file://"));
        self.browser.show()

    # Добавление в html чат фразы пользователя
    def addyouphrasetohtml(self, phrase):
        global htmltemplate
        global htmlcode
        htmlcode='<div class="you">'+phrase+'</div>'+htmlcode
        htmlresult=htmltemplate.replace('%code%',htmlcode)
        self.browser.setHtml(htmlresult, QtCore.QUrl("file://"));
        self.browser.show()

    # Произносим ответ вслух синтезом речи
    def speakphrase(self, phrase):
        global engine
        engine.say(phrase)
        engine.runAndWait()
        engine.stop()
 
    # Функция в которой решаем что отвечать на фразы пользователя    
    def myvopros(self, data):
        global predurls
        global predcmd
        # Получаем фразу от пользователя
        vp=data[0].lower()
        # Отображаем её в чате
        self.addrobotphrasetohtml(vp)
        # Ответ по умолчанию
        ot='Я не расслышала'
        # Выполняем разные действия в зависимости от наличия ключевых слов фо фразе
        if(vp=='пока' or vp=='выход' or vp=='выйти' or vp=='до свидания'):
            ot='Ещё увидимся!'
            self.addyouphrasetohtml(ot)
            self.speakphrase(ot)
            sys.exit(app.exec_())
        elif('анекдот' in vp):
            ot=myfunc.anekdot()
        elif('запусти' in vp):
            ot=myfunc.zapusti(vp)
        elif(((vp.find("youtube")!=-1) or (vp.find("ютюб")!=-1)  or (vp.find("ютуб")!=-1) or (vp.find("you tube")!=-1)) and (vp.find("смотреть")!=-1)):
            self.browser2.load(QtCore.QUrl(myfunc.findyoutube(vp)))
            ot='Вот видео.'
        elif((vp.find("слушать")!=-1) and (vp.find("песн")!=-1)):
            self.browser2.load(QtCore.QUrl(myfunc.findyoutube(vp)))
            ot='Вот песня.'
        elif(((vp.find("найти")!=-1) or (vp.find("найди")!=-1)) and not(vp.find("статью")!=-1)):
            zapros=myfunc.cleanphrase(vp,['найти','найди','про','про то', 'о том'])
            q=myfunc.mysearch(zapros)
            self.browser2.load(QtCore.QUrl(q[0]))
            ot='Вот ответ' 
        else:
            # Если ключевых слов не нашли, используем Dialogflow
            ot=AiMessage(vp)
        # Добавляем ответ в чат
        self.addyouphrasetohtml(ot)
        # Читаем ответ вслух
        self.speakphrase(ot)
        
    # Функция меняет картинку если ассистент тебя не расслышал
    def mydontlisten(self, data): 
        self.label.setText("<center><img src='file:///"+os.getcwd()+"/img/3.jpg'></center>")



# Запускаем программу на выполнение    
app = QApplication([])
w = W()
# Размер окна
w.resize(1340,615)
w.show()
app.exec_()
