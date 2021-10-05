import sys
import time
import requests
from bs4 import BeautifulSoup as bs
from pony.orm import *

from PyQt5 import QtWidgets
from PyQt5 import QtGui, QtCore

db = Database()


class News(db.Entity):
    date = Required(str)
    news = Required(str)
    link = Required(str)


db.bind(provider="postgres", user="test", password="12345678", host="localhost", database="news1")
db.generate_mapping(create_tables=True)


class Example(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUi()

    @db_session
    def write_db(self, date, news, link):
        for r in News.select(lambda p: p.link == link):
            if link == r.link:
                # log.warning(f"запись '{news}' не добавлена, т.к. уже присутствует в базе")
                print(f"запись {news} не добавлена")
                break
        else:
            News(date=date, news=news, link=link)
            # log.info(f"запись '{news}' добавлена в базу")
            print(f"запись {news} добавлена")

    @db_session
    def get_news_count_from_db(self, date):
        news_count = count(n for n in News if n.date == date)
        return news_count

    def get_news_from_db(self, date):
        self.txt.setText("")
        #     # log.info(f"выводим данные за {date}")
        print(f"выводим данные за {date}")
        news_count = self.get_news_count_from_db(date=date)
        if news_count != 0:
            news_db = self.read_db(date=date)
            for r in news_db:
                self.txt.append(date)
                self.txt.append(r.news)
                self.txt.append(r.link)
                # self.txt.acceptRichText()
                self.txt.setOpenExternalLinks(True)
                self.txt.append(f"<a href='{r.link}'>{r.news}</a>")
                self.txt.append("-----")
        else:
            self.txt.append(f"Новостей за {date} нет")

    @db_session
    def read_db(self, date):
        news_db = News.select(lambda p: p.date == date)[:]
        return news_db

    def pri(self):
        self.txt.append(self.message)

    def read(self):
        self.txt.setText("")
        date = self.dateTimeEdit.dateTime().toString("dd/MM/yyyy")
        self.get_news_from_db(date=date)
        # self.txt.append(date)
        print(date)

    def parse(self):
        self.txt.setText("")
        self.txt.setOpenExternalLinks(True)
        self.txt.append("Parsing")
        res = requests.get(url="https://lenta.ru")
        if res.status_code == 200:
            html_doc = bs(res.text, features="html.parser")
            name_of_news = html_doc.findAll("a", class_="titles")

            for name in name_of_news:
                url = name.get("href")
                if url.split("/")[3] != time.strftime("%m") or url.split("/")[4] != time.strftime("%d"):
                    continue
                main_url = "https://lenta.ru" + name["href"]
                news = name.text
                date = time.strftime("%d/%m/%Y")
                self.write_db(date=date, news=news, link=main_url)
                # print(news)

    def initUi(self):
        QtWidgets.QToolTip.setFont(QtGui.QFont("SansSerif", 10))
        # self.setToolTip("this is a <h1>widget</h1>")

        self.btnParse = QtWidgets.QPushButton("Parse", self)
        self.btnParse.setToolTip("Press to start parsing")
        self.btnParse.clicked.connect(self.parse)
        # self.btnParse.resize(btn.sizeHint())
        self.btnParse.move(950, 50)

        self.btnRead = QtWidgets.QPushButton("Read DB", self)
        self.btnRead.clicked.connect(self.read)
        self.btnRead.resize(self.btnRead.sizeHint())
        self.btnRead.move(950, 100)

        self.txt = QtWidgets.QTextBrowser(self)
        self.txt.setToolTip(f"список новостей")
        self.txt.move(10, 10)
        self.txt.resize(830, 580)

        self.dateTimeEdit = QtWidgets.QDateTimeEdit(QtCore.QDate.currentDate(), self)
        self.dateTimeEdit.setToolTip("Введите дату")
        self.dateTimeEdit.move(850, 102)

        self.setGeometry(300, 300, 1050, 600)
        self.setWindowTitle("News")
        # self.setWindowIcon(QtGui.QIcon("smile.jpg"))
        self.show()


app = QtWidgets.QApplication(sys.argv)
ex = Example()
sys.exit(app.exec())
