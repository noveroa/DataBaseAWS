import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cStringIO import StringIO
import base64
import seaborn as sns


def getPieOne(df, conference):
    fig = plt.figure()
    fig = df.plot(kind = 'pie', 
                  colormap = 'Blues', 
                  title = '', 
                  subplots = True, 
                  legend = False, 
                  labels = ['' for x in np.arange(len(df))])
    plt.ylabel('')
    plt.legend( list(df.index), 
               bbox_to_anchor=(1.1, 1),
              fontsize = "xx-small")
    
    io = StringIO()
    plt.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
   
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())
    script = '''<img src="data:image/png;base64,{}";/>'''
    plt.close()
    return script.format(data)


def getBar(df, conference, xaxis, yaxis, orientation, ylabel = 'count', xlabel = 'trada'):
    plt.cla()
    fig = sns.barplot(data = df, 
                      y =  yaxis,#'keyword', 
                      x = xaxis, #'count', 
                      palette='Blues', 
                      orient = orientation)
    fig.set_ylabel(ylabel)
    fig.set_xlabel(xlabel)
    
    io = StringIO()
    plt.tight_layout()
    plt.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
   
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())
    script = '''<img src="data:image/png;base64,{}";/>'''
    plt.close()
    return script.format(data)


def getHeatMap(data_frame, indexCol = 'confName', cols = 'pubYear', vals = 'counts', annotation = False):
    plt.cla()
    plt.xticks(rotation=90)
    fig = sns.heatmap(data_frame.pivot_table(index=indexCol, 
                                             columns=cols, 
                                             values=vals),
                                             annot = annotation,
                                             cmap = 'Blues')
    
    
    
    io = StringIO()
    plt.tight_layout()
    plt.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
   
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())
    script = '''<img src="data:image/png;base64,{}";/>'''
    plt.close()
    return script.format(data)

def getHeatMap2(data_frame, indexCol = 'confName', cols = 'pubYear', vals = 'counts', 
                annotation = False, filename = 'static/Images/test.png'):
    plt.cla()
    plt.xticks(rotation=90)
    fig = sns.heatmap(data_frame.pivot_table(index=indexCol, 
                                             columns=cols, 
                                             values=vals),
                                             annot = annotation,
                                             cmap = 'Blues')
    
    
   
               
    plt.tight_layout()
    
    plt.savefig((filename))
    
    plt.close()
    return fig

def getLine(data_frame, xaxis = 'confName', yaxis = 'counts'):
    plt.cla()
    fig = sns.swarmplot(data = data_frame, 
                        x=xaxis, 
                        y = yaxis,
                        palette = 'Blues')
   
    io = StringIO()
    plt.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
   
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())
    script = '''<img src="data:image/png;base64,{}";/>'''
    return script.format(data)


def getaffilbar(xaxis, yaxis, filename = 'static/Images/countryaffiliation.png'):
    
    plt.cla()
    plt.figure()
    plt.xticks(rotation=90)
   
    image = sns.barplot(x = xaxis, 
                        y = yaxis,
                        palette='Blues')
    for p in image.patches:
        image.annotate(
            s='{:.0f}'.format(p.get_height()), #label
            xy=(p.get_x()+p.get_width()/2.,p.get_height()), #position
            ha='center',va='center',
            xytext=(0,10),
            textcoords='offset points'
            )
    image.set_ylabel('Count')
    image.set_xlabel("Country")
    plt.tight_layout()
    plt.savefig((filename))
    return image



def createSpot(data_frame, xlabel = 'Country', ylabel = 'Counts', filename = 'static/Images/testCtsGroup.png'):
    
    plt.cla()
    #set the labels
    plt.xticks( np.arange(len(data_frame)), data_frame.index, rotation = 90)
    plt.xlim(-.5,len(data_frame))
    plt.ylim(0, max(data_frame.max(axis = 1)) + 5)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    plt.grid(False)
    
    colors = sns.color_palette('GnBu_d')
    #plot!
    for i,column in enumerate(data_frame.columns):
        image = plt.scatter(x = data_frame.reset_index().index, 
                            y = data_frame[column], 
                            s = data_frame[column], 
                            c = colors[i])
    
    
    #format the legend
    plt.legend(list (map(str,data_frame.columns)), 
               loc = 'upper left')
               
    plt.tight_layout()
    
    plt.savefig((filename))
    
        
    return image

def areaPlot(data_frame, xlabel, ylabel, filename = 'static/Images/countryAP.png'):
    plt.cla()
    fig = plt.figure()
    fig = data_frame.plot(kind = 'area',  colormap = 'Blues', stacked = False)
    fig.patch.set_facecolor('lightgray')
    plt.xticks( np.arange(len(data_frame)), data_frame.index, rotation = 90)
    plt.xlim(0,len(data_frame))
    plt.ylim(0, max(data_frame.max(axis = 1)) + 5)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(False)
    
    plt.tight_layout()
    
    plt.savefig((filename))
    
##DRAFTS##
def getPie2():
    import matplotlib.pyplot as plt

    with sqlite3.connect(mydb) as con:
        sqlcmd = "SELECT Conf, Year FROM ABSTRACTSTOTAL"
        df = pd.read_sql_query(sqlcmd, con)
        keys = list(df['Conf'].unique())
    
        fig, axes = plt.subplots(nrows=len(keys) + 1, ncols=1,
                             sharex=False
                            )
        fig = df.groupby(['Conf'])["Conf"].count().plot(kind = 'pie', colormap = 'ocean', 
                                                subplots = True, ax = axes[0] )    
        for i, conference in enumerate(keys):
            fig = df.query('Conf == "%s"' % conference).groupby('year').count().plot(kind = 'pie', 
                                                                           ax = axes[i+1],
                                                                           colormap = 'ocean',
                                                                           subplots = True)
                                                    
                                                                          
        html = '''
        <html>
        <head>
         <h1> Conferences by year %s</h1>
        </head>
        <body> 
        
            <img src="data:image/png;base64,{}" />
        
        </body>
        </html>
        '''
        io = StringIO()
        plt.savefig(io, format='png')
        data = base64.encodestring(io.getvalue())

    return html.format(data)


def getPie(start):
    df = pd.DataFrame(start[["Conf", "year"]])
    fig = plt.figure()
    
    df.groupby(['Conf'])["Conf"].count().plot(kind = 'pie', 
                                              colormap = 'ocean', 
                                              subplots = True, 
                                              title = 'Conferences', 
                                              )
    for conference in df['Conf'].unique():
        df.query('Conf == "%s"' % conference).groupby('year').count().plot(kind = 'pie', 
                                                                           subplots = True,
                                                                           colormap = 'ocean',
                                                                           title = conference, 
                                                                          )
        plt.legend(bbox_to_anchor=(1, 1), bbox_transform=plt.gcf().transFigure)
    
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())

    return html.format(data)
    
def getBardd(df, conference):
    plt.figure()
    fig =  df.plot(kind = 'bar', 
                   colormap = 'ocean', 
                   title = conference, 
                   subplots = True,
                   legend = False)
   
    io = StringIO()
    plt.savefig(io, format='png')
    img = base64.encodestring(io.getvalue())
   
    io = StringIO()
    plt.savefig(io, format='png')
    data = base64.encodestring(io.getvalue())
    script = '''<img src="data:image/png;base64,{}";/>'''
    plt.close()
    return script.format(data)
