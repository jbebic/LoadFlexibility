# -*- coding: utf-8 -*-
"""
Created on Sat May 12 10:52:18 2018

@author: jbebic

Synthetic load profiles in 3-column file format: DateTime, Value, CustomerID
"""

#%% Importing all the necessary Python packages
import pandas as pd # multidimensional data analysis
import numpy as np # vectorized calculations

from datetime import datetime # time stamps
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

def GenerateSyntheticProfiles(NumProfiles, tstart, tend, meMean=200, htllr=2.0, # meMean: monthly energy Mean [MWh], htllr: high to low load ratio
                              dirout='./', fnameout='synthetic.csv', 
                              dirlog='./', fnameLog='GenerateSyntheticProfiles.log',
                              IDlen=6): # IDlen: Length of randomly assigned ID
                              
    #%% Version and copyright info to record on the log file
    codeName = 'GenerateSyntheticProfiles.py'
    codeVersion = '1.0'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = open(os.path.join(dirlog, fnameLog), 'w')
    
    #%% Output header information to log file
    foutLog.write('This is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))

    foutLog.write('Generating %d profiles\n' %(NumProfiles))
    foutLog.write('High to low load ratio: %.2f\n' %(htllr))
    foutLog.write('Mean value of monthly load energy: %.2f [MWh]\n' %(meMean))

    doymax = 31+28+31+30+31+30+31 # July 31 is the day-of-year with the maxi load

    time = pd.date_range(tstart, tend, freq='15min')
    temp1 = pd.to_datetime(tstart)
    temp2 = pd.to_datetime(tend)
    dtime = temp2 - temp1
    nint  = dtime/np.timedelta64(15, 'm') + 1 # number of 15 min intervals in the specified date range

    days  = dtime.total_seconds()/(24.*3600.) # total days in the time range
    # temp0 = pd.to_datetime(str(temp1.year), format='%Y') # year of tstart
    doytstart  = temp1.dayofyear # day of year tstart
    
    # gamma distribution for annual averages of individual loads
    gamk = 3; gamth = 2
    anAvgs = 12*meMean/(gamk*gamth)*np.random.gamma(gamk,scale=gamth,size=NumProfiles)

    df = pd.DataFrame(columns = ['datetime','Demand','CustomerID'])
    ids = [] # an empty list of customer ids
    i = 0
    while i < NumProfiles:
        cid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=IDlen)) # creates a random alphanumeric string of specified length
        if cid in ids: 
            break # guards against a possibility of a newly generated string matching one from before  
        else:
            ids.append(cid)
            # create a synthetic profile
            c = np.array([cid for _ in np.arange(nint)]) # customer id turned into a string
            t = np.arange(nint)/nint*days*24 # time[hours] subsamlpes are decimals
            y0 = anAvgs[i]
            y1max = 1/3*np.abs(np.random.normal(0,1)) # p.u. peak for daily variation
            y1max = np.min([y1max, 0.5]) # limit daily variation peak to 0.5 (max to min daily variation 1.5/0.5 = 3)
            y1max = y0*y1max # set peak in engineering units
            y1 = y1max*np.sin(((t%24.)-11.5)*2.*np.pi/24.) # generate daily variation as a sin(x) over 24h interval
            y2max = 1/3*np.abs(np.random.normal(0,1)) # pu peak for annual variation
            y2max = np.min([y2max, (htllr-1.0)/(htllr+1.0)]) # limit annual variation peak to user-specified value htllr; solved from: (av+pk)/(av-pk) = htllr
            y2max = y0*y2max # set peak in engineering units
            y2 = y2max*np.sin((2.*(t/24.+(doymax-(doytstart-1)+365./4.)))*2.*np.pi/365.) # seasonal variation sin(2x)
            y = y0+y1+y2
            y = np.min(y, 0.0) # ensure load can never be negative
            df1 = pd.DataFrame({'datetime':time,'Demand':y,'CustomerID':c})
            df = df.append(df1, ignore_index=True)
            i += 1

    #%% generating SCE-like datetime string
    df['datetimestr']=df['datetime'].dt.strftime('%d%b%Y:%H:%M').str.upper()
    df.sort_values(['CustomerID', 'datetimestr'], ascending=[True, True], inplace=True)

    print("Writing output file")
    # df1.to_csv('synthetic2.csv', index_label='datetime', columns=['Demand','CustomerID'], header=['Demand','CustomerID'], float_format='%.5f', date_format='%Y-%m-%d %H:%M')
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df.to_csv(os.path.join(dirout,fnameout), index=False, columns=['datetimestr','Demand','CustomerID'], header=['datetimestr','Demand','CustomerID'], float_format='%.5f')
    logTime(foutLog, '\nRunFinished at: ', codeTstart)

    return

#%% Main script begins here
if __name__ == "__main__":
    GenerateSyntheticProfiles(2, '2017-01-01 00:00', '2017-12-31 23:45', 
                              IDlen=6, 
                              dirout='input/', fnameout='synthetic2.csv', 
                              dirlog='output/')
