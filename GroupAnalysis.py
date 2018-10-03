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
import os # operating system interface
import matplotlib.pyplot as plt # plotting 
import matplotlib.backends.backend_pdf as dpdf # pdf output

#%% Importing supporting modules
from SupportFunctions import getData, logTime, createLog,  assignDayType #findUniqueIDs,

#%% Version and copyright info to record on the log file
codeName = 'GroupAnalysis.py'
codeVersion = '1.4'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Irene Berry, GE Global Research\n"

# %% Function definitions
def plotDailyDeltas(ax0, df, lw=1, c='b', ls='-'):
    
    """ adds specific day's power & energy deltas to axis """
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Delta')
    ax0.set_xlabel('Hour of the Day [h]')
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    y = [yy for yy in range(-40, 41,1)]
    ax0.set_yticks(y)  
    ax0.xaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5) 
    y = np.cumsum(df['NormDmnd'])/4
    y = y - np.min(y)
    ax0.fill_between(np.arange(df.shape[0]), 0,  df['NormDmnd'],  label='Load [pu]')      
    ax0.plot(np.arange(df.shape[0]), y, ls, lw=lw*2, c='purple', label='Energy [pu-h]')
    
    return ax0, np.max(y)

def plotDailyLoads(ax0, df, lw=1, c='b', ls='-', label=''):
    
    """ adds specific day's load curve to axis """
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Normalized Load [pu]')
    ax0.set_xlabel('Hour of the Day [h]')
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    y = [yy for yy in range(-40, 41,1)]
    ax0.set_yticks(y )  
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    ax0.plot(np.arange(df.shape[0]), df['NormDmnd'], ls,  lw=2, c=c, label=label)
    
    return ax0

def plotHistogram(ax2, dailyEnergy, shiftedEnergy):

    y = np.asarray(shiftedEnergy)/np.asarray(dailyEnergy)*100
    yMax = np.ceil(np.max(y))
    ax2.hist(y,bins='auto', color='purple', lw=0, alpha=0.5)   
#    ax2.hist(shiftedEnergy,bins='auto', color='purple', lw=0)   
    ax2.set_xlabel('Shiftable Energy [% of Daily Energy]')
    ax2.set_ylabel('Number of Days')
    ax2.set_xlim([0,yMax])  
    
    return ax2


def formatShiftedEnergy(ax0):
    
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    ax0.set_ylabel('Shiftable Energy [MWh]')
    ax0.set_xlabel('Hour of the Day')
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])
    
    return

def plotShiftedEnergy(ax0, df, lw=1, c='b', ls='-',a=1.0):
    
    """ adds specific day's shifted energy to axis """
    df = df.sort_values(by='datetime', ascending=True)                  
    y = np.cumsum(df['NormDmnd'])
    y = y - np.min(y)  
    ax0.plot(np.arange(df.shape[0]), y, ls, lw=lw, c=c, alpha=a)
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])

    return ax0, np.max(y)

def plotDeltaDuration(ax0, df, lw=1, c='b', ls='-', a=1.0):
    
    """ adds specific day's duration curve to axis """
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_xlabel('Duration [h]')
    x = [x for x in range(0,int(df.shape[0])+int(df.shape[0]/(24/4)), int(df.shape[0]/(24/4)))]
    ax0.set_xticks(x)
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    ax0.set_xlim([0,  int(df.shape[0]*24/24) ])   
       
    df1 = df.copy()
    charge = df1.loc[df1['NormDmnd']>0]
    discharge = df1.loc[df1['NormDmnd']<0]      
    
    charge = charge.sort_values('NormDmnd', ascending=False)
    discharge = discharge.sort_values('NormDmnd', ascending=True)
    
    ax0.step(np.arange(charge.shape[0]), charge['NormDmnd'] * 4.0 ,  ls, lw=lw, c=c, alpha=a)
    ax0.step(np.arange(discharge.shape[0]), discharge['NormDmnd'] * 4.0,  ls, lw=lw, c=c, alpha=a)
    
    ymax = np.max([ np.max(abs(charge['NormDmnd'])) * 4.0 , np.max(abs(discharge['NormDmnd'])) * 4.0 ])
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    
    return ax0, ymax


def plotLoadDuration(ax0, df, lw=1, c='b', ls='-', a=1.0):
    
    """ adds specific day's duration curve to axis """
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_xlabel('Duration [h]')
    x = [x for x in range(0,int(df.shape[0])+int(df.shape[0]/(24/4)), int(df.shape[0]/(24/4)))]
    ax0.set_xticks(x)
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    ax0.set_xlim([0,  int(df.shape[0]*24/24) ])   
       
    df1 = df.copy()
    df1 = df1.sort_values('Others', ascending=False)
    ax0.step(np.arange(df1.shape[0]), df1['Others'] * 4.0,  ls, lw=lw, c=c, alpha=a)
    
    e = np.sum( df1['Others'].values)
    ymax = np.max([  np.max(abs(df1['Others'])) * 4.0 ])
    if np.isnan(ymax) or np.isinf(ymax):
        ymax = 0.0
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    
    return ax0, ymax, e

def annualSummaryPage(pltPdf1, df1, fnamein, normalized=False):
    """ create page summary for specific month & add to pdf """
    
    # initialize figure
    #fig, ax = plt.subplots(nrows=1, ncols=2,figsize=(8,6),sharex=False)
    #ax1 = ax[1]
    #ax0 = ax[0]
    fig = plt.figure(figsize=(8,6))
    fig.suptitle(fnamein + " / entire year" )  
    plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
    ax0 = plt.subplot2grid((2, 2), (0, 0),  fig=fig)
    ax1 = plt.subplot2grid((2, 2), (0, 1),  fig=fig)
    ax2 = plt.subplot2grid((2, 2), (1, 0),  fig=fig)
    ax3 = plt.subplot2grid((2, 2), (1, 1),  fig=fig)
    
    # initialize variables
    month = df1.index.month
    day = df1.index.day
    ymax = 0
    yMax = 0
    yMaxD = 1.0
    yMaxP = 0.0
    
    # iterate over each month
    dailyEnergy = []
    shiftedEnergy = []
    for m in range(1, 13,1):
        days = list(set(df1.loc[(month==m)].index.day))
        
        # plot shifted energy
        ax0.set_title( "Energy" ) 
        # iterate for each day in month
        for d in days:
            relevant = (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                pass
            else:
                ax0, ymax = plotShiftedEnergy(ax0, df1.loc[relevant], c='purple', a=0.1)
                yMax  = np.max([yMax, ymax])
                shiftedEnergy.append(ymax)
        yMax = np.ceil(yMax)
        ax0.set_ylim([0,yMax])
        if normalized:
            ax0.set_ylabel('Shiftable Energy [p.u.h]')
        else:
            ax0.set_ylabel('Shiftable Energy [MWh]')
            
            
            
        # plot load-duration
        ax1.set_title( "Load")
        # iterate for each day in month
        for d in days:
            relevant = (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                pass
            else:
                ax1, ymax = plotDeltaDuration(ax1, df1.loc[relevant], c='steelblue', a=0.1) 
                yMaxD = np.max([yMaxD , ymax])
        if normalized:
            ax1.set_ylabel('Shiftable Load [p.u.]')
        else:
            ax1.set_ylabel('Shiftable Load [MW]')
        ax1.set_ylim([-yMaxD , yMaxD ])
        
        
        # plot duration curve
        # iterate for each day in month
        for d in days:
            relevant = (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                pass
            else:
                ax3, ymax, emax = plotLoadDuration(ax3, df1.loc[relevant], c='steelblue', a=0.1) 
                yMaxP = np.max([yMaxP , ymax])
                dailyEnergy.append(emax)
        if normalized:
            ax3.set_ylabel('Load [p.u.]')
        else:
            ax3.set_ylabel('Load [MW]')
        ax3.set_ylim([0.0, yMaxP ])        
        
    # plot histogram
    ax2 = plotHistogram(ax2, dailyEnergy, shiftedEnergy) 
    xmax = ax2.get_xlim()
    yMaxH = xmax[1]
    formatShiftedEnergy(ax0)
    
    # save to pdf
    pltPdf1.savefig() 
    plt.close() 
        
    return pltPdf1, yMax, yMaxD, yMaxP, yMaxH

def monthlySummaryPages(pltPdf1, df1, fnamein, yMaxE, yMaxD, yMaxP, yMaxH, normalized=False):
    """ create page summary for specific month & add to pdf"""
    
    month = df1.index.month
    day = df1.index.day
    
    # iterate over each month
    for m in range(1, 13,1):
        days = list(set(df1.loc[(month==m)].index.day))
        
#        # initialize figure
#        fig, ax = plt.subplots(nrows=1, ncols=2,figsize=(8,6),sharex=False)
#        plt.subplots_adjust(wspace=0.3)
        
        # initialize figure
        #fig, ax = plt.subplots(nrows=1, ncols=2,figsize=(8,6),sharex=False)
        #ax1 = ax[1]
        #ax0 = ax[0]
        fig = plt.figure(figsize=(8,6))
        fig.suptitle(fnamein + " / entire year" )  
        plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
        ax0 = plt.subplot2grid((2, 2), (0, 0),  fig=fig)
        ax1 = plt.subplot2grid((2, 2), (0, 1),  fig=fig)
        ax2 = plt.subplot2grid((2, 2), (1, 0),  fig=fig)
        ax3 = plt.subplot2grid((2, 2), (1, 1),  fig=fig)
        fig.suptitle(fnamein  + " / " + date(2016, m,1).strftime('%B') )   
        
        # plot shifted energy
        ax0.set_title( "Energy" )  
        
        # iterate for each day of the month
        dailyEnergy = []
        shiftedEnergy = []
        for d in days:
            relevant =  (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                ax0,ymax0 = plotShiftedEnergy(ax0, df1.loc[relevant], c='gray', a=0.2)
            else:
                ax0,ymax0 = plotShiftedEnergy(ax0, df1.loc[relevant], c='purple', a=0.5)
                shiftedEnergy.append(ymax0)
                
        ax0.set_ylim([0,yMaxE])
        if normalized:
            ax0.set_ylabel('Shifted Energy [p.u.h]')
        else:
            ax0.set_ylabel('Shifted Energy [MWh]')
            
        # plot load-duration
        ax1.set_title( "Load Duration")  
        
        # iterate for each day of the month
        for d in days:
            relevant =  (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                ax1, ymax1 = plotDeltaDuration(ax1, df1.loc[relevant], c='gray', a=0.2)
            else:
                ax1, ymax1 = plotDeltaDuration(ax1, df1.loc[relevant], c='steelblue', a=0.5)
        ax1.set_ylim([-yMaxD, yMaxD])
        if normalized:
            ax1.set_ylabel('Shifted Load [p.u.]')
        else:
            ax1.set_ylabel('Shifted Load [MW]')
            
            
       # plot duration curve
        # iterate for each day in month
        for d in days:
            relevant = (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                pass
            else:
                ax3, ymax2, emax = plotLoadDuration(ax3, df1.loc[relevant], c='steelblue', a=0.1) 
                dailyEnergy.append(emax)
        if normalized:
            ax3.set_ylabel('Load [p.u.]')
        else:
            ax3.set_ylabel('Load [MW]')
        ax3.set_ylim([0.0, yMaxP ])        
        
        # plot histogram
        ax2 = plotHistogram(ax2, dailyEnergy, shiftedEnergy)             
        ax2.set_xlim([0.0, yMaxH ])        
        if normalized:
            ax0.set_xlabel('Shifted Energy [p.u.h]')
        else:
            ax0.set_xlabel('Shifted Energy [MWh]')
            
        formatShiftedEnergy(ax0)
        
        # save figure to pdf
        pltPdf1.savefig() 
        plt.close()  
        
    return pltPdf1

def DeltaLoads(dirin='./', fnameinL='IntervalData.csv',   fnameino='groups.csv', 
                  dirout='./', fnameout='delta.csv',
                  dirlog='./', fnameLog='DeltaLoads.log',
                  dataName = 'delta'):
    
    """ calculates delta between leaders & others in a group """
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
       
    # load time-series data for leaders & others
    df1, UniqueIDs, foutLog = getData(dirin, fnameinL, foutLog, varName=['NormDmnd','DailyAverage', 'Demand'],usecols=[0,1,2,3,4], datetimeIndex=False)
    df2, UniqueIDs, foutLog = getData(dirin, fnameino, foutLog, varName=['NormDmnd','DailyAverage', 'Demand'],usecols=[0,1,2,3,4], datetimeIndex=False)
    
    # calculate delta
    df3 = df2.copy()
    df3['NormDelta'] = df1['NormDmnd'] - df2['NormDmnd']
    df3['AbsDelta']  = df3['NormDelta'] * ( df2['DailyAverage']  )
    df3['Leaders'] = df1['Demand']
    
    # asign cid as CustomerID
    cid = np.asarray([ dataName for i in range(0,len(df3),1)])
    df3 = df3.assign(CustomerID=pd.Series(cid,index=df3.index))
    
    # write to file
    print('Writing output file: %s' %os.path.join(dirout,fnameout))
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df3.to_csv( os.path.join(dirout,fnameout), columns=['CustomerID', 'datetime', 'NormDelta','AbsDelta', 'Leaders', 'Demand'], float_format='%.5f', date_format='%Y-%m-%d %H:%M', index=False) # this is a multiindexed dataframe, so only the data column is written

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

def PlotDeltaSummary(dirin='./', fnamein='IntervalData.normalized.csv', 
                 dirout='plots/', fnameout='DurationCurves.pdf', 
                 normalized=False,
                 dirlog='./', fnameLog='PlotDeltaSummary.log'):
    
    """Creates pdf with 13 pages: 1 page summary of entire year followed by monthly. Each page shows shifted energy & duration curves """
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # load data from file, find initial list of unique IDs. Update log file
    if normalized:
        df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog,  varName=['NormDmnd', 'AbsDemand', 'Leaders', 'Others'], usecols=[0,1,2])
    else:
        df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog, varName=[ 'NormDmnd', 'Leaders', 'Others'], usecols=[0,1,3, 4, 5])
    
    # add season & day type
    df1 = assignDayType(df1)

    # open pdf for figures
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    # create annual summary of shifted energy & load duration
    foutLog.write("Creating annual figure" )
    print("Creating annual figure" )
    pltPdf1, yMaxE, yMaxD, yMaxP, yMaxH = annualSummaryPage(pltPdf1, df1, fnamein, normalized)
    
    # create monthly summaries of shifted energy & load duration
    foutLog.write("Creating monthly figures" )
    print("Creating monthly figures" )
    pltPdf1 = monthlySummaryPages(pltPdf1, df1, fnamein, yMaxE, yMaxD, yMaxP, yMaxH, normalized)  
    
    # Closing plot files
    print('Writing output file: %s' %os.path.join(os.path.join(dirout, fnameout)))
    foutLog.write('\n\nWriting: %s' %os.path.join(dirout, fnameout))
    pltPdf1.close()

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return




def PlotDeltaByDay(dirin='./', fnameinL='leaders.csv',   fnameino='others.csv', 
                  dirout='./', fnameout='delta.csv',
                  dirlog='./', fnameLog='PlotDeltaByDay.log'):
    
    """ Creates pdf with 365 pages showing the leader and other loads & the delta for each day of the year"""
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    # load time-series data for leaders & others
    df1, UniqueIDs, foutLog = getData(dirin, fnameinL, foutLog, varName='NormDmnd')
    df2, UniqueIDs, foutLog = getData(dirin, fnameino, foutLog, varName='NormDmnd')

    # assign season & day type
    df1 = assignDayType(df1)
    df2 = assignDayType(df2)
    
    month = df1.index.month
    day = df1.index.day
    
    # calculate delta
    df3 = df2.copy()
    df3['NormDmnd'] = df1['NormDmnd'] - df2['NormDmnd']

    # open pdf for figures
    print("Opening plot files")
    pltPdf1 = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    # find max y limits
    ymax = np.ceil(np.max([ df1['NormDmnd'].max() *2  , df2['NormDmnd'].max()*2  ])) / 2

    # find min / max for delta figure
    ymaxDelta = 1.0
    yminDelta = np.floor( np.min(df3['NormDmnd'])*2)/2
    for m in range(1, 13,1):
        days = list(set(df1.loc[(month==m)].index.day))  
        for d in days:
            relevant = (month==m) & (day==d)
            y = np.cumsum(df3.loc[relevant,'NormDmnd'])/4
            y = y - np.min(y)
            ymaxDelta = np.max([ ymaxDelta, np.max(y) ])
    ymaxDelta = np.ceil( ymaxDelta * 2.0 ) / 2.0
    
    # iterate over each month of the year
    for m in range(1, 13,1):
        print('Plotting daily loads & deltas for %s' %(date(2016, m,1).strftime('%B')))
        
        # iterate over each day of the month
        days = list(set(df1.loc[(month==m)].index.day))  
        for d in days:
            
            # find this day in the data
            relevant = (month==m) & (day==d)
            
            # initialize figure
            fig, ax = plt.subplots(nrows=2, ncols=1,figsize=(8,6),sharex=True)
            fig.suptitle( fnameinL + " / " +  date(2016, m,1).strftime('%B')  + " / " + str(int(d)) +  " / " + df1.loc[relevant, 'DayType'][0])   
            
            # plot loads of leaders & others 
            ax0=ax[0]
            ax0 = plotDailyLoads(ax0, df1.loc[relevant], c='b', lw=1, label='leaders')
            ax0 = plotDailyLoads(ax0, df2.loc[relevant], c='k', lw=1, label='others')
            ax0.set_ylim([0.0,ymax])
            ax0.legend()
            
            # plot delta between leaders & others 
            ax1=ax[1]
            ax1,temp = plotDailyDeltas(ax1, df3.loc[relevant])
            ax1.set_ylim([yminDelta,ymaxDelta])
            ax1.legend(loc=1)
            
            # add to pdf
            pltPdf1.savefig() 
            plt.close()   
                
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    pltPdf1.close()

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return