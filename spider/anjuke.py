# -*- coding:utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import re
import threadpool
import time
from area import AreaNode
from lp import LouPan


class Anjuke(object):

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
            # request = urllib2.Request(start_url, headers = self.headers)
            # # 利用urlopen获取页面代码
            # response = urllib2.urlopen(request)
            # # 将页面转化为UTF-8编码
            # pageData = response.read().decode('utf-8')
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
    def getCounty(self, area_url):
        # 保存当前楼盘列表地址
        lp_href = []
        try:
            # 获取区县数据
            pageData = self.get(area_url)
            if pageData is None:
                return lp_href
            bs = BeautifulSoup(pageData)

            div = bs.select('div[class="item-area"] div[class="filter"]')
            if div.__len__() > 0:
                _as = div.pop(0).select("a")
                for a in _as:
                    tup = (a.string, a.get("href"))
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
        pageData = self.get(lp[1])
        if pageData is None:
            return lps
        bs = BeautifulSoup(pageData)
        divs = bs.select('div[class="key-list"] > div[class="item-mod"]')

        # 处理每个楼盘信息
        for div in divs:
            loupan = LouPan('', '', '', '', '', '', '', '', '', '') #创建楼盘信息对象
            data_link = div.get("data-link")
            lp_data = self.get(data_link)

            if lp_data is None:
                continue
            loupan.county = lp[0]
            loupan.href = data_link

            lp_bs = BeautifulSoup(lp_data)
            title = lp_bs.select_one('div[class="lp-tit"] > h1')
            loupan.name = title.string

            container = lp_bs.select_one('div[id="container"]')
            # container = lp_bs.select_one('div[id="container"] div[class="basic-parms-wrap"]')
            p_price = container.select_one('dd[class="price"] p')
            price = p_price.select_one("em")
            if price is not None:
                loupan.price = price.string
                pattern = re.compile('</em>.*?\n', re.S)
                unit = re.findall(pattern, str(p_price))
                if unit.__len__() > 0:
                    if unit[0].__contains__("万"):
                        loupan.unit = "万/套"
                    elif unit[0].__contains__("元"):
                        loupan.unit = "元/平"

            around_price = container.select_one('dd[class="around-price"] span')
            if around_price is not None:
                loupan.around_price = around_price.string

            # 获取开盘时间和交房时间
            # times = container.select('p')
            times = container.select('p.info-new span')
            if times.__len__() > 0:
                loupan.start_time = times[0].string
                if times.__len__() > 1:
                    loupan.deliver_time = times[1].string
            lps.append(loupan)
        # 递归调用,处理后面页码
        if page <= 1:
            page += 1
            lps.extend(self.getLouPan(lp, page))
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
            print "地址:", url, ",连接失败;"
            if hasattr(e, "reason"):
                print "错误原因:", e.reason
            return None
        return pageData

    def post(self, url):
        pass

    def dealAreaNode(self, node):
        # 获取当前区县下的所有楼盘连接列表
        lp_hrefs = self.getCounty(node.getHref())
        # if lp_hrefs.__len__() == 0:
        #     return
        for lp_href in lp_hrefs:
            lps = self.getLouPan(lp_href, 1)
            if lps.__len__() == 0:
                continue
            node.lps = lps
            for loupan1 in node.lps:
                print node.area, node.city, loupan1.county, loupan1.name, loupan1.price, loupan1.around_price, loupan1.unit, loupan1.href

    def start(self):
        self.getAreas("https://cq.fang.anjuke.com/?from=navigation")
        nodes = self.areaNodes
        start_time = time.time()
        pool = threadpool.ThreadPool(1)
        requests = threadpool.makeRequests(self.dealAreaNode, nodes)
        [pool.putRequest(req) for req in requests]
        pool.wait()
        print 'get lp info spend %d second' % (time.time() - start_time)
        # count = 0
        # for node in self.areaNodes:
        #     lp_hrefs = self.getCounty(node.getHref())
        #     if lp_hrefs.__len__() == 0:
        #         continue
        #     for lp_href in lp_hrefs:
        #         lps = self.getLouPan(lp_href, 1)
        #         if lps.__len__() == 0:
        #             continue
        #         node.lps = lps
        #         for loupan1 in node.lps:
        #             print node.area, node.city, loupan1.county, loupan1.name, loupan1.price, loupan1.around_price, loupan1.unit, loupan1.href
        #             count += 1
        # print count

ajk = Anjuke()
ajk.start()

