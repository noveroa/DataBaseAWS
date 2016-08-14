import pandas as pd
import sqlite3


''' Attempt to play with terms data
  using set and strips to get into single instances of each terms.
  - Will need to first strip each row entry and then and send to table.
  - regex didn't work, but will try as much faster computationally
  - wondering if one should just create tables and then run a df.apply scheme?
  
'''

'''Need to get terms into lists of the keywords.  
    Assuming each entry should have the keywords/terms only once
'''
 

def findTermSet(tableDF, keyword = 'terms'):
    ''' Parse the TOTALABSTRACTS table dataframe terms column.
        Create a single set of all terms
        
        : param tableDF : a Pandas DataFrame (ie TOTALABSTRACTS table as DF)
        : param keyword : column name to be recast and set of terms found from
        
        : output : a master set of terms set as a list (no duplicates)
    '''
    
    df = tableDF
    
    #recast - since made a string during the entry into the sqlite db.
    terms = df[keyword].apply(lambda x: set([ e.strip(' \'') for e in x.strip('[]\'').split(',')]))
    
    #create a single set
    termSet = frozenset().union(*terms)
    
    #return as a list
    return list(termSet)
    
