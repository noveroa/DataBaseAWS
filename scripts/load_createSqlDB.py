import sys, os
import sqlite3
import pandas as pd
import sqlcommands as cmd



def main():
    #load and create total table of database: raw data as a SQL table
    df = cmd.createTOTALTable()
    
    #create tables database: 
    cmd.createConfTable(df)
    cmd.createPublicationsTable(df)
    cmd.createKEYSTable(df)
    cmd.createAUTHORSTable(df)
    
    affilDF= cmd.createAFFILIATIONTable(df)
    paperDF= cmd.createPAPERTable(df)
    
    #Composite Tables
    cmd.createPAPERKEYTable(paperDF)
    cmd.createAFFILIATIONPAPERTable(paperDF, affilDF)
    cmd.createPAPERAUTHORTable(paperDF[['paperID', 'authors']])

    return df

if __name__ == '__main__':
    
    main()