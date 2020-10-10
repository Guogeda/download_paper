# encoding:utf-8
from PIL import Image


from aip import AipOcr


APP_ID = '22789065'
API_KEY = 'HbxVcKK61DzpI7n2SdxjrIsl'
SECRET_KEY = 'FIqgzp75O66RuCmq9CGolAvNkEXXUW1E'

class baidu_ocr():
    def __init__(self, filePath):      
        self.filePath = filePath  
        self.client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    
    def get_result(self):
        image = self.get_file_content()
        result = self.client.basicAccurate(image)['words_result'][0]['words']
        return result
    """ 读取图片 """
    def get_file_content(self):
        with open(self.filePath, 'rb') as fp:
            return fp.read()

if __name__ == "__main__":

    img = Image.open('original_code.png')
    x, y = img.size
    left_rate = 800 / 2736
    upper_rate = 100 / 1824 
    right_rate = 1010 / 2736
    lower_rate = 200 / 1824
    cropped = img.crop((left_rate * x, upper_rate * y, right_rate * x, lower_rate * y))  # (left, upper, right, lower)
    cropped.save('code.png')
    demo = baidu_ocr('code.png')
    print(demo.get_result())