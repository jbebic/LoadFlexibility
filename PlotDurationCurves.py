# -*- coding: utf-8 -*-
"""
Created on Wed May 10 17:05:28 2018

@author: jbebic

Load duration curves of normalized loads
"""

#%% Importing all the necessary Python packages
import pandas as pd # multidimensional data analysis
import numpy as np # vectorized calculations
from datetime import datetime # time stamps
from datetime import date
import os # operating system interface
import matplotlib.pyplot as plt # plotting 
import matplotlib.backends.backend_pdf as dpdf # pdf output

#%% Importing modules
from SupportFunctions import getData, logTime, createLog, findUniqueIDs, readHighlightIDs

#%%  Version and copyright info to record on the log file
codeName = 'PlotDurationCurves.py'
codeVersion = '1.5'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Jovan Bebic & Irene Berry, GE Global Research\n"

#%% Function Definitions
def outputAnnualDurationCurve(ax0, df, cid, foutLog,varName='NormDmnd', applyNormalization=False, addTitle=True, addXLabel=True):
    """ creates duration curve for entire year for one customer"""
    
    ymin = 0.0
    if addTitle:
        ax0.set_title('Annual')
    ax0.set_ylabel('Load [pu]')
    ax0.set_xlim([0,8760*4])
    ax0.set_xticks(np.linspace(0, 8760*4, num=5).tolist())
    ax0.set_xticklabels(np.linspace(0, 8760, num=5, dtype=np.int16).tolist())
    if addXLabel:
        ax0.set_xlabel('Hour')
    ax0.set_aspect('auto')
    try:
        df1 = df.sort_values(varName, ascending=False)
        if applyNormalization:
            dAvg = df1[varName].mean()
            df1[varName] = df1[varName].copy()/dAvg 
        ymax = np.ceil(df1[varName].max()*2)/2  
        ax0.step(np.arange(df1.shape[0]), (df1[varName]), 'steelblue')
        ax0.set_ylim([ymin,ymax])   
        ax0.plot([0, df1.shape[0]], [1.0, 1.0], lw=1, color='gray', alpha=0.25)
    except:
        foutLog.write("\n*** Unable to create annual duration plot for %s " %cid )
        print("*** Unable to create duration annual plot for %s " %cid)
    return ax0

def outputDailyDurationCurve(ax0, df, cid, foutLog, varName='NormDmnd', applyNormalization=False, addTitle=True, addXLabel=True):
    """ creates duration curve for entire year for one customer"""
    if addTitle:
        ax0.set_title('Daily')
    ax0.set_xlim([0,24*4])
    ax0.set_xticks(np.linspace(0, 24*4, num=5).tolist())
    ax0.set_xticklabels(np.linspace(0, 24, num=5, dtype=np.int16).tolist())
    if addXLabel:
        ax0.set_xlabel('Hour')
    ax0.set_aspect('auto')
    
    for m in range(0,13,1):
        try:
            for d in range(0,31,1):
                try:
                    df0 = df.loc[ (df['datetime'].dt.month==m) & (df['datetime'].dt.day==d) ]
                except:
                    df0 = df.loc[ (df.index.month==m) & (df.index.day==d)]
                    
                if len(df0)>0:
                    df1 = df0.sort_values(varName, ascending=False)
                    if applyNormalization:
                        dAvg = df1[varName].mean()
                        df1[varName] = df1[varName].copy()/dAvg 
                    ax0.step(np.arange(df1.shape[0]), (df1[varName]), 'steelblue', label='Normalized Demand [pu]', alpha=0.15)
        except:
            foutLog.write("\n*** Unable to create daily duration plot for %s " %cid )
            print("*** Unable to create dailyduration plot for %s " %cid)
    ax0.plot([0, df1.shape[0]], [1.0, 1.0], lw=1, color='gray', alpha=0.25)
    return ax0

def outputMonthlyDurationCurve(ax0, df, cid, foutLog, varName='NormDmnd', applyNormalization=False, addTitle=True, addXLabel=True):
    """ creates duration curve for entire year for one customer"""
    if addTitle:
        ax0.set_title('Monthly')
    ax0.set_xlim([0,31*24*4])
    ax0.set_xticks(np.linspace(0, 31*24*4, num=5).tolist())
    ax0.set_xticklabels(np.linspace(0, 31*24, num=5, dtype=np.int16).tolist())
    if addXLabel:
        ax0.set_xlabel('Hour')
    ax0.set_aspect('auto')
    for m in range(0,13,1):
#        try:
        try:
            df0 = df.loc[ df['datetime'].dt.month==m]
        except:
            df0 = df.loc[ df.index.month==m]
        df1 = df0.sort_values(varName, ascending=False)
        if applyNormalization:
            dAvg = df1[varName].mean()
            df1[varName] = df1[varName].copy()/dAvg 
        ax0.step(np.arange(df1.shape[0]), (df1[varName]), c='steelblue', label='Normalized Demand [pu]', alpha=0.5)
#        except:
#            foutLog.write("\n*** Unable to create monthly duration plot for %s " %cid )
#            print("*** Unable to create monthly duration plot for %s " %cid)
    ax0.plot([0, df1.shape[0]], [1.0, 1.0], lw=1, color='gray', alpha=0.25)
    return ax0


def outputDurationCurve(pltPdf, df, fnamein, cid, foutLog):
    """ creates duration curve for entire year for one customer"""
    
    fig, (ax0) = plt.subplots(nrows=1, ncols=1,figsize=(8,6),sharex=True)
    fig.suptitle(fnamein + "/" + cid) # This titles the figure    
    ymin = 0.0

    ax0.set_title('Normalized Load')
    ax0.set_ylabel('Load [pu]')

    ax0.set_xlim([0,8760*4])
    ax0.set_xticks(np.linspace(0, 8760*4, num=5).tolist())
    ax0.set_xticklabels(np.linspace(0, 8760, num=5, dtype=np.int16).tolist())
    ax0.set_xlabel('Hour')
    ax0.set_aspect('auto')
    
    try:
        ymax = np.ceil(df['NormDmnd'].max()*2)/2  
        df1 = df.sort_values('NormDmnd', ascending=False)
        ax0.step(np.arange(df1.shape[0]), (df1['NormDmnd']), 'C3', label='Normalized Demand [pu]')
        ax0.plot([0, df1.shape[0]], [1.0, 1.0], lw=1, color='gray', alpha=0.25)
        ax0.set_ylim([ymin,ymax])
        pltPdf.savefig() # Saves fig to pdf
        plt.close() # Closes fig to clean up memory
        
    except:
        
        foutLog.write("\n*** Unable to create duration plot for %s " %cid )
        print("*** Unable to create duration plot for %s " %cid)
        
        try:
            plt.close()    
        except:
            pass
        
    return

# individual ID: create duration curve for entire year, one month after another "
def outputDurationCurveByMonth(pltPdf, df, fnamein, cid, foutLog):
    """ creates duration curve for entire year for one customer, showing monthly segments """
    
    ymin = 0.0
    # x-axis labels: If more than one year of data is given use "Mmm 'yy", otherwise use "Mmm"
    if df.index.year.unique().shape[0] > 1:
        xlabels = df.index.strftime("%b '%y").unique().tolist()
    else:
        xlabels = df.index.strftime("%b").unique().tolist()
            
    fig, (ax0) = plt.subplots(nrows=1, ncols=1, figsize=(8,6), sharex=True) 
    fig.suptitle(fnamein + "/" + cid)
    ax0.set_title('Normalized Load')
    ax0.set_ylabel('Load [pu]')
    ax0.set_xlim([0, pd.date_range(df.index.min(), df.index.max(), freq='15min').shape[0]])
    ax0.set_xticklabels(xlabels)
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)
    ax0.set_aspect('auto')
    ymax = np.ceil(df['NormDmnd'].max()*2)/2
    
    color='blue'
    alpha = 0.5
    
    try:
        tickindex = []
        # Go month by month: create a placeholder for full month, and fill with values sorted in the descending order
        for year in df.index.year.unique().tolist():
            for month in df[df.index.year == year].index.month.unique().tolist():
                try:
                    df2 = df[(df.index.year == year) & (df.index.month == month)]
                    index2 = pd.date_range(df2.index.min(), df2.index.max(), freq='15min').values
                    df2 = df2.reindex(index=index2, method='ffill')
                    df3 = pd.DataFrame(data = df2.sort_values(['NormDmnd'], ascending=False)['NormDmnd'].values, columns=['NormDmnd'], index = None)
                    xshift = pd.date_range(df.index.min(), df2.index.min(), freq='15min').shape[0]
                    ax0.step(xshift+np.arange(df3.shape[0]), (df3['NormDmnd']), color=color, alpha=alpha)
                    tickindex.append(xshift)
                except:
                    pass

        ax0.set_ylim([ymin,ymax])
        ax0.set_xticks(tickindex)
        
        pltPdf.savefig() 
        plt.close()    
        
    except:
        
        foutLog.write("\n*** Unable to create duration plot for %s " %cid )
        print("*** Unable to create duration plot for %s " %cid)
        
        try:
            plt.close()    
        except:
            pass
        
    
    return

# individual ID: create duration curve for entire year, one month after another "
def outputDurationCurveByMonthWithDailyProfiles(pltPdf, df, fnamein, cid, foutLog):
    """ creates duration curve for entire year for one customer, showing monthly segments with daily profiles"""
    
    ymin = 0.0
    # x-axis labels: If more than one year of data is given use "Mmm 'yy", otherwise use "Mmm"
    if df.index.year.unique().shape[0] > 1:
        xlabels = df.index.strftime("%b '%y").unique().tolist()
    else:
        xlabels = df.index.strftime("%b").unique().tolist()
            
    fig, (ax1, ax0) = plt.subplots(nrows=2, ncols=1, figsize=(8,6), sharex=True) 
    fig.suptitle(fnamein + "/" + cid)
    ax0.set_title('Daily Duration Curves')
    ax0.set_ylabel('Load [pu]')
    ax0.set_xlim([0, pd.date_range(df.index.min(), df.index.max(), freq='1M').shape[0]*24*4]) # Each month will have 24*4 x axis
    ax0.set_xticklabels(xlabels)
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)
    ax0.set_aspect('auto')

    ax1.set_title('Daily Load Curves')
    ax1.set_ylabel('Load [pu]')
    ax1.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)
    ax1.set_aspect('auto')
    
    ymax = np.ceil(df['NormDmnd'].max()*2)/2

    color='blue'
    alpha = 0.5
    
    try:
        tickindex = []
        shiftYear = 0
        shiftMon  = 0
        # Go month by month: create a placeholder for full month, and fill with values sorted in the descending order
        for year in df.index.year.unique().tolist():
            for month in df[df.index.year == year].index.month.unique().tolist():
                try:
                    df2 = df[(df.index.year == year) & (df.index.month == month)]
                    index2 = pd.date_range(df2.index.min(), df2.index.max(), freq='15min').values
                    df2 = df2.reindex(index=index2, method='ffill')
                    xshift = (shiftYear*12 + shiftMon)* 24*4
                    for day in df2.index.day.unique().tolist():
                        df3 = df2[df2.index.day == day]
                        df4 = pd.DataFrame(data = df3.sort_values(['NormDmnd'], ascending=False)['NormDmnd'].values, columns=['NormDmnd'], index = None)
                        ax1.step(xshift+np.arange(df3.shape[0]), (df3['NormDmnd']), color=color, alpha=alpha)
                        ax0.step(xshift+np.arange(df4.shape[0]), (df4['NormDmnd']), color=color, alpha=alpha)
                except:
                    pass
                tickindex.append(xshift)
                shiftMon += 1
            shiftYear += 1

        ax0.set_ylim([ymin,ymax])
        ax0.set_xticks(tickindex)
        
        pltPdf.savefig() 
        plt.close()    
        
    except:
        foutLog.write("\n*** Unable to create duration plot for %s " %cid )
        print("*** Unable to create duration plot for %s " %cid)
        
        try:
            plt.close()    
        except:
            pass
        
    
    return


def outputFamilyOfDurationCurvesByMonth(pltPdf, df, foutLog, title='', skipLegend=False, hIDs=[]):
    """ creates duration curve for entire year for one customer, showing monthly segments """
    
    ymin = 0.0
    # x-axis labels: If more than one year of data is given use "Mmm 'yy", otherwise use "Mmm"
    if df.index.year.unique().shape[0] > 1:
        xlabels = df.index.strftime("%b '%y").unique().tolist()
    else:
        xlabels = df.index.strftime("%b").unique().tolist()
            
    fig, (ax0) = plt.subplots(nrows=1, ncols=1, figsize=(8,6), sharex=True) 
    fig.suptitle(title)
    ax0.set_title('Normalized Load')
    ax0.set_ylabel('Load [pu]')
    ax0.set_xlim([0, pd.date_range(df.index.min(), df.index.max(), freq='15min').shape[0]])
    ax0.set_xticklabels(xlabels)
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)
    ax0.set_aspect('auto')
    ymax = np.ceil(df['NormDmnd'].max()*2)/2

    try:
        tickindex = []
        # Go month by month: create a placeholder for full month, and fill with values sorted in the descending order
        for year in df.index.year.unique().tolist():
            for month in df[df.index.year == year].index.month.unique().tolist():
                df2a = df[(df.index.year == year) & (df.index.month == month)]
                print("Plotting %d-%02d" %(year,month))
                xshift = pd.date_range(df.index.min(), df2a.index.min(), freq='15min').shape[0]
                tickindex.append(xshift)
                if len(hIDs) > 0:
                    color = '#d3d3d3'
                    alpha = 1
                else:
                    color = 'blue'
                    alpha = 0.5
                for cid in df['CustomerID'].unique().tolist():
                    try:
                        df2 = df2a[df2a['CustomerID'] == cid]
                        index2 = pd.date_range(df2.index.min(), df2.index.max(), freq='15min').values
                        df2 = df2.reindex(index=index2, method='ffill')
                        df3 = pd.DataFrame(data = df2.sort_values(['NormDmnd'], ascending=False)['NormDmnd'].values, columns=['NormDmnd'], index = None)
                        ax0.step(xshift+np.arange(df3.shape[0]), (df3['NormDmnd']), color=color, alpha=alpha)
                    except:
                        foutLog.write("\n*** Unable to create duration plot for %s " %cid )
                        print("*** Unable to create duration plot for %s " %cid)
                if len(hIDs) > 0:
                    color = 'blue'
                    alpha = 0.5
                    for cid in hIDs:
                        try:
                            df2 = df2a[df2a['CustomerID'] == cid]
                            index2 = pd.date_range(df2.index.min(), df2.index.max(), freq='15min').values
                            df2 = df2.reindex(index=index2, method='ffill')
                            df3 = pd.DataFrame(data = df2.sort_values(['NormDmnd'], ascending=False)['NormDmnd'].values, columns=['NormDmnd'], index = None)
                            ax0.step(xshift+np.arange(df3.shape[0]), (df3['NormDmnd']), color=color, alpha=alpha)
                        except:
                            foutLog.write("\n*** Unable to create duration plot for %s " %cid )
                            print("*** Unable to create duration plot for %s " %cid)

        ax0.set_ylim([ymin,ymax])
        ax0.set_xticks(tickindex)
        if skipLegend:
            legend = ax0.legend()
            legend.remove()
        
        pltPdf.savefig() 
        plt.close()    
    except:
        try:
            plt.close()    
        except:
            pass
        
    
    return

# family: create group of duration curves "
def outputFamilyOfDurationCurves(pltPdf, df, foutLog, title='', skipLegend=False, hIDs=[]):
    """ Creates one figure with an annual duration curve for each customer """
    
    fig, (ax0) = plt.subplots(nrows=1,ncols=1,figsize=(8,6),sharex=True)    
    fig.suptitle(title) # This titles the figure

    ymin = 0.0
    ymax = np.ceil(df['NormDmnd'].max()*2)/2
    
    ax0.set_title('Normalized Load')
    ax0.set_ylim([ymin,ymax])
    ax0.set_ylabel('Load [pu]')

    ax0.set_xlim([0,8760*4])
    ax0.set_xticks(np.linspace(0, 8760*4, num=5).tolist())
    ax0.set_xticklabels(np.linspace(0, 8760, num=5, dtype=np.int16).tolist())
    ax0.set_xlabel('Hour')
    ax0.set_aspect('auto')
 
    if len(hIDs) > 0:
        color = '#d3d3d3'
        alpha = 1
    else:
        color = 'blue'
        alpha = 0.5
    
    UniqueIDs = df['CustomerID'].unique()
    i = 1
    for cID in UniqueIDs:
        print ('Processing %s (%d of %d) ' %(cID, i, len(UniqueIDs)))
        i +=1
        try:
            df1 = df[df['CustomerID']==cID]
            df2 = df1.sort_values('NormDmnd', ascending=False)
            ax0.step(np.arange(df2.shape[0]), (df2['NormDmnd']), label=cID, color=color, alpha = alpha)
        except:
            foutLog.write("\n*** Unable to create duration plot for %s " %cID)
            print("*** Unable to create duration plot for %s " %cID)

    if len(hIDs) > 0:
        i = 1
        color = 'blue'
        alpha = 0.5
        for cID in hIDs:
            print ('Highlighting %s (%d of %d) ' %(cID, i, len(hIDs)))
            i +=1
            try:
                df1 = df[df['CustomerID']==cID]
                df2 = df1.sort_values('NormDmnd', ascending=False)
                ax0.step(np.arange(df2.shape[0]), (df2['NormDmnd']), label=cID, color=color, alpha = alpha)
            except:
                foutLog.write("\n*** Unable to create duration plot for %s " %cID)
                print("*** Unable to create duration plot for %s " %cID)
        
        if skipLegend:
            legend = ax0.legend() # plt.legend()
            legend.remove()
    
    pltPdf.savefig() # Saves fig to pdf
    plt.close() # Closes fig to clean up memory
    
    return


def PlotDurationCurveSequence(dirin='./', fnamein='IntervalData.csv', 
                 ignoreCIDs='', considerCIDs='',
                 dirout='plots/', fnameout='DurationCurveSequence.pdf', 
                 dirlog='./', fnameLog='PlotDurationCurveSequence.log',
                  varName='NormDmnd'):
    
    """ Create pdf with one page per customer showing annual duration curve, with or without monthly segments """

    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "PlotDurationCurveSequence", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    # load data from file, find initial list of unique IDs. Update log file
#    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog)
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog, varName=["NormDmnd", "DailyAverage", "Demand"],usecols=[0,1,2,3,4], datetimeIndex=False)

    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs, considerCIDs)
    
    # open pdf for figures
    print('Opening plot file: %s' %(os.path.join(dirout, fnameout)))
    foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout)))
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    # iterate over UniqueIDs to create figure for each in the pdf
    figN = 0
    i = 1
    for cID in UniqueIDs: 
        print ('Processing %s (%d of %d)' %(cID, i, len(UniqueIDs)))
        i += 1
        df2 = df1[df1['CustomerID']==cID]
        
        dAvg = df2["Demand"].mean()
        df2["NormDmndAnnual"] = df2["Demand"].copy()/dAvg 
                
        fig, ax = plt.subplots(2,3, figsize=(8,6), sharey=True)
        fig.suptitle(fnamein + "/" + cID) # This titles the figure    
        plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
        
        ax[0,0]= outputAnnualDurationCurve( ax[0,0], df2, cID, foutLog, varName="NormDmndAnnual", applyNormalization=False, addXLabel=False)
        ax[0,1] = outputMonthlyDurationCurve( ax[0,1], df2, cID, foutLog,  varName="NormDmndAnnual", applyNormalization=False, addXLabel=False)
        ax[0,2] = outputDailyDurationCurve( ax[0,2], df2, cID, foutLog,  varName="NormDmndAnnual",applyNormalization=False, addXLabel=False)
        
        ax[1,0]= outputAnnualDurationCurve( ax[1,0], df2, cID, foutLog, varName="Demand", applyNormalization=True, addTitle=False)
        ax[1,1] = outputMonthlyDurationCurve( ax[1,1], df2, cID, foutLog,  varName="Demand", applyNormalization=True, addTitle=False)
        ax[1,2] = outputDailyDurationCurve( ax[1,2], df2, cID, foutLog,  varName="Demand",applyNormalization=True, addTitle=False)
        
        # save to pdf
        pltPdf1.savefig() 
        plt.close() 
        
    # Closing plot files
    print("Closing plot files")
    pltPdf1.close()
    
    foutLog.write('\nNumber of customer IDs for which figures were generated: %d\n' % figN)
    print('Number of customer IDs for which figures were generated: ' + str( figN))

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

def PlotDurationCurves(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='plots/', fnameout='DurationCurves.pdf', 
                 dirlog='./', fnameLog='PlotDurationCurves.log',
                 byMonthFlag=False, 
                 withDailyProfiles=False):
    
    """ Create pdf with one page per customer showing annual duration curve, with or without monthly segments """
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "PlotDurationCurves", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog, varName='NormDmnd', usecols=[0,1,2])
    
    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs, considerCIDs)
    
    # open pdf for figures
    print('Opening plot file: %s' %(os.path.join(dirout, fnameout)))
    foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout)))
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    # iterate over UniqueIDs to create figure for each in the pdf
    figN = 0
    i = 1
    for cID in UniqueIDs: 
        print ('Processing %s (%d of %d)' %(cID, i, len(UniqueIDs)))
        i += 1
        df2 = df1[df1['CustomerID']==cID]
        if byMonthFlag:
            if withDailyProfiles:
                outputDurationCurveByMonthWithDailyProfiles(pltPdf1, df2, fnamein, cID, foutLog)
            else:
                outputDurationCurveByMonth(pltPdf1, df2, fnamein, cID, foutLog)
            figN += 1
        else:
            outputDurationCurve(pltPdf1, df2, fnamein, cID, foutLog)
            figN += 1
            
    # Closing plot files
    print("Closing plot files")
    pltPdf1.close()
    
    foutLog.write('\nNumber of customer IDs for which figures were generated: %d\n' % figN)
    print('Number of customer IDs for which figures were generated: ' + str(figN))

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

def PlotFamilyOfDurationCurves(dirin='./', fnamein='IntervalDataMultipleIDs.normalized.csv', 
                               ignoreCIDs='', considerCIDs='', highlightCIDs = '',
                               dirout='./', fnameout='DurationCurvesFamily.pdf', 
                               dirlog='./', fnameLog='PlotFamilyOfDurationCurves.log',
                               skipPlots = False,
                               skipLegend = True,
                               byMonthFlag = False):
    
    """ Create pdf with one page showing a plot with a duration curve for each customer """
    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, "PlotFamilyOfDurationCurves", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog, varName='NormDmnd', usecols=[0,1,2])
    
    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs, considerCIDs)
    df1a = df1[df1['CustomerID'].isin(UniqueIDs)]
    
    HighlightIDs, foutlog = readHighlightIDs(dirin, UniqueIDs, foutLog, highlightCIDs)

    # foutLog.write('Number of interval records after re-indexing: %d\n' %df1['NormDmnd'].size)
    foutLog.write('Time records start on: %s\n' %df1.index[0].strftime('%Y-%m-%d %H:%M'))
    foutLog.write('Time records end on: %s\n' %df1.index[-1].strftime('%Y-%m-%d %H:%M'))
    deltat = df1.index[-1]-df1.index[0]
    foutLog.write('Expected number of interval records: %d\n' %(deltat.total_seconds()/(60*15)+1))
    
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))
    if byMonthFlag:
        outputFamilyOfDurationCurvesByMonth(pltPdf1, df1a, foutlog, title=fnamein, skipLegend=skipLegend, hIDs=HighlightIDs)
    else:
        outputFamilyOfDurationCurves(pltPdf1, df1a, foutlog, title=fnamein, skipLegend=skipLegend, hIDs=HighlightIDs)

    # Closing plot files
    print("Closing plot files")
    pltPdf1.close()

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

# main 
if __name__ == "__main__":
    PlotDurationCurves(dirin='output/', fnamein='synthetic2.normalized.csv',
                       dirout='plots/', fnameout='DurationCurves.synthetic2.pdf',
                       dirlog='output/')

    PlotFamilyOfDurationCurves(dirin='output/', fnamein='synthetic2.normalized.csv',
                               dirout='plots/', fnameout='FamilyOfDurationCurves.synthetic2.pdf',
                               dirlog='output/')
