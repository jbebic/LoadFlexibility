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

#%%  Version and copyright info to record on the log file
codeName = 'SupportFunctions.py'
codeVersion = '1.0'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Jovan Bebic & Irene Berry, GE Global Research\n"

#%% Function Definitions

def logTime(foutLog, logMsg, tbase):
    """ writes final time & delta since start to log file """
    codeTnow = datetime.now()
    foutLog.write('%s%s\n' %(logMsg, str(codeTnow)))
    codeTdelta = codeTnow - tbase
    foutLog.write('Time delta since start: %.3f seconds \n' %((codeTdelta.seconds+codeTdelta.microseconds/1.e6)))
    foutLog.write('Time delta since start: %.3f hours \n' %((codeTdelta.seconds+codeTdelta.microseconds/1.e6)/3600))
    
def createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart): # Capture start time of code execution and open log file
    """ creates log file and writes code version information """
    
    foutLog = open(os.path.join(dirlog, fnameLog), 'w')
    
    # Output header information to log file
    print('\nThis is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('\nThis is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))

    return foutLog

def getData(dirin, fnamein, foutLog, varName='NormDmnd', usecols=[1,2,0], datetimeIndex=True): # Capture start time of code execution and open log file    
    """ Retrieves data from specified folder and csv file, where format is [CustomerID, datetime, varName] """

    if isinstance(varName, list):
        columnNames = ['CustomerID', 'datetimestr']
        for temp in varName:
            columnNames.append(temp)
    else:
        columnNames = ['CustomerID', 'datetimestr', varName]
        
    # Output information to log file
    print("Reading input file " + fnamein)
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))
    df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                      header = 0, 
                      usecols = usecols, 
                      names=columnNames) # add dtype conversions
    
    foutLog.write('Number of interval records read: %d\n' %df1['CustomerID'].size)
    df1['datetime'] = pd.to_datetime(df1['datetimestr'], format='%Y-%m-%d %H:%M')
    df1.drop(['datetimestr'], axis=1, inplace=True) # drop redundant column
    
    # if selected, set the datetime as the index and sort
    if datetimeIndex:
        df1.set_index(['datetime'], inplace=True)
        df1.sort_index(inplace=True) # sort on datetime
        
        # foutLog.write('Number of interval records after re-indexing: %d\n' %df1['NormDmnd'].size)
        foutLog.write('Time records start on: %s\n' %df1.index[0].strftime('%Y-%m-%d %H:%M'))
        foutLog.write('Time records end on: %s\n' %df1.index[-1].strftime('%Y-%m-%d %H:%M'))
        deltat = df1.index[-1]-df1.index[0]
        foutLog.write('Expected number of interval records: %.1f\n' %(deltat.total_seconds()/(60*15)+1))

    UniqueIDs = df1['CustomerID'].unique().tolist()

    return df1, UniqueIDs, foutLog


def findUniqueIDs(dirin, UniqueIDs,foutLog, ignoreCIDs='', considerCIDs=''):
    """ applys considerCIDs and ignoreCIDs to calculate list of UniqueIDS in the data"""

    if considerCIDs!='' or ignoreCIDs!='':

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
    print('Number of customer IDs after consider/ignore: ' + str(len(UniqueIDs)))
    
    return UniqueIDs, foutLog


def assignDayType(df):
    """ Adds Season (w or s) & DayType (h, o, we, or wd) to dataframe"""
    
    df['Season'] = 'w'
    df.loc[(df.index.month > 5) & (df.index.month < 10), 'Season'] = 's'
    
    # Holidays: 
    #   Jan 1 (New Year's Day)
    #   3rd Monday in February (Presidents' Day)
    #   July 4 (Independence Day)
    #   1st Monday in September (Labor Day)
    #   Nov 11 (Veterans Day)
    #   4th Thursday in November (Thanksgiving Day)
    #   Dec 25 (Christmas)
    # When a holidays falls on Sunday, the following Monday is recognized as an off-peak period)
        
    df['DayType'] = 'wd' # weekday
    df.loc[df.index.dayofweek >= 5, 'DayType'] = 'we' # weekend
    # New Year's Day
    if (df[(df.index.month == 1) & (df.index.day == 1)].index[0].dayofweek == 6):
        df.loc[(df.index.month == 1) & (df.index.day == 1), 'DayType'] = 'h'
        df.loc[(df.index.month == 1) & (df.index.day == 2), 'DayType'] = 'o'
    else:
        df.loc[(df.index.month == 1) & (df.index.day == 1), 'DayType'] = 'h'

    # Presidents' Day: 3rd Monday in February
    df.loc[(df.index.month == 2) & (df.index.dayofweek == 0) &
           (15 <= df.index.day) & (df.index.day <= 21), 'DayType'] = 'h'
    
    # Independence Day    
    if (df[(df.index.month == 7) & (df.index.day == 4)].index[0].dayofweek == 6):
        df.loc[(df.index.month == 7) & (df.index.day == 4), 'DayType'] = 'h'
        df.loc[(df.index.month == 7) & (df.index.day == 5), 'DayType'] = 'o'
    else:
        df.loc[(df.index.month == 7) & (df.index.day == 4), 'DayType'] = 'h'
    
    # Labor Day: 1st Monday in September
    df.loc[(df.index.month == 9) & (df.index.dayofweek == 0) & 
           (1 <= df.index.day) & (df.index.day <= 7), 'DayType'] = 'h'

    # Veterans Day
    if (df[(df.index.month == 11) & (df.index.day == 11)].index[0].dayofweek == 6):
        df.loc[(df.index.month == 11) & (df.index.day == 11), 'DayType'] = 'h'
        df.loc[(df.index.month == 11) & (df.index.day == 12), 'DayType'] = 'o'
    else:
        df.loc[(df.index.month == 11) & (df.index.day == 11), 'DayType'] = 'h'

    # Thanksgiving Day: 4th Thursday in November
    df.loc[(df.index.month == 11) & (df.index.dayofweek == 3) &
           (22 <= df.index.day) & (df.index.day <= 28), 'DayType'] = 'h'

    # Christmas Day
    if (df[(df.index.month == 12) & (df.index.day == 25)].index[0].dayofweek == 6):
        df.loc[(df.index.month == 12) & (df.index.day == 25), 'DayType'] = 'h'
        df.loc[(df.index.month == 12) & (df.index.day == 26), 'DayType'] = 'o'
    else:
        df.loc[(df.index.month == 12) & (df.index.day == 25), 'DayType'] = 'h'    
    
    return df


def reduceDataFile(dirin='./', fnamein='IntervalData.csv', ignoreCIDs='', considerCIDs='',
                   dirout='./', fnameout='IntervalData.normalized.csv', 
                   dirlog='./', fnameLog='reduceDataFile.log'):
    
    return

