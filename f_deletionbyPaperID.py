import sys
import sqlite3 as sql
import pandas as pd
import f_RESTful as r
import f_SqlScripts as sqlCMDS

''' Delete by PaperID : removes instances of the given paperID from the composite tables, paper table and
the TOTALABSTRACTS table.  Not removed from the others as they are not unqiue to given paper'''

DEFAULTDB = 'scripts/Abstracts_aug14.db'

def selectPaperID(db, paperID):
    '''
    param  db str : Database name to connect to
    param paperID int : integer value (Primary Key Value) to delete from tables
    ''' 
    with sql.connect(db) as con:
        c = con.cursor()
        c.execute("SELECT abstract, confName, pubYear FROM PAPER WHERE paperID = {my_id} ".format(my_id = paperID)) 
        x = c.fetchone()
        return x
    
def mergeCountOne(db, entryID, table1, pk1, table2, pk2, table3, pk3):
    '''Due to contrainst of no Full Joins in SQL and current FOREIGN KEY disfunctionality: 
    Numerous joins are performed to be able to delete from a primary table, composite keys 
    with counts less than one when a primary key from one of the composites is deleted.
    Returns a Pandas DataFrame of those keys.
    param  db str : Database name to connect to
    param entryID int : integer value (Primary Key Value) to delete from tables
    param table1 str : Table Name of First Joined in composite, noncomposite
    param pk1 str : primary key column name of Table 1
    param table2 str : Table Name of Second Table to Join - the composite table
    param pk2 str : primary key column name of Table 2
    param table3 str : Table Name of Second Table's primary Table, non composite
    param pk3 str : primary key column name of Table 2
    '''

    with sql.connect(db) as con:
        
        sqlcmd1 = sqlCMDS.sqlJoin(table1 = table1, pk1 = pk1, 
                                  table2 = table2, pk2 = pk2)
        sqlcmd2 = sqlCMDS.sqlJoinSelect(table1 = table1, pk1 = pk1, 
                                        table2 = table2, pk2 = pk2,  
                                        entryID = entryID)
        
        #get all papers and their keywords
        df= pd.read_sql(sqlcmd1, con)
        #get all keywords in my paper
        df2 = pd.read_sql(sqlcmd2, con)
        if table2 == 'AFFILIATIONPAPER':
            vals = df2[pk2].values[0]
            print vals
            #get the keyword IDs given the keywords
            sqlcmd3 =  sqlCMDS.sqlSelectRowbyID(table = table3, pk = pk2, entryID = vals)
            df3 = pd.read_sql(sqlcmd3, con)
        else:
            assert table2 == 'PAPERKEY'
            vals = tuple(eval(d).encode('utf-8') for d in df2[pk2])
            #get the keyword IDs given the keywords
            sqlcmd3 =  ''' SELECT * FROM {tn3} WHERE %s IN %s '''.format(tn3 = table3)%(pk2, vals)
            
            df[pk2] = df[pk2].apply(lambda k : eval(k))
            df3 = pd.read_sql(sqlcmd3, con)
        
        
        #merge the all papers and keywords with only keywords in paper. If count < = 1, remove from KEYS table
        c = pd.merge(df, df3)
        c = pd.DataFrame(c.groupby([pk2,
                                   pk3]).size()
                        ).reset_index().rename(columns = {0:'Count'}).query('Count <= 1')
        
        return c


def deletefromAFFILIATIONS(entryID, pkcol, db, mpkcol = 'affilID'):
    '''Due to contrainst of no Full Joins in SQL and current FOREIGN KEY disfunctionality: 
    Numerous joins are performed to be able to delete from a primary table, composite keys 
    with counts less than one when a primary key from one of the composites is deleted.
    Deletes entries from the composite table and primary AFFILIATIONS Table
    param entryID int : integer value (Primary Key Value) to delete from tables
    param pkcol str : primary key column name of the entryID's primary column
    param  db str : Database name to connect to
    param mpkcol str : pk column name of the primary table(ie AFFILIATIONS) to delete from
    '''
    keys = mergeCountOne(db, entryID,
                         'PAPER', 'paperID', 
                         'AFFILIATIONPAPER', 'affilID', 
                         'AFFILIATIONS', 'affiliation')
    #need to delete keys from PAPERKEY based on PaperID now
    r.deleteRowPK(db, 'AFFILIATIONPAPER', pkcol, entryID)
    
    deleted = [x for x in keys[mpkcol].apply(lambda key: r.deleteRowPK(db = db, 
                                                                    table = 'AFFILIATIONS', 
                                                                    pkcol = mpkcol, 
                                                                    entryID = key
                                                                     )
                                             )]
    return deleted

def deletefromKEYS(entryID, pkcol, db, mpkcol = 'keyID'):
    '''Due to contrainst of no Full Joins in SQL and current FOREIGN KEY disfunctionality: 
    Numerous joins are performed to be able to delete from a primary table, composite keys 
    with counts less than one when a primary key from one of the composites is deleted.
    Deletes entries from the composite table and primary KEYS Table
    param entryID int : integer value (Primary Key Value) to delete from tables
    param pkcol str : primary key column name of the entryID's primary column
    param  db str : Database name to connect to
    param mpkcol str : pk column name of the primary table(ie KEYS) to delete from
    '''
    keys = mergeCountOne(db, entryID, 
                         'PAPER','paperID', 
                         'PAPERKEY', 'keyword', 
                         'KEYS', 'keyID')
    #need to delete keys from PAPERKEY based on PaperID now
    r.deleteRowPK(db, 'PAPERKEY', pkcol, entryID)
    
    deleted = [x for x in keys[mpkcol].apply(lambda key: r.deleteRowPK(db = db, 
                                                                    table = 'KEYS', 
                                                                    pkcol = mpkcol, 
                                                                    entryID = key))]
    return deleted
 
        
def deleteRowTABLE(db, paperID, table = 'ABSTRACTSTOTAL'):
    '''Deleting a Record by PRIMARY KEY
    param  db str : Database name to connect to
    param paperID int : integer value (Primary Key Value) to delete from table
    param table str : Table Name to delete from
    '''
    values = selectPaperID(db, paperID)
    print values
    with sql.connect(db) as con:
       
        con.execute("DELETE FROM {tn} WHERE Abstract = '%s' AND Conf= '%s' AND year = '%s'".format(tn=table)%(values[0],
                                                                                                              values[1],
                                                                                                              values[2]))

        df = r.sqlCMDToPD('ABSTRACTSTOTAL', db)
    
        return df

        
def deletebyPaper(pk, pkcol = 'paperID', db = DEFAULTDB):
    '''Deleting a Record from datbase by paperID
    param pk int : integer value (Primary Key Value) to delete from table
    param pkcol str : primary column name being used,
    param  db str : Database name to connect to
    '''

    print (pk)
    #delete from KEYS
    deletefromKEYS(pk, pkcol, db)
    
    #delete from Affiliations
    deletefromAFFILIATIONS(pk, pkcol, db)
    
    
    #delete from composites (within deleting from Keys)
    #r.deleteRowPK(db, 'PAPERKEY', pkcol, pk)
    #r.deleteRowPK(db, 'AFFILIATIONPAPER', pkcol, pk)
    r.deleteRowPK(db, 'PAPERAUTHOR', pkcol, pk)

    

    #delete from TOTAL ABSTRACTS
    deleteRowTABLE(db, pk)

    #delete the paper from paperTable LAST!
    r.deleteRowPK(db, 'PAPER', pkcol, pk)
    
    print 'Deletion Complete'
