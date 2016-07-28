import sqlite3
import pandas as pd

with sqlite3.connect("EmpData.db") as con:
    
    print("Opened database successfully")
    cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
    cur.execute("DROP TABLE IF EXISTS User")
        #and recreates it
    cur.execute("CREATE TABLE User(\
        userID INTEGER PRIMARY KEY AUTOINCREMENT, \
        Name TEXT NOT NULL,\
        Role TEXT NOT NULL,\
        Contact TEXT NOT NULL)") 
    
    cur.execute("INSERT INTO User VALUES(0,'Aileen Novero', 'Masters Student, Site Author', 'novero.a@gmail.com')")
    cur.execute("INSERT INTO User VALUES(1,'Dr. Ian Gorton', 'NEU Dept Director, Supevisor', 'i.gorton@northeastern.edu')")
    con.commit() 
    print("Table created successfully");
