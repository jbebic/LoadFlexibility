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
from SupportFunctions import getData, logTime, createLog, findUniqueIDs

#%%  Version and copyright info to record on the log file
codeName = 'PlotDurationCurves.py'
codeVersion = '1.3'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Jovan Bebic & Irene Berry, GE Global Research\n"

#%% Function Definitions
def outputDurationCurve(pltPdf, df, fnamein, cid):
    """ creates duration curve for entire year for one customer"""
    
    fig, (ax0) = plt.subplots(nrows=1, ncols=1,
                              figsize=(8,6),
                              sharex=True)

    fig.suptitle(fnamein + "/" + cid) # This titles the figure

    ymin = 0.0
    ymax = np.ceil(df1['NormDmnd'].max()*2)/2   
    
    ax0.set_title('Normalized Load')
    ax0.set_ylim([ymin,ymax])
    ax0.set_ylabel('Load [pu]')

    ax0.set_xlim([0,8760*4])
    ax0.set_xticks(np.linspace(0, 8760*4, num=5).tolist())
    ax0.set_xticklabels(np.linspace(0, 8760, num=5, dtype=np.int16).tolist())
    ax0.set_xlabel('Hour')

    ax0.set_aspect('auto')
 
    df1 = df.sort_values('NormDmnd', ascending=False)
    ax0.step(np.arange(df1.shape[0]), (df1['NormDmnd']), 'C3', label='Normalized Demand [pu]')
    
    pltPdf.savefig() # Saves fig to pdf
    plt.close() # Closes fig to clean up memory
        
    return

# individual ID: create duration curve for entire year, one month after another "
def outputDurationCurveByMonth(pltPdf, df, fnamein, cid):
    """ creates duration curve for entire year for one customer, showing monthly segments """
    
    fig, (ax0) = plt.subplots(nrows=1, ncols=1,
                              figsize=(8,6),
                              sharex=True)

    fig.suptitle(fnamein + "/" + cid)

    ymin = 0.0
    ymax = np.ceil(df1['NormDmnd'].max()*2)/2    
    
    df = df.assign(month=pd.Series(np.asarray( df.index.month ), index=df.index))
    df = df.assign(monthInverse=pd.Series(12 - np.asarray( df.index.month ), index=df.index))
    df1 = df.sort_values(['monthInverse', 'NormDmnd'], ascending=False)
    months = np.asarray(df['month'])
    tickindex = [ np.asarray(np.where(months==i))[0][0] for i in range(1,13,1)]
    monthsList = [ date(2016, i,1).strftime('%b') for i in range(1,13,1)]

    ax0.set_title('Normalized Load')
    ax0.set_ylim([ymin,ymax])
    ax0.set_ylabel('Load [pu]')
    ax0.set_xlim([0,8760*4])
    ax0.set_xticks(tickindex)
    ax0.set_xticklabels(monthsList)
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.set_aspect('auto')

    ax0.step(np.arange(df1.shape[0]), (df1['NormDmnd']),  label='Normalized Demand [pu]')
    
    pltPdf.savefig() 
    plt.close()    
    
    return

# family: create group of duration curves "
def outputFamilyOfDurationCurves(pltPdf, df, title, skipLegend):
    """ Creates one figure with an annual duration curve for each customer """
    
    fig, (ax0) = plt.subplots(nrows=1, ncols=1,
                              figsize=(8,6),
                              sharex=True)
    
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
 
    UniqueIDs = df['CustomerID'].unique()
    i = 1
    for cID in UniqueIDs:
        print ('Processing %s (%d of %d) ' %(cID, i, len(UniqueIDs)))
        i +=1
        try:
            df1 = df[df['CustomerID']==cID]
            df2 = df1.sort_values('NormDmnd', ascending=False)
            ax0.step(np.arange(df2.shape[0]), (df2['NormDmnd']), label=cID)
        except:
            print("*** Unable to create duration plot for %s " %cID)
    
    if skipLegend:
        legend = ax0.legend() # plt.legend()
        legend.remove()
    
    pltPdf.savefig() # Saves fig to pdf
    plt.close() # Closes fig to clean up memory
    return

def PlotDurationCurves(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='plots/', fnameout='DurationCurves.pdf', 
                 dirlog='./', fnameLog='PlotDurationCurves.log',
                 byMonthFlag = False):
    
    """ Create pdf with one page per customer showing annual duration curve, with or without monthly segments """
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog)
    
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
        try:
            if byMonthFlag:
                outputDurationCurveByMonth(pltPdf1, df2, fnamein, cID)
                figN += 1
            else:
                outputDurationCurve(pltPdf1, df2, fnamein, cID)
                figN += 1
        except:
            foutLog.write("\n*** Unable to create duration plot for %s " %cID )
            print("*** Unable to create duration plot for %s " %cID)
            
    # Closing plot files
    print("Closing plot files")
    pltPdf1.close()
    
    foutLog.write('\nNumber of customer IDs for which figures were generated: %d\n' % figN)
    print('Number of customer IDs for which figures were generated: ' + str( figN))

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

def PlotFamilyOfDurationCurves(dirin='./', fnamein='IntervalDataMultipleIDs.normalized.csv', ignoreCIDs='', considerCIDs='',
                               dirout='./', fnameout='DurationCurvesFamily.pdf', 
                               dirlog='./', fnameLog='PlotFamilyOfDurationCurves.log',
                               skipPlots = False,
                               skipLegend = True):
    
    """ Create pdf with one page showing a plot with a duration curve for each customer """
    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog)
    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs, considerCIDs)
    df1a = df1[df1['CustomerID'].isin(UniqueIDs)]

    # foutLog.write('Number of interval records after re-indexing: %d\n' %df1['NormDmnd'].size)
    foutLog.write('Time records start on: %s\n' %df1.index[0].strftime('%Y-%m-%d %H:%M'))
    foutLog.write('Time records end on: %s\n' %df1.index[-1].strftime('%Y-%m-%d %H:%M'))
    deltat = df1.index[-1]-df1.index[0]
    foutLog.write('Expected number of interval records: %d\n' %(deltat.total_seconds()/(60*15)+1))
    
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))
    outputFamilyOfDurationCurves(pltPdf1, df1a, fnamein, skipLegend)

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
