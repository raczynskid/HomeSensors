#!/usr/bin/env python3

import sqlite3
# db_file = 'home/Kiermasz/projects/station/enviro.db'
def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn
    
def create_record(conn, record):
    sql = ''' INSERT INTO weather(temperature,humidity,pressure,recordDate)
				VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, record)
    conn.commit()
    return cur.lastrowid
