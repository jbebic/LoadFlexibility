# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 08:21:32 2018

@author: jbebic

Utiliy functions to cope with data irregularities
"""

#%% Importing all the necessary Python packages
import pandas as pd # multidimensional data analysis
import numpy as np # vectorized calculations

from datetime import datetime # time stamps
from pytz import timezone
import os # operating system interface

import string
import random

# %% Function definitions
# Time logging
def logTime(foutLog, logMsg, tbase):
    codeTnow = datetime.now()
    foutLog.write('%s%s\n' %(logMsg, str(codeTnow)))
    codeTdelta = codeTnow - tbase
    foutLog.write('Time delta since start: %.3f seconds\n' %((codeTdelta.seconds+codeTdelta.microseconds/1.e6)))

def AnonymizeCIDs(dirin='./', fnamein='IntervalData.SCE.csv', 
           dirout='./', fnameout='IntervalData.csv', fnameKeys='IntervalData.lookup.csv',
           dirlog='./', fnameLog='AnonymizeCIDs.log',
           IDlen=6):
    #%% Version and copyright info to record on the log file
    codeName = 'AnonymizeCIDs.py'
    codeVersion = '1.0'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = open(os.path.join(dirlog, fnameLog), 'w')
    foutKeys = open(os.path.join(dirout, fnameKeys), 'w')

    #%% Output header information to log file
    print('\nThis is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('This is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))

    #%% Output file information to log file
    print('Reading: %s' %os.path.join(dirin,fnamein))
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))

    df1 = pd.read_csv(os.path.join(dirin,fnamein))
    foutLog.write('Read %d records\n' %df1.shape[0])
    df1['aCID'] = ''

    #%% Processing CIDs
    print('Processing customers')
    uniqueCIDs = df1['CustomerID'].unique()
    print('Number of unique customer IDs in the file: %d' %uniqueCIDs.size)
    foutLog.write('Number of unique customer IDs in the file: %d\n' %uniqueCIDs.size)
    foutKeys.write('CustomerID, AnonymizedID\n')
    aids = [] # an empty list of anonymized customer ids
    i = 1 # sequential CID number being processed
    for cid in uniqueCIDs:
        print('Anonymizing: %s (%d of %d)' %(str(cid), i, uniqueCIDs.size))
        foutLog.write('Anonymizing: %s\n' %(str(cid)))
        i += 1
        while True:
            aid = ''.join(random.choices(string.ascii_uppercase, k=1)) + \
                  ''.join(random.choices(string.ascii_uppercase + string.digits, k=IDlen-1))
            if not(aid in aids): # guarding agains assigning a duplicate key
                aids.append(aid)
                df1.loc[df1['CustomerID']==cid, 'aCID'] = aid
                foutKeys.write('%s, %s\n' %(str(cid), aid))
                break # breaks a while loop
    
    df1.drop(['CustomerID'], axis=1, inplace=True)
    df1.rename(columns={'aCID':'CustomerID'}, inplace=True)
    
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df1.to_csv(os.path.join(dirout,fnameout), index=False, float_format='%.1f') # this is a multiindexed dataframe, so only the data column is written

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    foutLog.close()
    foutKeys.close()
    print('Finished\n')

    return

def ExportLoadFiles(dirin='./', fnamein='IntervalData.csv', explist='ExportCIDs.csv',
           dirout='./', # fnameout derived from customer IDs
           dirlog='./', fnameLog='ExportLoadFiles.log',):
    #%% Version and copyright info to record on the log file
    codeName = 'ExportLoadFiles.py'
    codeVersion = '1.0'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = open(os.path.join(dirlog, fnameLog), 'w')

    #%% Output header information to log file
    print('\nThis is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('This is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))
    # Output file information to log file

    print('Reading: %s' %os.path.join(dirin,explist))
    foutLog.write('Reading: %s\n' %os.path.join(dirin,explist))
    df9 = pd.read_csv(os.path.join(dirin,explist), 
                      header = 0, 
                      usecols = [0], 
                      names=['CustomerID'],
                      dtype={'CustomerID':np.str})
    print('Total number of CIDs to export: %d' %df9['CustomerID'].size)
    foutLog.write('Total number of interval records read: %d\n' %df9['CustomerID'].size)
    
    # Output file information to log file
    print('Reading: %s' %os.path.join(dirin,fnamein))
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))
    df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                      header = 0, 
                      usecols = [0, 1, 2], 
                      names=['datetimestr', 'Demand', 'CustomerID'],
                      dtype={'datetimestr':np.str, 'Demand':np.float64, 'CustomerID':np.str})

    print('Total number of interval records read: %d' %df1['Demand'].size)
    foutLog.write('Total number of interval records read: %d\n' %df1['Demand'].size)
    
    export_list = df9['CustomerID'].tolist()
    for cid in export_list:
        # Check if the cid exists in the input file and export if yes
        if cid in df1['CustomerID'].unique().tolist():
            df2 = df1[df1['CustomerID'] == cid]
            fnameout = str(cid)+'.csv'
            print('Writing: %s' %os.path.join(dirout,fnameout))
            foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
            df2.to_csv(os.path.join(dirout,fnameout), float_format='%.1f', index=False) 
        else: 
            print('%s not found in input file, skipping' %str(cid))
            foutLog.write('%s not found in input file, skipping\n' %str(cid))

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    foutLog.close()
    print('Finished\n')

    return

def FixDST(dirin='./', fnamein='IntervalDataDST.csv', 
           dirout='./', fnameout='IntervalData.csv', 
           dirlog='./', fnameLog='FixDST.log',
           tzinput = 'America/Los_Angeles',
           OutputFormat = 'SCE',
           VectorProcessTimeRecords = True):
    #%% Version and copyright info to record on the log file
    codeName = 'FixDST.py'
    codeVersion = '1.0'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = open(os.path.join(dirlog, fnameLog), 'w')

#%% Prep DST transition times dataframe
    tz = timezone(tzinput)
    tzTransTimes = tz._utc_transition_times
    tzTransInfo = tz._transition_info
    df2 = pd.DataFrame.from_dict({'DSTbeginsUTC':tzTransTimes[11:-2:2], 'DSTendsUTC':tzTransTimes[12:-1:2],
                                  'tzinfob'     :tzTransInfo[11:-2:2],  'tzinfoe'   :tzTransInfo[12:-1:2]})
    df2['year']=pd.DatetimeIndex(df2['DSTbeginsUTC']).year.values
    df2.set_index('year', inplace=True)

    
    #%% Output header information to log file
    print('\nThis is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('This is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))

    # Output file information to log file
    print('Reading: %s' %os.path.join(dirin,fnamein))
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))

    df1 = pd.read_csv(os.path.join(dirin,fnamein))
    foutLog.write('Read %d records\n' %df1.shape[0])
    foutLog.write('Columns are: %s\n' %' '.join(str(x) for x in df1.columns.tolist()))

    if VectorProcessTimeRecords:
        print('Vector processing time records, this takes a while...')
        foutLog.write('Vector processing time records\n')
        dstr = df1['datetimestr'].str.split(':').str[0]
        # print(dstr.head())
        hstr = df1['datetimestr'].str.split(':').str[1]
        # print(tstr.head())
        mstr = df1['datetimestr'].str.split(':').str[2]
        # sstr = df1['datetimestr'].str.split(':').str[3]
        temp = dstr + ' ' + hstr + ':' + mstr
        df1['datetime'] = pd.to_datetime(temp, format='%d%b%Y %H:%M')
        logTime(foutLog, '\nFinished processing time records: ', codeTstart)

    print('Processing customers')
    uniqueCIDs = df1['CustomerID'].unique()
    print('Number of unique customer IDs in the file: %d' %uniqueCIDs.size)
    foutLog.write('Number of unique customer IDs in the file: %d\n' %uniqueCIDs.size)
    i = 1
    for cid in uniqueCIDs:
        print('Processing time records for: %s (%d of %d)' %(str(cid), i, uniqueCIDs.size))
        foutLog.write('Processing time records for: %s\n' %(str(cid)))
        i += 1
        
        if not VectorProcessTimeRecords:
            dstr = df1[df1['CustomerID'] == cid]['datetimestr'].str.split(':').str[0]
            # print(dstr.head())
            hstr = df1[df1['CustomerID'] == cid]['datetimestr'].str.split(':').str[1]
            # print(tstr.head())
            mstr = df1[df1['CustomerID'] == cid]['datetimestr'].str.split(':').str[2]
            # sstr = df1['datetimestr'].str.split(':').str[3]
            temp = dstr + ' ' + hstr + ':' + mstr
            df1.loc[(df1['CustomerID'] == cid), 'datetime'] = pd.to_datetime(temp, format='%d%b%Y %H:%M')

        if df1[df1['CustomerID'] == cid]['datetime'].dt.strftime('%Y').unique().size > 1:
            print('  Time records contain more than one year of data - aborting\n')
            foutLog.write('\n  Time records contain more than one year of data - aborting\n')
            logTime(foutLog, '\nRunFinished at: ', codeTstart)
            return
        
        # Find the transtion times for the year in df1
        year = df1[df1['CustomerID'] == cid]['datetime'].iloc[0].year
        dst1 = df2['DSTbeginsUTC'][year]+df2['tzinfob'][year][0]
        dst2 = df2['DSTendsUTC'][year]  +df2['tzinfoe'][year][0]
        
        dst1a = dst1 - pd.Timedelta(hours=1)
        # dst2a = dst2 + pd.Timedelta(hours=1)
        dst2b = dst2 + pd.Timedelta(hours=2)
        if df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst1a)].empty:
            # There is a blank record at the start of DST, shift the records to the left
            df1.loc[(df1['CustomerID'] == cid) & (df1['datetime'] > dst1a) & (df1['datetime'] < dst2b), 'datetime'] = df1[(df1['CustomerID'] == cid) & (df1['datetime'] > dst1a) & (df1['datetime'] < dst2b)]['datetime'] - pd.Timedelta(hours=1)
            td = pd.Timedelta('0 min') # pd.Timedelta('15 min'), pd.Timedelta('30 min'), pd.Timedelta('45 min')
            if (df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].size > 1):
                ix = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)].index[0]
                temp = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].iloc[0] + pd.Timedelta(hours=1)
                df1.at[ix, 'datetime'] = temp
            td = pd.Timedelta('15 min') # pd.Timedelta('30 min'), pd.Timedelta('45 min')
            if (df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].size > 1):
                ix = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)].index[0]
                temp = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].iloc[0] + pd.Timedelta(hours=1)
                df1.at[ix, 'datetime'] = temp
            td = pd.Timedelta('30 min') # , pd.Timedelta('45 min')
            if (df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].size > 1):
                ix = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)].index[0]
                temp = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].iloc[0] + pd.Timedelta(hours=1)
                df1.at[ix, 'datetime'] = temp
            td = pd.Timedelta('45 min')
            if (df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].size > 1):
                ix = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)].index[0]
                temp = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].iloc[0] + pd.Timedelta(hours=1)
                df1.at[ix, 'datetime'] = temp
            
            # df1.at[:, 'datetimestr'] = df1['datetime'].dt.strftime('%d%b%Y:%H:%M').upper()
    df1['datetimestr'] = df1['datetime'].dt.strftime('%d%b%Y:%H:%M').str.upper()
            
    if OutputFormat == 'SCE':
        print('\nWriting: %s in %s format' %(os.path.join(dirout,fnameout), OutputFormat))
        foutLog.write('Writing: %s in %s format\n' %(os.path.join(dirout,fnameout), OutputFormat))
        df1.sort_values(by=['CustomerID', 'datetimestr'], inplace = True)
        df1.to_csv(os.path.join(dirout,fnameout), index=False, float_format='%.1f', columns=['datetimestr', 'Demand', 'CustomerID'])
    elif OutputFormat == 'ISO':
        print('\nWriting: %s in %s format' %(os.path.join(dirout,fnameout), OutputFormat))
        foutLog.write('Writing: %s in %s format\n' %(os.path.join(dirout,fnameout), OutputFormat))
        df1.set_index(['CustomerID', 'datetime'], inplace=True)
        df1.sort_index(inplace=True) # need to sort on datetime **TODO: Check if this is robust
        # df1.drop(['datetimestr'], axis=1, inplace=True) # drop redundant column
        df1.to_csv(os.path.join(dirout,fnameout), index=True, float_format='%.1f', date_format='%Y-%m-%d %H:%M', columns=['Demand'])
    else:
        print('\nUnrecognized output format, writing in %s in SCE format' %os.path.join(dirout,fnameout))
        foutLog.write('\nUnrecognized output format, writing in %s in SCE format\n' %os.path.join(dirout,fnameout))
        df1.sort_values(by=['CustomerID', 'datetimestr'], inplace = True)
        df1.to_csv(os.path.join(dirout,fnameout), index=False, float_format='%.1f', columns=['datetimestr', 'Demand', 'CustomerID'])
        
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    foutLog.close()
    print('Finished\n')
    
def ConvertFeather(dirin='./', fnamein='IntervalData.feather', 
                   dirout='./', fnameout='IntervalData.csv', 
                   dirlog='./', fnameLog='ConvertFeather.log',
                   renameDict={},
                   writeOutput = False):
    #%% Version and copyright info to record on the log file
    codeName = 'ConvertFeather.py'
    codeVersion = '1.0'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = open(os.path.join(dirlog, fnameLog), 'w')
    
    #%% Output header information to log file
    print('\nThis is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('This is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))

    # Output file information to log file
    print('Reading: %s' %os.path.join(dirin,fnamein))
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))

    df1 = pd.read_feather(os.path.join(dirin,fnamein))
    foutLog.write('Read %d records\n' %df1.shape[0])
    foutLog.write('Columns are: %s\n' %' '.join(str(x) for x in df1.columns.tolist()))
    if len(renameDict) > 0:
        df1.rename(columns=renameDict, inplace=True)
    
    # Add CustomerID
    if not('CustomerID' in df1.columns): df1['CustomerID'] = '1515Grocer'

    # revise the date format to 
    df1['datetimestr']=df1['datetimestr'].dt.strftime('%d%b%Y:%H:%M').str.upper()
    
    df1.sort_values(by=['CustomerID', 'datetimestr'], inplace=True)
    
    if writeOutput:
        print('\nWriting: %s' %os.path.join(dirout,fnameout))
        foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
        df1.to_csv(os.path.join(dirout,fnameout), index=False, float_format='%.1f', columns=['datetimestr', 'Demand', 'CustomerID'])

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    foutLog.close()
    print('Finished\n')

    return

def SplitToGroups(ngroups, 
                  dirin='/testdata', fnamein='synthetic20.normalized.csv', ignoreCIDs='', considerCIDs='',
                  dirout='/testdata', foutbase='synthetic20', # 
                  dirlog='/testdata', fnameLog='SplitToGroups.log'):
    
    #%% Version and copyright info to record on the log file
    codeName = 'SplitToGroups.py'
    codeVersion = '1.0'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = open(os.path.join(dirlog, fnameLog), 'w')
    
    #%% Output header information to log file
    print('This is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('This is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))
    
    # Output information to log file
    print("Reading input file")
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))
    df1 = pd.read_csv(os.path.join(dirin,fnamein), header = 0, usecols = [1, 2, 0], names=['CustomerID', 'datetimestr', 'NormDmnd']) # add dtype conversions
    foutLog.write('Number of interval records read: %d\n' %df1['NormDmnd'].size)

    UniqueIDs = df1['CustomerID'].unique().tolist()
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
    foutLog.write('Number of customer IDs after consider/ignore: %d\n' %len(UniqueIDs))

    print("Writing groups...")
    gid = 1
    nidspg = int(len(UniqueIDs)/ngroups)+1 # number of IDs per group
    i1 = 0
    i2 = i1 + nidspg
    while i1<i2:
        cIDgroup = UniqueIDs[i1:i2]
        i1 = i2
        i2 = i1+nidspg
        i2 = min(i2, len(UniqueIDs))
        # print(cIDgroup)
        df1 = pd.DataFrame(cIDgroup, columns=['CustomerID'])
        df1.to_csv(os.path.join(dirout,foutbase+'.g'+str(gid)+'c.csv'), index=False)
        gid += 1

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

def AssignRatePeriods_TOUGS3B(df):
    # https://www.sce.com/NR/sc3/tm2/pdf/CE281.pdf
    # Summer: [June 1 00:00AM, Sep 30, 23:45]
    # Winter: complement
    df['Season'] = 'w'
    df.loc[(df['datetime'].dt.month > 5) & (df['datetime'].dt.month < 10), 'Season'] = 's'

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
    df.loc[df['datetime'].dt.dayofweek > 5, 'DayType'] = 'we' # weekend
    # New Year's Day
    if (df[(df['datetime'].dt.month == 1) & (df['datetime'].dt.day == 1)]['datetime'].dt.values.iloc[0].dayofweek == 6):
        df.loc[(df['datetime'].dt.month == 1) & (df['datetime'].dt.day == 1), 'DayType'] = 'h'
        df.loc[(df['datetime'].dt.month == 1) & (df['datetime'].dt.day == 2), 'DayType'] = 'o'
    else:
        df.loc[(df['datetime'].dt.month == 1) & (df['datetime'].dt.day == 1), 'DayType'] = 'h'

    # Presidents' Day: 3rd Monday in February
    df.loc[(df['datetime'].dt.month == 2) & (df['datetime'].dt.dayofweek == 0) &
           (15 <= df['datetime'].dt.day) & (df['datetime'].dt.day <= 21), 'DayType'] = 'h'
    
    # Independence Day    
    if (df[(df['datetime'].dt.month == 7) & (df['datetime'].dt.day == 4)]['datetime'].dt.values.iloc[0].dayofweek == 6):
        df.loc[(df['datetime'].dt.month == 7) & (df['datetime'].dt.day == 4), 'DayType'] = 'h'
        df.loc[(df['datetime'].dt.month == 7) & (df['datetime'].dt.day == 5), 'DayType'] = 'o'
    else:
        df.loc[(df['datetime'].dt.month == 7) & (df['datetime'].dt.day == 4), 'DayType'] = 'h'
    
    # Labor Day: 1st Monday in September
    df.loc[(df['datetime'].dt.month == 9) & (df['datetime'].dt.dayofweek == 0) & 
           (1 <= df['datetime'].dt.day) & (df['datetime'].dt.day <= 7), 'DayType'] = 'h'

    # Veterans Day
    if (df[(df['datetime'].dt.month == 11) & (df['datetime'].dt.day == 11)]['datetime'].dt.values.iloc[0].dayofweek == 6):
        df.loc[(df['datetime'].dt.month == 11) & (df['datetime'].dt.day == 11), 'DayType'] = 'h'
        df.loc[(df['datetime'].dt.month == 11) & (df['datetime'].dt.day == 12), 'DayType'] = 'o'
    else:
        df.loc[(df['datetime'].dt.month == 11) & (df['datetime'].dt.day == 11), 'DayType'] = 'h'

    # Thanksgiving Day: 4th Thursday in November
    df.loc[(df['datetime'].dt.month == 11) & (df['datetime'].dt.dayofweek == 3) &
           (22 <= df['datetime'].dt.day) & (df['datetime'].dt.day <= 28), 'DayType'] = 'h'

    # Christmas Day
    if (df[(df['datetime'].dt.month == 12) & (df['datetime'].dt.day == 25)]['datetime'].dt.values.iloc[0].dayofweek == 6):
        df.loc[(df['datetime'].dt.month == 12) & (df['datetime'].dt.day == 25), 'DayType'] = 'h'
        df.loc[(df['datetime'].dt.month == 12) & (df['datetime'].dt.day == 26), 'DayType'] = 'o'
    else:
        df.loc[(df['datetime'].dt.month == 12) & (df['datetime'].dt.day == 25), 'DayType'] = 'h'

    # Weekdays and non-holidays
    # Summer on peak  = 1 (12pm to 6pm)
    #        mid peak = 2 (8am-12pm, 6pm - 11pm)
    #        off peak = 3 (all other hours)
    #             cpp = 4 (2pm-6pm) # provision only, not used in TOU GS3 Option B
    # Winter mid peak = 5 (8am - 9pm)
    #        off peak = 6 (all other hours)
    df.loc[df['Season'] == 's', 'RatePeriod'] = 3
    df.loc[(12 <= df['datetime'].dt.hour) & (df['datetime'].dt.hour < 18) & (df['Season'] == 's'), 'RatePeriod'] = 1
    df.loc[( 8 <= df['datetime'].dt.hour) & (df['datetime'].dt.hour < 12) & (df['Season'] == 's'), 'RatePeriod'] = 2
    df.loc[(18 <= df['datetime'].dt.hour) & (df['datetime'].dt.hour < 23) & (df['Season'] == 's'), 'RatePeriod'] = 2
    df.loc[df['Season'] == 'w', 'RatePeriod'] = 6
    df.loc[( 8 <= df['datetime'].dt.hour) & (df['datetime'].dt.hour < 21) & (df['Season'] == 'w'), 'RatePeriod'] = 5
    return df

def CalculateBilling(dirin='./', fnamein='IntervalData.csv', ignoreCIDs='', considerCIDs='', ratein='TOU-GS3-B.csv',
                     dirout='./', fnameout='IntervalCharges.csv',
                     dirlog='./', fnameLog='CalculateBilling.log',):
    #%% Version and copyright info to record on the log file
    codeName = 'ReviewLoads.py'
    codeVersion = '1.0'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = open(os.path.join(dirlog, fnameLog), 'w')
    
    #%% Output header information to log file
    print('This is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('This is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))

    # Output file information to log file
    print('Reading: %s' %os.path.join(dirin,fnamein))
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))
    df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                      header = 0, 
                      usecols = [0, 1, 2], 
                      names=['CustomerID', 'datetimestr', 'Demand'],
                      dtype={'CustomerID':np.str, 'datetimestr':np.str, 'Demand':np.float})
    
    df1['datetime'] = pd.to_datetime(df1['datetimestr'], format='%Y-%m-%d %H:%M')
        
    # df1.set_index(['CustomerID', 'datetime'], inplace=True)
    # df1.sort_index(inplace=True) # need to sort on datetime **TODO: Check if this is robust

    df1.drop(['datetimestr'], axis=1, inplace=True) # drop redundant column

    print('Assigning rate periods')
    df1['Season'] = ''
    df1['DayType'] = ''
    df1['RatePeriod'] = np.nan
    df1 = AssignRatePeriods_TOUGS3B(df1)
    df2 = pd.read_csv(os.path.join(dirin,ratein),
                      header = 0,
                      usecols = [0, 1, 2],
                      names = ['RatePeriod', 'EnergyCost', 'DemandCost'],
                      dtype = {'RatePeriod':np.int8, 'EnergyCost':np.float, 'DemandCost':np.float})
    df3 = pd.merge(df1, df2, how='left', on=['RatePeriod'])
    df3['EnergyCharge'] = 0
    df3['DemandCharge'] = 0
    df3['TotalCharge'] = 0

    print('Processing...')
    UniqueIDs = df1['CustomerID'].unique().tolist()
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
    
    df4 = pd.DataFrame(index=np.arange(0, 31*24, 0.25), columns=np.arange(0,3))
    i = 1
    for cid in UniqueIDs:
        print ('%s (%d of %d)' %(cid, i, len(UniqueIDs)))
        i += 1
        # Calculate energy charge for every interval
        df3.loc[df3['CustomerID'] == cid, 'EnergyCharge'] = df3[df3['CustomerID'] == cid]['Demand'] * df3[df3['CustomerID'] == cid]['EnergyCost']
        # Calculate demand charges, based on the peak Demand in the relevant RatePeriod
        dix = df3.columns.get_loc('DemandCharge')
        for mNo in (np.arange(0, 12, 1)+1):
            df4.iloc[:] = np.nan # resetting all values to nan to prevent backfilling from other months
            df4 = df3[(df3['CustomerID']==cid) & (df3['datetime'].dt.month == mNo)][['datetime','RatePeriod','Demand']]
            if df4[df4['RatePeriod'] == 1].shape[0] > 0:
                idxmax = df4[df4['RatePeriod'] == 1]['Demand'].idxmax()
                df3.iloc[idxmax, dix] = df3.iloc[idxmax]['Demand'] * df3.iloc[idxmax]['DemandCost'] * 4.
            if df4[df4['RatePeriod'] == 2].shape[0] > 0:
                idxmax = df4[df4['RatePeriod'] == 2]['Demand'].idxmax()
                df3.iloc[idxmax, dix] = df3.iloc[idxmax]['Demand'] * df3.iloc[idxmax]['DemandCost'] * 4.
            # Winter demand charges are zero in TOU-GS-3-B rate, so the following 6 lines of code are unnecessary for TOU-GS-3-B
            if df4[df4['RatePeriod'] == 4].shape[0] > 0:
                idxmax = df4[df4['RatePeriod'] == 4]['Demand'].idxmax()
                df3.iloc[idxmax, dix] = df3.iloc[idxmax]['Demand'] * df3.iloc[idxmax]['DemandCost'] * 4.
            if df4[df4['RatePeriod'] == 5].shape[0] > 0:
                idxmax = df4[df4['RatePeriod'] == 5]['Demand'].idxmax()
                df3.iloc[idxmax, dix] = df3.iloc[idxmax]['Demand'] * df3.iloc[idxmax]['DemandCost'] * 4.
        
        # Sum the energy and demand charges into total cost for each interval
        df3.loc[df3['CustomerID'] == cid, 'TotalCharge'] = df3[df3['CustomerID'] == cid]['EnergyCharge'] + df3[df3['CustomerID'] == cid]['DemandCharge']
               
    # Write data file with charges for each time period         
    print('Writing: %s' %os.path.join(dirout,fnameout))
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df3.to_csv(os.path.join(dirout,fnameout), 
               index=False, 
               float_format='%.2f',
               date_format='%Y-%m-%d %H:%M',
               columns = ['CustomerID', 'datetime', 'Demand', 'EnergyCharge', 'DemandCharge', 'TotalCharge']) 


    # Write Summary Data file with total charges for each month
    df3 = df3.assign(month=pd.Series(np.asarray( df3['datetime'].dt.month ), index=df3.index))
    df_summary = pd.pivot_table(df3, values=['Demand', 'EnergyCharge', 'DemandCharge', 'TotalCharge'], index= ['CustomerID'], columns=['month'], aggfunc='sum', fill_value=0.0, margins=False, dropna=True, margins_name='All')
    df_summary.to_csv(os.path.join(dirout,"summary." + fnameout), 
               index=True, 
               float_format='%.2f')      
    
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    foutLog.close()
    print('Finished')
    
    return

if __name__ == "__main__":
    if False:
        SplitToGroups(3, 
                      dirin='testdata/', fnamein='synthetic20.normalized.csv', ignoreCIDs='', considerCIDs='',
                      dirout='testdata/', foutbase='synthetic20', # 
                      dirlog='testdata/', fnameLog='SplitToGroups.log')    
    if False:
        ConvertFeather(dirin='input/', fnamein='GroceryTOU_GS3B_Q1O15_152017.feather',
                    dirout='input/', fnameout='GroceryTOU_GS3B_Q1O15_152017.csv',
                    dirlog='output/',
                    renameDict={'DatePeriod':'datetimestr', 'Usage':'Demand'},
                    writeOutput = True)
    
        FixDST(dirin='input/', fnamein='two_grocers_DST_test.csv', 
                       dirout='output/', fnameout='two_grocers.csv', 
                       dirlog='output/', fnameLog='FixDST.log',
                       tzinput = 'America/Los_Angeles',
                       OutputFormat = 'SCE')
    
        ExportLoadFiles(dirin='./', fnamein='two_grocers.csv', explist='ExportCIDs.csv',
                       dirout='./', # fnameout derived from customer IDs
                       dirlog='./', fnameLog='ExportLoadFiles.log')
    
        AnonymizeCIDs(dirin='./', fnamein='IntervalData.SCE.csv', 
                      dirout='./', fnameout='IntervalData.csv', fnameKeys='IntervalData.lookup.csv',
                      dirlog='./', fnameLog='AnonymizeCIDs.log',
                      IDlen=6)
