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

# %% Function definitions

# Time logging "
def logTime(foutLog, logMsg, tbase):
    codeTnow = datetime.now()
    foutLog.write('%s%s\n' %(logMsg, str(codeTnow)))
    codeTdelta = codeTnow - tbase
    foutLog.write('Time delta since start: %.3f seconds\n' %((codeTdelta.seconds+codeTdelta.microseconds/1.e6)))


# create log  "
def createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart): # Capture start time of code execution and open log file
    
    foutLog = open(os.path.join(dirlog, fnameLog), 'w')
    
    # Output header information to log file
    print('This is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('This is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))

    return foutLog

# load data and unique IDs "
def getData(dirin, fnamein, foutLog): # Capture start time of code execution and open log file    

    # Output information to log file
    print("Reading input file")
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))
    df1 = pd.read_csv(os.path.join(dirin,fnamein), header = 0, usecols = [1, 2, 0], names=['CustomerID', 'datetimestr', 'NormDmnd']) # add dtype conversions
    foutLog.write('Number of interval records read: %d\n' %df1['NormDmnd'].size)
    df1['datetime'] = pd.to_datetime(df1['datetimestr'], format='%Y-%m-%d %H:%M')
    df1.set_index(['datetime'], inplace=True)
    df1.drop(['datetimestr'], axis=1, inplace=True) # drop redundant column
    df1.sort_index(inplace=True) # sort on datetime
        
    # foutLog.write('Number of interval records after re-indexing: %d\n' %df1['NormDmnd'].size)
    foutLog.write('Time records start on: %s\n' %df1.index[0].strftime('%Y-%m-%d %H:%M'))
    foutLog.write('Time records end on: %s\n' %df1.index[-1].strftime('%Y-%m-%d %H:%M'))
    deltat = df1.index[-1]-df1.index[0]
    foutLog.write('Expected number of interval records: %.1f\n' %(deltat.total_seconds()/(60*15)+1))

    UniqueIDs = df1['CustomerID'].unique().tolist()

    return df1, UniqueIDs, foutLog

# Apply ignore and consider to uniqueID "
def findUniqueIDs(dirin, UniqueIDs, ignoreCIDs, considerCIDs, foutLog):

    foutLog.write('Number of customer IDs in the input file: %d\n' %len(UniqueIDs))
    ignoreIDs = []
    if ignoreCIDs != '':
        print('Reading: %s' %os.path.join(dirin,ignoreCIDs))
        foutLog.write('Reading: %s\n' %os.path.join(dirin,ignoreCIDs))
        df9 = pd.read_csv(os.path.join(dirin,ignoreCIDs), 
                          header = 0, 
                          usecols = [0], 
                          comment = '#',
                          names=['CustomerID'],
                          dtype={'CustomerID':np.str})

        ignoreIDs = df9['CustomerID'].tolist()

    if considerCIDs != '':
        print('Reading: %s' %os.path.join(dirin,considerCIDs))
        foutLog.write('Reading: %s\n' %os.path.join(dirin,considerCIDs))
        df9 = pd.read_csv(os.path.join(dirin,considerCIDs), 
                          header = 0, 
                          usecols = [0],
                          comment = '#',
                          names=['CustomerID'],
                          dtype={'CustomerID':np.str})
        considerIDs = df9['CustomerID'].tolist()
        considerIDs = list(set(considerIDs)-set(ignoreIDs))
        UniqueIDs = list(set(UniqueIDs).intersection(considerIDs))
    else:
        considerIDs = list(set(UniqueIDs)-set(ignoreIDs))
        UniqueIDs = list(set(UniqueIDs).intersection(considerIDs))

    foutLog.write('Number of customer IDs after consider/ignore: %d\n' %len(UniqueIDs))
    
    return UniqueIDs, foutLog


# individual ID: create duration curve for entire year "
def outputDurationCurve(pltPdf, df, fnamein, cid):
    
    fig, (ax0) = plt.subplots(nrows=1, ncols=1,
                              figsize=(8,6),
                              sharex=True)

    fig.suptitle(fnamein + "/" + cid) # This titles the figure

    ymin = 0.0
    ymax = df['NormDmnd'].max()
    
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
    
    fig, (ax0) = plt.subplots(nrows=1, ncols=1,
                              figsize=(8,6),
                              sharex=True)

    fig.suptitle(fnamein + "/" + cid)

    ymin = 0.0
    ymax = 2.0 # df['NormDmnd'].max()
    
    ax0.set_title('Normalized Load')
    ax0.set_ylim([ymin,ymax])
    ax0.set_ylabel('Load [pu]')
    ax0.set_xlim([0,8760*4])
    ax0.set_xticks(np.linspace(0, 8760*4, num=13).tolist())
    monthsList = [ date(2016, i,1).strftime('%b') for i in [1,2,3,4,5,6,7,8,9,10,11,12,1]]
    ax0.set_xticklabels(monthsList)
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.set_aspect('auto')

    df = df.assign(month=pd.Series(np.asarray( df.index.month ), index=df.index))
    df = df.assign(monthInverse=pd.Series(12 - np.asarray( df.index.month ), index=df.index))

    df1 = df.sort_values(['monthInverse', 'NormDmnd'], ascending=False)
    ax0.step(np.arange(df1.shape[0]), (df1['NormDmnd']),  label='Normalized Demand [pu]')
    
    pltPdf.savefig() 
    plt.close()    
    
    return

# family: create group of duration curves "
def outputFamilyOfDurationCurves(pltPdf, df, title, skipLegend):
    fig, (ax0) = plt.subplots(nrows=1, ncols=1,
                              figsize=(8,6),
                              sharex=True)
    fig.suptitle(title) # This titles the figure

    ymin = 0.0
    ymax = df['NormDmnd'].max()
    
    ax0.set_title('Normalized Load')
    ax0.set_ylim([ymin,ymax])
    ax0.set_ylabel('Load [pu]')

    ax0.set_xlim([0,8760*4])
    ax0.set_xticks(np.linspace(0, 8760*4, num=5).tolist())
    ax0.set_xticklabels(np.linspace(0, 8760, num=5, dtype=np.int16).tolist())
    ax0.set_xlabel('Hour')

    ax0.set_aspect('auto')
 
    UniqueIDs = df['CustomerID'].unique()

    for cID in UniqueIDs:
        df1 = df[df['CustomerID']==cID]
        df2 = df1.sort_values('NormDmnd', ascending=False)
        ax0.step(np.arange(df2.shape[0]), (df2['NormDmnd']), label=cID)
    
    if skipLegend:
        legend = ax0.legend() # plt.legend()
        legend.remove()
    
    pltPdf.savefig() # Saves fig to pdf
    plt.close() # Closes fig to clean up memory
    return

# plot duration curves - with or without monthly segments "
def PlotDurationCurves(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='plots/', fnameout='DurationCurves.pdf', 
                 dirlog='./', fnameLog='PlotDurationCurves.log',
                 byMonthFlag = False):

    # Version and copyright info to record on the log file
    codeName = 'PlotDurationCurves.py'
    codeVersion = '1.0'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog)
    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, ignoreCIDs, considerCIDs, foutLog)
    
    # open pdf for figures
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    # iterate over UniqueIDs to create figure for each in the pdf
    i = 1
    for cID in UniqueIDs: 
        print ('Processing %s (%d of %d)' %(cID, i, len(UniqueIDs)))
        i += 1
        df2 = df1[df1['CustomerID']==cID]
        if byMonthFlag:
            outputDurationCurveByMonth(pltPdf1, df2, fnamein, cID)
        else:
            outputDurationCurve(pltPdf1, df2, fnamein, cID)
            
    # Closing plot files
    print("Closing plot files")
    pltPdf1.close()

    # finish log with run time
    codeTfinish = datetime.now()
    logTime(foutLog, '\nRunFinished at: ', codeTfinish)
    
    return


# create family of duration curves "
def PlotFamilyOfDurationCurves(dirin='./', fnamein='IntervalDataMultipleIDs.normalized.csv', ignoreCIDs='', considerCIDs='',
                               dirout='./', fnameout='DurationCurvesFamily.pdf', 
                               dirlog='./', fnameLog='PlotFamilyOfDurationCurves.log',
                               skipPlots = False,
                               skipLegend = True):
    
    # Version and copyright info to record on the log file
    codeName = 'PlotFamilyOfDurationCurves.py'
    codeVersion = '1.0'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"


    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog)
    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, ignoreCIDs, considerCIDs, foutLog)

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
