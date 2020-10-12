### 利用数据库批量下载论文

利用校园网下载文献，可以下载的数据库有
```python
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
```


#### 使用须知[参考](http://mp.weixin.qq.com/s?__biz=MzI0ODU5NjcyOQ==&mid=100000792&idx=1&sn=910ddf0f2fb39bdd63ec6dc9d9e81357&chksm=699f158e5ee89c985c586caf219334f417e8c7fac1f6be8fd06d8497b3416553b3f22a20c8d5#rd)

#### 使用流程操作

1. 安装chromedriver + selenium 

   [参考链接](https://www.cnblogs.com/lfri/p/10542797.html)

2. 百度识图申请api

   [参考链接](https://login.bce.baidu.com/)

   修改程序 baidu_api.py 中的申请到的相关数据

   ```python
   APP_ID = ''
   API_KEY = ''
   SECRET_KEY = ''
   ```

3. 修改程序 ocr_selenium.py 文件中的

   ```python
   def handle_code(self):
           img = Image.open(self._default_original_code)
           x, y = img.size
           cropped = img.crop((320, 200, 800, 350))# 
           该部分于电脑分辨率有关系，需要自己根据使用电脑设置
   ```

4. 使用 demo

   ```python
   test_doi = '10.1109/3.328589' # iEEEE
   demo = getpaper(test_doi).find_url()
   ```

#### 其他参考资料

[python导出WOS的参考文献](http://mp.weixin.qq.com/s?__biz=MzI0ODU5NjcyOQ==&mid=100000769&idx=1&sn=9b4cb2311df156889486497c0a32e1e7&chksm=699f15975ee89c819ceb28923d27deb8c9060a1672b4151b432140f401ebbedfb7ac3444266e#rd)

[本篇实现爬虫的细节分享](http://mp.weixin.qq.com/s?__biz=MzI0ODU5NjcyOQ==&mid=100000809&idx=1&sn=f97b21aa044e146dede51b0d8fb5f9e0&chksm=699f15bf5ee89ca933e8f0614c8d6be435331bf64139dad1d49c3dfce63a63453fe3b8d8bf96#rd)





