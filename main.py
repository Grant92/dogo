from redbox import EmailBox
from redbox.query import UNSEEN
import codecs 
import pandas as pd
import openpyxl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time 
import safe
from bs4 import BeautifulSoup
import sys


################redbox_extractor####################
#projde maily a z nepřečteného mailu identifikuje kdo dobil kredity a kolik



box = EmailBox(
    host='imap.centrum.cz',
    port='993',
    username= safe.box_username[0],
    password= safe.box_password[0]
)

inbox = box["INBOX"]

try:
    msgs = inbox.search(unseen = True)
    msg = msgs[0]
##test
except IndexError:
   print("Žádná nová platba")
   sys.exit(1)
msg_text = msg.html_body
soup = BeautifulSoup(msg_text,'html.parser')
list = []
for el in soup.find_all("p"):
    list.append (el.get_text())
 
credits = list[7]
student = list[13]
sstudent = student.split('/')[0]
sstudent = sstudent+"/"+((student.split("/")[1])[0:4])
credits = credits.replace("+","")
credits = credits.replace(".","")
credits = credits.replace(",00 CZK","")

######################## dobijec ###################################

###script pro dobíjení kreditů

#hledání url karty studenta
path = "students_url.xlsx"
table = pd.read_excel(path)
names = table.Ucet
urls = table.URL
students_dict = {names[i]: urls[i] for i in range(len(names))}
#najít studenta v seznamu
dict_key = sstudent
#najít správné url
odkaz = students_dict.get(dict_key)

#spustí prohlížeč a pomocí chromedriveru začne se přihlásí na web a vyplní u vybraného studenta dobití kreditů

chrome_options = webdriver.ChromeOprions()
chrome_service = Service('/usr/lib/chromium-browser/chromedriver')
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
driver.implicitly_wait(10) 
web = "https://dogres.cz/users/sign_in"
driver.get(web)
driver.implicitly_wait(30);
#vyplní přihlašovací okno
driver.find_element("id","user_email").send_keys(safe.web_username[0])
time.sleep(3);
driver.find_element("id","user_password").send_keys(safe.web_password[0])
time.sleep(3);
driver.find_element("id","user_password").send_keys(u'\ue007')
time.sleep(5);
#otevřít kartu studenta a vyplnit kredity
driver.get(odkaz)
driver.find_element("id","credit_log_name").send_keys("Automatizovane dobiti kreditu pres ucet")
time.sleep(2);
driver.find_element("id","credit_log_credits").send_keys(credits)
time.sleep(2);
driver.find_element("id","credit_log_price").send_keys(credits)
time.sleep(2);
driver.find_element("name","commit").submit()
driver.close()

print("Bylo dobito:"+credits+"pro cislo uctu"+sstudent)


