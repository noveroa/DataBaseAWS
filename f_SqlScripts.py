import sys, os

'''PYTHONIC SQL COMMANDS, no connection to databases'''

def sqlJoin(table1, pk1, table2, pk2):
    '''Join Two Tables ON Table1.pk1 == Table2.pk2 
    of TABLE 1 is the given entry ID
    param table1 str : Table Name of First Join
    param pk1 str : primary key column name of Table 1
    param table2 str : Table Name of Second Table to Join
    param pk2 str : primary key column name of Table 2
    '''
    
    sqlcmd = '''
    SELECT {tn1}.%s, {tn2}.%s
    FROM {tn1}
    JOIN {tn2}
    ON {tn1}.%s = {tn2}.%s
    '''.format(tn1 = table1, 
               tn2= table2)%(pk1, pk2, pk1, pk1)
    
    return sqlcmd

def sqlJoinSelect(table1, pk1, table2, pk2, entryID):  
    '''Select Rows of Two Joined Tables where by PRIMARY KEY 
    of TABLE 1 is the given entry ID
    param table1 str : Table Name of First Join
    param pk1 str : primary key column name of Table 1
    param table2 str : Table Name of Second Table to Join
    param pk2 str : primary key column name of Table 2
    param entryID int : integer value (Primary Key Value) to delete from table
    '''
    
    sqlcmd = '''
    SELECT {tn2}.%s
    FROM {tn1}
    JOIN {tn2}
    ON {tn1}.%s = {tn2}.%s
    WHERE {tn1}.%s = {myid}
    '''.format(tn1 = table1, 
               tn2= table2, 
               myid = entryID)%(pk2, pk1, pk1, pk1)
    
    return sqlcmd

def sqlSelectRowbyID(table, pk, entryID):
    '''Select the Total Row Record by PRIMARY KEY
    param table str : Table Name to delete from
    param pkcol str : primary column name being used, 
    param entryID int : integer value (Primary Key Value) to delete from table
    '''
    sqlcmd =  ''' SELECT * FROM {tn} WHERE {pkcol} = {my_id} '''.format(tn = table, 
                                                                        pkcol = pk, 
                                                                        my_id = entryID)
    return sqlcmd
