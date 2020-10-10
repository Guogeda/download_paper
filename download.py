import requests
from bs4 import BeautifulSoup
import re
import time
import os

import orc_selenium

class getpaper():
    def __init__(self, doi, path=''):
        '''
        lib = (
        'osapublishing',
        'iopscience',
        'ieeexplore',
        'onlinelibrary',
        'aip.scitation',
        'nature',
        'journals.aps',
        'linkinghub', # sci
        )
        '''
        if not os.path.exists('./pdf'):
            os.mkdir('./pdf')
        self.path = './pdf'  if not path else path
        self.doi = doi
        self.session = requests.session()
        self.headers = {
            'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.70',
        }
        self.base_url = 'http://doi.org/'

    def find_url(self):
        url = self.base_url + self.doi
        self.find_response = self.session.get(url=url, verify=False, headers = self.headers)
        
        # return (self.find_response.url)
        self.find_url = self.find_response.url
        if 'osapublishing' in self.find_url:
            self.osa_download()
        elif 'iopscience' in self.find_url:
            self.iop_download()
        elif 'ieeexplore' in self.find_url:
            self.i3e_download()
        elif 'onlinelibrary' in self.find_url:
            self.onlinelib_download()
        elif 'aip.scitation' in self.find_url:
            self.aip_download()
        elif 'nature' in self.find_url:
            self.nature_download()
        elif 'journals' in self.find_url:
            self.journals_download()
        elif 'linkinghub' in self.find_url:
            self.linkhub_download()
        
        else:
            return (self.find_response.url)
            raise Exception('database no  recording')
        
    def osa_download(self):
        print(self.find_url)
        find_soup = BeautifulSoup(self.find_response.text, 'lxml')
        self.paper_url = find_soup.find(name='meta', attrs ={'property':"og:url"})['content']
        download_url = find_soup.find(name='li', attrs={'class':'pdf-download'}).a['href']
        download_url = 'https://www.osapublishing.org/ol/' + download_url
        download = orc_selenium.Identifica_code(download_url, self.doi, path=self.path).get_pdf(5)
        
    def iop_download(self): # 小心，这个网站很小气，很容易封ip
        print(self.find_url)
        download_url = self.find_url + '/pdf'
        pdf_response = self.session.get(download_url,headers =self.headers)
        self.save(pdf_response)
        
    def i3e_download(self): 
        print(self.find_url)
        # I3E 也需要重新设置header
        header = self.headers
        header['Host'] = 'ieeexplore.ieee.org'
        header['Connection'] = 'keep-alive'
        header['Upgrade-Insecure-Requests'] = str(1)
        header['Sec-Fetch-Dest'] = 'document'
        header['Sec-Fetch-User'] = '?1'
        header['Pragma'] = 'no-cache'
        header['Sec-Fetch-Mode'] = 'navigate'
        header['Sec-Fetch-Site'] = 'same-origin'
        header['Cache-Control'] = 'no-cache'
        header['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        header['Accept-Encoding'] = 'gzip, deflate, br'

        pdf_pattern = re.compile(r'document/(\S+?)/')
        arnumber = pdf_pattern.search(self.find_url).group(1)
        pdf_url = 'https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={}&ref='.format(arnumber)
        paper_reponse = self.session.get(url = pdf_url, headers = header)
        self.save(paper_reponse)

    def onlinelib_download(self):
        download_url = self.find_url.replace('full','pdfdirect') + '?download=true'
        r = self.session.get(url=download_url, headers = self.headers)
        self.save(r)
        
    def aip_download(self):
        print(self.find_url)
        download_url = self.find_url.replace('doi','doi/pdf')
        r = self.session.get(url=download_url, headers = self.headers)
        self.save(r)
        
    def nature_download(self):
        print(self.find_url)
        download_url = self.find_url + '.pdf'
        r = self.session.get(url=download_url, headers = self.headers)
        self.save(r)
    
    def journals_download(self):
        print(self.find_url)
        download_url = self.find_url.replace('abstract','pdf')
        r = self.session.get(url=download_url, headers = self.headers)
        self.save(r)

    def linkhub_download(self): 
        # sci 网页重定向太多，一个一个找

        # 正真的论文界面 url 
        paper_url = self.find_url.replace('linkinghub.elsevier.com/retrieve','www.sciencedirect.com/science/article') + '?via%3Dihub'
        
        # 如果要获取pdf链接，需要重新设置header的值
        header = self.headers
        header['referer'] = self.find_url
        header['authority'] = 'www.sciencedirect.com'
        header['method'] = 'GET'
        paper_response = self.session.get(url= paper_url, headers = header)
        paper_soup = BeautifulSoup(paper_response.text, 'lxml')
        download_url = paper_soup.find(name='script',attrs={'type':'application/json'})

        # 利用 re 正则提取 pdf 链接，这里有个 异步加载，所以需要用正则
        pdf_pattern = re.compile(r'"linkToPdf":"(\S+?)"')
        download_url = 'https://www.sciencedirect.com' + pdf_pattern.search(str(download_url)).group(1)

        # 进入 pdf 界面需要重新更新 header 头
        header['referer'] = download_url
        download_respons = self.session.get(url = download_url, headers = header, timeout = 1)
        
        # 上面的 url 需要一定的时间才能加载，不知道是什么原因， 不过可以通过 获取的页面 提取正真的 下载 url
        ture_pdf_pattern = re.compile(r"window.location = '(\S+?)'")
        ture_download_url = ture_pdf_pattern.search(str(download_respons.text)).group(1)
        # print(ture_download_url)
        ture_response = self.session.get(url = ture_download_url, headers = header, timeout = 1)
        self.save(ture_response)

        print ('ok')

    def science_download(self):
        print(self.find_url)

    def save(self, response):
        file_name = '{}.pdf'.format(self.doi.replace('.','_').replace('/','__'))
        with open(self.path + '/' + file_name, 'wb+') as f:
            f.write(response.content)

def get_doi(file_name):
    packages = []
    package_dict = {}
    flag = False
    with open(file_name, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline()
            if line:
                if line[:2] != 'ER':
                    if line[:2] != '  ':
                        flag = False
                        if not flag:
                            temp_str = ''
                            temp_title = ''
                        temp_title = line[:2]
                        temp_str = line[3:-1] if temp_title != 'AU' else line[3:-1] + ';'
                        package_dict[temp_title] = temp_str   
                    elif line[:2] == '  ' and line != '\n':
                        flag = True
                        temp_str += line[2:-1] if temp_title != 'AU' else line[3:-1] + ';'
                        package_dict[temp_title] = temp_str 
                else:
                    packages.append(package_dict)
                    package_dict = {}
            else:
                break
    return packages


if __name__ == "__main__":
    file_name = 'LNOI.txt'
    allpapers = get_doi(file_name)
    fail = []
    # print("total has {} papers".format(len(allpapers)))
    # for index, items in enumerate(allpapers[0:90]):
    #     try:
    #         doi = items['DI']
    #         if doi == '10.1109/JLT.2006.874605':
    #             print(index)
    #     except Exception :
    #         print('no doi')

    # strat 56   '10.1103/PhysRevA.97.013813' 第 61 
    # end 83  ’10.1109/JLT.2006.874605‘ 第90
    for index, items in enumerate(allpapers[57]):
        try:
            doi = items['DI']
            # print(doi)
            pdf = getpaper(doi).find_url()
        except Exception :
            print('no doi')
            fail.append(index)
            print(items)
            # print('{} download fail'.format(items['TI']))
    # print(fail)
    with open('61-83_fail.txt', 'w', encoding= 'utf-8') as f :
        f.write(','.join(str(i + 56) for i in fail))
    
    




    # print(len(allpapers))
    # print(allpapers[0]['DI'])
    # test_doi = '10.1088/2040-8978/18/10/104001'

    # test_doi = '10.1364/OL.44.000618' # osa
    # test_doi = '10.1364/OPTICA.7.000040'# osa
    # 'http://doi.org/10.1088/2040-8978/18/10/104001' # iop
    # test_doi = '10.1109/3.328589' # iEEEE
    # test_doi = '10.1002/adma.201504722' # onlinelib
    # test_doi = '10.1063/1.4931601' # aip
    # test_doi = '10.1038/37539' # nature
    # test_doi = '10.1103/PhysRevLett.85.74' # journals
    # test_doi = '10.1016/j.optcom.2014.05.021' # linkhub  sci 
    # test_doi = '10.1126/science.1193968'
    # demo = getpaper(test_doi)
    # print(demo.find_url())

    


    
