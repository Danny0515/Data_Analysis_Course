import pymysql


# Get MySQL connect information
def get_mysql_config():
    with open('./config/mysql.txt', 'r', encoding='utf-8') as f:
        host, user, pwd, db = f.read().split(',')
    return host, user, pwd, db

def conn_mysql(host='10.2.16.174', user='userName', pwd='userPwd', db='test'):
    conn = pymysql.connect(
        host=host, port=3306,
        user=user, passwd=pwd,
        db=db
    )
    cursor = conn.cursor()
    return conn, cursor

def close_conn_mysql(conn, cursor):
    conn.commit()
    cursor.close()
    conn.close()


