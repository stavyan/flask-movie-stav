# coding: utf8
import pymysql
from sshtunnel import SSHTunnelForwarder

with SSHTunnelForwarder(
        ('47.94.129.228', 22),  # B机器的配置
        ssh_password="root",
        ssh_username="qq617946852..",
        remote_bind_address=('127.0.0.1', 3306)) as server:  # A机器的配置

    conn = pymysql.connect(host='127.0.0.1',  # 此处必须是是127.0.0.1
                           port=3306,
                           user='root',
                           passwd='qq617946852',
                           db='test')
    print(123)
