import pymysql


def get_connection():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="rootpass123",
        database="library",
        cursorclass=pymysql.cursors.DictCursor,
    )
