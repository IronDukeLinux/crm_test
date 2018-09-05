from django.test import TestCase

# Create your tests here.

import requests
import re


# 获取网页数据  常见get 和 post
# 解析网页数据  正则表达式、xpath解析
# 存储网页数据  txt文本、json文本或者数据库
# 分析网页数据  NumPy  Pandas  Matplotlib  进行数据分析

def getHero_data():
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        url = 'http://lol.qq.com/biz/hero/champion.js'
        res = requests.get(url, headers=headers)  # 获取网页
        res.raise_for_status()  # 失败请求抛出异常
        res.encoding = res.apparent_encoding  # 获取当前编码
        text = res.text  # 以encoding解析返回内容，字符串方式的响应体会自动根据响应头部的字符编码进行解码
        hero_id = re.findall(r'"id":"(.*?)","key"', text)
        hero_num = re.findall(r'"key":"(.*?)"', text)
        return hero_id, hero_num
    except:
        return '获取失败', '2'


def getUrl(hero_num):
    part1 = 'https://game.gtimg.cn/images/daoju/app/lol/medium/2-'
    part3 = '-9.jpg'
    skin_num = []
    url_list = []
    for i in range(1, 21):
        i = str(i)
        if len(i) == 1:
            i = '00' + i
        elif len(i) == 2:
            i = '0' + i
        else:
            continue
        skin_num.append(i)
    for hn in hero_num:
        for sn in skin_num:
            part2 = hn + sn
            url = part1 + part2 + part3
            url_list.append(url)
    print('图片url获取成功')
    return url_list


def PicName(hero_id, path):
    pic_name_list = []
    for id in hero_id:
        for i in range(1, 21):
            pic_name = path + id + str(i) + '.jpg'
            pic_name_list.append(pic_name)
    return pic_name_list


def download_pic(pic_name_list, url_list):
    count = 0
    n = len(url_list)
    try:
        for i in range(n):
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
            }
            res = requests.get(url_list[i], headers=headers).content
            if len(res) != 19:  # 用来排除掉网址错误的情况  404 ...
                with open(pic_name_list[i], 'wb') as f:
                    f.write(res)
                    count += 1
                    print('\r当前进度: {:.2f}%'.format(100 * (count / n)), end='')
            else:
                count += 1
                print('\r当前进度: {:.2f}%'.format(100 * (count / n)), end='')
    except:
        return '失败'


if __name__ == '__main__':
    path = r'D:\pic\\'
    hero_id, hero_num = getHero_data()
    url_list = getUrl(hero_num)
    pic_name_list = PicName(hero_id, path)
    print('正在下载图片')
    download_pic(pic_name_list, url_list)
    print('over')
