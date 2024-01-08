import sqlite3

conn = sqlite3.connect('userFileData.db', check_same_thread=False)
cursor = conn.cursor()

def getDB():
    return conn, cursor