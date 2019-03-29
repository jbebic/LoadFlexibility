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
from datetime import date
from pytz import timezone
import os # operating system interface
import string
import random
import matplotlib.pyplot as plt # plotting 
import matplotlib.backends.backend_pdf as dpdf # pdf output
import matplotlib.pylab as pl

#%% Importing modules
from SupportFunctions import getData, getDataAndLabels, logTime, createLog, assignDayType, findUniqueIDs, readHighlightIDs

#%% Version and copyright info to record on the log file
codeName = 'UtilityFunctions.py'
codeVersion = '1.5'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Jovan Bebic & Irene Berry, GE Global Research\n"

#%% Function definitions
def readTOURates(dirin, ratein):
    
    df2 = pd.read_csv(os.path.join(dirin,ratein),
                      header = 0,
                      usecols = [0,1,2,3,4,5,6,7,8,9, 10, 11, 12], 
                      comment = '#',
                      names = [ 'Season', 'RateName',  'AllOtherHours', 'WeekDaysOnly',"DeliveryCost", "GenerationCost", 'EnergyCost', 'DemandCost', "FacilityCost", 'HourStart','HourStop', 'MonthStart', 'MonthStop'],
                      dtype = { 'Season': str, 'RateName': str,  'AllOtherHours':bool,'WeekDaysOnly': bool,'DeliveryCost':np.float,'GenerationCost':np.float, 'EnergyCost':np.float, 'DemandCost':np.float, 'FacilityCost':np.float, 'HourStart':np.int8, 'HourStop': np.int8,  "MonthStart": np.int8 , "MonthStop": np.int8 })
    df2['RatePeriod'] = df2.index
    
    data = df2.to_dict('series')
    
    return data

#%% Externally-Facing Function definitions
def AnonymizeCIDs(dirin='./', fnamein='IntervalData.SCE.csv', 
           dirout='./', fnameout='IntervalData.csv', fnameKeys='IntervalData.lookup.csv',
           dirlog='./', fnameLog='AnonymizeCIDs.log',
           IDlen=6):
    
    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, 'AnonymizeCIDs', codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    # load data from file, find initial list of unique IDs. Update log file
    df1 = pd.read_csv(os.path.join(dirin,fnamein))
    foutKeys = open(os.path.join(dirout, fnameKeys), 'w')

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
           dirlog='./', fnameLog='ExportLoadFiles.log'):
    
    
    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, 'ExportLoadFiles', codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

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
#    df1 = pd.read_csv(os.path.join(dirin,fnamein), 
#                      header = 0, 
#                      usecols = [1, 2, 0], 
#                      names=['datetimestr', 'Demand', 'CustomerID'],
#                      dtype={'datetimestr':np.str, 'Demand':np.float64, 'CustomerID':np.str})

    df1, UniqueIDs, foutLog = getDataAndLabels(dirin,  fnamein, foutLog, datetimeIndex=True)
    
    print('Total number of interval records read: %d' %df1.shape[0])
    foutLog.write('Total number of interval records read: %d\n' %df1.shape[0])
    
    export_list = df9['CustomerID'].tolist()
    for cid in export_list:
        # Check if the cid exists in the input file and export if yes
        if cid in df1['CustomerID'].unique().tolist():
            df2 = df1[df1['CustomerID'] == cid]
            fnameout = str(cid)+'.csv'
            print('Writing: %s' %os.path.join(dirout,fnameout))
            foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
            df2.to_csv(os.path.join(dirout,fnameout), index=True) # float_format='%.1f', 
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
    
    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, 'FixDST', codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
              
    # Prep DST transition times dataframe
    tz = timezone(tzinput)
    tzTransTimes = tz._utc_transition_times
    tzTransInfo = tz._transition_info
    df2 = pd.DataFrame.from_dict({'DSTbeginsUTC':tzTransTimes[11:-2:2], 'DSTendsUTC':tzTransTimes[12:-1:2],
                                  'tzinfob'     :tzTransInfo[11:-2:2],  'tzinfoe'   :tzTransInfo[12:-1:2]})
    df2['year']=pd.DatetimeIndex(df2['DSTbeginsUTC']).year.values
    df2.set_index('year', inplace=True)
    
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
        hstr = df1['datetimestr'].str.split(':').str[1]
        mstr = df1['datetimestr'].str.split(':').str[2]
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
            hstr = df1[df1['CustomerID'] == cid]['datetimestr'].str.split(':').str[1]
            mstr = df1[df1['CustomerID'] == cid]['datetimestr'].str.split(':').str[2]
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
        dst2b = dst2 + pd.Timedelta(hours=2)
        if df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst1a)].empty:
            # There is a blank record at the start of DST, shift the records to the left
            df1.loc[(df1['CustomerID'] == cid) & (df1['datetime'] > dst1a) & (df1['datetime'] < dst2b), 'datetime'] = df1[(df1['CustomerID'] == cid) & (df1['datetime'] > dst1a) & (df1['datetime'] < dst2b)]['datetime'] - pd.Timedelta(hours=1)
            td = pd.Timedelta('0 min') # pd.Timedelta('15 min'), pd.Timedelta('30 min'), pd.Timedelta('45 min')
            if (df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].size > 1):
                ix = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)].index[0]
                temp = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].iloc[0] + pd.Timedelta(hours=1)
                df1.at[ix, 'datetime'] = temp
            td = pd.Timedelta('15 min') 
            if (df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].size > 1):
                ix = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)].index[0]
                temp = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].iloc[0] + pd.Timedelta(hours=1)
                df1.at[ix, 'datetime'] = temp
            td = pd.Timedelta('30 min') 
            if (df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].size > 1):
                ix = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)].index[0]
                temp = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].iloc[0] + pd.Timedelta(hours=1)
                df1.at[ix, 'datetime'] = temp
            td = pd.Timedelta('45 min')
            if (df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].size > 1):
                ix = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)].index[0]
                temp = df1[(df1['CustomerID'] == cid) & (df1['datetime'] == dst2+td)]['datetime'].iloc[0] + pd.Timedelta(hours=1)
                df1.at[ix, 'datetime'] = temp
            
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
    
    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, 'ConvertFeather', codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

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
    
    
    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, 'SplitToGroups', codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

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
        df1 = pd.DataFrame(cIDgroup, columns=['CustomerID'])
        df1.to_csv(os.path.join(dirout,foutbase+'.g'+str(gid)+'c.csv'), index=False)
        gid += 1

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

def AssignRatePeriods(df, rate, tzinput = 'America/Los_Angeles', datetimeIndex=False, addRate=False):
    
    # initialize and then assign DayType & RatePeriod
    df['DayType'] = ''
    df['RatePeriod'] = np.nan
    df = assignDayType(df, datetimeIndex=datetimeIndex)
    
    if datetimeIndex:
        df['datetime'] = df.index.copy()

    df = df.sort_values(by=['CustomerID', 'datetime'])
    df = df.reset_index(drop=True)
        
    # Daylight Savings Time Transition Dataframe
    tz = timezone(tzinput)
    tzTransTimes = tz._utc_transition_times
    tzTransInfo = tz._transition_info
    df2 = pd.DataFrame.from_dict({'DSTbeginsUTC':tzTransTimes[11:-2:2], 
                                  'DSTendsUTC':tzTransTimes[12:-1:2],
                                  'tzinfob':tzTransInfo[11:-2:2],  
                                  'tzinfoe'   :tzTransInfo[12:-1:2]})
    df2['year']=pd.DatetimeIndex(df2['DSTbeginsUTC']).year.values
    df2.set_index('year', inplace=True)
    year = df['datetime'].iloc[0].year
    
    dst1 = df2['DSTbeginsUTC'][year]+df2['tzinfob'][year][0]
    dst2 = df2['DSTendsUTC'][year]  +df2['tzinfoe'][year][0]
    
    springForward = dst1 - pd.Timedelta(hours=1)
    fallBack = dst2 + pd.Timedelta(hours=2)    
    offset = np.asarray([ 0.0 for x in range(0, len(df),1) ])
    for cid in list(set(df['CustomerID'])):
        df0 = df[(df['CustomerID']==cid) ]
        try:
            springIndex = df0[ ( df0['datetime'].dt.month==springForward.month) &  (df0['datetime'].dt.day==springForward.day) & (df0['datetime'].dt.hour==springForward.hour) ].index[0]
        except:
            springIndex = df0.index[0]
        try:
            fallIndex = df0 [(df0['datetime'].dt.month==fallBack.month) & (df0['datetime'].dt.day==fallBack.day) & (df0['datetime'].dt.hour==fallBack.hour) ].index[0]
        except:
            fallIndex = df0.index[len(df0)-1]
        try:
            offset[int(springIndex):int(fallIndex)] = 1.0
        except:
            print('Unable to adjusted ' + cid + ' for DST')
        
        
    # initialize default rates for "AllOtherHours"
    for r in rate['RatePeriod']:
        if rate['AllOtherHours'][r]:
            
            # relevent months of the year
            if rate[ 'MonthStop'][r] > rate['MonthStart'][r]:
                months = (rate['MonthStart'][r] <= df['datetime'].dt.month) & (df['datetime'].dt.month < rate['MonthStop'][r])
            else:
                months = (rate[ 'MonthStop'][r] > df['datetime'].dt.month) | (df['datetime'].dt.month >= rate['MonthStart'][r])
            
            df.at[months, 'RatePeriod'] = r  
            if addRate:
                df.at[months, 'EnergyCost'] = rate['EnergyCost'][r]  
            
    # assign other rate periods
    for r in rate['RatePeriod']:            
        
        if not(rate['AllOtherHours'][r]):
            
            # relevent months of the year
            if rate[ 'MonthStop'][r] > rate[ 'MonthStart'][r]:
                months = (rate['MonthStart'][r] <= df['datetime'].dt.month) & (df['datetime'].dt.month < rate['MonthStop'][r])
            else:
                months = (rate['MonthStop'][r] > df['datetime'].dt.month) | (df['datetime'].dt.month >= rate[ 'MonthStart'][r])
            
            # relevent days of the year
            if rate['WeekDaysOnly'][r]:
                days = (df['DayType'] == 'wd')
            else:
                days =  (df['DayType'] == 'wd') |  (df['DayType'] == 'we')  |  (df['DayType'] == 'o')  |  (df['DayType'] == 'h') 
            
            # relevent hours of the year
            if rate[ 'HourStop'][r] > rate['HourStart'][r]:
                hours = (rate['HourStart'][r] <=( df['datetime'].dt.hour+offset)) & ((df['datetime'].dt.hour+offset) < rate[ 'HourStop'][r])
            else:
                hours = (rate['HourStop'][r] > (df['datetime'].dt.hour+offset)) | ((df['datetime'].dt.hour+offset) >= rate['HourStart'][r]) 
            
            df.at[ hours & days & months, 'RatePeriod'] = r
            if addRate:
                df.at[ hours & days & months,'EnergyCost'] = rate['EnergyCost'][r]    
                
    if datetimeIndex:
        df = df.set_index('datetime')
                
    return df  

def CalculateBilling(dirin='./', fnamein='IntervalData.csv', ignoreCIDs='', considerCIDs='', 
                     dirrate  = './', ratein='TOU-GS3-B.csv',
                     dirout='./', fnameout='IntervalCharges.csv', fnameoutsummary=[],
                     dirlog='./', fnameLog='CalculateBilling.log',
                     tzinput = 'America/Los_Angeles',
                     demandUnit='Wh', varName='Demand',
                     writeDataFile=False,
                     writeSummaryFile=True,
                     writeRatePeriod=False):
    
    # if no summary file output name is specified:
    if fnameoutsummary:
        pass
    else:
        fnameoutsummary = 'summary.'  + fnameout
        
    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, 'CalculateBilling', codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    # read data & down-select to uniqueIDs   
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin,  fnamein, foutLog, datetimeIndex=False)
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs, considerCIDs)
    df1.loc[df1['CustomerID'].isin(UniqueIDs)]
    
    # update units into kWh
    if "kW" in demandUnit:
        scale = 1.0
    elif "MW" in demandUnit:
        scale = 1000.0
    elif "GW" in demandUnit:
        scale = 1000.0 * 1000.0
    elif "W" in demandUnit:
        scale = 1.0/1000.0
    if not('h' in demandUnit):
        deltaT = df1.ix[1,'datetime'] - df1.ix[0,'datetime']
        timeStep = deltaT.seconds/60
        scale = scale * timeStep / 60
    if np.isclose(scale,1.0):
        pass
    else:
        print("Converting Demand from " + demandUnit + " to kWh using scaling factor of " +  str(scale))
        df1['Demand']  = df1['Demand'] * scale    

    df1['DayType'] = ''
    df1['RatePeriod'] = np.nan
    
    print('reading TOU rates...')
    rates = readTOURates(dirrate, ratein)
    
    print('Assigning rate periods...')
    df3 = AssignRatePeriods(df1, rates, tzinput)

    # merge data & rate period info
    df3['EnergyCharge'] = 0.0
    df3['DemandCharge'] = 0.0
    df3['FacilityCharge'] = 0.0
    df3['TotalCharge'] = 0.0
            
    if writeRatePeriod:
        print('Writing: %s' %os.path.join(dirout,'ratePeriods.csv'))
        foutLog.write('Writing: %s\n' %os.path.join(dirout,'ratePeriods.csv'))
        df3.loc[df3['CustomerID'] == UniqueIDs[0], ['datetime', 'DayType', 'RatePeriod', 'Season', 'RateName', 'EnergyCost', 'DemandCost', 'FacilityCost']].to_csv(os.path.join(dirout,'ratePeriods.csv'),index=False) 

    foutLog.write('Number of customer IDs after consider/ignore: %d\n' %len(UniqueIDs))
    print('Processing...')
    df4 = pd.DataFrame(index=np.arange(0, 31*24, 0.25), columns=np.arange(0,4))
    i = 1
    for cid in UniqueIDs:
        print ('%s (%d of %d)' %(cid, i, len(UniqueIDs)))
        i += 1
        
        # Calculate demand charges, based on the peak Demand in the relevant RatePeriod
        for mNo in (np.arange(0, 12, 1)+1):
            
            df4.iloc[:] = np.nan # resetting all values to nan to prevent backfilling from other months
            df4 = df3[(df3['CustomerID']==cid) & (df3['datetime'].dt.month == mNo)][['datetime','RatePeriod',varName]]
            
            # adding demand charges for this month
            ratesThisMonth = list(set(df4['RatePeriod']))
            for r in ratesThisMonth:
                if rates['DemandCost'][r]> 0:
                    idxmax = df4[df4['RatePeriod'] == r][varName].idxmax()
                    df3.at[idxmax, 'DemandCharge'] = df3.at[idxmax,varName] * rates['DemandCost'][r] * 4.
            
            # Adding facilities related demand charge
            temp1 = rates['FacilityCost'][0] # Facility charge
            if df4.shape[0] > 0:
                idxmax = df4[varName].idxmax()
                df3.at[idxmax, 'FacilityCharge'] = df3.at[idxmax,varName] * temp1 * 4.
            
    # Sum the energy and demand charges into total cost for each interval
    # Calculate energy charge for every interval
    energyCost = [rates['EnergyCost'][r] for r in df3['RatePeriod'].values]
    df3['EnergyCharge'] = df3['Demand'] * energyCost 
    df3['TotalCharge'] = df3['DemandCharge'] + df3['FacilityCharge'] + df3['EnergyCharge']
    
    # Write data file with charges for each time period  
    if writeDataFile:       
        print('Writing: %s' %os.path.join(dirout,fnameout))
        foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
        dfwrite = df3.loc[df3['CustomerID'].isin(UniqueIDs)]
        dfwrite.to_csv(os.path.join(dirout,fnameout), 
                   index=False, 
                   float_format='%.4f',
                   date_format='%Y-%m-%d %H:%M',
                   columns = ['CustomerID', 'datetime', 'Demand', 'EnergyCharge', 'DemandCharge', 'FacilityCharge', 'TotalCharge']) 

    # Write Summary Data file with total charges for each month
    if writeSummaryFile:
        
        print("Solve for monthly & annual bills")
        dfm = df3.loc[df3['CustomerID'].isin(UniqueIDs)]
        dfm = dfm.assign(month=pd.Series( np.asarray( dfm['datetime'].dt.month ), index=dfm.index))
		
        dfy = df3.loc[df3['CustomerID'].isin(UniqueIDs)]
        inputArray = np.asarray(['entire year' for i in dfy['datetime'].dt.month])
        dfy = dfy.assign(month=pd.Series( inputArray , index=dfy.index))
		
        dfy = pd.pivot_table(dfy, values=['Demand', 'EnergyCharge', 'DemandCharge', 'FacilityCharge', 'TotalCharge'], index= ['CustomerID'], columns=['month'], aggfunc=np.sum, fill_value=0.0, margins=False, dropna=True, margins_name='All')
        dfm = pd.pivot_table(dfm, values=['Demand', 'EnergyCharge', 'DemandCharge', 'FacilityCharge', 'TotalCharge'], index= ['CustomerID'], columns=['month'], aggfunc=np.sum, fill_value=0.0, margins=False, dropna=True, margins_name='All')
        df_summary = pd.merge(dfy, dfm,  left_index=True, right_index=True)
        
        foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameoutsummary))
        print('Writing: %s' %os.path.join(dirout,fnameoutsummary))
        df_summary.to_csv(os.path.join(dirout, fnameoutsummary), index=True, float_format='%.2f')   
        
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    foutLog.close()
    print('Finished')
    
    return 
def CalculateGroups(dirin='./', fnamein='summary.billing.csv', ignoreCIDs='', considerCIDs='', highlightCIDs='',
                     dirout='./', fnamebase='naics',
                     dirplot='./',
                     dirlog='./', fnameLog='CalculateGroups.log',
                     energyPercentiles = [0, 25, 50, 75, 100], 
                     ratePercentiles = [0,10, 100],
                     plotGroups=True, 
                     chargeType="Total", 
                     ignore1515=False, matchGroupLength=False):
    
    if dirplot=='./':
        dirplot = dirout
            
    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName,'CalculateGroups', codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # Capture start time of code execution and open log file
    chargeColumnName = chargeType + "Charge"
    energyColumnName = 'Demand'
       
    # Output file information to log file
    print('Reading: %s' %os.path.join(dirin,fnamein))
    foutLog.write('\nReading: %s' %os.path.join(dirin,fnamein))
    df1 = pd.read_csv(os.path.join(dirin, fnamein), index_col=[0])
    df1 = df1.drop('month')
    df1 = df1.drop('CustomerID')
    
    # Find UniqueIDs ignoring and considering selected IDs
    print('Processing...')
    UniqueIDs = df1.index.unique().tolist()
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs, considerCIDs)

    HighlightIDs, foutlog = readHighlightIDs(dirin, UniqueIDs, foutLog, highlightCIDs)

    # only consider customers within UniqueID
    df_summary = df1.loc[UniqueIDs]
    
    totalDemandCharge = np.asarray([ float(i) for i in df_summary["DemandCharge"] ]) +  np.asarray([ float(i) for i in df_summary["FacilityCharge"] ])
    df_summary= df_summary.assign(TotalDemandCharge =pd.Series(totalDemandCharge,index=df_summary.index))

    for mNo in range(1,13,1):
        mtotalDemandCharge = np.asarray([ float(i) for i in df_summary["DemandCharge." + str(mNo)] ]) +  np.asarray([ float(i) for i in df_summary["FacilityCharge." + str(mNo)] ])
        df_summary["TotalDemandCharge." + str(mNo)] = pd.Series(mtotalDemandCharge,index=df_summary.index)

    # deal with the data format of the demand and total charge
    totalEnergy = np.asarray([ float(i) for i in df_summary[energyColumnName] ])
    energyCharge = np.asarray([ float(i) for i in df_summary["EnergyCharge"] ])
    demandCharge = np.asarray([ float(i) for i in df_summary["TotalDemandCharge"] ])
    totalCharge = np.asarray([ float(i) for i in df_summary[chargeColumnName] ])
    
    # assign back to df_summary
    df_summary = df_summary.assign(Energy=pd.Series(totalEnergy,index=df_summary.index))
    df_summary = df_summary.assign(TotalCharge =pd.Series(totalCharge,index=df_summary.index))
    df_summary = df_summary.assign(ChargePerUnitYear =pd.Series(100 * totalCharge/totalEnergy,index=df_summary.index))
    df_summary = df_summary.assign(EnergyChargePerUnitYear =pd.Series(100 * energyCharge/totalEnergy,index=df_summary.index))
    df_summary = df_summary.assign(DemandChargePerUnitYear =pd.Series(100 * demandCharge/totalEnergy,index=df_summary.index))

    # ignore customers paying an average of $0/kWh, that is an error
    df_summary = df_summary.loc[df_summary['ChargePerUnitYear']>0]
    
    # recalculate UniqueIDs
    UniqueIDs = list(set( df_summary.index))

    for mNo in range(1,13,1):
        monthlyEnergy = np.asarray([ float(i) for i in df_summary[energyColumnName + "." + str(mNo)] ])
        df_summary["Energy." + str(mNo)]=pd.Series(monthlyEnergy,index=df_summary.index)
        df_summary["ChargePerUnit." + str(mNo)]=pd.Series(100 * df_summary[chargeColumnName + "." + str(mNo)]/df_summary['Energy'+ "." + str(mNo)],index=df_summary.index)
    
    # solve for transitions between quartiles of energy demand
    qD = np.percentile(totalEnergy, energyPercentiles)
    
    N = len(qD) - 2
    qB = []
    Leaders = {}
    Others = {}
    for n in range(0,N+1,1):
        Others[n] = []
        Leaders[n] = []
        
    Excluded = UniqueIDs.copy()
    for n in range(0, N+1,1):
        
        # find demand group
        if n==0:
            group = df_summary.loc[ (df_summary["Energy"] >= qD[n])  &  (df_summary["Energy"] <= qD[n+1]) ]
        else:
            group = df_summary.loc[ (df_summary["Energy"] > qD[n])  &  (df_summary["Energy"] <= qD[n+1]) ]
            
        chargePerUnit = np.asarray([ float(i) for i in group['ChargePerUnitYear'] ])
        ratePerc = ratePercentiles.copy() 
        ratePerc[1] = ratePerc[1]-1.0
        leaders = list([])
        others = list([])
        maxShareL = 0.0
        
        if ignore1515: 
            
            # use default percentile to find leaders & others
            ratePerc = ratePercentiles.copy() 
            qb = np.percentile( chargePerUnit, ratePerc)
            leaders = list(group.loc[ (group['ChargePerUnitYear']<=qb[1]) ].index)
            others = list(group.loc[ (group['ChargePerUnitYear']>qb[1]) ].index)
            
        else:
            
            # iterate percentiles to get at least 15 leaders
            while len(leaders)<15:
                ratePerc[1] = ratePerc[1]+1.0
                if ratePerc[1] >=100:
                    break
                qb = np.percentile( chargePerUnit, ratePerc) 
                leaders = list(group.loc[ (group['ChargePerUnitYear']<=qb[1]) ].index)
                others = list(group.loc[ (group['ChargePerUnitYear']>qb[1]) ].index)
                
            # iterate percentiles to get at least 15 others
            while len(others)<15:
                ratePerc[1] = ratePerc[1]-1.0
                if ratePerc[1] <=0:
                    break
                qb = np.percentile( chargePerUnit, ratePerc) 
                leaders = list(group.loc[ (group['ChargePerUnitYear']<=qb[1]) ].index)            
                others = list(group.loc[ (group['ChargePerUnitYear']>qb[1]) ].index)
            
         # make both groups the same length  
        if matchGroupLength:
            if len(others)>len(leaders):
                others = others[:len(leaders)]
            elif len(leaders)>len(others):
                leaders = leaders[:len(others)]
            
        # find max individual share of the group of leaders
        leadersMaxD = np.max(group.loc[leaders, 'Energy'])
        leadersTotalD = np.sum(group.loc[leaders, 'Energy'])
        maxShareL = leadersMaxD/leadersTotalD  * 100          
        
        # find max individual share of the group of others
        othersMaxD = np.max(group.loc[others, 'Energy'])
        othersTotalD = np.sum(group.loc[others, 'Energy'])
        maxShareO = othersMaxD/othersTotalD  * 100   
        
        scaleEnergy = 1/1000
        unitEnergy = 'MWh'
        
        # write to file, if 1515 is passed
        if ((len(leaders)>=15) and (maxShareL<=15) and (len(others)>=15)  and (maxShareL<=15) )  or (ignore1515):
            Leaders[n] = leaders
            Others[n]  = others
            qB.append( qb[1] )
            
            # print/log compliance to 15/15
            print("\nGroup " + str(n+1) + ": annual demand between " + str(round(qD[n]*scaleEnergy,1)) + " & " +  str(round(qD[n+1]*scaleEnergy,1)) + " MWh")
            foutLog.write("\n\nGroup " + str(n+1) + ": annual demand between " + str(round(qD[n]*scaleEnergy,1)) + " & " +  str(round(qD[n+1]*scaleEnergy,1)) + " MWh")
            if (len(leaders)>=15) and (maxShareL<=15) and (len(others)>=15)  and (maxShareL<=15) :
                print("-- Passed 15/15 splitting into leaders/others at " + str(int( ratePerc[1] ) )+ "%")
                foutLog.write("\n-- Passed 15/15 splitting into leaders/others at " + str(int( ratePerc[1] ) )+ "%")
            else:
                print("** IGNORING 15/15 while splitting into leaders/others at " + str(int( ratePerc[1] ) )+ "%")
                foutLog.write("\n-- IGNORING 15/15 while splitting into leaders/others at " + str(int( ratePerc[1] ) )+ "%")

            # print/log stats on leaders / others groups
            foutLog.write("\n  " + str(int(len(Leaders[n]))) + " Leaders with a max share of " + str(int(maxShareL)) + "%")# 
            foutLog.write("\n  " + str(int(len(Others[n]))) + " Others with a max share of " + str(int(maxShareO)) + "%")# 
            print("  " + str(int(len(Leaders[n]))) + " Leaders with a max share of " + str(int(maxShareL)) + "%")# 
            print("  " + str(int(len(Others[n]))) + " Others with a max share of " + str(int(maxShareO)) + "%")# 
            
            # write leaders to file
            foutLog.write('\n  Writing: %s' %os.path.join(dirout,fnamebase + ".g" + str(int(n+1)) + "L.groupIDs.csv"))
            print('  Writing: %s' %os.path.join(dirout,fnamebase + ".g" + str(int(n+1)) + "L.groupIDs.csv"))
            pd.DataFrame(Leaders[n], columns=['CustomerID']).to_csv(os.path.join(dirout,fnamebase + ".g" + str(int(n+1)) + "L.groupIDs.csv"), index=False) 
            
            # write others to file
            foutLog.write('\n  Writing: %s' %os.path.join(dirout, fnamebase + ".g" + str(int(n+1)) + "o.groupIDs.csv"))
            print('  Writing: %s' %os.path.join(dirout,fnamebase + ".g" + str(int(n+1)) + "o.groupIDs.csv"))
            pd.DataFrame(Others[n], columns=['CustomerID']).to_csv(os.path.join(dirout,fnamebase + ".g" + str(int(n+1)) + "o.groupIDs.csv"), index=False) 
        
        else:
            
            # print/log compliance to 15/15
            foutLog.write("\n\nGroup " + str(n+1) + " -- Did **NOT** pass 15/15 Rule ***")
            print("\nGroup " + str(n+1) + " -- Did **NOT** pass 15/15 Rule ***")
            
            # error message and print/log stats on leaders / others groups
            foutLog.write("\n  " + str(int(len(leaders))) + " LEADERS with a max share of " + str(int(maxShareL)) + "%")# 
            foutLog.write("\n  " + str(int(len(others))) + " OTHERS with a max share of " + str(int(maxShareO)) + "%")# 
            print("  " + str(int(len(leaders))) + " LEADERS with a max share of " + str(int(maxShareL)) + "%")# 
            print("  " + str(int(len(others))) + " OTHERS with a max share of " + str(int(maxShareO)) + "%")#             
            qB.append( np.nan )

        for i in Leaders[n]:
            Excluded.remove(i)
            
        for i in Others[n]:
            Excluded.remove(i)
    
    qB = np.asarray(qB)
    
    if plotGroups:
        
        print("\nPlotting Energy Consumption vs Total Cost of Energy")
        pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnamebase + ".groups.pdf"))
                
        # set marker edge width (ew) and size (ms)
        if len(UniqueIDs)<100:
            ew = 2
            ms = 7
        else:
            ew = 1
            ms = 5
                    
        # Plot Annual Energy vs Rate of bill
        fig, ax = plt.subplots(nrows=1, ncols=1,figsize=(8,7))
        if chargeType=="Energy":
            ax.set_xlabel('Energy Only Average Cost [₵/kWh]') 
            ax.set_title("Entire Year - Energy Charges Only")
        elif chargeType=="Demand":
            ax.set_xlabel('Demand Only Average Cost [₵/kWh]') 
            ax.set_title("Entire Year - Demand Charges Only")
        elif chargeType=="Facility":
            ax.set_xlabel('Facility Only Average Cost [₵/kWh]') 
            ax.set_title("Entire Year - Facility Charges Only")
        elif chargeType=="TotalDemand":
            ax.set_xlabel('Total Demand Only Average Cost [₵/kWh]') 
            ax.set_title("Entire Year - Total Demand Charges Only")
        else:
            ax.set_xlabel('Total Bill Average Cost [₵/kWh]')
            ax.set_title("Entire Year - All Charges")
            
        ax.set_ylabel('Total Energy [' + unitEnergy + ']')

        if len(HighlightIDs) > 0:
            colorsV = ['#d3d3d3'] * (N+1)
        else:
            colorsV = ['blue', 'limegreen','gold', 'red']
            if N>3:
                colorsV = pl.cm.jet(np.linspace(0,1,N+1))
        
        for n in range(0,N+1,1):
            ax.plot(df_summary.loc[Leaders[n],'ChargePerUnitYear' ], df_summary.loc[Leaders[n],'Energy']*scaleEnergy, '^', color=colorsV[n], ms=ms, label="G" + str(n))        
        
        for n in range(0,N+1,1):
            ax.plot(df_summary.loc[Others[n],'ChargePerUnitYear'], df_summary.loc[Others[n],'Energy']*scaleEnergy, 'o', color=colorsV[n] , ms=ms, markerfacecolor='none', markeredgewidth=ew)

        ax.plot(df_summary.loc[Excluded,'ChargePerUnitYear'], df_summary.loc[Excluded,'Energy' ]*scaleEnergy, 'x', color="#d3d3d3" , ms=ms, markerfacecolor='#d3d3d3', markeredgewidth=ew)

        if len(HighlightIDs) > 0:
            ax.plot(df_summary.loc[HighlightIDs,'ChargePerUnitYear'], df_summary.loc[HighlightIDs,'Energy' ]*scaleEnergy, 'd', color='blue' , ms=ms, markerfacecolor='blue', markeredgewidth=ew)
        
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        for n in range(0,len(qD),1):
            ax.plot([xlim[0], xlim[1]], [qD[n]*scaleEnergy,  qD[n]*scaleEnergy], '-',lw=0.5, color="#999999" )
                    
        for n in range(0,N+1,1):
            ax.plot([ qB[n], qB[n]], [qD[n]*scaleEnergy,  qD[n+1]*scaleEnergy], '-',lw=0.5,color="#999999" )
        ax.plot([xlim[0], xlim[1]], [np.max(qD)*scaleEnergy,  np.max(qD)*scaleEnergy], '-',lw=0.5, color="#999999" )
                
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        
        chartBox = ax.get_position()
        ax.set_position([chartBox.x0, chartBox.y0*1.5, chartBox.width, chartBox.height*0.95])
        ax.legend(labels=['G1', 'G2', 'G3', 'G4'], loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
        
        pltPdf1.savefig() # Saves fig to pdf
        plt.close() # Closes fig to clean up memory
    
        # Plot for all 12 months of the year
        for mNo in [1,2,3,4,5,6,7,8,9,10,11,12]:
            
            fig, ax = plt.subplots(nrows=1, ncols=1,figsize=(8,7))
               
            if chargeType=="Energy":
                ax.set_xlabel('Energy Only Average Cost [₵/kWh]') 
                ax.set_title(date(2016, mNo,1).strftime('%B') + " - Energy Charges Only")
                
            elif chargeType=="Demand":
                ax.set_xlabel('Demand Only Average Cost [₵/kWh]') 
                ax.set_title(date(2016, mNo,1).strftime('%B') + " - Demand Charges Only")
                
            elif chargeType=="Facility":
                ax.set_xlabel('Facility Only Average Cost [₵/kWh]') 
                ax.set_title(date(2016, mNo,1).strftime('%B') + " - Facility Charges Only")
                
            elif chargeType=="TotalDemand":
                ax.set_xlabel('Total Demand Only Average Cost [₵/kWh]') 
                ax.set_title(date(2016, mNo,1).strftime('%B') + " - Total Demand Charges Only")   
                
            else:
                ax.set_xlabel('Total Bill Average Cost [₵/kWh]')
                ax.set_title(date(2016, mNo,1).strftime('%B') + " - All Charges")
                
            ax.set_ylabel('Total Energy [' + unitEnergy + ']')
           
            for n in range(0,N+1,1):
                ax.plot(df_summary.loc[Leaders[n],'ChargePerUnit' + "." + str(mNo) ], df_summary.loc[Leaders[n],'Energy' + "." + str(mNo)]*scaleEnergy, '^', color=colorsV[n], ms=ms, label="G" + str(n))        
            
            for n in range(0,N+1,1):
                ax.plot(df_summary.loc[Others[n],'ChargePerUnit' + "." + str(mNo)], df_summary.loc[Others[n],'Energy' + "." + str(mNo)]*scaleEnergy, 'o', color=colorsV[n] , ms=ms, markerfacecolor='none', markeredgewidth=ew)
            
            ax.plot(df_summary.loc[Excluded,'ChargePerUnit' + "." + str(mNo)], df_summary.loc[Excluded,'Energy' + "." + str(mNo)]*scaleEnergy, 'x', color="#d3d3d3" , ms=ms, markerfacecolor='#d3d3d3', markeredgewidth=ew)
            if len(HighlightIDs) > 0:
                ax.plot(df_summary.loc[HighlightIDs,'ChargePerUnit' + "." + str(mNo)], df_summary.loc[HighlightIDs,'Energy' + "." + str(mNo)]*scaleEnergy, 'd', color='blue' , ms=ms, markerfacecolor='blue', markeredgewidth=ew)
            
            chartBox = ax.get_position()
            ax.set_position([chartBox.x0, chartBox.y0*1.5, chartBox.width, chartBox.height*0.95])
            ax.legend(labels=['G1', 'G2', 'G3', 'G4'], loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
            pltPdf1.savefig() # Saves fig to pdf
            plt.close() # Closes fig to clean up memory
            
        # Plot Demand vs Energy Components of Bill
        fig, ax = plt.subplots(nrows=1, ncols=1,figsize=(8,7))
        
        ax.set_xlabel('Energy Only Average Cost [₵/kWh]') 
        ax.set_ylabel('Demand Only Average Cost [₵/kWh]') 
        ax.set_title("Entire Year - Demand vs Energy Cost")
        
        if len(HighlightIDs) > 0:
            colorsV = ['#d3d3d3'] * (N+1)
        else:
            colorsV = ['blue', 'limegreen','gold', 'red']
            if N>3:
                colorsV = pl.cm.jet(np.linspace(0,1,N+1))
        
        for n in range(0,N+1,1):
            ax.plot(df_summary.loc[Leaders[n],'EnergyChargePerUnitYear' ], df_summary.loc[Leaders[n],'DemandChargePerUnitYear' ], '^', color=colorsV[n], ms=ms, label="G" + str(n))        
        
        for n in range(0,N+1,1):
            ax.plot(df_summary.loc[Others[n],'EnergyChargePerUnitYear'], df_summary.loc[Others[n],'DemandChargePerUnitYear' ], 'o', color=colorsV[n] , ms=ms, markerfacecolor='none', markeredgewidth=ew)

        ax.plot(df_summary.loc[Excluded,'EnergyChargePerUnitYear'], df_summary.loc[Excluded,'DemandChargePerUnitYear' ], 'x', color="#d3d3d3" , ms=ms, markerfacecolor='#d3d3d3', markeredgewidth=ew)

        if len(HighlightIDs) > 0:
            ax.plot(df_summary.loc[HighlightIDs,'EnergyChargePerUnitYear'], df_summary.loc[HighlightIDs,'DemandChargePerUnitYear' ], 'd', color='blue' , ms=ms, markerfacecolor='blue', markeredgewidth=ew)
        
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
                        
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        
        chartBox = ax.get_position()
        ax.set_position([chartBox.x0, chartBox.y0*1.5, chartBox.width, chartBox.height*0.95])
        ax.legend(labels=['G1', 'G2', 'G3', 'G4'], loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
        
        pltPdf1.savefig() # Saves fig to pdf
        plt.close() # Closes fig to clean up memory       
        
        # save figures to pdf file
        print('Writing: %s' %os.path.join(dirplot,fnamebase + ".groups.pdf"))
        foutLog.write('\n\nWriting: %s' %os.path.join(dirplot,fnamebase + ".groups.pdf"))
        pltPdf1.close()
        
    logTime(foutLog, '\n\nRunFinished at: ', codeTstart)
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