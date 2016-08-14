#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys
import pandas as pd
from pandas import HDFStore
import parseFiles as parser
''' initializeDBstore.py:

    Creates from command line a hdf5 file of the following key:values.
    sys.argv[1] = list of the files to run through parser.parseEntrytoDF.
    
    'files' : Pandas Series of list of successfully parsed files
    'errors' : Pandas Series of list of failed parsed files
    'dfs' : Concatenated Pandas Dataframe of successfully parsed dataframes from files
'''


def printFileName(filename):
    print filename
    return filename

def createHDF(filenames, errors, dfs):
    '''Create the hdf5 storage file.
        : param filenames: [str]. List of filenames successfully 
                    parsed as Pandas DataFrames
        : param errors : [str]. List of filenames that threw errors 
                    when parsing as Pandas DataFrames
        : param dfs : [PandasDataFrames]. List of the Pandas DataFrames 
                    successfully parsed to be concatenated
    '''
    
    s = pd.Series.from_array(filenames)
    e = pd.Series.from_array(errors)
    totalDF = pd.concat(dfs, axis = 0)
    
    store = HDFStore('DFstore_aug1.h5')
    
    
    store['files'] = s
    store['errors'] = e
    store['df'] = totalDF
    
    store.close()
    
def main():
    '''Run the program iteratively:
        for each file in list of sys.argv[:1]
        '''
    #create lists to capture successful files, dataframes, and errors 
    files = []
    dfs = []
    errants = []
    args = sys.argv[1:]
 
    for filename in args:
        #print files read in to the output.txt
        f = printFileName(filename)
        
        try: 
            #try parsing the file into a Pandas DataFrame
            nextdf = parser.parseEntrytoDF(f)
            
            
            dfs.append(nextdf)
            files.append(f)
            
            
        except:
            #capture errantfiles
            errants.append(f)
   
    #store in HDF5 file store
    createHDF(files, errants, dfs)
    
    
    print 'Entered successfully: ' , len(dfs), len(files)
  
    print 'Found error: ' , len(errants)
    
    

if __name__ == '__main__':
    main()


#From the console, start :
#python intialiazeDBstore.py cwd/*.txt > *.txt
