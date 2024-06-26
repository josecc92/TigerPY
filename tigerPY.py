from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd

import time
TIMEOUT =30
# 初始化 WebDriver（這裡使用 ChromeDriver）

def wait_for_page_load(driver, timeout=10):
    # 等待直到頁面的 readyState 變成 complete
    WebDriverWait(driver, timeout).until(
        lambda x: x.execute_script("return document.readyState === 'complete'")
    )
class tiger:
    departure_date = None
    #XX7 關東
    #XX8 關西
    #XX9 九州
    #XX2 北海道
    #XX6 中部
    #XX5 東北
    departure = None
    arrival = None
    adult = 2
    children = 0
    def __init__(self, departure, arrival, adult=1, children=0):
        self.departure = departure
        self.arrival = arrival
        self.adult = adult
        self.children = children
    pass
    def wait_for_page_load(driver, TIMEOUT):
        # 等待直到頁面的 readyState 變成 complete
        WebDriverWait(driver, TIMEOUT).until(
            lambda x: x.execute_script("return document.readyState === 'complete'")
        )
    def create_driver(self):
        # 設置Chrome選項
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--incognito")  # 啟用無痕模式

        # 創建WebDriver並設置選項
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        return driver

    def get_date_and_cost(self,base_date_str,driver=None,departure=None,arrival=None,adult=None,children=None):
        result_dict = []
        #if departure is not none
        if departure is not None:
            self.departure = departure
        if arrival is not None:
            self.arrival = arrival
        if adult is not None:            
            self.adult = adult
        if children is not None:
            self.children = children            
        
        departure_date = datetime.strptime(base_date_str, "%Y/%m/%d")
        return_date = departure_date + timedelta(days=5)
        # 將結果轉換回字串格式
        departure_date_str = departure_date.strftime("%Y-%m-%d")
        return_date_str = return_date.strftime("%Y-%m-%d")

        url = f"https://booking.tigerairtw.com/?type=roundTrip&outbound={self.departure}-{self.arrival}&inbound={self.arrival}-{self.departure}&departureDate={departure_date_str}&returnDate={return_date_str}&adult={self.adult}&children={self.children}&infant=0&languageCode=zh-tw&promotionCode="
        # print(url)
        driver.get(url)
        wait_for_page_load(driver)
        results = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.link.text-caption'))
        )
        time.sleep(3)
        WebDriverWait(driver, TIMEOUT)
        html_content = driver.page_source
        # print(html_content)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        gutters = soup.find_all('div', class_='q-gutter-y-md')
        try:
            for index, gutter in enumerate(gutters): #左右區塊
                # print(f"gutter {gutter} 是第 {index+1} 個")
                w_way = gutter.select('div.station-pair')[0].text
                spans = gutter.select('span.q-btn__content')
                for span in spans:
                    captions = span.find_all('div', class_='text-caption')
                    if(len(captions) ==2): #抓到日期價格欄位
                        if(captions[1].text=="-" or captions[1].text==""):
                            continue
                        w_date = captions[0].text
                        w_cost = int(captions[1].text.replace(",", ""))
                        result_dict.append({'w_way': w_way, 'w_date': w_date, 'w_cost': w_cost})
                            
                
            # print('==========')
        except Exception as e:
            print(f"發生錯誤: {str(e)}")
        # print(result_dict)
        return result_dict
    def calculate_best_price(self, data=None):

        # data =[{'w_way': '台灣 - 所有機場east九州地區 - 所有機場', 'w_date': '03/03', 'w_cost': 2399}, {'w_way': '台灣 - 所有機場east九州地區 - 所有機場', 'w_date': '03/04', 'w_cost': 1999}, {'w_way': '台灣 - 所有機場east九州地區 - 所有機場', 'w_date': '03/05', 'w_cost': 2699}, {'w_way': '台灣 - 所有機場east九州地區 - 所有機場', 'w_date': '03/06', 'w_cost': 2699}, {'w_way': '台灣 - 所有機場east九州地區 - 所有機場', 'w_date': '03/07', 'w_cost': 2999}, {'w_way': '九州地區 - 所有機場east台灣 - 所有機場', 'w_date': '03/08', 'w_cost': 1999}, {'w_way': '九州地區 - 所有機場east台灣 - 所有機場', 'w_date': '03/09', 'w_cost': 2299}, {'w_way': '九州地區 - 所有機場east台灣 - 所有機場', 'w_date': '03/10', 'w_cost': 2599}, {'w_way': '九州地區 - 所有機場east台灣 - 所有機場', 'w_date': '03/11', 'w_cost': 1999}, {'w_way': '九州地區 - 所有機場east台灣 - 所有機場', 'w_date': '03/12', 'w_cost': 2299}]
        # 分類資料
        df = pd.DataFrame(data)
        # 使用 unique() 方法找出不重複的 TYPE 值
        unique_types = df["w_way"].unique()
        print(unique_types[0].replace("east", "→"))
        in_data = [entry for entry in data if entry["w_way"] == unique_types[0]]
        out_data = [entry for entry in data if entry["w_way"] == unique_types[1]]
        combinations = []
        # 所有可能的組合，計算 COST 總和並存儲
        for in_entry in in_data:
            for out_entry in out_data:
                total_cost = in_entry["w_cost"] + out_entry["w_cost"]
                combinations.append((total_cost, in_entry, out_entry,in_entry["w_cost"],out_entry["w_cost"]))
        combinations.sort(key=lambda x: x[0])
        top_combinations = combinations[:5]
        # 列出最佳三個選項的組合
        for i, (cost_sum, in_entry, out_entry, in_cost, out_cost) in enumerate(top_combinations):
            date_range = (in_entry["w_date"], out_entry["w_date"])
            print(f"第{i+1}名{date_range} Cost: {in_cost} + {out_cost} = {cost_sum} NTD")
        data = None

if __name__ == "__main__":
    tiger1 = tiger( 'TPE', 'XX7')
    driver = tiger1.create_driver()
    dic = tiger1.get_date_and_cost('2024/08/11',driver,"TPE", "XX8", 2, 2)
    tiger1.calculate_best_price(dic)
    dic = tiger1.get_date_and_cost('2024/08/11',driver,"TPE", "XX7", 2, 2)
    tiger1.calculate_best_price(dic)    
    dic = tiger1.get_date_and_cost('2024/08/11',driver,"TPE", "XX9", 2, 2)
    tiger1.calculate_best_price(dic)
    dic = tiger1.get_date_and_cost('2024/08/11',driver,"TPE", "XX2", 2, 2)
    tiger1.calculate_best_price(dic)
    dic = tiger1.get_date_and_cost('2024/08/11',driver,"TPE", "XX6", 2, 2)
    tiger1.calculate_best_price(dic)
    dic = tiger1.get_date_and_cost('2024/08/11',driver,"TPE", "XX5", 2, 2)
    tiger1.calculate_best_price(dic)    
    driver.quit()
    #XX3 台灣
    #XX7 關東
    #XX8 關西
    #XX9 九州
    #XX2 北海道
    #XX6 中部
    #XX5 東北
