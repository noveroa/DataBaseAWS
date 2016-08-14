import sys
import sqlite3 as sql
import pandas as pd

sql_FK = """
SELECT sql
  FROM (
        SELECT sql sql, type type, tbl_name tbl_name, name name
          FROM sqlite_master
         UNION ALL
        SELECT sql, type, tbl_name, name
          FROM sqlite_temp_master
       )
WHERE type != 'meta'
   AND sql NOTNULL
   AND name NOT LIKE 'sqlite_%'
 ORDER BY substr(type, 2, 1), name"""

def getTablesFK(cmd = sql_FK, db):
    '''
    : param cmd str: sql command to execute
    : param db str : Database name to connect to
    : output : Returns a pandas dataframe of the schema structure, with foreign keys
    ''' 
    with sql.connect(db) as con:
    
        df = pd.read_sql_query(cmd, con)
        df_splitter = lambda x: pd.Series([i for i in x.split(',')])
        df = df['sql'].apply(foo)
        return df
        

def deleteRowPK(db, table1, pkcol, entryID, table2):
    '''Deleting a Record by PRIMARY KEY
    param  db str : Database name to connect to
    param table str : Table Name to delete from
    param pkcol str : primary column name being used, 
    param entryID int : integer value (Primary Key Value) to delete from table
    param table2 str : Table Name to delete from
    '''
    with sql.connect(db) as con:
        con.execute("PRAGMA foreign_keys = ON")
        con.execute("DELETE FROM {tn} WHERE {idf}={my_id}".format(tn=tab1e1, idf=pkcol, my_id=entryID))

        con.commit()

        df1  = con.execute("select * from {b}".format(b = table2)).fetchall()
        df2 =  con.execute("select * from {tn}".format(tn = table1)).fetchall()
    
    return df1, df2

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