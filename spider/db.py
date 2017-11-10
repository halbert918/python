# -*- coding:utf-8 -*-
import pymysql
import ConfigParser
import os
import logger


class dbutil(object):

    def __init__(self):
        self.conf = self.readConf()

    # 读取配置文件
    def open(self):
        return self.openConf(self.conf)

    # 读取配置文件
    def openConf(self, conf):
        dbuser = conf.get("database", "dbuser")
        dbpassword = conf.get("database", "dbpassword")
        dbname = conf.get("database", "dbname")
        dbhost = conf.get("database", "dbhost")
        dbport = conf.getint("database", "dbport")
        dbcharset = conf.get("database", "dbcharset")
        return self.doConnect(dbuser, dbpassword, dbname, dbhost, dbport, dbcharset)

    # 建立连接
    def doConnect(self, user, passwd, database, host, port, charset):
        db = pymysql.connect(host, user, passwd, database, port, charset=charset)
        return db

    def save(self, sql):
        db = self.open()
        try:
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
        except BaseException, e:
            logger.error(">>插入数据sql %s 异常,原因: %s", sql, e.reason)
            db.rollback()
        finally:
            db.close()

    def update(self, sql):
        pass

    def delete(self, sql):
        db = self.open()
        try:
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
        except BaseException, e:
            logger.error(">>删除数据sql %s 异常,原因: %s", sql, e.reason)
            db.rollback()
        finally:
            db.close()

    def query(self, sql):
        pass

    # 读取db配置文件
    def readConf(self):
        config = ConfigParser.ConfigParser()
        path = os.path.split(os.path.realpath(__file__))[0] + '/db.conf'
        config.read(path)
        return config
