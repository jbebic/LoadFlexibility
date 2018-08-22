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

# %% Function definitions
# Time logging
def logTime(foutLog, logMsg, tbase):
    codeTnow = datetime.now()
    foutLog.write('%s%s\n' %(logMsg, str(codeTnow)))
    codeTdelta = codeTnow - tbase
    foutLog.write('Time delta since start: %.3f seconds\n' %((codeTdelta.seconds+codeTdelta.microseconds/1.e6)))

def ReviewLoads(dirin='./', fnamein='IntervalData.csv', 
                dirout='./', fnameout='IntervalData.summary.csv', 
                dirlog='./', fnameLog='ReviewLoads.log',,
                InputFormat = 'ISO',
                skipPlots = True):
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
    uniqueCIDs = df1['CustomerID'].unique()
    foutLog.write('Number of unique customer IDs in the file: %d\n' %uniqueCIDs.size)
    foutLog.write('Total number of interval records read: %d\n' %df1['Demand'].size)
    foutLog.write('CustomerID, RecordsRead, minDemand, avgDemand, maxDemand\n')
    i = 1
    for cid in uniqueCIDs:
        print ('%s (%d of %d)' %(cid, i, uniqueCIDs.size))
        i += 1
        df2 = df1[df1['CustomerID'] == cid]
        foutLog.write('%s, %d, %.2f, %.2f, %.2f\n' %(cid, df2['Demand'].size, df2['Demand'].min(), df2['Demand'].mean(), df2['Demand'].max()))

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    print('Finished')
    return
    
def NormalizeLoads(dirin='./', fnamein='IntervalData.csv', ignorein='', group='',
                   dirout='./', fnameout='IntervalData.normalized.csv', 
                   dirlog='./', fnameLog='NormalizeLoads.log',
                   InputFormat = 'ISO',
                   skipPlots = True):
    #%% Version and copyright info to record on the log file
    codeName = 'NormalizeLoads.py'
    codeVersion = '1.0'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"

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
        
    df1.set_index(['CustomerID', 'datetime'], inplace=True)
    df1.sort_index(inplace=True) # need to sort on datetime **TODO: Check if this is robust

    df1.drop(['datetimestr'], axis=1, inplace=True) # drop redundant column

    # Dropping ignored CIDs
    if ignorein != '':
        print('Reading: %s' %os.path.join(dirin,ignorein))
        foutLog.write('Reading: %s\n' %os.path.join(dirin,ignorein))
        df9 = pd.read_csv(os.path.join(dirin,ignorein), 
                          header = 0, 
                          usecols = [0], 
                          names=['CustomerID'],
                          dtype={'CustomerID':np.str})

        if(len(df9['CustomerID'].tolist())>0):
            df1.drop(df9['CustomerID'].tolist(), inplace=True, level=0)
    
    # Processing records by CID
    uniqueCIDs = df1.index.get_level_values('CustomerID').unique().values # df1['CustomerID'].unique()
    print('Number of unique customer IDs in the file: %d' %uniqueCIDs.size)
    foutLog.write('Number of unique customer IDs in the file: %d\n' %uniqueCIDs.size)
    if group != '':
        df9 = pd.read_csv(os.path.join(dirin,group), 
                          header = 0, 
                          usecols = [0], 
                          names=['CustomerID'],
                          dtype={'CustomerID':np.str})
        groupIDs = df9['CustomerID'].tolist()
        uniqueCIDs = list(set(uniqueCIDs).intersection(groupIDs))

    df1['NormDmnd']=np.nan # Add column of normalized demand to enable setting it with slice index later
    i = 1
    for cid in uniqueCIDs:
        print ('Processing %s (%d of %d)' %(cid, i, uniqueCIDs.size))
        i += 1
        df2 = df1.loc[cid] # df1[df1['CustomerID'] == cid]
#        df2['deltaT'] = pd.to_timedelta('15min')
#        df2.loc[df2.index[1:-1], 'deltaT'] = df2.index.values[1:-1] - df2.index.values[0:-2]
#        dTunique = df2['deltaT'].unique()
#        dToddballs = np.extract(dTunique != np.timedelta64(15, 'm'), dTunique)
#        # print(dToddballs/np.timedelta64(1, 'm'))
#        if dToddballs.size > 0:
#            foutLog.write('There are interval records with irregular time deltas\n')
#            for dT in dToddballs:
#                foutLog.write('  dT = %.1f minutes at:' %(dT/np.timedelta64(1, 'm')))
#                for ix in df2[df2['deltaT'] == dT].index:
#                    foutLog.write(' %s' %(ix.strftime('%Y/%m/%d %H:%M')))
#                foutLog.write('\n\n')
        
        foutLog.write('\nCustomerID: %s\n' %(cid))
        foutLog.write('Time records start on: %s\n' %df2.index[0].strftime('%Y-%m-%d %H:%M'))
        foutLog.write('Time records end on: %s\n' %df2.index[-1].strftime('%Y-%m-%d %H:%M'))
        deltat = df2.index[-1]-df2.index[0]
        foutLog.write('Expected number of interval records: %.1f\n' %(deltat.total_seconds()/(60*15)+1))
        
        dAvg = df2['Demand'].mean()
        dMin = df2['Demand'].min()
        dMax = df2['Demand'].max()
        foutLog.write('maxDemand: %.2f\n' %dMax)
        foutLog.write('avgDemand: %.2f\n' %dAvg)
        foutLog.write('minDemand: %.2f\n' %dMin)
        df1.loc[cid]['NormDmnd'] = df2['Demand']/dAvg

    print('\nWriting: %s' %os.path.join(dirout,fnameout))
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df1.to_csv(os.path.join(dirout,fnameout), columns=['NormDmnd'], float_format='%.5f', date_format='%Y-%m-%d %H:%M') # this is a multiindexed dataframe, so only the data column is written
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    print('Finished')
    
    return

if __name__ == "__main__":
    ReviewLoads(dirin='input/', fnamein='synthetic2.csv',
                dirout='output/', fnameout='synthetic2.summary.csv',
                dirlog='output/')

    NormalizeLoads(dirin='input/', fnamein='synthetic2.csv', ignorein='synthetic2.ignoreCIDs.csv',
                   dirout='output/', fnameout='synthetic2.normalized.csv',
                   dirlog='output/')
