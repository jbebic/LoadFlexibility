# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 09:39:16 2018

@author: 200018380
"""
#%% Importing all the necessary Python packages
import pandas as pd # multidimensional data analysis
import numpy as np # vectorized calculations
from datetime import datetime # time stamps
import os # operating system interface

#%% Function Definitions

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
    print('\nThis is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('\nThis is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))

    return foutLog

# load data and unique IDs "
def getData(dirin, fnamein, foutLog, varName='NormDmnd'): # Capture start time of code execution and open log file    

    # Output information to log file
    print("Reading input file")
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))
    df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                      header = 0, 
                      usecols = [1, 2, 0], 
                      names=['CustomerID', 'datetimestr', varName]) # add dtype conversions
    foutLog.write('Number of interval records read: %d\n' %df1[varName].size)
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
def findUniqueIDs(dirin, UniqueIDs,foutLog, ignoreCIDs='', considerCIDs=''):

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
        ignoreIDs = [x.replace(" ", "") for x in ignoreIDs]

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
        considerIDs = [x.replace(" ", "") for x in considerIDs]
        
        considerIDs = list(set(considerIDs)-set(ignoreIDs))
        UniqueIDs = list(set(UniqueIDs).intersection(considerIDs))
    else:
        considerIDs = list(set(UniqueIDs)-set(ignoreIDs))
        UniqueIDs = list(set(UniqueIDs).intersection(considerIDs))

    foutLog.write('Number of customer IDs after consider/ignore: %d\n' %len(UniqueIDs))
    
    return UniqueIDs, foutLog


def reduceDataFile(dirin='./', fnamein='IntervalData.csv', ignoreCIDs='', considerCIDs='',
                   dirout='./', fnameout='IntervalData.normalized.csv', 
                   dirlog='./', fnameLog='reduceDataFile.log'):
    
    return

