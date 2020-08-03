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
import threading

try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    CurrentPath = sys._MEIPASS
except Exception:
    CurrentPath = os.path.abspath(".")

BOARD_URL = 'https://24h.pchome.com.tw/store/DGBJHC'
SEARCH_URL = 'https://ecshweb.pchome.com.tw/search/v3.3/?q=%E5%8B%95%E7%89%A9%E6%A3%AE%E5%8F%8B%E6%9C%83%20%E5%8B%95%E6%A3%AE&scope=24h&sortParm=new&sortOrder=dc&cateId=DGBJ'
WEEKLY_URL = 'https://24h.pchome.com.tw/store/DGBJHC?style=2'
PRODUCT_LIST_URL = 'https://24h.pchome.com.tw/store/DGBJDE?style=2'

token = 'oooooooooow6k7SlTHNuvTFsBegCO0vWpoooooooooo' # 自己
DATA_FILE = os.path.join(CurrentPath, 'product_data.json')

img_url = list()

product_info = dict()
product_list = dict()

def Parse_Board(driver, url):
    driver.get(url)
    product_id_list = list()
    pageSource = driver.page_source  # 取得網頁原始碼
    soup = BeautifulSoup(pageSource, "html.parser")
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

def Parse_Search_Page(driver):
    driver.get(SEARCH_URL)
    product_id_list = list()

    pageSource = driver.page_source  # 取得網頁原始碼
    soup = BeautifulSoup(pageSource, "html.parser")
    # driver.close()  # 關閉瀏覽器

    for products in soup.select('{}'.format("div#ItemContainer dl")):
        is_send = False
        product_info = parse_search_product(products)
        product_id_list.append(product_info['id'])
        is_send = update_product_list(product_info)

        if is_send:
            send_prd_info(product_info)
            save_data(DATA_FILE)

    # old_product_clean_up(product_id_list)

def Parse_Product_Page(driver, url):
    driver.get(url)
    product_id_list = list()

    pageSource = driver.page_source  # 取得網頁原始碼
    soup = BeautifulSoup(pageSource, "html.parser")
    # driver.close()  # 關閉瀏覽器

    for products in soup.select('{}'.format("div#ProdListContainer dl")):
        is_send = False
        product_info = parse_product_list(products)
        product_id_list.append(product_info['id'])
        is_send = update_product_list(product_info)

        if is_send:
            send_prd_info(product_info)
            save_data(DATA_FILE)

    # old_product_clean_up(product_id_list)

def parse_search_product(products):
    product_id = products['id']
    product_url = products.select_one('{}'.format(".prod_img"))
    product_img = products.select_one('{}'.format(".prod_img img"))
    product_name = products.select_one('{}'.format("dd.c2f h5.prod_name a"))
    product_price = products.select_one('{}'.format("dd.c3f ul.price_box li span.price span"))

    id = product_id
    url = product_url['href']
    img = product_img['src']
    name = product_name.text
    price = product_price.text

    product_info = dict()
    product_info['id'] = id
    product_info['url'] = url
    product_info['img'] = img
    product_info['name'] = name
    product_info['price'] = price

    return product_info

def parse_product_list(products):
    product_id = products['_id']
    product_url = products.select_one('{}'.format(".prod_img"))
    product_img = products.select_one('{}'.format(".prod_img img"))
    product_name = products.select_one('{}'.format("dd.c2f h5.nick a span.extra"))
    product_price = products.select_one('{}'.format("dd.c3f ul.price_box li span.price span"))

    id = product_id
    url = product_url['href']
    img = product_img['src']
    name = product_name.text
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

def Fetch_Board(url):
    driver = create_driver()
    while True:
        error_times = 0
        print("Page：" + str(datetime.datetime.now()))
        try:
            Parse_Board(driver, url)
        except:
            error_times += 1
            print("Page error times = " + str(error_times))
            print(traceback.format_exc())
            pass
        time.sleep(0.5)
    driver.close()  # 關閉瀏覽器

def Run_Search():
    driver = create_driver()
    while True:
        error_times = 0
        print("Srarch：" + str(datetime.datetime.now()))
        try:
            Parse_Search_Page(driver)
        except:
            error_times += 1
            print("Srarch error times = " + str(error_times))
            print(traceback.format_exc())
            pass
        time.sleep(0.5)
    driver.close()  # 關閉瀏覽器

def Fetch_Products(url):
    driver = create_driver()
    while True:
        error_times = 0
        print("Get Product：" + str(datetime.datetime.now()))
        try:
            Parse_Product_Page(driver, url)
        except:
            error_times += 1
            print("Srarch error times = " + str(error_times))
            print(traceback.format_exc())
            pass
        time.sleep(0.5)
    driver.close()  # 關閉瀏覽器

def load_data(file):
    try:
        global img_url, product_list

        with open(file, "r", encoding='utf8') as f:
            data = json.load(f)
            img_url = data['message_board']
            product_list = data['product_list']
    except:
        print(traceback.format_exc())

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    # 不加載圖片, 提升速度
    chrome_options.add_argument('blink-settings=imagesEnabled=false')

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
    return driver

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

    # 建立子執行緒
    t1 = threading.Thread(target = Fetch_Board, args=(BOARD_URL,))
    # t2 = threading.Thread(target = Run_Search)
    t3 = threading.Thread(target = Fetch_Products, args=(PRODUCT_LIST_URL,))
    t4 = threading.Thread(target = Fetch_Products, args=(WEEKLY_URL,))

    # 執行子執行緒
    t1.start()
    # t2.start()
    t3.start()
    t4.start()

    # 等待子執行緒結束
    t1.join()
    # t2.join()
    t3.join()
    t4.join()
