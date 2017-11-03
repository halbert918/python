# -*- coding:utf-8 -*-
class AreaNode(object):

    def __init__(self, area, city, href):
        self.area = area
        self.city = city
        self.href = href

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

    def setHref(self, href):
        self.href = href
