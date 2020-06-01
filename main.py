from bs4 import BeautifulSoup
from selenium import webdriver
from modules.SaveImg import SaveImg
from modules.LineNotifier import SendNotifyMessage
import datetime
import time

URL = 'https://24h.pchome.com.tw/store/DGBJHC'
token = 'oooooooooow6k7SlTHNuvTFsBegCO0vWpoooooooooo'
img_url = list()

def Parse():
    driver = webdriver.PhantomJS(executable_path=r'D:\play_ground\phantomjs-2.1.1-windows\bin\phantomjs.exe')  # PhantomJs
    driver.get(URL)  # 輸入範例網址，交給瀏覽器 
    pageSource = driver.page_source  # 取得網頁原始碼
    soup = BeautifulSoup(pageSource, "html.parser")
    # print(soup.find(id="Block4Container").prettify())  #輸出排版後的HTML內容

    for item in soup.select('{}'.format("div.mL.mEvt a.prod_img img")):
        if item['src'] not in img_url:
            img_url.append(item['src'])
            now = datetime.datetime.now()
            timestamp = time.mktime(now.timetuple())
            file = SaveImg("https:" + item['src'], str(int(timestamp)))
            SendNotifyMessage(token, "賣場留言板更新", file)
        else:
            print("next...")

    driver.close()  # 關閉瀏覽器

def Run():
    while True:
        Parse()
        time.sleep(60)

if __name__ == '__main__':
    Run()
