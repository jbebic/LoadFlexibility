# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 11:51:10 2018

@author: berryi
"""
#%% Importing all the necessary Python packages
import pandas as pd # multidimensional data analysis
import numpy as np # vectorized calculations
from datetime import datetime # time stamps
from datetime import date
#from pytz import timezone
import os # operating system interface
#import string
#import random
import matplotlib.pyplot as plt # plotting 
import matplotlib.backends.backend_pdf as dpdf # pdf output
#import matplotlib.pylab as pl
from SupportFunctions import getData, findUniqueIDs, createLog, logTime

#%% Version and copyright info to record on the log file
codeName = 'GroupAnalysis.py'
codeVersion = '1.0'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Irene Berry, GE Global Research\n"

def addLoadCurveByDayEO(ax0, df, lw=1, c='b', ls='-',a=1.0):
        
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Shifted Energy [puh]')
    ax0.set_xlabel('Hour of the Day')
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    ax0.set_yticks([-1.0, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1.0])  
    ax0.set_yticklabels([-1.0, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1.0])  
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    y = np.cumsum(df['NormDmnd'])/4
    y = y - np.min(y)
#    ax0.plot(np.arange(df.shape[0]), df['NormDmnd'], ls, label='Normalized Demand [pu]', lw=lw, c=c)
    ax0.plot(np.arange(df.shape[0]), y, ls, lw=lw, c=c, alpha=a)
    
    return ax0

def addAverageDelta(ax0, df, lw=1, c='b', ls='-'):
        
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Load Delta [pu]')
    ax0.set_xlabel('Duration [h]')

    ax0.set_xlim([0,16])
    ax0.set_xticks([x for x in range(0, 28,4)]) 
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    ax0.set_yticks([-0.2, -0.15, -.1,-0.075, -0.05,-0.025 , 0,0.025, 0.05, 0.075, 0.1,0.15,  0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0])  
    ax0.set_yticklabels([-0.2, -0.15, -.1,-0.075, -0.05,-0.025 , 0,0.025, 0.05, 0.075, 0.1,0.15,  0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0])  
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
#    ax0.set_xlim([-int(df.shape[0]*16/24) ,  int(df.shape[0]*16/24) ])          
    df1 = df.sort_values('NormDmnd', ascending=False)
    charge = df1.loc[df1['NormDmnd']>0]
    discharge = df1.loc[df1['NormDmnd']<0]      
    
    ax0.plot(charge.shape[0]/4 , np.mean(charge['NormDmnd']), "o", lw=2, c=c)
    ax0.plot(discharge.shape[0]/4 , np.mean(discharge['NormDmnd']), "o", lw=2, c=c)
    
    return ax0

def addDurationCurveByDay(ax0, df, lw=1, c='b', ls='-', a=1.0):
        
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Load Delta [pu]')
    ax0.set_xlabel('Duration [h]')
    x = [x for x in range(0,int(df.shape[0])+int(df.shape[0]/(24/4)), int(df.shape[0]/(24/4)))]
#    x2 = [x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))]
    ax0.set_xticks(x)
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    ax0.set_yticks([-0.5, -0.4, -0.3, -0.2, -.1, 0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0])  
    ax0.set_yticklabels([-0.5, -0.4,-0.3, -0.2, -.1, 0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0])  
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    ax0.set_xlim([0,  int(df.shape[0]*24/24) ])          
    df1 = df.copy()
    charge = df1.loc[df1['NormDmnd']>0]
    discharge = df1.loc[df1['NormDmnd']<0]      
    charge = charge.sort_values('NormDmnd', ascending=False)
    discharge = discharge.sort_values('NormDmnd', ascending=True)
    ax0.step(np.arange(charge.shape[0]), charge['NormDmnd'] ,  ls, lw=lw, c=c, alpha=a)
    ax0.step(np.arange(discharge.shape[0]), discharge['NormDmnd'],  ls, lw=lw, c=c, alpha=a)
    
    return ax0

def addLoadCurveByDay(ax0, df, lw=1, c='b', ls='-'):
        
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Load [pu]')
    ax0.set_xlabel('Hour of the Day [h]')
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    ax0.set_yticks([-0.5, -0.4, -0.3, -0.2, -.1, 0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0])  
    ax0.set_yticklabels([-0.5, -0.4,-0.3, -0.2, -.1, 0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0])  
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
                   
    ax0.plot(np.arange(df.shape[0]), df['NormDmnd'], ls, label='Normalized Demand [pu]', lw=lw, c=c)
    ax0.plot(np.arange(df.shape[0]), np.cumsum(df['NormDmnd'])/4, ls, lw=lw*2, c='r')
    
    return ax0

def addLoadDelta(ax0, df, lw=1, c='b', ls='-'):
        
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Load [pu]')
    ax0.set_xlabel('Hour of the Day [h]')
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    ax0.set_yticks([-0.5, -0.4, -0.3, -0.2, -.1, 0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0])  
    ax0.set_yticklabels([-0.5, -0.4,-0.3, -0.2, -.1, 0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0])  
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    y = np.cumsum(df['NormDmnd'])/4
    y = y - np.min(y)
    ax0.plot(np.arange(df.shape[0]), df['NormDmnd'], ls, label='Shifted Load [pu]', lw=lw, c=c)
    ax0.plot(np.arange(df.shape[0]), y, ls, lw=lw*2, c='r', label='Shifted Energy [pu-h]')
    
    return ax0

def addLoadCurve(ax0, df, lw=1, c='b', ls='-', label=''):
        
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Load [pu]')
    ax0.set_xlabel('Hour of the Day [h]')
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    ax0.set_yticks([-0.5, -0.4, -0.3, -0.2, -.1, 0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0,1.1, 1.2, 1.3, 1.4, 1.5])  
    ax0.set_yticklabels([-0.5, -0.4, -0.3, -0.2, -.1, 0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0,1.1, 1.2, 1.3, 1.4, 1.5])  
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
                   
    ax0.plot(np.arange(df.shape[0]), df['NormDmnd'], ls,  lw=lw, c=c, label=label)
    
    return ax0

#def addLoadCurveByMonth(ax0, df, lw=1, c='b', ls='-'):
#        
#    df = df.sort_values(by='datetime', ascending=True)
#    ax0.set_ylabel('Load [pu]')
#    ax0.set_xlabel('Hour of the Day [h]')
#    ax0.set_xlim([0,df.shape[0]])
##    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
##    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
#    ax0.set_yticks([-0.5, -0.4, -0.3, -0.2, -.1, 0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0])  
#    ax0.set_yticklabels([-0.5, -0.4,-0.3, -0.2, -.1, 0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,1.0])  
#    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
#    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
#                   
#    ax0.plot(np.arange(df.shape[0]), df['NormDmnd'], ls, label='Normalized Demand [pu]', lw=lw, c=c)
#    ax0.plot(np.arange(df.shape[0]), np.cumsum(df['NormDmnd'])/4, ls, lw=lw*2, c='r')
#    
#    return ax0

def DeltaLoads(dirin='./', fnameinL='IntervalData.csv',   fnameino='groups.csv', 
                  dirout='./', fnameout='delta.csv',
                  dirlog='./', fnameLog='CompareLoads.log',
                  plotDeltas=False,
                  InputFormat='SCE',
                  dataName = 'delta'):
       
    # load time-series data 
    df1 = pd.read_csv(os.path.join(dirin,fnameinL), 
                          header = 0, 
                          usecols = [0, 1, 2], 
                          names=['CustomerID', 'datetime', 'Demand'])  

    df2 = pd.read_csv(os.path.join(dirin,fnameino), 
                          header = 0, 
                          usecols = [0, 1, 2], 
                          names=['CustomerID', 'datetime', 'Demand']) 
    
    df3 = df2.copy()
    df3['Demand'] = df1['Demand'] - df2['Demand']
    cid = np.asarray([ dataName for i in range(0,len(df3),1)])
    df3 = df3.assign(CustomerID=pd.Series(cid,index=df3.index))
    print('Writing: %s' %os.path.join(dirout,fnameout))
#    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df3.to_csv( os.path.join(dirout,fnameout), columns=['CustomerID', 'datetime', 'Demand'], float_format='%.5f', date_format='%Y-%m-%d %H:%M', index=False) # this is a multiindexed dataframe, so only the data column is written
#    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    print('Finished')
    
    return

def PlotGroup(dirin='./', fnamein='IntervalData.normalized.csv', considerCIDs='',
                  fnameGroup = "group.normalized.csv",
                 dirout='plots/', fnameout='GroupPlots.pdf', 
                 dirlog='./', fnameLog='PlotGroup.log'):

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin=dirin, fnamein=fnamein, foutLog=foutLog) #, varName='NormDmnd')

    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin=dirin, UniqueIDs=UniqueIDs, considerCIDs=considerCIDs, foutLog=foutLog)
    df1 = df1.loc[df1['CustomerID'].isin(UniqueIDs)]
    
    # load grouped data from file, find initial list of unique IDs. Update log file
    dfgroup, groupUniqueIDs, foutLog = getData(dirin=dirin, fnamein=fnameGroup,  foutLog=foutLog)#, varName='NormDmnd')
    
    # open pdf for figures
    print("Opening plot files")
    pltPdf1 = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    # iterate over UniqueIDs to create figure for each in the pdf
    customer = df1.CustomerID
    month = df1.index.month
    day = df1.index.day
    groupMonth = dfgroup.index.month
    groupDay = dfgroup.index.day
    for m in range(1, 13,1):
        days = list(set(df1.loc[(month==m)].index.day))
        print ('Processing Month %d of %d' %( m,12))
        for d in days:
                
            fig, (ax0) = plt.subplots(nrows=1, ncols=1,figsize=(8,6),sharex=True)
            fig.suptitle( fnameGroup  )    
            
            for cID in UniqueIDs: 
                relevant =  (customer==cID) & (month==m) & (day==d)
                ax0 = addLoadCurveByDay(ax0, df1.loc[relevant], lw=0.5, c='b', ls='--')
                
            relevant =  (groupMonth==m) & (groupDay==d)
            ax0 = addLoadCurveByDay(ax0, dfgroup.loc[relevant], lw=5, c='k', ls='-')
            ax0.set_title(date(2016, m,1).strftime('%B') + "/" +  str(int(d)) )   
            
            if np.abs(np.mean(dfgroup['NormDmnd'])-1.0)<=0.1:
                ax0.set_ylim([0,2.0])
            pltPdf1.savefig() 
            plt.close()   
    
    # Closing plot files
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    foutLog.write('\n\nWriting: %s' %os.path.join(dirout, fnameout))
    pltPdf1.close()

    # finish log with run time
    codeTfinish = datetime.now()
    logTime(foutLog, '\nRunFinished at: ', codeTfinish)
    
    return    

# plot duration curves - with or without monthly segments "
def PlotDelta(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='plots/', fnameout='DurationCurves.pdf', 
                 dirlog='./', fnameLog='PlotDelta.log', dailyPlot=True):

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog)
    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    if considerCIDs=='' and ignoreCIDs=='':
        pass
    else:
        UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, ignoreCIDs, considerCIDs, foutLog)
    
    # open pdf for figures
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    # iterate over UniqueIDs to create figure for each in the pdf
    i = 1
    for cID in UniqueIDs: 
        i += 1
        customer = df1.CustomerID
        month = df1.index.month
        day = df1.index.day
        for m in range(1, 13,1):
            print ('Processing Month %d of %d' %( m,12))
            days = list(set(df1.loc[(month==m)].index.day))
            
            if dailyPlot:
                for d in days:
                    fig, (ax0) = plt.subplots(nrows=1, ncols=1,figsize=(8,6),sharex=True)
                    fig.suptitle( fnamein )   
                    ax0.set_title(  date(2016, m,1).strftime('%B')  + "/" + str(int(d)))   
                    relevant =  (customer==cID) & (month==m) & (day==d)
                    ax0 = addLoadCurveByDay(ax0, df1.loc[relevant])
                    ax0.set_ylim([-0.5,1.0])
                    pltPdf1.savefig() 
                    plt.close()   
                
            else:
                fig, (ax0) = plt.subplots(nrows=1, ncols=1,figsize=(8,6),sharex=True)
                fig.suptitle(fnamein       )   
                ax0.set_title(  date(2016, m,1).strftime('%B') )  
                cmap = plt.get_cmap('jet', len(days))
                for d in days:
                    relevant =  (customer==cID) & (month==m) & (day==d)
                    ax0 = addLoadCurveByDayEO(ax0, df1.loc[relevant], c=cmap(d))
                ax0.set_ylim([-0.1,1.1])
                pltPdf1.savefig() 
                plt.close()   
    
    # Closing plot files
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    foutLog.write('\n\nWriting: %s' %os.path.join(dirout, fnameout))
    pltPdf1.close()

    # finish log with run time
    codeTfinish = datetime.now()
    logTime(foutLog, '\nRunFinished at: ', codeTfinish)
    
    return

# plot duration curves - with or without monthly segments "
def PlotDeltaDuration(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='plots/', fnameout='DurationCurves.pdf', 
                 dirlog='./', fnameLog='PlotDelta.log', dailyPlot=True):

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog)
    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    if considerCIDs=='' and ignoreCIDs=='':
        pass
    else:
        UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, ignoreCIDs, considerCIDs, foutLog)
    
    # open pdf for figures
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    # iterate over UniqueIDs to create figure for each in the pdf
    i = 1
    for cID in UniqueIDs: 
        i += 1
        customer = df1.CustomerID
        month = df1.index.month
        day = df1.index.day
        for m in range(1, 13,1):
            print ('Processing Month %d of %d' %( m,12))
            days = list(set(df1.loc[(month==m)].index.day))
            cmap = plt.get_cmap('jet', len(days))
            if dailyPlot:
                for d in days:
                    fig, (ax0) = plt.subplots(nrows=1, ncols=1,figsize=(8,6),sharex=True)
                    fig.suptitle( fnamein )   
                    ax0.set_title(  date(2016, m,1).strftime('%B')  + "/" + str(int(d)))   
                    relevant =  (customer==cID) & (month==m) & (day==d)
                    ax0 = addLoadCurveByDay(ax0, df1.loc[relevant])
                    ax0.set_ylim([-0.2,0.2])
                    pltPdf1.savefig() 
                    plt.close()   
                
            else:
                fig, (ax0) = plt.subplots(nrows=1, ncols=1,figsize=(8,6),sharex=True)
                fig.suptitle(fnamein       )   
                ax0.set_title(  date(2016, m,1).strftime('%B') )  
                for d in days:
                    relevant =  (customer==cID) & (month==m) & (day==d)
                    ax0 = addDurationCurveByDay(ax0, df1.loc[relevant], c=cmap(d))
                ax0.set_ylim([-0.2,0.2])
                pltPdf1.savefig() 
                plt.close()   
    
    # Closing plot files
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    foutLog.write('\n\nWriting: %s' %os.path.join(dirout, fnameout))
    pltPdf1.close()

    # finish log with run time
    codeTfinish = datetime.now()
    logTime(foutLog, '\nRunFinished at: ', codeTfinish)
    
    return


# plot duration curves - with or without monthly segments "
def PlotAvgDelta(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='plots/', fnameout='DurationCurves.pdf', 
                 dirlog='./', fnameLog='PlotDelta.log', dailyPlot=True):

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog)
    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    if considerCIDs=='' and ignoreCIDs=='':
        pass
    else:
        UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, ignoreCIDs, considerCIDs, foutLog)
    
    # open pdf for figures
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    # iterate over UniqueIDs to create figure for each in the pdf
    i = 1
    for cID in UniqueIDs: 
        i += 1
        customer = df1.CustomerID
        month = df1.index.month
        day = df1.index.day
        for m in range(1, 13,1):
            print ('Processing Month %d of %d' %( m,12))
            days = list(set(df1.loc[(month==m)].index.day))
            cmap = plt.get_cmap('jet', len(days))

            fig, (ax0) = plt.subplots(nrows=1, ncols=1,figsize=(8,6),sharex=True)
            fig.suptitle(fnamein       )   
            ax0.set_title(  date(2016, m,1).strftime('%B') )  
            for d in days:
                relevant =  (customer==cID) & (month==m) & (day==d)
                ax0 = addAverageDelta(ax0, df1.loc[relevant], c=cmap(d))
            ax0.set_ylim([-0.1,0.1])
            ax0.set_xlim([0,16])
            pltPdf1.savefig() 
            plt.close()   
    
    # Closing plot files
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    foutLog.write('\n\nWriting: %s' %os.path.join(dirout, fnameout))
    pltPdf1.close()

    # finish log with run time
    codeTfinish = datetime.now()
    logTime(foutLog, '\nRunFinished at: ', codeTfinish)
    
    return



# plot duration curves - with or without monthly segments "
def PlotPage(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='plots/', fnameout='DurationCurves.pdf', 
                 dirlog='./', fnameLog='PlotDelta.log'):

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog)
    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    if considerCIDs=='' and ignoreCIDs=='':
        pass
    else:
        UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, ignoreCIDs, considerCIDs, foutLog)
    
    # open pdf for figures
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    # iterate over UniqueIDs to create figure for each in the pdf
    
    for cID in UniqueIDs: 
        customer = df1.CustomerID
        month = df1.index.month
        day = df1.index.day
        
        fig, ax = plt.subplots(nrows=1, ncols=2,figsize=(8,6),sharex=False)
        plt.subplots_adjust(wspace=0.3)
        fig.suptitle(fnamein + " / entire year" )  
        cmap = plt.get_cmap('jet', 365)
        i = 0
        for m in range(1, 13,1):
            print ('Processing Month %d of %d' %( m,12))
            days = list(set(df1.loc[(month==m)].index.day))

            ax0 = ax[0]
            ax0.set_title( "Energy" )  
            for d in days:
                relevant =  (customer==cID) & (month==m) & (day==d)
                ax0 = addLoadCurveByDayEO(ax0, df1.loc[relevant], c=cmap(i), a=0.1)
            ax0.set_ylim([-1.0,1.0])
            ax0.set_ylabel('Shifted Energy [p.u.h]')
            ax1 = ax[1]
            ax1.set_title( "Load Duration")  
            for d in days:
                relevant =  (customer==cID) & (month==m) & (day==d)
                ax1 = addDurationCurveByDay(ax1, df1.loc[relevant], c=cmap(i), a=0.1)
                i+=1
            ax1.set_ylim([-0.3,0.3])
            ax1.set_ylabel('Shifted Load [p.u.]')
                
        pltPdf1.savefig() 
        plt.close()      
    
    for cID in UniqueIDs: 
        customer = df1.CustomerID
        month = df1.index.month
        day = df1.index.day
        for m in range(1, 13,1):
            print ('Processing Month %d of %d' %( m,12))
            days = list(set(df1.loc[(month==m)].index.day))
            cmap = plt.get_cmap('jet', len(days))

            fig, ax = plt.subplots(nrows=1, ncols=2,figsize=(8,6),sharex=False)
            plt.subplots_adjust(wspace=0.3)
            fig.suptitle(fnamein  + " / " + date(2016, m,1).strftime('%B') )   
            
            ax0 = ax[0]
            ax0.set_title( "Energy" )  
            for d in days:
                relevant =  (customer==cID) & (month==m) & (day==d)
                ax0 = addLoadCurveByDayEO(ax0, df1.loc[relevant], c=cmap(d), a=0.5)
            ax0.set_ylim([-1.0,1.0])
            ax0.set_ylabel('Shifted Energy [p.u.h]')
            ax1 = ax[1]
            ax1.set_title( "Load Duration")  
            for d in days:
                relevant =  (customer==cID) & (month==m) & (day==d)
                ax1 = addDurationCurveByDay(ax1, df1.loc[relevant], c=cmap(d), a=0.5)
            ax1.set_ylim([-0.3,0.3])
            ax1.set_ylabel('Shifted Load [p.u.]')
            pltPdf1.savefig() 
            plt.close()   
    
    # Closing plot files
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    foutLog.write('\n\nWriting: %s' %os.path.join(dirout, fnameout))
    pltPdf1.close()

    # finish log with run time
    codeTfinish = datetime.now()
    logTime(foutLog, '\nRunFinished at: ', codeTfinish)
    
    return

def PlotLoads(dirin='./', fnameinL='IntervalData.csv',   fnameino='groups.csv', 
                  dirout='./', fnameout='delta.csv',
                  dirlog='./', fnameLog='CompareLoads.log',
                  plotDeltas=False):
       
    # load time-series data 
    df1 = pd.read_csv(os.path.join(dirin,fnameinL), 
                          header = 0, 
                          usecols = [0, 1, 2], 
                          names=['CustomerID', 'datetimestr', 'NormDmnd'])  
    df1['datetime'] = pd.to_datetime(df1['datetimestr'], format='%Y-%m-%d %H:%M')
    df1.set_index(['datetime'], inplace=True)
    df1.drop(['datetimestr'], axis=1, inplace=True) # drop redundant column
    df1.sort_index(inplace=True) # sort on datetime
    
    df2 = pd.read_csv(os.path.join(dirin,fnameino), 
                          header = 0, 
                          usecols = [0, 1, 2], 
                          names=['CustomerID', 'datetimestr', 'NormDmnd']) 
    df2['datetime'] = pd.to_datetime(df2['datetimestr'], format='%Y-%m-%d %H:%M')
    df2.set_index(['datetime'], inplace=True)
    df2.drop(['datetimestr'], axis=1, inplace=True) # drop redundant column
    df2.sort_index(inplace=True) # sort on datetime

    # open pdf for figures
    print("Opening plot files")
    pltPdf1 = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    df3 = df2.copy()
    df3['NormDmnd'] = df1['NormDmnd'] - df2['NormDmnd']
    
    # iterate over UniqueIDs to create figure for each in the pdf
    month = df1.index.month
    day = df1.index.day
    for m in range(1, 13,1):
        print ('Processing Month %d of %d' %( m,12))
        days = list(set(df1.loc[(month==m)].index.day))
        
        for d in days:
            fig, ax = plt.subplots(nrows=2, ncols=1,figsize=(8,6),sharex=True)
            fig.suptitle( fnameinL + " / " + fnameino  + " / " +  date(2016, m,1).strftime('%B')  + "/" + str(int(d)))   
            
            ax0=ax[0]
#            ax0.set_title(  date(2016, m,1).strftime('%B')  + "/" + str(int(d)))   
            relevant =  (month==m) & (day==d)
            ax0 = addLoadCurve(ax0, df1.loc[relevant], c='k', lw=1, label='leaders')
            ax0 = addLoadCurve(ax0, df2.loc[relevant], c='b', lw=1, label='others')
            ax0.set_ylim([0.5,1.5])
            ax0.legend()
            
            ax1=ax[1]
#            ax0.set_title(  date(2016, m,1).strftime('%B')  + "/" + str(int(d)))   
            relevant =  (month==m) & (day==d)
            ax1 = addLoadDelta(ax1, df3.loc[relevant])
            ax1.set_ylim([-0.5,1.0])
            ax1.legend()
            
            pltPdf1.savefig() 
            plt.close()   
                
    
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    pltPdf1.close()

    # finish log with run time
#    codeTfinish = datetime.now()
#    logTime(foutLog, '\nRunFinished at: ', codeTfinish)
    
    return