# -*- coding: utf-8 -*-
"""
Created on Wed May  9 10:37:28 2018

@author: jbebic

v1.1 JZB20180822
Moved pivoting outside of plot function to mitigate the impact of dynamic memory allocation
Added optional input to limit the customerIDs to a specific group

v1.0 JZB20180509
Heatmaps and daily wisker plots of normalized loads

"""

#%% Importing all the necessary Python packages
import pandas as pd # multidimensional data analysis
import numpy as np # vectorized calculations

from datetime import datetime # time stamps
import os # operating system interface

import matplotlib.pyplot as plt # plotting 
import matplotlib.backends.backend_pdf as dpdf # pdf output

# %% Function definitions
# Time logging
def logTime(foutLog, logMsg, tbase):
    codeTnow = datetime.now()
    foutLog.write('%s%s\n' %(logMsg, str(codeTnow)))
    codeTdelta = codeTnow - tbase
    foutLog.write('Time delta since start: %.3f seconds\n' %((codeTdelta.seconds+codeTdelta.microseconds/1.e6)))

#%%
def outputLoadHeatmap1h(pltPdf, df1, title):
    fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1,
                              figsize=(8,6),
                              sharex=True)

    fig.suptitle(title) # This titles the figure

    cmin = 0.
    cmax = df1.max().max()
    ax0.set_title('Load [pu]')
    im0 = ax0.imshow(df1.iloc[:,:], interpolation='none', #'nearest'
                                          cmap='viridis', 
                                          origin='lower', 
                                          vmin = cmin, 
                                          vmax = cmax)
    ax0.set_xlim([0,365])
    ax0.set_ylim([0,96])
    ax0.set_yticks(np.linspace(0, 96, num=4).tolist())
    ax0.set_yticklabels(np.linspace(0, 24, num=4, dtype=np.int16).tolist())
    # ax0.set_yticklabels(['0', '6', '12', '18', '24'])
    ax0.set_aspect('auto')
    ax0.set_ylabel('Hour')

    ax1.set_title('Daily box-plots')
    ax1.set_ylim([0,cmax]) # ax1.set_ylim([0,24])
    ax1.set_ylabel('Demand')
    ax1.set_aspect('auto')
    
    temp  = df1.values
    # temp1 = temp[:,~np.isnan(temp).any(axis=0)] # eliminates the whole day with NaNs
    # temp[np.isnan(temp)] = -0.001 # replaces the NaNs with negative epsilon to hide from the chart
    temp[np.isnan(temp)] = -np.inf # replaces the NaNs with negative infinity to elimiante from the chart
    ax1.boxplot(temp, manage_xticks = False)

    ax1.set_xlabel('Day')
    ax1.set_xlim([0,365])
    ax1.set_xticks(np.arange(0, 365, step=50).tolist())
    fig.colorbar(im0, ax=[ax0,ax1])
    
    pltPdf.savefig() # Saves fig to pdf
    plt.close() # Closes fig to clean up memory
    return

#%%
def PlotHeatMaps(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='./', fnameout='HeatMaps.pdf', 
                 dirlog='./', fnameLog='PlotHeatMaps.log',
                 skipPlots = False):
    # Version and copyright info to record on the log file
    codeName = 'PlotHeatMaps.py'
    codeVersion = '1.1'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = open(os.path.join(dirlog, fnameLog), 'w')
    
    # Output header information to log file
    print('This is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('This is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))
    
    # Output csv file information to log file
    print('Reading: %s' %os.path.join(dirin,fnamein))
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))
    df1 = pd.read_csv(os.path.join(dirin,fnamein), header = 0, usecols = [0, 1, 2], names=['CustomerID', 'datetimestr', 'NormDmnd'])
    foutLog.write('Number of interval records read: %d\n' %df1['NormDmnd'].size)
    df1['datetime'] = pd.to_datetime(df1['datetimestr'], format='%Y-%m-%d %H:%M')
    df1.set_index(['datetime'], inplace=True)
    df1.drop(['datetimestr'], axis=1, inplace=True) # drop redundant column
    df1.sort_index(inplace=True) # sort on datetime
    df1['day'] = df1.index.dayofyear
    df1['hour'] = df1.index.hour + df1.index.minute/60.
        
    # foutLog.write('Number of interval records after re-indexing: %d\n' %df1['NormDmnd'].size)
    foutLog.write('Time records start on: %s\n' %df1.index[0].strftime('%Y-%m-%d %H:%M'))
    foutLog.write('Time records end on: %s\n' %df1.index[-1].strftime('%Y-%m-%d %H:%M'))
    deltat = df1.index[-1]-df1.index[0]
    foutLog.write('Expected number of interval records: %d\n' %(deltat.total_seconds()/(60*15)+1))
    
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

    print('Opening plot file: %s' %(os.path.join(dirout, fnameout)))
    foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout)))
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    df3 = pd.DataFrame(index=np.arange(0, 24, 0.25), columns=np.arange(0,367))
    i = 1
    for cID in UniqueIDs:
        print ('Processing %s (%d of %d)' %(cID, i, len(UniqueIDs)))
        i += 1
        df2 = df1[df1['CustomerID']==cID]
        df3.iloc[:] = np.nan # resetting all values to nan to prevent backfilling from other customers
        df3 = df2.pivot(index='hour', columns='day', values='NormDmnd') 
        outputLoadHeatmap1h(pltPdf1, df3, fnamein+'/'+cID)

    #%% Closing plot files
    print('Closing plot files')
    foutLog.write('Closing plot files\n')
    pltPdf1.close()

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

if __name__ == "__main__":
    PlotHeatMaps(dirin='output/', fnamein='synthetic2.normalized.csv',
                 dirout='plots/', fnameout='HeatMaps.synthetic2.pdf',
                 dirlog='output/')
