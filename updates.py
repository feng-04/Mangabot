from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import time
from urllib.parse import urlparse
from datetime import datetime

month_dict = {
            "JAN": "01", 
            "FEB": "02", 
            "MAR": "03", 
            "APR": "04", 
            "MAY": "05", 
            "JUN": "06", 
            "JUL": "07", 
            "AUG": "08", 
            "SEPT": "09", 
            "OCT": "10", 
            "NOV": "11",
            "DEC": "12", 
            "SEP": "09"
        }


class update:
    def __init__(self, name):
        self.name = name
        self.driver = self.get_driver()
        self.actions = ActionChains(self.driver)


    def get_driver(self):
        chrome_option = Options()
        #chrome_option.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_option)
        return driver


    def navigate(self, xpath):
        stuff = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, f"{xpath}"))
        )
        self.actions.click(stuff).perform()

    # go to the title page
    def finding_title(self):
        stuff = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{self.name}')]"))
        )
        self.actions.click(stuff).perform()

        # parse url
        current_url = self.driver.current_url
        parsed_url = urlparse(current_url)
        components = [comp for comp in parsed_url.path.split('/') if comp]
        
        # in case it doesnt go into the chapter page directly
        if components[0] == "updates":
            stuff = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{self.name}')]"))
            )
            self.actions.click(stuff).perform()


    # to get to the main webpage of mangaplus
    def main_page(self):
        self.driver.get("https://mangaplus.shueisha.co.jp/updates")

        self.actions.move_by_offset(10, 10).click().perform()

        # cookies
        self.navigate("//*[@id='onetrust-accept-btn-handler']")
    
        # select language page
        self.navigate("//*[@id='app']/div[2]/div/div[1]/header/div/div[3]/div/span")

        # langugae
        self.navigate("//*[@id='app']/div[2]/div/div[1]/div[1]/div[2]/div[1]/div/div[1]")


    # get to the chapter page
    def chapter_page(self):

        self.main_page()
        # we are in the title page rn
        self.finding_title()

        time.sleep(1)

        date = self.reformat()
        # go to the chapter page
        stuff = self.driver.find_elements(By.CLASS_NAME, "ChapterListItem-module_chapterListItem_ykICp")
        
        self.actions.click(stuff[7]).perform()
        
        # parse url for later verification
        current_url = self.driver.current_url
        parsed_url = urlparse(current_url)
        components = [comp for comp in parsed_url.path.split('/') if comp]

        # check if the current page is the title page or chapter page
        if components[0] == "titles":
            self.actions.click(stuff[7]).perform()

        return date


    # to check what chapter it is, 
    def get_chapter(self):

        # find the chapter number from the chapter page
        find_number = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div/div[3]/div[1]/div[2]/div/p'))
        )

        chap_number = find_number.text

        url = self.driver.current_url
        return url, chap_number
    
    
    # always use after get_chapter, so that it doesnt click where it is not supposed to
    def reformat(self):
        # release date from mangaplus is 9 SEPT 2024 format, need a dict also
        date_element = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_any_elements_located((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div/div[2]/main/div/div[9]/div[1]/p[2]'))
        )
        
        # release date
        stringdate = date_element[0].text
        length = len(stringdate)
        day = 0
        month = 0
        year = 0
        
        # keep track of which index is space
        space_indices = []
        for i in range(length):
            if stringdate[i] == " ":
                space_indices.append(i)
        
        # space indices are now populated

        day = stringdate[0:space_indices[0]]
        month = month_dict[stringdate[space_indices[0]+1:space_indices[1]]]
        year = stringdate[space_indices[1]+1:length]
        unformat = [year, month, day]
        date = "-".join([str(item) for item in unformat])
        return date
    
    # check for break
    def check_break(self):
        self.main_page()
        self.finding_title()
        print(self.driver.current_url)
       
        raw_text = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_any_elements_located((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div/div[2]/topside/div[2]/p[1]/span'))
        )
        
        # get the text containing relase date
        # parse the release date
        good_text = raw_text[0].text
        comma = []

        # split when there is a , 
        for i in range(len(good_text)):
            if good_text[i] == ",":
                comma.append(i)
        rough_date = good_text[comma[0]+2:comma[1]]

        # split the date
        substring_list = rough_date.split(" ")
        month = month_dict[substring_list[0].upper()]
        day = substring_list[1]
        year = '0'

        date_now = datetime.now()
        current_month = date_now.strftime("%m")
        currentyear = date_now.strftime('%Y')

        # checking if we are at the end of the year
        if current_month == "12" and month == "01":
            # new chapter coming out next year
            year = int(currentyear) + 1
        else:
            year = currentyear

        datelist = [year, month, day]
        release_date = '-'.join([str(item) for item in datelist])
        return release_date
