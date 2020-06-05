from bs4 import BeautifulSoup
from selenium import webdriver
from modules.SaveImg import SaveImg
from modules.LineNotifier import SendNotifyMessage
import datetime
import time
import os
import traceback
import json
from selenium.webdriver.chrome.options import Options

try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    CurrentPath = sys._MEIPASS
except Exception:
    CurrentPath = os.path.abspath(".")

URL = 'https://24h.pchome.com.tw/store/DGBJHC'
token = 'oooooooooow6k7SlTHNuvTFsBegCO0vWpoooooooooo'
DATA_FILE = os.path.join(CurrentPath, 'product_data.json')

img_url = list()

product_info = dict()
product_list = dict()

def Parse():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    # 指定在要使用的 Agent 身份，會做這項設置，是因為PCHome，會阻擋 Chrome Headless 的 Agent
    ua = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
    chrome_options.add_argument("user-agent={}".format(ua))
    chrome_options.add_argument("--incognito")  # 使用無痕模式
    chrome_options.add_argument('log-level=3')
    #info(default) = 0
    #warning = 1
    #LOG_ERROR = 2
    #LOG_FATAL = 3

    executable_path = './chromedriver.exe'
    driver = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options)
    driver.get(URL)
    product_id_list = list()
    # driver = webdriver.PhantomJS(executable_path=r'D:\play_ground\phantomjs-2.1.1-windows\bin\phantomjs.exe')  # PhantomJs
    # driver.get(URL)  # 輸入範例網址，交給瀏覽器
    pageSource = driver.page_source  # 取得網頁原始碼
    soup = BeautifulSoup(pageSource, "html.parser")
    driver.close()  # 關閉瀏覽器
    # print(soup.prettify())
    # print(soup.find(id="Block4Container").prettify())  #輸出排版後的HTML內容

    for item in soup.select('{}'.format("div.mL.mEvt a.prod_img img")):
        if item['src'] not in img_url:
            img_url.append(item['src'])
            now = datetime.datetime.now()
            timestamp = time.mktime(now.timetuple())
            file = SaveImg("https:" + item['src'], str(int(timestamp)))
            SendNotifyMessage(token, "賣場留言板更新", file)
            save_data(DATA_FILE)

    for products in soup.select('{}'.format("div#Block4Container dd")):
        is_send = False
        product_info = parse_product(products)
        product_id_list.append(product_info['id'])
        is_send = update_product_list(product_info)

        if is_send:
            send_prd_info(product_info)
            save_data(DATA_FILE)

    for products in soup.select('{}'.format("dl#ProdGridContainer dd")):
        is_send = False
        product_info = parse_product(products)
        product_id_list.append(product_info['id'])
        is_send = update_product_list(product_info)

        if is_send:
            send_prd_info(product_info)
            save_data(DATA_FILE)

    old_product_clean_up(product_id_list)

def parse_product(products):
    product_id = products.find(attrs = {"_id" : True})
    product_url = products.select_one('{}'.format(".prod_img"))
    product_img = products.select_one('{}'.format(".prod_img img"))
    product_nick = products.select_one('{}'.format(".prod_info .nick a"))
    product_price = products.select_one('{}'.format(".prod_info .price_box .price .value"))

    if not product_id:
        id = products['_id']
    else:
        id = product_id['_id']

    url = product_url['href']
    img = product_img['src']
    name = product_nick.text
    price = product_price.text

    product_info = dict()
    product_info['id'] = id
    product_info['url'] = url
    product_info['img'] = img
    product_info['name'] = name
    product_info['price'] = price

    return product_info

def update_product_list(product_info):
    is_send = False
    id = product_info['id']
    url = product_info['url']
    img = product_info['img']
    name = product_info['name']
    price = product_info['price']

    if id not in product_list:
            product_list[id] = product_info
            is_send = True
    else:
        if product_list[id]['url'] != url:
            print("Before : " + product_list[id]['url'])
            print("After : " + url)
            product_list[id]['url'] = url
            is_send = True

        if product_list[id]['img'] != img:
            print("Before : " + product_list[id]['img'])
            print("After : " + img)
            product_list[id]['img'] = img
            # The image url of product, seems have load balance mechanism,
            # it is not fix.
            # is_send = True

        if product_list[id]['name'] != name:
            print("Before : " + product_list[id]['name'])
            print("After : " + name)
            product_list[id]['name'] = name
            is_send = True

        if product_list[id]['price'] != price:
            print("Before : " + product_list[id]['price'])
            print("After : " + price)
            product_list[id]['price'] = price
            is_send = True
    return is_send

def send_prd_info(product_info):
    id = product_info['id']
    url = "https:" + product_info['url']
    img = "https:" + product_info['img']
    name = product_info['name']
    price = product_info['price']

    file = SaveImg(img, id)

    msg = "\n" + "ID : " + id + "\n"
    msg = msg + "名稱 : " + name + "\n"
    msg = msg + "URL : " + url + "\n"
    # msg = msg + "圖片 : " + img + "\n"
    msg = msg + "價格 : " + price + "\n"

    print("ID : " + id)
    print("名稱 : " + name)
    print("URL : " + url)
    print("圖片 : " + img)
    print("價格 : " + price)
    print('-------------------')

    SendNotifyMessage(token, msg, file)

def old_product_clean_up(product_id_list):
    if product_id_list:
        for key in list(product_list):
            if key not in product_id_list:
                del product_list[key]
    save_data(DATA_FILE)

def Run():
    while True:
        error_times = 0
        print(datetime.datetime.now())
        try:
            Parse()
        except:
            error_times += 1
            print("error times = " + str(error_times))
            print(traceback.format_exc())
            pass
        time.sleep(30)

def load_data(file):
    try:
        global img_url, product_list

        with open(file, "r", encoding='utf8') as f:
            data = json.load(f)
            img_url = data['message_board']
            product_list = data['product_list']
    except:
        print(traceback.format_exc())

def save_data(file):
    try:
        global img_url, product_list

        data = dict()
        with open(file, 'w') as fp:
            data['message_board'] = img_url
            data['product_list'] = product_list
            json.dump(data, fp, indent=4)
        return True
    except:
        print(traceback.format_exc())

if __name__ == '__main__':
    load_data(DATA_FILE)
    Run()
