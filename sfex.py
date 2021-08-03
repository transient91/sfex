#！/usr/bin/env python3
#-*-coding: UTF-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import os
from tqdm import tqdm
import sys
import getopt
import json
from fake_useragent import UserAgent


def get_html_respond(url, param=None):
    proxy = ''
    with open('config.json', 'r', encoding='utf-8') as f:
        try:
            cookie = json.load(f)['cookie']
            f.seek(0)
            proxy = json.load(f)['proxy']
        except json.decoder.JSONDecodeError:
            print('请先设置cookie后再使用')
            sys.exit(1)
        except KeyError:
            pass

    headers = {'Cookie': cookie, "User-Agent": UserAgent().random}
    proxies = {'https': proxy}
    r = requests.get(url,
                     params=param,
                     timeout=30,
                     headers=headers,
                     proxies=proxies)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r


def get_download_images(download_images_str, last_image):
    #输入要下载的页码（如1-20,22）和最大页码，返回要下载的所有页码构成的列表
    download_images = []
    download_images_list = download_images_str.split(',')
    for str in download_images_list:
        if '-' in str:
            begin2end = str.split('-')
            for i in range(int(begin2end[0]), int(begin2end[-1]) + 1):
                if i >= 1 and i <= int(last_image):
                    download_images.append(i)
        else:
            if int(str) >= 1 and int(str) <= int(last_image):
                download_images.append(int(str))

    download_images = list(set(download_images))
    download_images.sort()
    return download_images


def print_usage():
    print('Usage:')
    print('python sfex.py [options]\t# 使用源码')
    print('or')
    print('sfex.exe [options]\t\t# 使用可执行文件\n')
    print('Options:')
    print('-h,--help\tShow help.')
    print('-u\t\t待下载网址.')
    print('-p\t\t待下载页码（默认全部下载，可选1-20,22）.')
    print('-c\t\t设置cookie.')
    print('--proxy\t\thttps设置代理.')
    print('-t\t\t是否使用日语标题（默认是，使用该选项则使用英语标题）.')
    print('-o\t\t是否下载原图（默认是，使用该选项则为否）.')
    print('-r\t\t下载文件位置（默认当前文件夹）.')


def set_json(param, filename='config.json'):
    if os.path.getsize(filename) != 0:
        with open(filename, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data[param] = arg
            f.seek(0)
            f.truncate()
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({param: arg}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    try:
        # h帮助 u:输入网址 p:下载页码 t:文件夹名语言 o是否下载原图 -r:下载文件位置 -c:设置cookie --proxy:设置代理
        opts, args = getopt.getopt(sys.argv[1:], 'hu:p:tor:c:',
                                   ['help', 'proxy='])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    if len(opts) == 0:
        print_usage()
        sys.exit(2)

    if not os.path.exists('config.json'):
        print('缺少config.json')
        sys.exit(1)

    origin = True
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_usage()
            sys.exit()
        elif opt == '-u':
            url = arg
        elif opt == '-o':
            origin = False
        elif opt == '-c':
            set_json('cookie')
        elif opt == '--proxy':
            set_json('proxy')

    soup = BeautifulSoup(get_html_respond(url).text, 'html.parser')
    last_image = re.search(r'Showing \d* - \d* of (\d*) images',
                           soup.find(name='p', class_='gpc').string).group(1)
    download_images = get_download_images('1-' + last_image, last_image)

    root = ''
    foldername = soup.find(name='h1', id='gj').string
    for opt, arg in opts:
        if opt == '-p':
            download_images = get_download_images(arg, last_image)
        elif opt == '-r':
            root = arg + '\\'
        elif opt == '-t':
            foldername = soup.find(name='h1', id='gn').string

    foldername = root + foldername
    if not os.path.exists(foldername):
        os.mkdir(foldername)

    last_page = soup.find_all(name='a', href=re.compile(url))[-2].string

    exit_flag = False
    with tqdm(total=len(download_images)) as pbar:
        for page in range(0, int(last_page)):
            soup = BeautifulSoup(
                get_html_respond(url, {
                    'p': str(page)
                }).text, 'html.parser')
            for tag in soup.find_all(name='img', alt=re.compile(r'\d*')):
                if int(tag['alt']) in download_images:
                    soup2 = BeautifulSoup(
                        get_html_respond(tag.parent['href'], {
                            'p': str(page)
                        }).text, 'html.parser')

                    try:
                        if origin is False:
                            raise TypeError
                        download_url = soup2.find(
                            name='a',
                            href=re.compile(
                                r'https://exhentai.org/fullimg.php'))['href']
                    except TypeError:
                        download_url = soup2.find(name='img', id='img')['src']

                    path = foldername + '\\' + tag['alt'] + '.jpg'
                    if not os.path.exists(path):
                        with open(path, mode='wb') as pic:
                            pic.write(get_html_respond(download_url).content)
                    pbar.update(1)
                if int(tag['alt']) == download_images[-1]:
                    exit_flag = True

            if exit_flag is True:
                break

    print('done!')