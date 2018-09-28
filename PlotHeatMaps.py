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

#%% Importing modules
from SupportFunctions import getData, logTime, createLog, findUniqueIDs

#%% Version and copyright info to record on the log file
codeName = 'PlotHeatMaps.py'
codeVersion = '1.2'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Jovan Bebic & Irene Berry, GE Global Research\n"


#%% Function Definitions
def outputLoadHeatmap1h(pltPdf, df1, title):
    """ creates an annual heatmap with daily bar charts for a single customer"""
    
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

def PlotHeatMaps(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='./', fnameout='HeatMaps.pdf', 
                 dirlog='./', fnameLog='PlotHeatMaps.log',
                 skipPlots = False):
    
    """ Create pdf with one page per customer showing heat map of demand and daily bar charts """

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog)
    df1['day'] = df1.index.dayofyear
    df1['hour'] = df1.index.hour + df1.index.minute/60.

    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs, considerCIDs)

    print('Opening plot file: %s' %(os.path.join(dirout, fnameout)))
    foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout)))
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    df3 = pd.DataFrame(index=np.arange(0, 24, 0.25), columns=np.arange(0,367))
    i = 1
    figN = 0
    for cID in UniqueIDs:
        print ('Processing %s (%d of %d) ' %(cID, i, len(UniqueIDs)))
        i += 1
        try:
            df2 = df1[df1['CustomerID']==cID]
            df3.iloc[:] = np.nan # resetting all values to nan to prevent backfilling from other customers
            df3 = df2.pivot(index='hour', columns='day', values='NormDmnd') 
            outputLoadHeatmap1h(pltPdf1, df3, fnamein+'/'+cID)
            figN += 1
        except:
            foutLog.write("\n*** Unable to create heatmap for %s " %cID )
            print("*** Unable to create heatmap for %s " %cID)
            
    foutLog.write('Number of customer IDs for which figures were generated: %d\n' % figN)
    print('Number of customer IDs for which figures were generated: ' + str( figN))

    # Closing plot files
    print('Closing plot files')
    foutLog.write('Closing plot files\n')
    pltPdf1.close()

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

if __name__ == "__main__":
    PlotHeatMaps(dirin='output/', fnamein='synthetic2.normalized.csv',
                 dirout='plots/', fnameout='HeatMaps.synthetic2.pdf',
                 dirlog='output/')