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
from SupportFunctions import getData, getDataAndLabels, logTime, createLog, findUniqueIDs

#%% Version and copyright info to record on the log file
codeName = 'NormalizeLoads.py'
codeVersion = '1.21'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Jovan Bebic & Irene Berry, GE Global Research\n"

# %% Function definitions
def ReviewLoads(dirin='./', fnamein='IntervalData.csv', ignoreCIDs='', considerCIDs='',
                dirout='./', fnameout='IntervalData.summary.csv', 
                dirlog='./', fnameLog='ReviewLoads.log',
                InputFormat = 'ISO',
                skipPlots = True):
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "ReviewLoads", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

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
    
    colNames = ['CustomerID','RecordsRead', 'minDemand', 'avgDemand', 'maxDemand', 'totalEnergy']
    df3 = pd.DataFrame(columns = colNames)
    
    foutLog.write('CustomerID, RecordsRead, minDemand, avgDemand, maxDemand, totalEnergy\n')
    i = 1
    for cid in UniqueIDs:
        print ('%s (%d of %d)' %(cid, i, len(UniqueIDs)))
        i += 1
        df2 = df1[df1['CustomerID'] == cid]
        foutLog.write('%s, %d, %.2f, %.2f, %.2f, %.2f\n' %(cid, df2['Demand'].size, df2['Demand'].min(), df2['Demand'].mean(), df2['Demand'].max(), df2['Demand'].sum()))
        temp = {'CustomerID' : cid,
                'RecordsRead': df2['Demand'].size,
                'minDemand': df2['Demand'].min(),
                'avgDemand' : df2['Demand'].mean(),
                'maxDemand' : df2['Demand'].max(),
                'totalEnergy' : df2['Demand'].sum()}
        df3 = df3.append(temp, ignore_index = True)

    print('\nWriting: %s' %os.path.join(dirout,fnameout))
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df3.to_csv( os.path.join(dirout,fnameout), float_format='%.2f', index=False)

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    print('Finished')
    return

# %% Function definitions
def ConvertTo1515(dirin='./', fnamein='IntervalData.csv', 
                  considerCIDs='', ignoreCIDs='',
                  dirout='./', fnameout='IntervalData.1515.csv', 
                  saveSummary = False, fnamesummary = 'IntervalData.summary.csv',
                  dirlog='./', fnameLog='ConvertTo1515.log', 
                  InputFormat = 'ISO'):

    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # Open log file
    foutLog = createLog(codeName, "ConvertTo1515", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin, fnamein, foutLog, datetimeIndex=True)
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs=ignoreCIDs, considerCIDs=considerCIDs)
    df1 = df1.sort_values(by=['CustomerID', 'datetime'])

    foutLog.write('Number of customer IDs in the input file: %d\n' %len(UniqueIDs))

    colNames = ['CustomerID', 'RecordsRead', 'minDemand', 'avgDemand', 'maxDemand', 'totalEnergy']
    df3 = pd.DataFrame(columns = colNames)
    
    foutLog.write('CustomerID, RecordsRead, minDemand, avgDemand, maxDemand, totalEnergy\n')
    i = 1
    for cid in UniqueIDs:
        print ('%s (%d of %d)' %(cid, i, len(UniqueIDs)))
        i += 1
        df2 = df1[df1['CustomerID'] == cid]
        foutLog.write('%s, %d, %.2f, %.2f, %.2f, %.2f\n' %(cid, df2['Demand'].size, df2['Demand'].min(), df2['Demand'].mean(), df2['Demand'].max(), df2['Demand'].sum()))
        temp = {'CustomerID' : cid,
                'RecordsRead': df2['Demand'].size,
                'minDemand': df2['Demand'].min(),
                'avgDemand' : df2['Demand'].mean(),
                'maxDemand' : df2['Demand'].max(),
                'totalEnergy' : df2['Demand'].sum()}
        df3 = df3.append(temp, ignore_index = True)

    if saveSummary:
        print('\nWriting: %s' %os.path.join(dirout,fnamesummary))
        foutLog.write('Writing: %s\n' %os.path.join(dirout,fnamesummary))
        df3.to_csv( os.path.join(dirout,fnamesummary), float_format='%.2f', index=False)
    
    print('\nExtracting 1515 data')
    foutLog.write('\nExtracting 1515 data\n')
    all_IDs = df3['CustomerID'].tolist()
    # Selecting linearly independent, 1515 compliant groups, pedestrian-way using two loops...
    # The inner loop creates a row array with exactly nSel elements set to 1
    # The outer loop checks if this new row is linearly independent relative to other already selected rows 
    # in the matrix by calculating the rank. A test matrix Mx2 is created and rank2 computed and 
    # if it is greater than the rank of existing Mx matrix the row is added. 
    N = len(all_IDs)
    nSel = 15
    Mx = np.zeros((1,N)).astype(int) # Zero row to enable np.vstack
    rank = np.linalg.matrix_rank(Mx) # rank is zero
    rowNum = 0
    df6 = pd.DataFrame(columns = ['1515Row', 'Demand'])
    df6.index.name = 'datetime'

    while rank < N:
        row = np.zeros(N).astype(int)
        while (row.sum() < nSel):
            i = np.random.randint(N)
            row[i] = 1 # Set it to 1 (it may already be 1, but it is faster to just set it then set conditionaly)
        # test if this set meets the 15/15 rule
        ix = row.nonzero()[0] # extract indices of nonzero elements
        ids = np.array(all_IDs)[ix].tolist() # sample the list of all_IDs with these indices to get the list of 15 chosen IDs
        chosen = df3.index[df3['CustomerID'].isin(ids)] # chosen are the df3 indices that have CustomerID in the list of 15 chosen IDs
        totalEn = df3.loc[chosen, 'totalEnergy'].sum() # totalEnergy of the group
        # print('.', end = '') # the last row takes a long time, uncomment this to animate the user
        if (df3.loc[chosen, 'totalEnergy'].max() < 0.15*totalEn):
            # The 15/15 criteria is met, the row can be added to the matrix if it is linearly independent of other rows already in the matrix
            Mx2 = np.vstack((Mx, row))
            rank2 = np.linalg.matrix_rank(Mx2)
            if rank2 > rank:
                # The row is linearly independent, add it to the matrix and save the records for export
                # add it to the matrix portion
                Mx = Mx2
                rank = rank2
                # save the records portion
                # need to add all values
                rowNum += 1
                print('Recording row %d' %(rowNum))
                df4 = df1.loc[df1['CustomerID'].isin(ids)]
                df4pivot = pd.pivot_table(df4, values=[ 'Demand'], index= ['datetime'], columns=None, aggfunc=np.sum, fill_value=0.0, margins=False, dropna=True, margins_name='All')
                df5 = pd.DataFrame(df4pivot.to_records())
                df5.set_index(['datetime'], inplace=True)
                df5.sort_index(inplace=True) # sort on datetime
                df5['1515Row'] = rowNum
                df6 = df6.append(df5)

    print('\nWriting: %s' %os.path.join(dirout,fnameout))
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df6.to_csv( os.path.join(dirout,fnameout), float_format='%.2f')
                
    df7 = pd.DataFrame(Mx[1:,:], columns = all_IDs)
    df7.index += 1
    df7.index.name = '1515Row'
    print('\nWriting: %s' %os.path.join(dirout,fnameout.replace('.csv', '.lookup.csv')))
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout.replace('.csv', '.lookup.csv')))
    df7.to_csv(os.path.join(dirout,fnameout.replace('.csv', '.lookup.csv')))

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    print('Finished')
    return

    
def NormalizeLoads(dirin='./', fnamein='IntervalData.csv', ignoreCIDs='', considerCIDs='',
                   dirout='./', fnameout='IntervalData.normalized.csv', 
                   dirlog='./', fnameLog='NormalizeLoads.log',
                   InputFormat = 'ISO', normalize=True,
                   skipPlots = True, normalizeBy='year'):

    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "NormalizeLoads", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
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
        df1 = pd.read_csv(os.path.join(dirin,fnamein), header = 0, usecols = [0, 1, 2], names=['CustomerID', 'datetimestr', 'Demand'])
        foutLog.write('Number of interval records read: %d\n' %df1['Demand'].size)
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
                if normalize:
                    df2.loc[relevant,'NormDmnd'] = df1.loc[relevant,'Demand'].copy()/dAvg 
                else:
                    df2.loc[relevant,'NormDmnd'] = df1.loc[relevant,'Demand'].copy()
                        
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
                    if normalize:
                        df2.loc[relevant,'NormDmnd'] = df1.loc[relevant,'Demand'].copy()/dAvg 
                    else:
                        df2.loc[relevant,'NormDmnd'] = df1.loc[relevant,'Demand'].copy()
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
            if normalize:
                df2.loc[relevant,'NormDmnd'] = df1.loc[relevant,'Demand'].copy() / dAvg
            else:
                df2.loc[relevant,'NormDmnd'] = df1.loc[relevant,'Demand'].copy() 
                
    # write to file & to log
    print('\nWriting: %s' %os.path.join(dirout,fnameout))
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df2.to_csv( os.path.join(dirout,fnameout), columns=['CustomerID', 'datetime', 'NormDmnd'], float_format='%.5f', date_format='%Y-%m-%d %H:%M', index=False) # this is a multiindexed dataframe, so only the data column is written
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    print('Finished')
            
    return


def NormalizeGroup(dirin='./', fnamein='IntervalData.csv', 
                   dirconsider='./', considerCIDs='',
                   dirout='./', fnameout='IntervalData.normalized.csv', 
                   dirlog='./', fnameLog='NormalizeGroup.log', 
                   InputFormat = 'ISO', groupName='group',
                   normalizeBy="day", demandUnit='Wh'):
    
    if dirconsider=='./':
        dirconsider = dirin  
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "NormalizeGroup", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # Output file information to log file
    print('Reading: %s' %os.path.join(dirin,fnamein))
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))
    
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin, fnamein, foutLog, datetimeIndex=False)
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs='', considerCIDs=considerCIDs)
    df1 = df1.sort_values(by=['CustomerID', 'datetime'])

    foutLog.write('Number of customer IDs in the input file: %d\n' %len(UniqueIDs))    
    
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
        df1['Demand']  = df1['Demand'] * scale    
    
    df1['DailyAverage'] = 0.0 # Add column of normalized demand to enable setting it with slice index later
    df1['NormDmnd'] = 0.0 # Add column of normalized demand to enable setting it with slice index later
    df2 = df1.loc[df1['CustomerID'].isin(UniqueIDs)]
    print(UniqueIDs)
    df2pivot = pd.pivot_table(df2, values=[ 'Demand',  'NormDmnd'], index= ['datetime'], columns=None, aggfunc=np.sum, fill_value=0.0, margins=False, dropna=True, margins_name='All')
    df2count = pd.pivot_table(df2, values=[ 'Demand',  'NormDmnd'], index= ['datetime'], columns=None, aggfunc=len, fill_value=0.0, margins=False, dropna=True, margins_name='All')
    df3 = pd.DataFrame(df2pivot.to_records())    
    df3c = pd.DataFrame(df2count.to_records()) 
    df3 = df3.assign(Count =pd.Series(df3c['Demand'].values, index=df3.index))
    df3['AvgDemand'] = df3['Demand'] / df3c['Demand']
    
    idList = ",".join(UniqueIDs)
    print("Normalizing group that includes " + idList)
    
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
            df3.loc[relevant,'NormDmnd'] = df3.loc[relevant,normalizeVar].copy()/dAvg 
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
                df3.loc[relevant,'NormDmnd'] = df3.loc[relevant,normalizeVar].copy()/dAvg 
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
        df3['NormDmnd'] = df3[normalizeVar].copy() /dAvg
        df3.loc[relevant,'DailyAverage'] = np.asarray([ df3['Demand'].mean() for x in range(0,len(relevant))])
            
    # assign groupName as CustomerID
    cid = np.asarray([groupName for i in range(0,len(df3),1)])
    df3 = df3.assign(CustomerID=pd.Series(cid,index=df3.index))
 
    # write to data file and to log
    print('Writing: %s' %os.path.join(dirout,fnameout))
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df3.to_csv( os.path.join(dirout,fnameout), columns=['CustomerID', 'datetime', 'NormDmnd', 'DailyAverage', 'Demand', 'AvgDemand'], float_format='%.5f', date_format='%Y-%m-%d %H:%M', index=False) # this is a multiindexed dataframe, so only the data column is written
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    print('Finished')

    return

#%% Testing
if __name__ == "__main__":
    if False:
        N = 115
        nSel = 15
        Mx = np.zeros((1,N)).astype(int)
        rank = np.linalg.matrix_rank(Mx)
        while rank < N:
            row = np.zeros(N).astype(int)
            while (row.sum() < nSel):
                i = np.random.randint(N)
                row[i] = 1 # Set it to 1 to save the if condition
            Mx2 = np.vstack((Mx, row))
            rank2 = np.linalg.matrix_rank(Mx2)
            if rank2 > rank:
                Mx = Mx2
                rank = rank2
        print(Mx)
        
    if False:
        ConvertTo1515(dirin='input/', fnamein='synthetic150.csv', 
                      dirout='input/', fnameout='synthetic150.1515.csv', 
                      saveSummary = True, fnamesummary = 'synthetic150.summary.csv',
                      dirlog='input/',
                      InputFormat = 'ISO')
            
    if False:
        ReviewLoads(dirin='input/', fnamein='synthetic150.csv',
                    dirout='input/', fnameout='synthetic150.summary.csv',
                    dirlog='input/', 
                    InputFormat = 'ISO')

    if True:
        NormalizeLoads(dirin='input/', fnamein='synthetic10-15min.csv', # ignoreCIDs='synthetic2.ignoreCIDs.csv',
                       dirout='output/', fnameout='synthetic10-15min.normalized.csv',
                       dirlog='output/')