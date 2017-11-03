# -*- coding:utf-8 -*-


class LouPan(object):

    # area 区域
    # city 城市
    # county 区县
    # name 楼盘名称
    # price 楼盘价格
    # around_price 周边价格
    # start_time 开盘时间
    # deliver_time 交房时间
    def __init__(self, area, city, county, name, unit, href, start_time, deliver_time, price='NULL', around_price='NULL'):
        self.area = area
        self.city = city
        self.county = county
        self.name = name
        self.price = price
        self.around_price = around_price
        self.unit = unit
        self.href = href
        self.start_time = start_time
        self.deliver_time = deliver_time

    def getArea(self):
        return self.area

    def setArea(self, area):
        self.area = area;

    def getCity(self):
        return self.city

    def setCity(self, city):
        self.city = city

    def getHref(self):
        return self.href
