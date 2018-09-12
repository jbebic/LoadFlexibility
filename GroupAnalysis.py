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
from pytz import timezone
import os # operating system interface
import string
import random
import matplotlib.pyplot as plt # plotting 
import matplotlib.backends.backend_pdf as dpdf # pdf output
import matplotlib.pylab as pl
from SupportFunctions import getData, findUniqueIDs, createLog, logTime

#%% Version and copyright info to record on the log file
codeName = 'GroupAnalysis.py'
codeVersion = '1.0'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Irene Berry, GE Global Research\n"


def addLoadCurveByDay(ax0, df, lw=1, c='b', ls='-'):
        
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Load [pu]')
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    

    ax0.plot(np.arange(df.shape[0]), df['NormDmnd'], ls, label='Normalized Demand [pu]', lw=lw, c=c)
        
    return ax0

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
    df1, UniqueIDs, foutLog = getData(dirin=dirin, fnamein=fnamein, foutLog=foutLog, varName='NormDmnd')

    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin=dirin, UniqueIDs=UniqueIDs, considerCIDs=considerCIDs, foutLog=foutLog)

    # load grouped data from file, find initial list of unique IDs. Update log file
    dfgroup, groupUniqueIDs, foutLog = getData(dirin=dirin, fnamein=fnameGroup,  foutLog=foutLog, varName='NormDmnd')
    
    # open pdf for figures
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
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
#                print(m,d,cID, len(relevant))
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
                    ax0.set_ylim([-1,1])
                    pltPdf1.savefig() 
                    plt.close()   
                
            else:
                fig, (ax0) = plt.subplots(nrows=1, ncols=1,figsize=(8,6),sharex=True)
                fig.suptitle(fnamein + "/" + date(2016, m,1).strftime('%b')       )   
                ax0.set_title(  date(2016, m,1).strftime('%B') )   
                for d in days:
                    relevant =  (customer==cID) & (month==m) & (day==d)
                    ax0 = addLoadCurveByDay(ax0, df1.loc[relevant])
                ax0.set_ylim([-1,1])
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