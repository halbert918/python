# -*- coding:utf-8 -*-
import pymysql


class dbutil(object):

    # 读取配置文件
    def open(self):
        # conf = read()
        # self.open(conf)
        pass

    # 读取配置文件
    def open(self, conf):
        # doConnect()
        pass

    # 建立连接
    def doConnect(self, user, passwd, database, host='127.0.0.1', port=3306, charset='utf8'):
        db = pymysql.connect(host, port, user, passwd, database, charset)
        return db

    def save(self, sql):
        try:
            db = self.open()
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
        except BaseException, e:
            db.rollback()
        finally:
            db.close()

    def update(self, sql):
        pass

    def delete(self, sql):
        pass

    def query(self, sql):
        pass

