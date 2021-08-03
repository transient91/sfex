# sfex
 一个e站小爬虫(spider for exhentai)。  
 
 基于requests库爬取。
 
 sfex.exe是使用pyinstaller打包源码得到的可执行文件，无需其他依赖，可以直接使用。

# 下载
```
git clone https://github.com/transient91/sfex.git
cd sfex
ni config.json
```
若使用源码则需要
```
pip install -r requirements.txt
```

# 使用方法
首先你得能够登上exhentai，之后通过浏览器的开发者工具（F12）获取cookie。

第一次使用时需要用-c开关设置cookie。

详细使用方法如下：
```
Usage:
python sfex.py [options]        # 使用源码
or
sfex.exe [options]              # 使用可执行文件

Options:
-h,--help       Show help.
-u              待下载网址.
-p              待下载页码（默认全部下载，可选1-20,22）.
-c              设置cookie.
--proxy         https设置代理.
-t              是否使用日语标题（默认是，使用该选项则使用英语标题）.
-o              是否下载原图（默认是，使用该选项则为否）.
-r              下载文件位置（默认当前文件夹）.
```
例如：
```
python sfex.py -c "your cookie" -u  https://exhentai.org/g/1663191/c8ec3baf07/ -p 5-10,1,2-4 
```
