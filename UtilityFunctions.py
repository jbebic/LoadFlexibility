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

# %% Function definitions
# Time logging
def logTime(foutLog, logMsg, tbase):
    codeTnow = datetime.now()
    foutLog.write('%s%s\n' %(logMsg, str(codeTnow)))
    codeTdelta = codeTnow - tbase
    foutLog.write('Time delta since start: %.3f seconds\n' %((codeTdelta.seconds+codeTdelta.microseconds/1.e6)))

def FixDST(dirin='./', fnamein='IntervalDataDST.csv', 
                   dirout='./', fnameout='IntervalData.csv', 
                   dirlog='./', fnameLog='FixDST.log',
                   tzinput = 'America/Los_Angeles'):
    #%% Version and copyright info to record on the log file
    codeName = 'FixDST.py'
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

    df1 = pd.read_csv(os.path.join(dirin,fnamein))
    foutLog.write('Read %d records\n' %df1.shape[0])
    foutLog.write('Columns are: %s\n' %' '.join(str(x) for x in df1.columns.tolist()))

    print('Processing time records...')
    foutLog.write('Processing time records\n')
    dstr = df1['datetimestr'].str.split(':').str[0]
    # print(dstr.head())
    hstr = df1['datetimestr'].str.split(':').str[1]
    # print(tstr.head())
    mstr = df1['datetimestr'].str.split(':').str[2]
    # sstr = df1['datetimestr'].str.split(':').str[3]
    temp = dstr + ' ' + hstr + ':' + mstr
    df1['datetime'] = pd.to_datetime(temp, format='%d%b%Y  %H:%M')

    tz = timezone(tzinput)
    tzTransTimes = tz._utc_transition_times
    tzTransInfo = tz._transition_info
    df2 = pd.DataFrame.from_dict({'DSTbeginsUTC':tzTransTimes[11:-2:2], 'DSTendsUTC':tzTransTimes[12:-1:2],
                                  'tzinfob'     :tzTransInfo[11:-2:2],  'tzinfoe'   :tzTransInfo[12:-1:2]})
    df2['year']=pd.DatetimeIndex(df2['DSTbeginsUTC']).year.values
    df2.set_index('year', inplace=True)

    # Find the transtion times for the year in df1
    year = df1['datetime'][0].year
    dst1 = df2['DSTbeginsUTC'][year]+df2['tzinfob'][year][0]
    dst2 = df2['DSTendsUTC'][year]  +df2['tzinfoe'][year][0]
    
    dst1a = dst1 - pd.Timedelta(hours=1)
    # dst2a = dst2 + pd.Timedelta(hours=1)
    dst2b = dst2 + pd.Timedelta(hours=2)
    if df1[df1['datetimestr'] == dst1a].empty:
        # There is a blank record at the start of DST, shift the records to the left
        df1.loc[(df1['datetimestr'] > dst1a) & (df1['datetimestr'] < dst2b), 'datetimestr'] = df1[(df1['datetimestr'] > dst1a) & (df1['datetimestr'] < dst2b)]['datetimestr'] - pd.Timedelta(hours=1)
        if (df1[df1['datetimestr'] == dst2]['datetimestr'].size > 1):
            # There is a double record at the end of DST, move one of them to the right
            for td in [pd.Timedelta('0 min'), pd.Timedelta('15 min'), pd.Timedelta('30 min'), pd.Timedelta('45 min')]:
                print(td)


    print('\nWriting: %s' %os.path.join(dirout,fnameout))
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df1.to_csv(os.path.join(dirout,fnameout), index=False, float_format='%.1f', columns=['datetimestr', 'Demand', 'CustomerID'])

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    print('Finished')
    
    
def ConvertFeather(dirin='./', fnamein='IntervalData.feather', 
                   dirout='./', fnameout='IntervalData.csv', 
                   dirlog='./', fnameLog='ConvertFeather.log',
                   tzinput = 'America/Los_Angeles',
                   renameDict={},
                   CorrectDST = False,
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
    print('This is: %s, Version: %s' %(codeName, codeVersion))
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
    
    if CorrectDST: # Correcting Daylight Savings   
        # Prepare a dataframe with daylight savings time transitions
        tz = timezone(tzinput)
        tzTransTimes = tz._utc_transition_times
        tzTransInfo = tz._transition_info
        df2 = pd.DataFrame.from_dict({'DSTbeginsUTC':tzTransTimes[11:-2:2], 'DSTendsUTC':tzTransTimes[12:-1:2],
                                      'tzinfob'     :tzTransInfo[11:-2:2],  'tzinfoe'   :tzTransInfo[12:-1:2]})
        df2['year']=pd.DatetimeIndex(df2['DSTbeginsUTC']).year.values
        df2.set_index('year', inplace=True)
    
        # Find the transtion times for the year in df1
        year = df1['datetimestr'][0].year
        dst1 = df2['DSTbeginsUTC'][year]+df2['tzinfob'][year][0]
        dst2 = df2['DSTendsUTC'][year]  +df2['tzinfoe'][year][0]
        
        dst1a = dst1 - pd.Timedelta(hours=1)
        dst2a = dst2 + pd.Timedelta(hours=1)
        dst2b = dst2 + pd.Timedelta(hours=2)
        if df1[df1['datetimestr'] == dst1a].empty:
            # There is a blank record at the start of DST, shift the records to the left
            df1.loc[(df1['datetimestr'] > dst1a) & (df1['datetimestr'] < dst2b), 'datetimestr'] = df1[(df1['datetimestr'] > dst1a) & (df1['datetimestr'] < dst2b)]['datetimestr'] - pd.Timedelta(hours=1)
            if (df1[df1['datetimestr'] == dst2]['datetimestr'].size > 1):
                # There is a double record at the end of DST, move one of them to the right
                for td in [pd.Timedelta('0 min'), pd.Timedelta('15 min'), pd.Timedelta('30 min'), pd.Timedelta('45 min')]:
                    print(td)    
            else:
                # There is a single record at the end of DST, split value into two and move one to the right
                for td in [pd.Timedelta('0 min'), pd.Timedelta('15 min'), pd.Timedelta('30 min'), pd.Timedelta('45 min')]:
                    dmnd = df1[df1['datetimestr']==dst2+td]['Demand'].values[0]/2.
                    year = df1[df1['datetimestr']==dst2+td]['year'].values[0]
                    temp = []
                    temp.insert(0, {'datetimestr': dst2a+td, 'Demand': dmnd, 'year': year})
                    df1 = pd.concat([pd.DataFrame(temp), df1], ignore_index=True)
                    df1.loc[(df1['datetimestr'] == dst2+td),'Demand'] = dmnd
                
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
    print('Finished')

    return

if __name__ == "__main__":
#    ConvertFeather(dirin='input/', fnamein='GroceryTOU_GS3B_Q1O15_152017.feather',
#                dirout='input/', fnameout='GroceryTOU_GS3B_Q1O15_152017.csv',
#                dirlog='output/',
#                renameDict={'DatePeriod':'datetimestr', 'Usage':'Demand'},
#                CorrectDST = True,
#                writeOutput = True)

    FixDST(dirin='input/', fnamein='synthetic2.csv', 
                   dirout='output/', fnameout='synthetic2a.csv', 
                   dirlog='output/', fnameLog='FixDST.log',
                   tzinput = 'America/Los_Angeles')
