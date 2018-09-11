# -*- coding: utf-8 -*-
"""
Created on Wed May  9 10:37:28 2018

@author: jbebic

Normalize load profiles based on the average value for the time period provided (generally a full year)
"""

#%% Importing all the necessary Python packages
import pandas as pd # multidimensional data analysis
import numpy as np # vectorized calculations

from datetime import datetime # time stamps
import os # operating system interface

#%% Version and copyright info to record on the log file
codeName = 'NormalizeLoads.py'
codeVersion = '1.1'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Jovan Bebic & Irene Berry, GE Global Research\n"


# %% Function definitions
# Time logging
def logTime(foutLog, logMsg, tbase):
    codeTnow = datetime.now()
    foutLog.write('%s%s\n' %(logMsg, str(codeTnow)))
    codeTdelta = codeTnow - tbase
    foutLog.write('Time delta since start: %.3f seconds\n' %((codeTdelta.seconds+codeTdelta.microseconds/1.e6)))

def ReviewLoads(dirin='./', fnamein='IntervalData.csv', ignoreCIDs='', considerCIDs='',
                dirout='./', fnameout='IntervalData.summary.csv', 
                dirlog='./', fnameLog='ReviewLoads.log',
                InputFormat = 'ISO',
                skipPlots = True):
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
    if InputFormat == 'SCE':
        df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                          header = 0, 
                          usecols = [0, 1, 2], 
                          names=['datetimestr', 'Demand', 'CustomerID'],
                          dtype={'datetimestr':np.str, 'Demand':np.float64, 'CustomerID':np.str})
    else:
        df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                          header = 0, 
                          usecols = [0, 1, 2], 
                          names=['CustomerID', 'datetime', 'Demand'])
            
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
    
    foutLog.write('CustomerID, RecordsRead, minDemand, avgDemand, maxDemand\n')
    i = 1
    for cid in UniqueIDs:
        print ('%s (%d of %d)' %(cid, i, len(UniqueIDs)))
        i += 1
        df2 = df1[df1['CustomerID'] == cid]
        foutLog.write('%s, %d, %.2f, %.2f, %.2f\n' %(cid, df2['Demand'].size, df2['Demand'].min(), df2['Demand'].mean(), df2['Demand'].max()))

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    print('Finished')
    return
    
def NormalizeLoads(dirin='./', fnamein='IntervalData.csv', ignoreCIDs='', considerCIDs='',
                   dirout='./', fnameout='IntervalData.normalized.csv', 
                   dirlog='./', fnameLog='NormalizeLoads.log',
                   InputFormat = 'ISO',
                   skipPlots = True, normalizeBy='year'):

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = open(os.path.join(dirout, fnameLog), 'w')
    
    #%% Output header information to log file
    print('This is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('This is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))
    
    # Output file information to log file
    print('Reading: %s' %os.path.join(dirin,fnamein))
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))
    if InputFormat == 'SCE':
        df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                          header = 0, 
                          usecols = [0, 1, 2], 
                          names=['datetimestr', 'Demand', 'CustomerID'],
                          dtype={'datetimestr':np.str, 'Demand':np.float64, 'CustomerID':np.str})
    
        print('Total number of interval records read: %d' %df1['Demand'].size)
        foutLog.write('Total number of interval records read: %d\n' %df1['Demand'].size)
    
        print('Processing time records...')
        foutLog.write('Processing time records\n')
        dstr = df1['datetimestr'].str.split(':').str[0]
        # print(dstr.head())
        hstr = df1['datetimestr'].str.split(':').str[1]
        # print(tstr.head())
        mstr = df1['datetimestr'].str.split(':').str[2]
        # sstr = df1['datetimestr'].str.split(':').str[3]
        temp = dstr + ' ' + hstr + ':' + mstr
        df1['datetime'] = pd.to_datetime(temp, format='%d%b%Y %H:%M')
    else:
        df1 = pd.read_csv(os.path.join(dirin,fnamein), header = 0, usecols = [0, 1, 2], names=['CustomerID', 'datetimestr', 'NormDmnd'])
        foutLog.write('Number of interval records read: %d\n' %df1['NormDmnd'].size)
        df1['datetime'] = pd.to_datetime(df1['datetimestr'], format='%Y-%m-%d %H:%M')
        
    # moved this line of code to before CustomerID is set to the index
    UniqueIDs = df1['CustomerID'].unique().tolist() 
        
#    df1.set_index(['CustomerID', 'datetime'], inplace=True)
#    df1.sort_index(inplace=True) # need to sort on datetime **TODO: Check if this is robust

    df1.drop(['datetimestr'], axis=1, inplace=True) # drop redundant column

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

    df1['NormDmnd'] = np.nan # Add column of normalized demand to enable setting it with slice index later
    df2 = df1.copy() #.loc[df1['CustomerID'].isin(UniqueIDs)]    

    if normalizeBy=='month':
        # normalize by average demand for each month
        i = 1
        for cid in UniqueIDs:
            print ('Processing monthly %s (%d of %d)' %(cid, i, len(UniqueIDs)))
            i += 1
            for m in range(1,13,1):
                month =  df1.datetime.dt.month
                customer = df1.CustomerID
                relevant =  (customer==cid) & (month==m) 
                dAvg = df1.loc[relevant,'Demand'].mean()
                dMin = df1.loc[relevant,'Demand'].min()
                dMax = df1.loc[relevant,'Demand'].max()
                df2.loc[relevant,'NormDmnd'] = df1.loc[relevant,'Demand'].copy()/dAvg 
                        
    elif normalizeBy=='day':
        # normalize by average demand over each day
        i = 1
        for cid in UniqueIDs:
            print ('Processing daily %s (%d of %d)' %(cid, i, len(UniqueIDs)))
            i += 1
            for m in range(1,13,1):
                month =  df1.datetime.dt.month
                day = df1.datetime.dt.day
                customer = df1.CustomerID
                days = list(set(df1.loc[(customer==cid) & (month==m), "datetime" ].dt.day))
                for d in days:
                    relevant =  (customer==cid) & (month==m) & (day==d)
                    dAvg = df1.loc[relevant,'Demand'].mean()
                    dMin = df1.loc[relevant,'Demand'].min()
                    dMax = df1.loc[relevant,'Demand'].max()
                    df2.loc[relevant,'NormDmnd'] = df1.loc[relevant,'Demand'].copy()/dAvg 
                                
    else:
        # normalize by average demand over entire year
        i = 1
        for cid in UniqueIDs:
            print ('Processing all data of %s (%d of %d)' %(cid, i, len(UniqueIDs)))
            i += 1
            customer = df1.CustomerID
            relevant =  (customer==cid) 
            dAvg = df1.loc[relevant,'Demand'].mean()
            dMin = df1.loc[relevant,'Demand'].min()
            dMax = df1.loc[relevant,'Demand'].max()
            df2.loc[relevant,'NormDmnd'] = df1.loc[relevant,'Demand'].copy() / dAvg
                
    # write to file & to log
    print('\nWriting: %s' %os.path.join(dirout,fnameout))
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df2.to_csv( os.path.join(dirout,fnameout), columns=['CustomerID', 'datetime', 'NormDmnd'], float_format='%.5f', date_format='%Y-%m-%d %H:%M', index=False) # this is a multiindexed dataframe, so only the data column is written
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    print('Finished')
            
    return

if __name__ == "__main__":
    ReviewLoads(dirin='input/', fnamein='synthetic2.csv',
                dirout='output/', fnameout='synthetic2.summary.csv',
                dirlog='output/')

    NormalizeLoads(dirin='input/', fnamein='synthetic2.csv', ignoreCIDs='synthetic2.ignoreCIDs.csv',
                   dirout='output/', fnameout='synthetic2.normalized.csv',
                   dirlog='output/')
