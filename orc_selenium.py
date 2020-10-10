from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import time
import os
# import pytesseract
# import pyautogui
import requests
import re

from baidu_api import baidu_ocr
 
DownloadTimes = 2

class Identifica_code():
    def __init__(self, url, doi, path='', option = 'baidu'):
        self.url = url
        self.option = option
        self.file_name = '{}.pdf'.format(doi.replace('.','_').replace('/','__'))
        self._default_original_code = 'original_code.png'
        self._default_code = 'code.png'
        if not os.path.exists('./pdf'):
            os.mkdir('./pdf')
        self.path = './pdf'  if not path else path

    def __str__(self):
        return ('you can use two methods ocr pic : "baidu" and "tesserate" default is {}'.format(self.option))

    def get_pdf(self, wait_time):
        global DownloadTimes
        while  DownloadTimes:
            print ('this is {} times of download'.format(DownloadTimes))
            self.get_code(wait_time)
            if self.file_name == find_new_file(self.path):
                print("download succesfull")
                break
            else:
                DownloadTimes -= 1 
                self.get_code(wait_time+5)

    def get_code(self, wait_time):
        # 初始化一个谷歌浏览器实例
        
        # 使用不显示浏览器界面
        options = webdriver.ChromeOptions()    
        # options.add_argument('headless')
        driver = webdriver.Chrome(chrome_options = options)
        driver.maximize_window()
        # 这里设置为你的电脑的分辨率，不然会影响到后期的截图处理 验证码
        # driver.set_window_size(2736, 1824)
        
        print('now chromdriver start load {}, you need wait {}s'.format(self.url, wait_time))
        driver.get(self.url)
        time.sleep(2) #  网页加载需要时间
        driver.get_screenshot_as_file(self._default_original_code)
        self.handle_code()
        print('Successfully obtained interception, now start to identify')
        code = self.ocr_code()
        driver.find_element_by_id('Answer').send_keys(code)
        driver.find_element_by_xpath('/html/body/div/div/form/input[3]').click()
        code_error = 'Incorrect code entered'
        if code_error in driver.page_source:
            driver.quit()
            print(code_error + '      restart!')
            self.get_code(wait_time)

        # -----------------------------最佳方法---------------------------------------
        time.sleep(wait_time)
        # uri = self._get_uri()
        print('The verification code is successfully recognized and the download starts')
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.70',
            'Origin':'https://www.osapublishing.org',
            'Host':'www.osapublishing.org',
        }
        url = driver.current_url
        r = requests.get(url=url, headers=headers)
        with open(self.path + '/' + self.file_name, 'wb+') as f:
            f.write(r.content)
        driver.quit()
        # -------------------------老方法 ---------------------------
        # element = driver.find_element_by_xpath("/html/body")
        # actionChains = ActionChains(driver)
        # actionChains.context_click(element).perform()
        
        # pyautogui.typewrite(['down', 'down', 'down'])  # 选中右键菜单中第3个选项
        # pyautogui.typewrite(['enter'])
        # time.sleep(2)
        # pyautogui.typewrite(['enter'])
        # time.sleep(wait_time)
        # ---------------------------------------------------------
    def _get_uri(self):
        url_pattern = re.compile(r'uri=(\S+)')
        return url_pattern.search(self.url).group(1)
    
    def _get_guid(self, guid_str):
        guid_partten = re.compile(r'guid=(\S+)')
        return guid_partten.search(guid_str).group(1)

    def handle_code(self):
        img = Image.open(self._default_original_code)
        x, y = img.size
        cropped = img.crop((320, 200, 800, 350))  # (left, upper, right, lower)
        # left_rate = 800 / 2736
        # upper_rate = 100 / 1824 
        # right_rate = 1100 / 2736
        # lower_rate = 200 / 1824
        # cropped = img.crop((left_rate * x, upper_rate * y, right_rate * x, lower_rate * y))
        cropped.save(self._default_code)

    def ocr_code(self):
        if self.option == 'baidu':
            try:
                print ('now use baidu api ')
                code = baidu_ocr(filePath='code.png').get_result().replace(' ','').lower()
                print('code is {}'.format(code))
            except Exception :
                print ('识别失败')
        elif self.option == 'tesserate':
            try:
                print('now use tesserate ocr')
                code = pytesseract.image_to_string(Image.open(self._default_code))
            except Exception :
                print('识别失败')
        else:
            raise Exception('you need choose a ture option!')

        return code

def find_new_file(dir):
    file_lists = os.listdir(dir)
    file_lists.sort(key=lambda fn: os.path.getmtime(dir + "\\" + fn)
                     if not os.path.isdir(dir + "\\" + fn) else 0)
    print('最新的文件为： ' + file_lists[-1])
    # __, adress = file_lists[-1].split('.')

    return file_lists[-1]

if __name__ == "__main__":
    url = 'https://www.osapublishing.org/optica/abstract.cfm?uri=optica-7-1-40'
    doi = '10.1364/OPTICA.7.000040'
    demo = Identifica_code(url, doi)
    demo.get_pdf(5)


