#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sqlite3
import pandas as pd

''' Some Starting Point Scripts for creating a SQL DB based on the 
    Abstracts Data parsed into a DataFrame'''

DEFAULTDB = 'Abstracts_aug14.db'
DEFAULTHDF = '../Abstracts_Gorton/DFstore_aug1.h5'

def getPatentDataFrame(hdffile = DEFAULTHDF, 
                       key = 'df'):
    '''Parse a h5 file into readble rows for a Abstracts Table.
       : param hdffile : str. directory location of the h5 file
               default : '../DataBaseParsing/DFstore.h5'
       : param key : str. h5 key for the DF with data.
               default : 'df'
               
       : output : Pandas Dataframe! 
    '''
    
    totalDF = pd.read_hdf(hdffile, key)
    print(totalDF.shape)
        
    return totalDF
    

def sqlCMDToPD(table, 
               db = DEFAULTDB):
    '''Take a sql db and return as a readable pandas DataFrame
       : param db : str. Name of db. (ie. 'Abstracts.db'
       : param sqlcmd : str. Sqlite3 cmd to execute. 
               default: "SELECT * FROM Abstracts" 
                           > select all from Abstracts table
    '''
    
    #connect to a db
    with sqlite3.connect(db) as con:
        
        #run command
        sqlcmd = "SELECT * FROM '%s'" %table
        df = pd.read_sql_query(sqlcmd, con)
        
        # Check resulting pandas DF shape
        print df.shape
        
        return df



def createTOTALTable(db = DEFAULTDB,
                     table = 'ABSTRACTSTOTAL',
                     data_frame = getPatentDataFrame()):
    '''Add entries to the given db
        
       : param db : str. Name of db. (ie. 'Abstracts.db'
       : param table : str. Name of Table to create or insert.
       : param data_frame : Pandas DataFrame. Insert into given table by row.
       
       
       : output : Pandas DataFrame for inspection, 
       : output : sql table created with rows inserted.
      
    '''
  
    with sqlite3.connect(db) as con:
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table +
                    "(\
                    Abstract TEXT, \
                    'Author affiliation' TEXT, \
                    Authors TEXT, \
                    Conf TEXT, \
                    Title TEXT, \
                    terms TEXT,\
                    year INT\
                    )");

        data_frame.to_sql(table, con, flavor='sqlite', 
                       schema=None, if_exists='append', 
                       index=False, index_label=None,
                       chunksize=None, dtype=None)
        print("Records %s created successfully" %table);
        
        sql = "SELECT * FROM " + table
        df = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
        return df  

def createConfTable(data_frame,
                    db = DEFAULTDB, 
                    DFCol = 'Conf',
                    table = 'CONFERENCES',
                    tableCol = ['confName']
                  ):
    
    ''' Creating the CONFERENCES Table with AutoIncremented PRIMARY Key as ConfID
         : param data_frame : Pandas DataFrame from which to create the CONFERENCE TABLE
         : param db : str. Name of db. (ie. 'Abstracts.db')
             : default 'test.db'
         : param DFCol : string Column name of data_frame with information.
             : default = 'Conf'
             : alternatively : enter with already unique table.
         : param table : str. Name of Table to create or insert.
             : default : CONFERENCES
         : param tableCol : tuple of str. Table keyword as a tuple of string
         
         : output : Pandas DataFrame as output for inspection
         : output : sql table created with rows inserted.
         '''
    
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
        confID INTEGER PRIMARY KEY AUTOINCREMENT, \
        confName TEXT NOT NULL)") 
    
        dfConf = pd.DataFrame(data_frame[DFCol].unique(), columns = tableCol)
    
        dfConf.to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records %s created successfully"%table);
        
    sql = "SELECT * FROM " + table
    df = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
    return df  
        
def createPublicationsTable(data_frame, 
                            db = DEFAULTDB,
                            DFCol = ('Conf', 'year'),
                            table = 'PUBLICATIONS',
                            tableCol = ['confName', 'year'],
                            foreignKey = 'CONFERENCES'):
    ''' Creating the PUBLICATIONS Table with AutoIncremented PRIMARY Key as pubID
             : param data_frame : Pandas DataFrame from which to create the PUBLICATIONS TABLE
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = 'Conf'
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : PUBLICATIONS
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('confName', 'year')
             : param foreignKey : str . Name of Foreign key table as str
         
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
    '''
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db);
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        print ('table dropped')
    
        
        #create the table
        cur.execute("CREATE TABLE " + table + 
                    "(pubID INTEGER PRIMARY KEY AUTOINCREMENT, \
                    year INT, \
                    confName TEXT NOT NULL, \
                    FOREIGN KEY(confName) REFERENCES '%s'(confID))" % foreignKey); 
        
        print('Created %s table' %table);
        data = list(data_frame.groupby(DFCol).count().index.get_values())
        dfPubs = pd.DataFrame(data, columns = tableCol)
        
        #insert into the table
        dfPubs.to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records %s created successfully"%table);
        
    sql = "SELECT * FROM " + table
    dfPubs = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
    return dfPubs           

    

    
def createKEYSTable(data_frame, 
                    db = DEFAULTDB, 
                    DFCol = 'terms',
                    table = 'KEYS' ,
                    tableCol = ['keyword']
                   ):
    ''' Creating the KEYS Table with 
        keyID as AUTOINCREMENTED PRIMARY KEY, 
             : param data_frame : Pandas DataFrame from which to create the KEYS TABLE
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = 'terms'
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : KEYS
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('keyword')
             
             :***NEED TO CREATE COMPOSITE***
         
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
         '''
    
    def findTermSet(data_frame, DFCol = DFCol):
        ''' Parse the TOTALABSTRACTS table dataframe terms column.
        Create a single set of all terms
        
        : param tableDF : a Pandas DataFrame (ie TOTALABSTRACTS table as DF)
        : param keyword : column name to be recast and set of terms found from
        
        : output : a master set of terms set as a list (no duplicates)
        '''
    
        #recast - since made a string during the entry into the sqlite db.
        terms = data_frame[DFCol].apply(lambda x: set([ e.strip(' \'') for e in x.strip('[]\'').split(',')]))
    
        #create a single set
        termset = list(frozenset().union(*terms))
        return pd.DataFrame(termset, columns = tableCol)
    
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
        keyID INTEGER PRIMARY KEY AUTOINCREMENT, \
        keyword TEXT NOT NULL)") 
        
        keyDF1 = findTermSet(data_frame)
        
        
        #insert into the table
        keyDF1.to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records %s created successfully"%table);
        
    sql = "SELECT * FROM " + table
    dfKeys = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
    return dfKeys  

def createAUTHORSTable(data_frame, 
                    db = DEFAULTDB, 
                    DFCol = 'Authors',
                    table = 'AUTHORS' ,
                    tableCol = ['authorName']
                   ):
    ''' Creating the AUTHORS Table with 
            authorID as AUTOINCREMENTED PRIMARY KEY, 
             : param data_frame : Pandas DataFrame from which to create the AUTHORS TABLE
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = 'Authors'
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : AUTHORS
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('authorName')
             : **NEED TO CREATE COMPOSITE **
         
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
         '''
    
    def findAuthorsSet(data_frame, DFCol = DFCol):
        ''' Parse the TOTALABSTRACTS table dataframe terms column.
        Create a single set of all terms
        
        : param data_frame : a Pandas DataFrame (ie TOTALABSTRACTS table as DF)
        : param DFCol : column name to be recast and set of terms found from
        
        : output : a master set of terms set as a list (no duplicates)
        '''
        import re
        commaQuote = re.compile('[\',]')
        
    
        #recast - since made a string during the entry into the sqlite db.
        authors = data_frame[DFCol].apply(lambda a: a.strip("[]'"))
        authors = authors.apply(lambda x: filter(lambda a: a != '',
                                                  commaQuote.sub(' ', x).split('   ')))
        
        
        #create single set and remove leading white space
        authors = list(frozenset().union(*authors))
        authors = [anew.strip(' ') for anew in authors]
        #need to reset becuase of the white space
        return list(set(authors))
    
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the Authors table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
        authorID INTEGER PRIMARY KEY AUTOINCREMENT, \
        authorName TEXT \
        )") 
        authors = findAuthorsSet(data_frame)
        print ('Author set created')
        
        #only take 1 -> becuase first is empty
        authorsDF = pd.DataFrame(authors[1:], columns = tableCol)
        
        #insert into the table
        authorsDF.to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records %s created successfully"%table);
        
    sql = "SELECT * FROM " + table
    dfAuthors = pd.read_sql_query(sql, con)
        
    #return table as Pandas DataFrame for inspection
    return dfAuthors


def createAFFILIATIONTable(data_frame, 
                    db = DEFAULTDB, 
                    DFCol = 'Author affiliation',
                    table = 'AFFILIATIONS' ,
                    tableCol = ['affiliation']
                   ):
    ''' Creating the AFFILIATIONS Table with 
        keyID as AUTOINCREMENTED PRIMARY KEY, 
             : param data_frame : Pandas DataFrame from which to create the AFFILIATIONS TABLE
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = 'Author affiliation'
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : AFFILATIONS
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('affiliation')
             
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
         '''
    
    def findAffiliationSet(data_frame, DFCol = DFCol):
        ''' Parse the TOTALABSTRACTS table dataframe terms column.
        Create a single set of all terms
        
        : param tableDF : a Pandas DataFrame (ie TOTALABSTRACTS table as DF)
        : param keyword : column name to be recast and set of terms found from
        
        : output : a master set of terms set as a list (no duplicates)
        '''
        #recast - since made a string during the entry into the sqlite db.
        affiliation = data_frame[DFCol]
    
        #create unique using .unique()
        
        return pd.DataFrame(affiliation.unique(), columns = tableCol)
    
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
        affilID INTEGER PRIMARY KEY AUTOINCREMENT, \
        affiliation TEXT NOT NULL)") 
        
        affilDF = findAffiliationSet(data_frame)
        
        #insert into the table
        affilDF.to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records %s created successfully"%table);
        
    sql = "SELECT * FROM " + table
    dfAffil = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
    return dfAffil


def createPAPERTable(data_frame,
                         db = DEFAULTDB, 
                         DFCol = ['Abstract','Title','terms','Authors',
                                  'Author affiliation','year','Conf'],
                         table = 'PAPER',
                         tableCol = ['abstract','title','terms',
                                     'authors', 'affiliation','pubYear','confName'],
                         foreignKey = ['PUBLICATIONS','CONFERENCES']):
    ''' Creating the PAPER Table with AutoIncremented PRIMARY Key as paperID
             : param data_frame : Pandas DataFrame from which to create the PUBLICATIONS TABLE
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = ['Abstract','Title','terms','year','Conf']
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : PAPER
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ['abstract','title','terms','pubYear','confName']
             : param foreignKey : str . Name of Foreign key table as str
                 : ['PUBLICATIONS','CONFERENCES']
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
    '''
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db);
        cur = con.cursor() 
        #drops the Abstracts table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        print ('table dropped')
        #create the table
        cur.execute("CREATE TABLE " + table +"(\
                    paperID INTEGER PRIMARY KEY AUTOINCREMENT, \
                    abstract TEXT, \
                    title TEXT, \
                    terms TEXT,\
                    authors TEXT,\
                    affiliation TEXT,\
                    pubYear INT,\
                    confName TEXT,\
                    FOREIGN KEY(pubYear) REFERENCES '%s'(pubID), \
                    FOREIGN KEY(confName) REFERENCES '%s'(confID))" % (foreignKey[0], foreignKey[1])
                    ); ##authors ids?
        
        
        data = list(data_frame.groupby(DFCol).count().index.get_values())
        dfPaper = pd.DataFrame(data, columns = tableCol)
        
        #insert into the table
        dfPaper.to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records %s created successfully"%table);
        
    sql = "SELECT * FROM " + table
    dfpaperkey = pd.read_sql_query(sql, con)
        
        #return table as Pandas DataFrame for inspection
    return dfpaperkey 

def createAFFILIATIONPAPERTable(data_frameP, data_frameA, 
                                joinON = 'affiliation', 
                                db = DEFAULTDB, 
                                table = 'AFFILIATIONPAPER' ,
                                tableCol = ['paperID', 'affilID'],
                                foreignKey = ['PAPER', 'AFFILIATION']
                               ):
    ''' Creating the AUTHORS Table with 
            authorID as AUTOINCREMENTED PRIMARY KEY, 
             : param data_frame : Pandas DataFrame from which to create the AUTHORS TABLE
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = 'Authors'
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : AUTHORS
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('authoName')
             : **NEED TO CREATE COMPOSITE **
         
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
         '''
    
    with sqlite3.connect(db) as con:
        #create dataframe
        mergedPaperAffiliation = data_frameP.merge(data_frameA, on = joinON)
        
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the PaperAffilation table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
        paperID INT, \
        affilID INT, \
        FOREIGN KEY(paperID) REFERENCES '%s'(paperID), \
        FOREIGN KEY(affilID) REFERENCES '%s'(affilID))" % (foreignKey[0], foreignKey[1])
                    );
        
        #insert into the table
        mergedPaperAffiliation[tableCol].to_sql(table, con, flavor='sqlite', 
                    schema=None, if_exists='append', 
                    index=False, index_label=None,
                    chunksize=None, dtype=None)
        print("Records %s created successfully"%table);
        
    sql = "SELECT * FROM " + table
    paperAffiliationDF = pd.read_sql_query(sql, con)
        
    #return table as Pandas DataFrame for inspection
    return paperAffiliationDF

def createPAPERKEYTable(data_frame, 
                    db = DEFAULTDB, 
                    DFCol = ['paperID','terms'],
                    table = 'PAPERKEY' ,
                    tableCol = ['paperID', 'keyword'],
                    foreignKey = ['PAPER', 'KEYS']
                   ):
    ''' Creating the PAPERKEY COMPOSITE Table with 
    
             : param data_frame : Pandas DataFrame from which to create the PAPER TABLE 
                 : - parsed paper table!
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = [paperID','terms']
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : 'PAPERKEY'
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('paperID', 'keyword')
             : param foreignKey : tuple of str. Foreign key names:
                 : default : 'PAPER', 'KEYS'
         
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
         '''
    parsedPaper = data_frame[DFCol]
    parsedPaper['NEWTERMS'] = parsedPaper[DFCol[-1]].apply(lambda x: 
                                                           list(set([e.strip(' \'') 
                                                                     for e in x.strip('[]\'').split(',')]))  
                                                          )
    
    termsnew = parsedPaper['NEWTERMS'].apply(lambda x: 
                                             pd.Series(str(x).split(',')))
    
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the Authors table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
            paperID INT,\
            keyword TEXT,\
            FOREIGN KEY(paperID) REFERENCES '%s'(paperID),\
            FOREIGN KEY(keyword) REFERENCES '%s'(keyword))" % 
                    (foreignKey[0],foreignKey[1]))
    
        for entry in zip(parsedPaper[DFCol[0]], termsnew.as_matrix()):
            
            paperID = entry[0]
            terms = entry[1]
            
            for term in terms:
                term = str(term).strip('[]')
                if term == None:
                    pass
                elif term == 'nan':
                    pass
                else:
                    cur.execute("INSERT INTO " + table  + " VALUES(?,?)",(paperID, term))
        
        print("Records %s created successfully"%table);
        
    sql = "SELECT * FROM " + table
    paperKeys = pd.read_sql_query(sql, con)
        
    paperKeys['keyword'] = paperKeys['keyword'].apply(lambda word: eval(word))
    
    return paperKeys

def createPAPERAUTHORTable(data_frame, 
                    db = DEFAULTDB, 
                    DFCol = ['paperID','authors'],
                    table = 'PAPERAUTHOR' ,
                    tableCol = ['paperID', 'author'],
                    foreignKey = ['PAPER', 'AUTHORS']
                   ):
    ''' Creating the PAPERAUTHOR COMPOSITE Table with 
    
             : param data_frame : Pandas DataFrame from which to create the PAPER TABLE 
                 : - parsed paper table!
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = [paperID','terms']
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : 'PAPERAUTHOR'
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('paperID', 'authorName')
             : param foreignKey : tuple of str. Foreign key names:
                 : default : 'PAPER', 'AUTHORS'
         
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
         '''
    
    import re
    commaQuote = re.compile('[\'],')
    
    parsedPaper = data_frame[DFCol]
    parsedPaper['NEWAUTHORS'] = parsedPaper[DFCol[-1]].apply(lambda a: a.strip("[]'"))
    parsedPaper['NEWAUTHORS'] = parsedPaper['NEWAUTHORS'].apply(lambda x: filter(lambda a: a != '', 
                                                               commaQuote.sub(' ', x).split('   ')))
    
    authors = parsedPaper['NEWAUTHORS'].apply(lambda x: pd.Series(str(x).split('  ')))
    
    #return authors
    with sqlite3.connect(db) as con:
        print ("Opened %s database successfully" %db); 
        cur = con.cursor() 
        #drops the Authors table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
            paperID INT,\
            authorName TEXT,\
            FOREIGN KEY(paperID) REFERENCES '%s'(paperID),\
            FOREIGN KEY(authorName) REFERENCES '%s'(authorID))" % 
                    (foreignKey[0],foreignKey[1]))
    
        for entry in zip(parsedPaper[DFCol[0]], authors.as_matrix()):
            
            paperID = entry[0]
            authors = entry[1]
            
            for author in authors:
                author = str(author).strip('\"\'[u""]')
                if author == None or author == 'nan':
                    pass
                elif len(author) <= 2:
                    pass
                elif '"' in  author:
                    pass
                elif "'" in author:
                    pass
                else:
                    cur.execute("INSERT INTO " + table  + " VALUES(?,?)",(paperID, author))
        
        print("Records %s created successfully"%table);
        
    sql = "SELECT * FROM " + table
    paperAuthors = pd.read_sql_query(sql, con)
        
    #return table as Pandas DataFrame for inspection
    return paperAuthors 

import numpy as np
def createPAPERAUTHORdf(db = DEFAULTDB):
    ''' Creating the PAPERAUTHOR COMPOSITE Table with 
    
             : param data_frame : Pandas DataFrame from which to create the PAPER TABLE 
                 : - parsed paper table!
             : param db : str. Name of db. (ie. 'Abstracts.db')
                 : default 'test.db'
             : param DFCol : tuple of strings Column names of data_frame with groupby cols.
                 : default = [paperID','terms']
                 : alternatively : enter with already unique table.
             : param table : str. Name of Table to create or insert.
                 : default : 'PAPERAUTHOR'
             : param tableCols : tuple of str. Table keywords as tuple of strings
                 : default  : ('paperID', 'authorName')
             : param foreignKey : tuple of str. Foreign key names:
                 : default : 'PAPER', 'AUTHORS'
         
             : output : Pandas DataFrame as output for inspection
             : output : sql table created with rows inserted.
         '''
    def rech(names):
        names2 = []
        for a in names.split("'"):
            if a.strip() == "," :
                pass
            elif a.strip() == '':
                pass
            else:
                names2.append(a)
        return names2
    
    def createdf(df):
        entries = []
        
        for each in df.index:
            paperID = df.iloc[each].paperID
            authors = df.iloc[each].NEWAUTHORS
            index = np.array([paperID]*len(authors))
            listau = zip(index, authors)
    
            entries.extend(listau)
    
        newdf = pd.DataFrame(entries)
        newdf.rename(columns = {0:'paperID', 1:'authorName'}, inplace = True)
        newdf.authorName = newdf.authorName.apply(lambda au: au.replace(",",' '))
    
        return newdf
    
    with sqlite3.connect(db) as con:
        sqlcmd = "SELECT * FROM AUTHORS"
        
        audf = pd.read_sql_query(sqlcmd, con)
        
        sqlcmd2 = "SELECT paperID, authors FROM PAPER"
        papdf = pd.read_sql_query(sqlcmd2, con)
        
        
        
        papdf['NEWAUTHORS'] = papdf["authors"].apply(lambda a: a.strip("[]'"))
        papdf['NEWAUTHORS'] = papdf["NEWAUTHORS"].apply(lambda a: rech(a))
        
        data_frame = createdf(papdf)
        
        return data_frame
    
def createPAPERAUTHORTable2( db = DEFAULTDB, table = "PAPERAUTHOR"):
    with sqlite3.connect(db) as con:
        #create dataframe
        df = createPAPERAUTHORdf()
        
        print df.head()
        cur = con.cursor() 
        #drops the PaperAffilation table if it exist in db already
        cur.execute("DROP TABLE IF EXISTS " + table)
        #and recreates it
        cur.execute("CREATE TABLE " + table + "(\
            paperID INT, \
            authorName TEXT)"
                       );
        
        #insert into the table
        df.to_sql(table, con, flavor='sqlite', 
                        schema=None, if_exists='append', 
                        index=False, index_label=None,
                        chunksize=None, dtype=None)
        print("Records %s created successfully"%table);
        
        sql = "SELECT * FROM " + table
        testerDF = pd.read_sql_query(sql, con)
        
        return testerDF