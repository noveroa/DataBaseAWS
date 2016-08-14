#!/usr/bin/python
#-*- coding: utf-8 -*-


import sys
import re
import pandas as pd


regXstripper = re.compile('[^a-zA-Z0-9\,]')
alphaComma = re.compile('[^a-zA-Z\,]')

setLabels = ['affiliation', 'Abstract', 'terms', 'Classification']

def parseFile(input, Labels = setLabels):
    ''' Recast the abstract dictionary as a Pandas DataFrame
        : param input : .txt file from scientific abstracts 
        : param Labels : ['str']. List of only using pre-set labels to parse as strings.
                : default : ['affiliation', 'Abstract', 'terms', 'Classification Code']
                
        : output : Python Dictionary of Dictionaries
                : primary key: value ===> abstractID : Python Dictionary
                : secondary key : value ===> abstractLabel : Datum
                
    '''
    i = 1
    abstracts = {}
    entry = {}
    terms = []
    
    with open(input, 'r+') as f:
        for line in f:
            if line[0].isdigit():
                
                #Only Title Lines Begin with Digit.
                entry['terms'] = terms #cast as a string for entry to sqlite3 table
                abstracts[i-1] = entry
                entry = {}
                #Title Lines are followed by Authors
                
                idx, title = line.split('.', 1)
                entry['Title'] =  regXstripper.sub(' ', title).strip()
                i = int(idx) + 1
                authors =  f.next() 
                entry['Authors'] =  regXstripper.sub(' ', authors).strip()
                terms = []
            else:
                for c in Labels:
                    #error thrown as Compilation terms of Copyright lines being incorporated
                    if (c in line) and ('Compilation' not in line):
                        if ('terms' in line):
                            terms.append( line.split(':', 1)[1].strip())
                        else:
                            label, text = line.split(':', 1)
                            text = regXstripper.sub(' ', text)
                            label = regXstripper.sub(' ', label)
                            entry[label.strip()] = text.strip()
                    
                        
                    
                
    f.close()
    
    return abstracts


def reparseAuthors(data_frame, column = 'Authors'):
    '''TO remove the superscripts that remained as well as separate
        multiple authors
        
        : param data_frame : Pandas DataFrame. Frame that has been parsed 
                from patent txt file.  Authors needs to be further parsed
        : param column : str. String name of column to be reparsed 
                default = 'Authors'  To remove remaining superscript numbers
                            separate the authors keeping initials
        : output : original DataFrame with authors reparsed.  Each row a str
                so can read into sqliteDB
                '''
    df = data_frame
    
    
    #keep alphacharacters and comma.  Remove digits, and split on white space
    #cannot strip on ',' as lose the initials of each author
    def reformatAuthors(authors):
        
        try:
            authors =  alphaComma.sub(' ', authors).split('  ')
            try:
                authors = str(filter(lambda a: a !=' ', authors))
                return authors
            except:
                return authors
        except:
            return authors
    
    #filter out empty strings, return as a single string for sqlite3 table entry
    df[column] = df[column].apply(reformatAuthors)
    
    #df[column] = df[column].apply(lambda author : )
    
    df[column] = df[column].apply(str)
    
    return df

def reparseAffiliations(data_frame, column = 'Author affiliation'):
    '''TO remove the superscripts that remained as well as separate
        multiple authors
        
        : param data_frame : Pandas DataFrame. Frame that has been parsed 
                from patent txt file.  Authors needs to be further parsed
        : param column : str. String name of column to be reparsed 
                default = 'Authors'  To remove remaining superscript numbers
                            separate the authors keeping initials
        : output : original DataFrame with authors reparsed.  Each row a str
                so can read into sqliteDB
                '''
    df = data_frame
    
    def reformatAffiliation(a):
        try:
            a = str(a).split('1', 1)[1].strip()
            return str(a)
        except:
            return None
    
    df[column] = df[column].apply(reformatAffiliation)
    df[column] = df[column].apply(str)
    return df

def reparseTerms(data_frame, column = 'terms'):
    '''TO remove the superscripts that remained as well as separate
        multiple authors
        
        : param data_frame : Pandas DataFrame. Frame that has been parsed 
                from patent txt file.  Authors needs to be further parsed
        : param column : str. String name of column to be reparsed 
                default = 'Authors'  To remove remaining superscript numbers
                            separate the authors keeping initials
        : output : original DataFrame with authors reparsed.  Each row a str
                so can read into sqliteDB
                '''
    df = data_frame
    
    def reformatTerms(terms):
        from itertools import chain
        try:
            terms = [entry.split(' - ') for entry in terms]
            return list(chain(*terms))
        except:
            return 'ERROR' + str(terms)
        
    df[column] = df[column].apply(reformatTerms)
    
    return df

def reparseCodes(data_frame, column = 'Classification Code'):
    '''TO remove the superscripts that remained as well as separate
        multiple authors
        
        : param data_frame : Pandas DataFrame. Frame that has been parsed 
                from patent txt file.  Authors needs to be further parsed
        : param column : str. String name of column to be reparsed 
                default = 'Authors'  To remove remaining superscript numbers
                            separate the authors keeping initials
        : output : original DataFrame with authors reparsed.  Each row a str
                so can read into sqliteDB
                '''
    df = data_frame
    
    def reformatcode(classcodes):
        try:
            codes = [x.split(' ',1)[1] for x in classcodes.split('   ')]
            codes = [alphaComma.sub(' ', c).strip() for c in codes] 
            return codes
        except:
            return [classcodes]
    try:    
        df[column] = df[column].apply(reformatcode)
    
        return df
    except: 
        df[column] = [[]] * len(df)

        
        return df

def makeAbstrDF(absDictionary, fname):
    ''' Recast the abstract dictionary as a Pandas DataFrame
        : param absDictionary : Python Dictionary of Dictionaries (see documentation above). 
            key: value ==> abstract idx (int) : abstract dictionary
        : output : Pandas DataFrame
            Given dictionary recast as dataframe with first row.  DataFrame Columns are Abstract Labels
    '''
    df = pd.DataFrame.from_dict(absDictionary, orient = 'index')
   
    df = df.drop(0, axis = 0)
    
    name = (fname.split('/')[-1]).strip('.txt')
    conf, year = name[:-4], name[-4:]
    df['Conf'] = conf
    df['year'] = year
    
    #Now to reformat and parse each column appropriately
    df = reparseAuthors(df)
    df = reparseAffiliations(df)
    df = reparseTerms(df)
    df = reparseCodes(df)
    
    df['terms'] = (df['terms'] + df['Classification Code']).apply(str)
    del df['Classification Code']

    
    return df


def parseEntrytoDF(input):
    ''' Recast the abstract dictionary as a Pandas DataFrame
        : param input : .txt file from scientific abstracts 
            
        : output : Pandas DataFrame
            recast the file into a pandas DataFrame
    '''
    return makeAbstrDF(parseFile(input), input)
