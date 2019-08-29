# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 11:03:42 2019

@author: jbebic
"""

#%% Import all the necessary Python packages
import pandas as pd # multidimensional data analysis
import numpy as np # vectorized calculations
from datetime import datetime # time stamps
from datetime import date
import os # operating system interface
import matplotlib.pyplot as plt # plotting 
import matplotlib.backends.backend_pdf as dpdf # pdf output
from copy import copy as copy
import pylab
import warnings

#%% Track warnings instead of writing them to the console
warnings.filterwarnings("ignore")

#%% Importing supporting modules
from SupportFunctions import getData, logTime, createLog, assignDayType, getDataAndLabels, findUniqueIDs
from UtilityFunctions import AssignRatePeriods, readTOURates
from NormalizeLoads import NormalizeGroup

#%% Version and copyright info to record on the log file
codeName = 'OutputsForMAPS.py'
codeVersion = '1.0'
codeCopyright = 'GNU General Public License v3.0'
codeAuthors = 'Jovan Bebic, GE Global Research\n'

def AggregateLoadsForMAPS(dirin='./', fnamein='IntervalData.csv', ignoreCIDs='',
                   dirconsider='./', considerCIDs='', 
                   dirout='./', fnameout='IntervalData.aggregated.csv', 
                   dirlog='./', fnameLog='AggregateLoadsForMAPS.log', 
                   InputFormat = 'ISO', groupName='group',
                   normalizeBy="day", demandUnit='Wh'):
    
    if dirconsider=='./':
        dirconsider = dirin  
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "AggregateLoadsForMAPS", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # Output file information to log file
    print('Reading: %s' %os.path.join(dirin,fnamein))
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))
    
    df1Base, UniqueIDsBase, foutLog = getDataAndLabels(dirin, fnamein, foutLog, datetimeIndex=False)
    if isinstance(considerCIDs, list):
        cIDlist = considerCIDs
    else:
        cIDlist = [considerCIDs]
    considerCIDs = None
    
    for considerCIDs in cIDlist:
        UniqueIDs, foutLog = findUniqueIDs(dirconsider, UniqueIDsBase, foutLog, ignoreCIDs=ignoreCIDs, considerCIDs=considerCIDs)
        df1 = df1Base.sort_values(by=['CustomerID', 'datetime'])
    
        foutLog.write('Number of customer IDs to be aggregated: %d\n' %len(UniqueIDs))    
        
        # update units into MWh
        if "kW" in demandUnit:
            scale = 1.0/1000.0
        elif "MW" in demandUnit:
            scale = 1.0
        elif "GW" in demandUnit:
            scale = 1000.0 
        elif "W" in demandUnit:
            scale = 1.0/1000.0/1000.0
        if not('h' in demandUnit):
            deltaT = df1.ix[1,'datetime'] - df1.ix[0,'datetime']
            timeStep = deltaT.seconds/60
            scale = scale * timeStep / 60
        if np.isclose(scale,1.0):
            pass
        else:
            print("Converting Demand from " + demandUnit + " to MWh using scaling factor of " +  str(scale))
            foutLog.write("Converting Demand from " + demandUnit + " to MWh using scaling factor of " +  str(scale) + "\n")
            df1['Demand']  = df1['Demand'] * scale    
        
        df1['DailyAverage'] = 0.0 # Add column of normalized demand to enable setting it with slice index later
        df1['AggrDmnd'] = 0.0 # Add column of normalized demand to enable setting it with slice index later
        df2 = df1.loc[df1['CustomerID'].isin(UniqueIDs)]
        print(UniqueIDs)
        df2pivot = pd.pivot_table(df2, values=[ 'Demand',  'AggrDmnd'], index= ['datetime'], columns=None, aggfunc=np.sum, fill_value=0.0, margins=False, dropna=True, margins_name='All')
        df2count = pd.pivot_table(df2, values=[ 'Demand',  'AggrDmnd'], index= ['datetime'], columns=None, aggfunc=len, fill_value=0.0, margins=False, dropna=True, margins_name='All')
        df3 = pd.DataFrame(df2pivot.to_records())    
        df3c = pd.DataFrame(df2count.to_records()) 
        df3 = df3.assign(Count =pd.Series(df3c['Demand'].values, index=df3.index))
        df3['AvgDemand'] = df3['Demand'] # / df3c['Demand']
        df3['AggrDmnd'] = df3['Demand']
        
        idList = ",".join(UniqueIDs)
        print("Normalizing group that includes " + idList)
        foutLog.write("Normalizing group that includes " + idList + "\n")
        
        normalizeVar = 'AvgDemand'
        if normalizeBy=='month':
            print("Normalizing demand in each month")
            # normalize by average demand for each month
            for m in range(1,13,1):
                month =  df3.datetime.dt.month
                relevant = (month==m) 
                dAvg = df3.loc[relevant,normalizeVar].mean()
                dMin = df3.loc[relevant,normalizeVar].min()
                dMax = df3.loc[relevant,normalizeVar].max()
                # df3.loc[relevant,'AggrDmnd'] = df3.loc[relevant,normalizeVar].copy() # /dAvg 
                df3.loc[relevant,'DailyAverage'] = np.asarray([ df3.loc[relevant,'Demand'].mean() for x in range(0,len(relevant))])
                    
        elif normalizeBy=='day':
            print("Normalizing demand in each day")
            # normalize by average demand over each day
            for m in range(1,13,1):
                month =  df3.datetime.dt.month
                day = df3.datetime.dt.day
                days = list(set(df3.loc[(month==m), "datetime" ].dt.day))
                for d in days:
                    relevant = (month==m) & (day==d)
                    dAvg = df3.loc[relevant,normalizeVar].mean()
                    dMin = df3.loc[relevant,normalizeVar].min()
                    dMax = df3.loc[relevant,normalizeVar].max()
                    # df3.loc[relevant,'AggrDmnd'] = df3.loc[relevant,normalizeVar].copy() # /dAvg 
                    df3.loc[relevant,'DailyAverage'] = np.asarray([ df3.loc[relevant,'Demand'].mean() for x in range(0,sum(relevant))])
        else:
            print("Normalizing demand in entire data set")
            # normalize by average demand over entire dataset
            dAvg = df3[normalizeVar].mean()
            dMin = df3[normalizeVar].min()
            dMax = df3[normalizeVar].max()
            foutLog.write('maxDemand: %.2f\n' %dMax)
            foutLog.write('avgDemand: %.2f\n' %dAvg)
            foutLog.write('minDemand: %.2f\n' %dMin)
            # df3['AggrDmnd'] = df3[normalizeVar].copy() # /dAvg
            # df3.loc[relevant,'DailyAverage'] = np.asarray([ df3['Demand'].mean() for x in range(0,len(relevant))])
            df3['DailyAverage'] = df3['Demand'].mean()
                
        # assign groupName as CustomerID
        cid = np.asarray([groupName for i in range(0,len(df3),1)])
        df3 = df3.assign(CustomerID=pd.Series(cid,index=df3.index))
     
        # write to data file and to log
        if considerCIDs == '': 
            fnamesave = 'all.' + fnameout
        else:
            fnamesave = considerCIDs + '.' + fnameout
        print('Writing: %s' %os.path.join(dirout,fnamesave))
        foutLog.write('Writing: %s\n' %os.path.join(dirout,fnamesave))
        df3.to_csv( os.path.join(dirout,fnamesave), columns=['CustomerID', 'datetime', 'AggrDmnd', 'DailyAverage', 'Demand', 'AvgDemand'], float_format='%.5f', date_format='%Y-%m-%d %H:%M', index=False) # this is a multiindexed dataframe, so only the data column is written
        logTime(foutLog, '\nRunFinished at: ', codeTstart)
        print('Finished: ' + considerCIDs)
        df1 = None
        df2 = None
        df2pivot = None
        df2count = None
        df3 = None
        df3c = None

    return


if __name__ == "__main__":
    AggregateLoadsForMAPS(dirin='input/', fnamein='synthetic2.csv', # dirconsider='./', considerCIDs='',
                   dirout='./', fnameout='synthetic2.aggregated.csv', 
                   dirlog='./', fnameLog='AggregateLoadsForMAPS.log', 
                   InputFormat = 'ISO', groupName='Group',
                   normalizeBy="all", demandUnit='Wh')
