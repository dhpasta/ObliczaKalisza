import pymysql

def connect_params(self):
    return pymysql.connect(
        host='172.18.0.2',
        port=3306,
        user='user', 
        password = 'password',
        db='data',
    )
