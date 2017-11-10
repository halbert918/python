# -*- coding:utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import re
import threadpool
import time
from datetime import datetime, timedelta
from time import sleep
import sys
from area import AreaNode
from lp import LouPan
from db import dbutil
import logger

reload(sys)
sys.setdefaultencoding("utf-8")


class Anjuke(object):

    pageNum = 1     #默认页码数量

    def __init__(self):
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        # 初始化headers
        self.headers = {'User-Agent': self.user_agent}
        # 存放区域对象
        self.areaNodes = []
        # 存放程序是否继续运行的变量
        self.enable = False

    def getAreas(self, start_url):
        try:
            pageData = self.get(start_url)

            bs = BeautifulSoup(pageData)
            dls = bs.select('div[class="sel-city"] > div > dl')
            for dl in  dls:
                dts = dl.select("dt")

                area = ''         #设置区域  华北东北  华东地区 ...
                if dts.__len__() > 0:
                    dt = dts.pop(0)
                    area = dt.string
                # 获取城市以及对应的连接
                _as = dl.select("dd > a")
                for a in _as:
                    # 构造area对象
                    node = AreaNode(area, a.string, a.get("href"))
                    self.areaNodes.append(node)
                # print self.areaNodes.__len__()
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print u"连接失败,错误原因", e.reason
                return None

    # 获取区县请求连接数据
    def getCounty(self, node):
        # 保存当前楼盘列表地址
        lp_href = []
        try:
            # 获取区县数据
            pageData = self.get(node.getHref())
            if pageData is None:
                return lp_href
            bs = BeautifulSoup(pageData)

            div = bs.select('div[class="item-area"] div[class="filter"]')
            if div.__len__() > 0:
                _as = div.pop(0).select("a")
                for a in _as:
                    # 元组(区域, 城市, 区县, 区县连接)
                    tup = (node.area, node.city, a.string, a.get("href"))
                    # lps.append(a.get("href"))
                    lp_href.append(tup)
                return lp_href
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print u"连接失败,错误原因", e.reason
            # return None
        return lp_href

    # 获取楼盘信息
    def getLouPan(self, lp, page):
        href = lp[1]
        # 构造多页请求地址
        if page > 1:
            href += "/p" + str(page) + "/"

        lps = []
        # 获取区县楼盘列表数据
        pageData = self.get(lp[3])
        if pageData is None:
            return lps

        bs = BeautifulSoup(pageData)

        if page == 1:
            pageNums = bs.select('div[class="pagination"] a')
            len = pageNums.__len__()
            if len > 1:
                global pageNum
                pageNum = int(pageNums.__getitem__(len - 2).string)

        divs = bs.select('div[class="key-list"] > div[class="item-mod"]')

        # 处理每个楼盘信息
        for div in divs:
            loupan = LouPan(lp[0], lp[1], lp[2], '', '', '', '', '', 'NULL', 'NULL') #创建楼盘信息对象
            data_link = div.get("data-link")
            lp_data = self.get(data_link)

            if lp_data is None:
                continue
            loupan.href = data_link

            lp_bs = BeautifulSoup(lp_data)
            title = lp_bs.select_one('div[class="lp-tit"] > h1')
            loupan.name = title.string

            container = lp_bs.select_one('div[id="container"]')
            # container = lp_bs.select_one('div[id="container"] div[class="basic-parms-wrap"]')
            p_price = container.select_one('dd[class="price"] p')
            price = p_price.select_one("em")
            # 判断是否为数字
            if price is not None and price.string.isdigit():
                loupan.price = price.string
                pattern = re.compile('</em>.*?\n', re.S)
                unit = re.findall(pattern, str(p_price))
                if unit.__len__() > 0:
                    if unit[0].__contains__("万"):
                        loupan.unit = "万/套"
                    elif unit[0].__contains__("元"):
                        loupan.unit = "元/平"

            around_price = container.select_one('dd[class="around-price"] span')
            if around_price is not None and around_price.string.isdigit():
                loupan.around_price = around_price.string

            # 获取开盘时间和交房时间
            # times = container.select('p')
            times = container.select('p.info-new span')
            if times.__len__() > 0:
                loupan.start_time = times[0].string
                if times.__len__() > 1:
                    loupan.deliver_time = times[1].string
            lps.append(loupan)

        # 保存数据库
        if lps.__len__() > 0:
            self.save(lps)
        # 递归调用,处理后面页码
        if page <= pageNum:
            page += 1
            # lps.extend(self.getLouPan(lp, page))
            self.getLouPan(lp, page)
        return lps

    # http get请求
    def get(self, url):
        try:
            request = urllib2.Request(url, headers=self.headers)
            # 利用urlopen获取页面代码
            response = urllib2.urlopen(request)
            # 将页面转化为UTF-8编码
            pageData = response.read().decode('utf-8')
        except BaseException, e:
            logger.error(">>请求地址:%s 连接失败", url)
            if hasattr(e, "reason"):
                logger.error(">>失败原因:", e.reason)
            return None
        return pageData

    def post(self, url):
        pass

    def save(self, lps):
        sql = "INSERT INTO loupan (`area`, `city`, `county`, `name`, `price`, `around_price`, `unit`, `href`, `start_time`, `deliver_time`, `create_time`) VALUES"
        for lp in lps:
            if lp.price == "":
                lp.price = "NULL"
            if lp.around_price == "":
                lp.around_price = "NULL"
            sql += "('" + lp.area + "','" + lp.city + "','" + lp.county + "','" + lp.name + "'," + lp.price + "," + lp.around_price + ",'" + lp.unit + "','" + lp.href + "','" + lp.start_time + "','" + lp.deliver_time + "',now()),"
        sql = sql[:-1]

        db = dbutil()
        # 保存数据
        db.save(sql)

    def dealAreaNode(self, node):
        # 清除当前已经爬取过的数据，防止重爬
        db = dbutil()
        currentDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        delsql = "DELETE FROM loupan WHERE DATE_FORMAT(create_time, '%Y-%m-%d')=" + "'" + currentDate + "'"
        db.delete(delsql)
        # 获取当前区县下的所有楼盘连接列表
        lp_hrefs = self.getCounty(node)
        for lp_href in lp_hrefs:
            logger.info(">>解析当前区域楼盘信息:%s %s %s %s", lp_href[0], lp_href[1], lp_href[2],  lp_href[3])
            lps = self.getLouPan(lp_href, 1)
            # if lps.__len__() == 0:
            #     continue
            # for loupan1 in lps:
            #     print loupan1.area, loupan1.city, loupan1.county, loupan1.name, loupan1.price, loupan1.around_price, loupan1.unit, loupan1.href

    def start(self):
        # nodes = []
        # node = AreaNode("中西部", "重庆", "https://cq.fang.anjuke.com")
        # nodes.append(node)

        self.getAreas("https://cq.fang.anjuke.com/?from=navigation")
        nodes = self.areaNodes
        start_time = time.time()
        pool = threadpool.ThreadPool(1)
        requests = threadpool.makeRequests(self.dealAreaNode, nodes)
        [pool.putRequest(req) for req in requests]
        pool.wait()
        logger.info(">>当前爬取任务执行完成,使用时间:%s second", (time.time() - start_time))
        # print 'get lp info spend %d second' % (time.time() - start_time)
        # 重启定时任务---增加一天
        nextSched = datetime.now() + timedelta(days=1)
        self.scheduler(nextSched)

    def scheduler(self, currentTime):
        schedTime = currentTime.replace(hour=17, minute=40, second=0, microsecond=0)
        logger.info(">>当前时间:%s 定时任务执行时间:%s", currentTime, schedTime)
        deltaTime = schedTime - datetime.now()
        sleeptime = deltaTime.total_seconds()
        sleep(sleeptime)
        logger.info(">>爬取任务开始执行...")
        self.start()

if __name__ == "__main__":
    ajk = Anjuke()
    ajk.scheduler(datetime.now())

