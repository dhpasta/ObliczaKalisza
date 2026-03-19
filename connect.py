import pymysql

def connect_params(self):
    return pymysql.connect(
        host='db',
        port=3306,
        user='user', 
        password = 'password',
        db='data',
    )
