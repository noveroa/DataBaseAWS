#!/usr/bin/env python
import matplotlib # at very start!  Put it in app.py
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('agg')
from flask import Flask
import os
import sqlite3
import pandas as pd
import numpy as np
import seaborn
import matplotlib.pyplot as plt
from collections import Counter

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask import abort,  jsonify

import images as images
images = reload(images)
import wordcloud_generator2 as wcg
wcg = reload(wcg)

app = Flask(__name__)

#current Databases being accessed:
DATABASE = '/var/www/html/flaskapp/EmpData.db'
DATABASE2 = '/var/www/html/flaskapp/Abstracts_aug1.db'

DEBUG = True

def connect_db():
#    Connects to the specific database.
    rv = sqlite3.connect(DATABASE2)
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
#   Opens a new database connection if there is none yet for the
#   current application context.
    if not hasattr(g, DATABASE2):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    db = get_db()
    with app.open_resource('creatEmpUsers.py', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def getTotalPD(db):
#    : param db str : address of the data_base to query
#    : output : pandas dataframe represenaton of sql database

    with sqlite3.connect(db) as con:
        sqlcmd = "SELECT * FROM ABSTRACTSTOTAL"
        df = pd.read_sql_query(sqlcmd, con)
        print ('Database : ', df.shape)
        
    return df

def logError(start):
#   Explicitely Prints error to the errorlog. @/var/log/apache2/error.log
    assert start
    import traceback, sys, StringIO
    err = sys.stderr
    buffer = sys.stderr = StringIO.StringIO()
    traceback.print_exc()
    sys.stderr = err
    print buffer.getvalue()

@app.teardown_appcontext
def close_db(error):
#   Closes the database again at the end of the request.
    if hasattr(g, DATABASE2):
        g.sqlite_db.close()

@app.route('/countme/<input_str>')
def count_me(input_str):
    input_counter = Counter(input_str)
    response = []
    for letter, count in input_counter.most_common():
        response.append('"{}": {}'.format(letter, count))
    return '<br>'.join(response)

@app.route('/')
def index():
#    Renders aboutme page html for '/' the index page

    return render_template('index.html')

@app.route('/aboutme/')
def aboutme():
#    Renders aboutme page html for sit author
    return render_template('extras/aboutMe.html')

@app.route('/welcome/<name>/')
def welcome(name):
#    param name str : name of person surfing the site
#    Renders welcome html for person...

    return render_template('extras/welcome.html', name=name)

@app.route('/users')
def getUsers():
#    '''TODO: USERS FOR ABSTRACTS_DB'''
    with sqlite3.connect(DATABASE) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM User")
        rows = cur.fetchall();
        
        keys = rows[0].keys()

        #return df
        return render_template('extras/tables.html', 
                               title = 'users' , rows = rows, keys = keys)

def dict_factory(cursor, row):
#    
#   :output : Returns a json dictionary of rows and columns
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

#"""TOTAL TABLES""" 

@app.route("/jsonTotal/<table>", methods=('GET',))
def getjsonTotal(table):
#   param table, str Table Name
#   output : Returns a json dictionary of the given table's attributes 
    with sqlite3.connect(DATABASE2) as con:
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute("SELECT * FROM '%s'" %table)
        entries = cur.fetchall()
    
    return jsonify(dict(data=entries))

@app.route("/totals/<table>", methods = ('GET',))
def jasonhtml(table):
#   Renders getjsonTotal(table) as html
    html = 'totaltables/jsonTotal' + table + '.html'
    return render_template(html)


@app.route("/jsonContents", methods = ('GET',))
def getContents():
#   param NONE 
#   output : Returns a json dictionary of the table names, entry counts, and 
#            links to tables of all table names in the database
    with sqlite3.connect(DATABASE2) as con:
    
        cursor = con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        mytables = (cursor.fetchall())
        myt = []
        for x in mytables[1:]:
            table_entry = {}
            table_name = x[0]
            table_entry['name'] = table_name
            html = 'totals/%s' % table_name
            table_entry['html'] = "<a href='%s'<button>click</button>></a>" %html
            table_entry['count'] = cursor.execute("SELECT COUNT(*) FROM %s"%table_name).fetchone()[0]
        
            myt.append(table_entry) 
            
    return jsonify(dict(data = myt))
    

@app.route("/contents", methods = ('GET',))
def jsonContents():
#   Renders getContents() as html
    return render_template('/totaltables/jsonContents.html')

@app.route("/jsonContentsconf", methods = ('GET',))
def getContentsconf():
#   : param NONE
#   : output : Returns a json dictionary of each conference with 
#              pie and bar chart visualizations of each broken down by year  
    with sqlite3.connect(DATABASE2) as con:
        sqlcmd = "SELECT Conf, Year FROM ABSTRACTSTOTAL"
        df = pd.read_sql(sqlcmd, con)
        myt = []
    
        
        conferences = list(df['Conf'].unique())
    
   
        for conf in conferences:
        
            entry = {}
            entry['conf'] = conf
        
        
            subDF = df.query('Conf == "%s"' % conf).groupby('year').count()
            
            entry['counts'] = subDF.reset_index().to_html(classes = 'counts')
            
            image = images.getPieOne(subDF, conf)
            entry['Pie']  = image
            
            subDF.reset_index(inplace = True)
            image2 = images.getBar(subDF, 
                                    conf, 
                                    xaxis = 'year', yaxis = 'Conf', 
                                    orientation = "v",
                                    ylabel = 'Count', xlabel = 'Publication Year')
            
            entry['Bar'] = image2
        
            myt.append(entry)
    
    return jsonify(dict(data = myt))

@app.route("/contentsconf", methods = ('GET',))
def jsonContentsconf():
#   Renders getContentsconf() as html
    return render_template('/conferences/jsonContentsconf.html')


@app.route("/jsonconfyrpapers/<year>/<conf>", methods=('GET',))
def getPapersConfYr(year, conf):
#   : param year str/int : Year of a conference within range of database 2004 - 2014
#   : param conf str : Valid Conference Name (WICSA, ECSA, QoSA)
#   : output : Returns a json dictionary of paperID, title, Abstract for given conf, year
    with sqlite3.connect(DATABASE2) as con:
        sqlcmd = "SELECT pubYear, confName, paperID, title, abstract FROM PAPER"
        PAPdf = pd.read_sql(sqlcmd, con)
    
        group = PAPdf.groupby(['pubYear', 'confName'], axis = 0)
    
        try:
            subgroup =  group.get_group((int(year), conf))
        
            mytable = []
            
            for idx in subgroup.index.get_values():
                entry = {}
                entry['paperID'] = subgroup.loc[idx]['paperID']
                entry['Title'] = subgroup.loc[idx]['title']
                entry['Abstract'] = subgroup.loc[idx]['abstract']    
                mytable.append(entry)
       
            return jsonify( dict(data = mytable))
        
        except:
           
            entry = {'paperID': 'NoConference',
                     'Title': 'NoConference',
                     'Abstract': 'NoConference',
                     }
            mytable = [entry]
            return jsonify(dict(data = mytable))
        
@app.route("/confyrpapers/<year>/<conf>", methods = ('GET',))
def jsonConfYrPaper(year, conf):
#   Renders getPapersConfYr(year, conf) as html

    return render_template('/conferences/ConfYrPaper.html', entry = [year, conf])


@app.route("/jsonconfyrbreakdown", methods=('GET',))
def getPapersConfYrTable():
#    : param NONE
#    : output : Returns a json dictionary of conferences, publication years, 
#               links to each conf/yr papers, top keywords, and authors    
    with sqlite3.connect(DATABASE2) as con:
        sqlcmd = "SELECT pubYear, confName, paperID, title, abstract FROM PAPER"
        PAPdf = pd.read_sql(sqlcmd, con)
    
        group = PAPdf.groupby(['pubYear', 'confName'], axis = 0)
        entries = []
        for year, conf in group.groups.keys():
            entry = {}
            entry['conference'] = conf
            entry['year'] = year
            
            html = "confyrpapers/" + str(year) + '/' + conf
            entry['paperbreakdown'] =  "<a href='%s'<button>See Papers</button>></a>" %html
            html2 =  "confKWbreakdown/"+ conf + '/' + str(year)
            entry['kwbreakdown'] =  "<a href='%s'<button>Top 10 Keywords</button>></a>" %html2
            html3 =  "/jsonconfyrAuthorbd/"+ conf + '/' + str(year)
            entry['authors'] =  "<a href='%s'<button>Authors</button>></a>" %html3
            
            entries.append(entry)
        
        return jsonify(dict(data  = entries))


@app.route("/confbreakdown", methods = ('GET',))
def confbreakdown():
#    Renders getPapersConfYrTable as html

    return render_template('/conferences/jsonbreakdown.html')
                            
@app.route('/search/<year>/<conf>', methods=('GET',))
def search_params(year, conf):
#    : param year str/int : Year of a conference within range of database 2004 - 2014
#    : param conf str : Valid Conference Name (WICSA, ECSA, QoSA)
#    : output : Returns a json dictionary of publication year, name, paperIDs, titles

    print "publication year", year
    print "conference", conf
    
    with sqlite3.connect(DATABASE2) as con:
        sqlcmd = "SELECT pubYear, confName, paperID, title, abstract FROM PAPER"
        PAPdf = pd.read_sql(sqlcmd, con)
    
        group = PAPdf.groupby(['pubYear', 'confName'], axis = 0)
       
        try:
            subgroup =  group.get_group((int(year), conf))

            mytable = []
            
            for idx in subgroup.index.get_values():
                entry = {}
                entry['paperID'] = subgroup.loc[idx]['paperID']
                entry['Title'] = subgroup.loc[idx]['title']
                entry['Abstract'] = subgroup.loc[idx]['abstract']    
                mytable.append(entry)
       
            return jsonify( dict(data = mytable))
        except:
            print (year, conf, 'subgroupfail')
            entry = {'paperID': 'NoConference',
                     'Title': 'NoConference',
                     'Abstract': 'NoConference',
                     }
            mytable = [entry]
            return jsonify(dict(data = mytable))

@app.route('/search')
def search():
#    Renders search_params(year, conf) as html
    return render_template("/conferences/search.html")


def getPapersKWgroup(grouper):
#    : param grouper: parameters to group paper keyword merged table by (ie. [confName, pubYear])
#    : output : Returns two python Pandas DataFrames . 
#            merged: PAPER and PAPERKEY merged on paperID
#            subgroup : merged grouped by given grouper

    with sqlite3.connect(DATABASE2) as con:
        sqlcmd = "SELECT paperID, title, confName, pubYear FROM PAPER "
        
        paperdf = pd.read_sql(sqlcmd, con)
        
        sqlcmd2 = "SELECT paperID, keyword FROM PAPERKEY "
        kwdf = pd.read_sql(sqlcmd2, con)
        kwdf['keyword'] = kwdf['keyword'].apply(lambda word: eval(word))
        
        merged = kwdf.merge(paperdf, on = 'paperID')
        
        subgrp = merged.groupby(grouper)
        
        return merged, subgrp

@app.route("/jsonPaperID/<paperid>", methods = ('GET',))
def getpaperbyID(paperid):
#   : param id integer: PaperID to return 
#   : output : Returns python dataframe of the paper with
    with sqlite3.connect(DATABASE2) as con:
        sqlcmd = "SELECT paperID, title, confName, pubYear, abstract FROM PAPER WHERE paperID == %d" %int(paperid)
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute(sqlcmd)
        entries = cur.fetchall()
    return jsonify(dict(data=entries))

@app.route("/PaperID/<paperid>", methods = ('GET',))
def PaperID(paperid):
#   Renders jsonPaperID(id) as html    
    return render_template('/papers/paperbyID.html', entry = paperid)
    
@app.route("/jsonContentskeys/<conf>/<year>", methods = ('GET',))
def confYrKeywords(year, conf, top = 10):
#    : param conf str : Valid Conference Name (WICSA, ECSA, QoSA)
#    : param year str/int : Year of a conference within range of database 2004 - 2014
#    : param top int : number of keywords to return, default 10
#    : output : Returns a json dictionary of the top 10 keywords for the given conference/year. 
#               And a bie and bar graph representation
    print 'Conf: ', conf, 'Year' , year
    grouper = ['confName', 'pubYear']
    m, f = getPapersKWgroup(grouper)
    print 'Got F'
    myentries = []
    try:
        group = (conf, int(year))
        print group
        keywordcts = f.get_group(group).groupby(["keyword"])["keyword"].count()
        print keywordcts
        kwdftop = keywordcts.sort_values(ascending = False).head(top)
        
        resetKW = pd.DataFrame(kwdftop).rename(columns = {'keyword' : 'count'})
        entry = {}
        entry['Group'] = group
        entry['Counts'] = resetKW.reset_index().to_html(classes = 'counts')
        
        image = images.getPieOne(resetKW, group)
        entry['Pie'] = image
        
        resetKW.reset_index(inplace = True)
        image2 = images.getBar(resetKW, 
                                  group, 
                                  xaxis = 'count', yaxis = 'keyword',
                                  orientation = 'h',
                                  ylabel = 'keyword', xlabel = 'Count')
        entry['Bar'] = image2
        
        
        
        myentries.append(entry)
    
    
        return jsonify(dict(data = myentries)) 
    except:
        entry = {
            'Group' :  "No Conference Data",
            'Counts' :  "No Conference Data",
            'Pie' :  "No Conference Data",
            'Bar' :  "No Conference Data"
            }
        myentries.append(entry)
    
    
        return jsonify(dict(data = myentries)) 


@app.route("/confKWbreakdown/<conf>/<year>", methods = ('GET',))
def jsonConfYrKW(conf, year):
#    Renders confYrKeywords() as html

    return render_template('/keywords/jsonContentsconfyrkw.html', entry = [conf, year])

@app.route("/papers/keywords", methods = ('GET',))
def getPaperKW():
#   : param NONE
#   : output : Returns a json dictionary of paperIDs and their keywords
    m, data_frame = getPapersKWgroup('paperID')
    entries = []
    for each in data_frame.groups:
        entry = {}
        entry['paperID'] = each
        entry['keywords'] = [key for key in data_frame.get_group(each)['keyword']]
        html2 =  "PaperID/"+ str(each)
        entry['getPaper'] =  "<a href='%s'<button>Paper Information</button>></a>" %html2  
        entries.append(entry)
    return jsonify(dict(data = entries))

@app.route("/paperKWs.html", methods = ('GET',))
def jsonPaperKW():
#   Renders getPaperKW() as html
    return render_template('/keywords/paperKWs.html')

@app.route('/search_kw')
def search_kw():
#   Renders search_kw_params() as html
    return render_template("/keywords/search_kw.html")

@app.route('/search_kw/<param>', methods=('GET',))
def search_kw_params(param):
#   : param param str: keyword string to be searched for
#   : output : Returns a json dictionary of papers associated to the given keyword
    print "keyword search: ", param
    
    
    m, f = getPapersKWgroup('keyword')
    
    cts = m.groupby(["keyword"])["keyword"].count().reset_index(name="counts")
   
    ctsmerge = cts.merge(m, on = 'keyword').groupby('keyword')   
    
    try:
        
        print param
        
        subgroup = ctsmerge.get_group(param)
        
        mytable = []
            
        for idx in subgroup.index.get_values():
            print idx
            entry = {}
            entry['paperID'] = subgroup.loc[idx].paperID
            entry['Title'] = subgroup.loc[idx]['title']
            entry['Conference'] = subgroup.loc[idx]['confName']   
            entry['PublicationYear'] = subgroup.loc[idx]['pubYear'] 
            mytable.append(entry)
       
        return jsonify(dict(data = mytable))
    except:
        print (param, 'subgroupfail')
        entry = {'paperID': 'No Keyword Found',
                     'Title': 'No Keyword Found',
                     'Conference': 'No Keyword Found',
                     'PublicationYear': 'No Keyword Found'
                     }
        mytable = [entry]
        return jsonify(dict(data = mytable))

@app.route('/seeKWTrend/<kw>', methods=('GET',))
def seeKWTrend(kw, grouper = 'keyword'):
#    : param param str: keyword string to be searched for
#    : output : Returns a json dicitonary of a table with the given keyword's associated 
#                papers, counts per conference and year,
##                and a heatmap representation
    print('My keyword: ' , kw)
    m, f = getPapersKWgroup(grouper)
    
    query2 = '"%s" == keyword' %kw
    
    data_frame = m.copy()
    ##could use this if want approx equality
    #data_frame = m[m['keyword'].str.contains(kw)==True]
    data_frame.query(query2, inplace = True)
    new = data_frame.copy()
    
    def findKWTrend(df, kw, KWgrouper = ["pubYear", "confName"]):
        try:
            df = df.groupby(KWgrouper)['keyword'].count().reset_index(name="counts")
            
            images.getHeatMap2(df, annotation = True,
                               filename = os.path.join(app.static_folder,'Images/test.png')
                              )
            html = "/kwHeattrend"
            return df, html
        except:
            logError(True)
            return render_template('extras/error.html')
        
    
    df, html = findKWTrend(new, kw)
    
    myentry = [{'table' : new.to_html(classes = 'counts'),
               'cts' : df.to_html(classes = 'counts'),
               'url' : "<a href='%s'<button>SeeHeatMap</button>></a>" %html  
               }]
    
    return jsonify(dict(data = myentry))   

@app.route('/kwHeattrend', methods=('GET',))
def seeKWTrendheat():
#    Renders seeKWTrend() as html
    
    return render_template('keywords/kwHeattrend.html')

@app.route('/seeKWTrends', methods=('GET',))
def seeKWTrends():
#    Renders seeKWTrend() as html
    
    return render_template('keywords/jsonKWTrends2.html')

@app.route('/seeKWTop', methods=('GET',))
def seeKWTop(top = 20):
#    : param top int: number of top keywords to return, default 20
#    : output : Returns a json dicitonary of the frequency of the top 
#                keywords over all years and a heatmap
    m, f = getPapersKWgroup('keyword')
    
    topWds = f.count().sort_values(by = 'confName', ascending = False)[:top]
    
    mTop = m[m['keyword'].isin(topWds.index)]
    
    mTop['counts'] = mTop.groupby(['confName', 'pubYear', 'keyword'])['keyword'].transform('count')
 
    try:
        image = images.getHeatMap2(mTop, indexCol='keyword', cols = ['confName', 'pubYear'],
                                   vals = 'counts',
                                   filename = os.path.join(app.static_folder,'Images/topheat.png')
                                   )
        
    
        html = "/topheat"
        topWds.reset_index(inplace = True)
        topWds.rename(columns = {'confName' : 'OverallCount'}, inplace = True)
        cts = topWds[['keyword', 'OverallCount']]
        
        return jsonify(dict(data = 
                            [{'Top' : cts.to_html(classes = 'counts'),
                              'HeatMap' : "<a href='%s'<button>SeeHeatMap</button>></a>" %html}])
                      )
    except:
        logError(True)
        return render_template('extras/error.html')
        

@app.route('/topKW', methods=('GET',))
def topKW():
#    Renders seeKWTop() as html
    return render_template('keywords/topKW.html')

@app.route('/topheat', methods=('GET',))
def topheat():
#    Renders getBasicAffiliationCount() as html
    
    return render_template('keywords/topheat.html')

@app.route('/KWcloud', methods=('GET',))
def KWcloud():
#   Renders KWs word cloud in html - creates and SAVES a newimage eachtime
    try:
        wordCloud =  wcg.cloud('kw',
                               outputFile = os.path.join(app.static_folder,"Images/kwCloud.png"))
        return render_template('keywords/wordcloudrender.html')
    except:
        logError(True)
        return render_template('extras/error.html')

def getAffiliation():
    
    with sqlite3.connect(DATABASE2) as con:
        sqlcmd = "SELECT paperID, affiliation, confName, pubYear FROM PAPER "
        
        paperdf = pd.read_sql(sqlcmd, con)
        
        
        return paperdf
@app.route('/searchAffiliation/<term>', methods=('GET',))
def searchAffiliation(term):
#    : param term: term by which to search Affiliations (ie country, number, abbreviation)
#    : output : json dictionary of paperID, affilation, and link to the PaperID Info 
   
    with sqlite3.connect(DATABASE2) as con:
        sqlcmd = "SELECT paperID, affiliation, confName, pubYear FROM PAPER "
        
        paperdf = pd.read_sql(sqlcmd, con)
        
        datadf = paperdf[paperdf['affiliation'].str.contains(term or term.lower())==True]
        
        mytable = []
        for idx in datadf.index.get_values():
            entry = {}
            entry['paperID'] = datadf.loc[idx]['paperID']
            entry['affiliation'] = datadf.loc[idx]['affiliation']
            html2 = "PaperID/"+ str(datadf.loc[idx]['paperID'])
            entry['getPaper'] =  "<a href='%s'<button>Paper Information</button>></a>" %html2  
            
            mytable.append(entry)
        
        return jsonify(dict(data = mytable))

@app.route('/seeAffil', methods=('GET',))
def seeAffil():
#    Renders searchAffiliation(term) as html
    return render_template('papers/seeAffil.html')

def getBasicAffiliationCount():
#    : param NONE:
#    : output : Dictionary of the found countries and their counts, barchart too
    from pycountry import countries 
    with sqlite3.connect(DATABASE2) as con:
        sqlcmd = "SELECT affiliation FROM PAPER "
        
        affildf = pd.read_sql(sqlcmd, con)
        countries = [country.name for country in countries]
        
        counts = {}
        for c in countries:
            count = len(affildf[affildf['affiliation'].str.contains(c or c.lower())==True])
            if count > 0:
                counts[c] = count
        try:
            
            image = images.getaffilbar(xaxis = counts.keys(),
                                       yaxis = counts.values(),
                                       filename = os.path.join(app.static_folder, "Images/countryaffiliation.png")
                                       )
        
    
        
            return counts, image
        except:
            logError(True)
            return render_template('extras/error.html')
        
@app.route('/seeCountries', methods=('GET',))
def seeCountries():
#    Renders getBasicAffiliationCount() as html
    seeCountries, image = getBasicAffiliationCount()
    
    return render_template('papers/seeCountries.html')

@app.route('/getCountryCounts', methods=('GET',))
def getCountryCounts():
#    : param : NONE
#    : output : json dictionary of the affiliation count and country 
#        (dictionary output of  getBasicAffiliationCount())
    cts, img = getBasicAffiliationCount()
    datadic=[]
    for i, (k, v) in enumerate(cts.iteritems()):
        datadic.append({'country' : k, 'count' : v})
    
    return jsonify(dict(data = datadic))

@app.route('/countryCts', methods=('GET',))
def seeCountryCounts():
#    Renders  getCountryCounts() as html
    return render_template('papers/seeCountryCounts.html')

def countryGr():
#    : param : NONE
#    : output : pandas DataFrame count and country grouped by Conferences

    from pycountry import countries 
    with sqlite3.connect(DATABASE2) as con:
        sqlcmd = "SELECT affiliation, confName FROM PAPER"
        
        affildf = pd.read_sql(sqlcmd, con)
        
        gr = affildf.groupby('confName')
        countries = [country.name for country in countries]
        grouped = {}
        for group in gr.groups.keys():
            temp = gr.get_group(group)
            counted = {}
            for c in countries:
                count = len(temp[temp['affiliation'].str.contains(c)==True])
                if count > 0 :
                    counted[c] = count
            grouped[group] = counted
        
        return pd.DataFrame.from_dict(grouped)
    
@app.route('/seeCountriesGR', methods=('GET',))
def seeCountriesGR():
#   Renders countryGr() as a Bubble Chart and as html
    try:
        image = images.createSpot(countryGr(), 
                                  filename = os.path.join(app.static_folder, "Images/testCtsGroup.png")
                                  )
    
        return render_template('papers/seeCountriesGR.html')
    
    except:
        logError(True)
        return render_template('extras/error.html')
    
@app.route('/seeCountriesAreaPlot', methods=('GET',))
def seeCountriesAreaPlot():
#    Renders countryGr() as an AreaPlot and as html
    try: 
        image = images.areaPlot(countryGr(),
                                xlabel = 'Countries',
                                ylabel = 'Counts',
                                filename = os.path.join(app.static_folder,'Images/countryAP.png')
                                )
    
        return render_template('papers/seeCountriesAreaPlot.html')
    except:
        logError(True)
        return render_template('extras/error.html')

def getAuthorsTotal():
    with sqlite3.connect(DATABASE2) as con:
        sqlcmd = "SELECT authorName FROM PAPERAUTHOR "
        
        return pd.read_sql_query(sqlcmd, con)
    
    
def AuthoredPapersDF(boolean):
#    : param boolean: control flow boolean
#    : output : Returns a python Pandas DataFrane of total database of paperIDs merged to authors 
    if boolean == 'start':
    
        with sqlite3.connect(DATABASE2) as con:
            sqlcmd = "SELECT * FROM PAPERAUTHOR"
        
            papaudf = pd.read_sql(sqlcmd, con)
        
            sqlcmd2 = "SELECT paperID,title,confName, pubYear FROM PAPER"
        
            pap  = pd.read_sql(sqlcmd2, con)
        
            merged = papaudf.merge(pap, on =  'paperID')
            merged['counts'] = merged.groupby(['authorName'])['authorName'].transform('count')
        
            return merged.sort_values(by = ['counts','authorName'], ascending = False)
            
            

@app.route('/AuthoredPapers', methods=('GET',))
def AuthoredPapers():
#    : param NONE:
#    : output : Returns a json dictionary of Authors and their associated papers by conference and year.
#               The count is the total number of papers the author has been ascribed over the entirety of the database 
    ap = AuthoredPapersDF('start')
    entries = []
    for row in ap.as_matrix():
        entry = {key: value for (key, value) in zip(ap.columns, row)}
        entries.append(entry)
        
    return jsonify(dict(data = entries))

@app.route('/authors/authoredpapers', methods=('GET',))
def authoredpapers():
#    Renders AuthoredPapers() as html
    return render_template('authors/authoredpapers.html')
    

@app.route('/getauthorsbyID/<paperID>', methods=('GET',))
def getauthorsbyID(paperID):
#    '''
#        : param paperID int: integer corresponding to the paperID
#        : output : Given a valid paperID returns a json dictionary of authors ascribed to the given paper, 
#                   Though redundant, paper title, conference, year is also returned.
#                   The count is the total number of papers the author has been ascribed over the entirety of the database
    print paperID
    ap = AuthoredPapersDF('start')
    query = 'paperID == %d' %int(paperID)
    
    ap = ap.query(query)
    entries = []
    
    for row in ap.as_matrix():
        entry = {key: value for (key, value) in zip(ap.columns, row)}
        entries.append(entry)
    return jsonify(dict(data = entries))

@app.route('/authors/seeAuthorsID', methods=('GET',))
def seeAuthorsID():
#    Renders getAuthors() as html
    return render_template('authors/seeAuthorsID.html')

@app.route('/getauthorsbyname/<name>', methods=('GET',))
def getauthorsbyname(name):
#        : param name str: string corresponding to an authors name. SPACE SENSITIVE
#        : output : Given a valid author name returns a json dictionary of papers ascribed to the author, 
#                    the conference, title, and year.
    print name
    ap = AuthoredPapersDF('start')
    
    #for author with name containing the name, thus only have to enter the last name.
    ap = ap[ap['authorName'].str.contains(name)==True]
    entries = []
    
    for row in ap.as_matrix():
        entry = {key: value for (key, value) in zip(ap.columns, row)}
        entries.append(entry)
    return jsonify(dict(data = entries))

@app.route('/authors/seeAuthorsName', methods=('GET',))
def seeAuthorsName():
#    Renders getauthorsbyname() as html
    return render_template('authors/seeAuthorsName.html')

@app.route('/confyrAuthor', methods=('GET',))
def confYrAuthor():
#        : param NONE
#        : output : Returns a json dictionary containing Papers,Authors merged grouped by Conference and Year. 
#        Used for inspection
    grouper = ['confName', 'pubYear']
    f = AuthoredPapersDF('start')
    grouper = ['confName', 'pubYear']
    testgroup = f.groupby(grouper)
    
    myentries = []
    for group in testgroup.groups.keys():
        authorcts = testgroup.get_group((group)).groupby(["authorName"])["authorName"].count()
        
        resetAU = pd.DataFrame(authorcts).rename(columns = {'authorName' : 'IndivCt'})
        resetAU.reset_index(inplace = True)
        
        mer = pd.merge(resetAU, testgroup.get_group((group)))
            
        entry = {}
        entry['Group'] = group
        entry['AuthoredPapers'] = mer.to_html()
        
        
        myentries.append(entry)
    
    return jsonify(dict(data = myentries))

@app.route('/authors/seeAuthorsCY', methods=('GET',))
def seeAuthorsCY():
#    Renders confYrAuthor() as html
    return render_template('authors/seeAuthorsCY.html')

@app.route('/confyrAuthor_bd/<conf>/<year>', methods=('GET',))
def confYrAuthor2(conf, year):
#        : param conf str : Valid Conference Name (WICSA, ECSA, QoSA)
#        : param year str/int : Year of a conference within range of database 2004 - 2014
#        : output : Returns a json dictionary containing Authors, paperIds, titles of papers published in given conf/year
#                    AuuthorYrCount is the total number of papers ascribd to a given author in the given conf/year
    grouper = ['confName', 'pubYear']
    f = AuthoredPapersDF('start')
    grouper = ['confName', 'pubYear']
    group = f.groupby(grouper)
    
    try:
        print (conf, year)
        subgroup =  group.get_group((conf, int(year)))
                                  
        print ('subgroupmade')
        cts = subgroup.groupby(["authorName"])["authorName"].count()
        
            
        resetAU = pd.DataFrame(cts).rename(columns = {'authorName' : 'IndivCt'})
        resetAU.reset_index(inplace = True)
        
        merged = pd.merge(resetAU, subgroup)

        mytable = []
        for idx in merged.index.get_values():
            entry = {}
            entry['Author'] = merged.loc[idx]['authorName']
            entry['paperID'] = merged.loc[idx]['paperID']
            entry['Title'] = merged.loc[idx]['title']
            entry['AuthorYrCount'] = merged.loc[idx]['IndivCt']    
            
            mytable.append(entry)
        
        return jsonify(dict(data = mytable))
    
    except:
        print('Conference Year error')
        mytable = {entry['Author'] : 'No Conference Data',
                   entry['paperID'] : 'No Conference Data',
                   entry['Title'] : 'No Conference Data',
                   entry['AuthorYrCount'] : 'No Conference Data'
                   }
        return jsonify(dict(data = mytable))

@app.route("/jsonconfyrAuthorbd/<conf>/<year>", methods = ('GET',))
def jsonconfyrAuthorbd(conf, year):
#    Renders confYrAuthor2() as html
    
    return render_template('authors/seeAuthorsCYbd.html', entry = [conf, year]) 

def getAuthorTop20(top = 20, column = 'authorName'):
#        : param top Int : Number representing the top group to be calculated
#                default: 20
#        : param column str : Name of the column being queried
#        : output : Returns a python Pandas DataFrame containing top authors and their counts 
#                 : Returns an list of the authors representing the top submitters.
    with sqlite3.connect(DATABASE2) as con:
        
        sqlcmd = "SELECT * FROM PAPERAUTHOR"
        papaudf = pd.read_sql_query(sqlcmd, con)
        
        sqlcmd2 = "SELECT paperID, confName FROM PAPER"
        pap  = pd.read_sql_query(sqlcmd2, con)
        
        merged = papaudf.merge(pap, on =  'paperID')
        merged['counts'] = merged.groupby([column])[column].transform('count')
        
        ap = merged.sort_values(by = ['counts',column], ascending = False).drop_duplicates(column)[:20]
        
        temp = merged.groupby('confName')
        selection = np.array(ap[column])
        
        return temp, selection
    
def getGrCts(data_frame, selection, column):
#        : param data_frame Pandas DataFrame : 
#        : param selection array : Array of values to be queried, filtered from dataframe
#        : output : Returns a python Pandas DataFrame containing selection and counts     
    grouped = {}
    for group in data_frame.groups.keys():
        temp = data_frame.get_group(group)
        counted = {}
        for au in selection:
            count = len(temp[temp[column].str.contains(au)==True])
            if count > 0 :
                counted[au] = count
            grouped[group] = counted
    return pd.DataFrame.from_dict(grouped)

@app.route('/auCloud', methods=('GET',))
def auCloud():
#   Renders Authors word cloud in html - creates and SAVES a newimage eachtime
    try:
        wordCloud =  wcg.cloud('au', 
                               outputFile = os.path.join(app.static_folder,
                                                         "Images/auCloud.png"))
        return render_template('authors/wordcloudrenderer_au.html')
    except:
        logError(True)
        return render_template('extras/error.html')

@app.route('/seeAuthorsSpot', methods=('GET',))
def seeAuthorsSpot():
#   Renders countryGr() as an Bubble and as html
    topauthors, selection = getAuthorTop20(top = 20)
    groupedAu = getGrCts(topauthors, selection, column = 'authorName')
    try:
        image = images.createSpot(groupedAu, xlabel = 'Author', 
                                  filename = os.path.join(app.static_folder, 'Images/authorBubble.png')
                                  )
        return render_template('authors/seeAuthorsSpot.html')
    except:
        logError(True)
        return render_template('extras/error.html')
          

@app.route('/seeAuthorsArea', methods=('GET',))
def seeAuthorsArea():
#    Renders countryGr() as an AreaPlot and as html
    topauthors, selection = getAuthorTop20(top = 20)
    groupedAu = getGrCts(topauthors, selection, column = 'authorName')
    try:
        image = images.areaPlot(groupedAu, xlabel = 'Authors', ylabel = 'counts', 
                            filename = os.path.join(app.static_folder, 'Images/authorAP.png')
                            )
        return render_template('authors/seeAuthorsArea.html')
    except:
        print logError(True)
        return render_template('extras/error.html')

if __name__ == '__main__':
   
    app.debug=True
    app.run(debug = True)
