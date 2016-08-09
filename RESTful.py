#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sqlite3 as sql
import pandas as pd

DEFAULTDB = 'Abstracts_aug1.db'
#DEFAULTJSON = "json4.json"

def jsonDF(jsonFile):
    '''Create a pandas dataframe from a Json File
    '''
    f = open(jsonFile, "r+")
    return pd.read_json(f, orient='index')

def sqlCMDToPD(table, 
               db = DEFAULTDB):
    '''Take a sql db and return as a readable pandas DataFrame
       : param db : str. Name of db. (ie. 'Abstracts.db'
       : param sqlcmd : str. Sqlite3 cmd to execute. 
               default: "SELECT * FROM Abstracts" 
                           > select all from Abstracts table
    '''
    
    #connect to a db
    with sql.connect(db) as con:
        
        #run command
        sqlcmd = "SELECT * FROM '%s'" %table
        df = pd.read_sql_query(sqlcmd, con)
        
        # Check resulting pandas DF shape
        print df.shape
        
        return df

def getContents():
    '''
    : param NONE
    : output : Returns a json dictionary of the table names, entry counts, and links to tables 
                of all table names in the database
    ''' 
    with sql.connect(mydb) as con:
    
        cursor = con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        mytables = (cursor.fetchall())
        myt = [t[0] for t in mytables]
        
        return myt
    
def insert_toTable(db, df, table = 'ABSTRACTSTOTAL'):
    '''Check to insert a new record into a database table, inserts if does not exist
    param  db str : Database name to connect to
    param df pandas dataframe : dataframe being inspected for entry
    param table str : Table Name to insert into, if does not exist will create
    output : new entry inserted
    '''
    with sql.connect(db) as con:
        df.to_sql(table, con, flavor='sqlite', 
                      schema=None, if_exists='append',
                      index=False, index_label=None,
                      chunksize=None, dtype=None)
            
        print("Records %s inserted"%table)
    
def insertcheckRecord(db, df, table = 'CONFERENCES', un = 'confName' ):
    '''Check to insert a new record into a database table, inserts if does not exist
    param  db str : Database name to connect to
    param df pandas dataframe : dataframe being inspected for entry
    param table str : Table Name to insert into, if does not exist will create
    param un str : unique column to check for entry to create a new pk, if not will just append
    '''
    t = sqlCMDToPD(table, mydb)
    if df[un][0] not in t[un].unique():
        insert_toTable(db, df[un], table)
    else:
        print(" %s already exists, try upserting with key value or deleting" %df[un][0])

    
def insertcheckRecordTWO(db, df, table = 'PUBLICATIONS', un = 'confName', un1 = 'year' ):
    '''Check to insert a new record into a database table, inserts if does not exist, checks for multiple
    entries as unique
    param  db str : Database name to connect to
    param df pandas dataframe : dataframe being inspected for entry
    param table str : Table Name to insert into, if does not exist will create
    param un str : unique column to check for entry to create a new pk, if not will just append
    param un1 str : unique column2 to check for entry to create a new pk, if fail un, if not will just append
    '''
    t = sqlCMDToPD(table, mydb)
    if df[un][0] not in t[un].unique():
        print df[un][0], 'is new'
        insert_toTable(db, df[[un, un1]], table)
    else:
        conf = df[un][0]
        tmp = t.query('@conf == confName') 
        
        if df[un1][0] not in tmp[un1].unique():
            print (df[[un, un1]].values), 'is a new entry'
            insert_toTable(db, df[[un, un1]], table)
        else:
            print(" %s already exists, try upserting with key value or deleting" %df[[un, un1]].values)


def insertValues(db, table, value1, value2):
    '''Insert a new record by value into a database table
    param  db str : Database name to connect to
    param table str : Table Name to insert into, if does not exist will create
    param value str : unique value entered into table
    '''
    with sql.connect(db) as con:
        try:
            con.execute("INSERT INTO {tn} VALUES('%s','%s')".format(tn=table)%(value1, value2))
            print('%s %s inserted into %s')%(value1, value2, table)
        except:
            con.execute("INSERT INTO {tn} VALUES(Null,'%s')".format(tn=table)%(value2))
            print('%s inserted into %s, single entry')%(value2, table)

        
def enterValueCheck_nested(db, table, values, cn):
    '''Check to insert a new record into a database table, inserts if does not exist
    param  db str : Database name to connect to
    param table str : Table Name to insert into, if does not exist will create
    param values python series : series being parsed and formated to inspection and entry into table
    param cn str : column name to check for entry to create a new pk
    '''
    keys = []
    tableDF = sqlCMDToPD(table, db)
    for i, ky in enumerate(values):
        for key in ky.split(','):
            if key not in tableDF[cn].unique():
                print key, 'is new'
                insertValues(db, table, None, key)
            else:
                print key, 'already exists in table'
            
            keys.append(key)
        return keys

def compositeCreation(db, table1, col, values, parentID, comptable):
    '''Creating Composite Tables 
    First, find the values needed to insert from first table based on query
    then insert each (parentID, value) pair into the composite table 
    param  db str : Database name to connect to
    param table1 str : Table Name to query for multiple values
    param col str : column name of value to retrieve iteratively 
    param values list : list of values to insert into the composite
    param parentID int : integer value (Primary Key Value) of parent table to enter
    param comptable str : Table Name of composite table
    '''
    t = sqlCMDToPD(table1, db)
    tmp = t.query('{cn} in @values'.format(cn = col))[col]
    for v in tmp.values:
        print v, paperK
        insertValues(db, comptable, parentID, v)
        
def getPK(db, table, pkCol):
    '''retrieve the PRIMARY KEY
    param  db str : Database name to connect to
    param table str : Table Name to delete from
    param pkcol str : primary column name being used, 
    '''
    with sql.connect(db) as c:
        cursor = c.cursor()
        cursor.execute("SELECT {idf} FROM {tn} ORDER BY {idf} DESC LIMIT 1".format(tn=table, idf=pkCol))
        key = cursor.fetchone()[0]

        return key
    
def deleteRowPK(db, table, pkcol, entryID):
    '''Deleting a Record by PRIMARY KEY
    param  db str : Database name to connect to
    param table str : Table Name to delete from
    param pkcol str : primary column name being used, 
    param entryID int : integer value (Primary Key Value) to delete from table
    '''
    with sql.connect(db) as con:
        
        con.execute("DELETE FROM {tn} WHERE {idf}={my_id}".format(tn=table, idf=pkcol, my_id=entryID))

        con.commit()

def deleteRowOTHER(db, table, cn, entry):
    '''Deleting a Record
    param  db str : Database name to connect to
    param table str : Table Name to delete from
    param cn str : column name being used for deletion comparason (if no PK column, ie, abstracts Total)
    param entry str : the str to be used to find and remove records (removes all records
    '''
    with sql.connect(db) as con:
        
        con.execute("DELETE FROM {tn} WHERE {idf}='%s'".format(tn=table, idf=cn)%entry)

        con.commit()
        
def entryintotables(db, jsonfile):
    '''Inserting a Record from a JsonFile
    param  db str : Database name to connect to
    param jsonfile str : name of Json File to be read into the database
    '''
    f = open(jsonfile, "r+")
    jdf = pd.read_json(f, orient='index')
    #TOTALABSTRACTS, check and then insert if needed, uniqueness based on Abstract column
    insert_toTable(db, jdf, table = 'ABSTRACTSTOTAL')
    


    #renaming of columns
    jdf.rename(columns = {'Conf':'confName'}, inplace= True)
    jdf.rename(columns = {'Author affiliation' : 'affiliation'}, inplace = True)
    jdf.rename(columns = {'Authors' : 'authors'}, inplace = True)
    
    #CONFERENCES, check and then insert if needed, uniqueness based on Abstract column
    insertcheckRecord(db, jdf, table = 'CONFERENCES', un = 'confName' )
    
    #PUBLICATIONS, check and then insert if needed, uniqueness based on Abstract column
    insertcheckRecordTWO(db, jdf, table = 'PUBLICATIONS', un = 'confName', un1 = 'year' )
    
    #AFFILIATIONS
    insertcheckRecord(db = db, df = jdf, table = 'AFFILIATIONS', un = 'affiliation')
    
    #For the nested: authors, keywords, and need to reparse/reformat, also to show numerous ways to insert:
    #KEYS
    keys = enterValueCheck_nested(db=db, table = 'KEYS', values = jdf.terms, cn = 'keyword')
    
    #AUTHORS
    authors = enterValueCheck_nested(db=db, table = 'AUTHORS', values = jdf.authors, cn = 'authorName')
    
    #PAPER
    jdf.rename(columns = {'year' : 'pubYear'}, inplace = True)
    insert_toTable(mydb, jdf, 'PAPER')
    paperID  = getPK(db, 'PAPER', 'paperID') 
    
    #COMPOSITE TABLE UPDATES
    #PAPERKEY
    compositeCreation(db, 'KEYS', 'keyword', keys, paperID, 'PAPERKEY')
    
    #PAPERAUTHOR
    compositeCreation(db, 'AUTHORS', 'authorName', authors, paperID, 'PAPERAUTHOR')
    
    #AFFILIATIONPAPER
    affilationID = getPK(db, 'AFFILIATIONS', 'affilID' )
    insertValues(mydb, "AFFILIATIONPAPER", paperID, affilationID)
    
    
    return jdf, keys, authors

def retrievals(db, table_name, column_2, column_3, id_column, some_id ):
    entries = []
    with sql.connect(db) as con:
        c =  cursor = con.cursor()
        # 1) Contents of all columns for row that match a certain value in 1 column
        c.execute('SELECT * FROM {tn} WHERE {cn}="ECSA"'.\
                  format(tn=table_name, cn=column_2))
        all_rows = c.fetchall()
        entries.append(('1):', all_rows))

    # 2) Value of a particular column for rows that match a certain value in column_1
        c.execute('SELECT ({coi}) FROM {tn} WHERE {cn}="ECSA"'.\
                  format(coi=column_2, tn=table_name, cn=column_2))
        all_rows = c.fetchall()
        entries.append(('2):', all_rows))

    # 3) Value of 2 particular columns for rows that match a certain value in 1 column
        c.execute('SELECT {coi1},{coi2} FROM {tn} WHERE {coi1}="ECSA"'.\
                  format(coi1=column_2, coi2=column_3, tn=table_name, cn=column_2))
        all_rows = c.fetchall()
        entries.append(('3):', all_rows))

    # 4) Selecting only up to 10 rows that match a certain value in 1 column
        c.execute('SELECT * FROM {tn} WHERE {cn}="ECSA" LIMIT 10'.\
                  format(tn=table_name, cn=column_2))
        ten_rows = c.fetchall()
        entries.append(('4):', ten_rows))

    # 5) Check if a certain ID exists and print its column contents
        c.execute("SELECT * FROM {tn} WHERE {idf}={my_id}".\
                  format(tn=table_name, cn=column_2, idf=id_column, my_id=some_id))
        id_exists = c.fetchone()
        if id_exists:
            entries.append(('5): {}'.format(id_exists)))
        else:
            entries.append(('5): {} does not exist'.format(some_id)))
        
        return entries