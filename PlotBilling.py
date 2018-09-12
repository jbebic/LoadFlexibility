# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 15:32:41 2018

@author: jbebic

Plots billing data
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

def outputBillingPage(pltPdf, df1, title):
    fig, axes = plt.subplots(nrows=6, ncols=2,
                              figsize=(8.5,11),
                              sharex=True)
    
    fig.suptitle(title) # This titles the figure

    ymin = 0 # df1['Demand'].min()
    ymax = df1['Demand'].max()
    y2min = 0
    y2max = df1['TotalCharge'].cumsum().max()/12.*1.5 # total for the year, divided by 12 months, then multiplied by 1.5 to allow for a peak month
    month = 1
    for cix in np.arange(axes.shape[1]):
        col = axes[:,cix]
        for ax0 in col:
            df = df1[df1.index.month == month] # df = df1[df1['datetime'].dt.month == month]
            month += 1
            
            # ax0.set_title('Load and Billing')
            ax0.set_ylim([ymin,ymax])
            # ax0.set_ylabel('Demand [kWh]')
        
            # ax0.set_xlim([0,8760*4])
            # ax0.set_xticks(np.linspace(0, 8760*4, num=5).tolist())
            # ax0.set_xticklabels(np.linspace(0, 8760, num=5, dtype=np.int16).tolist())
            # ax0.set_xlabel('Day')
        
            ax0.set_aspect('auto')
            ax0.step(df['fractionalday'], df['Demand'],'C3', label='Demand [kWh]')
            ax0t = ax0.twinx()
            ax0t.set_ylim([y2min,y2max])
            ax0t.step(df['fractionalday'], df['TotalCharge'].cumsum(),'C2', label='Charges [$]')
    
    pltPdf.savefig() # Saves fig to pdf
    plt.close() # Closes fig to clean up memory
    return

def PlotBillingData(dirin='./', fnamein='IntervalData.billing.csv', ignoreCIDs='', considerCIDs='',
                 dirout='plots/', fnameout='Billing.pdf', 
                 dirlog='./', fnameLog='PlotBillingData.log'):

    #%% Version and copyright info to record on the log file
    codeName = 'PlotBillingData.py'
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
    df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                      header = 0, 
                      usecols = [0, 1, 2, 3, 4, 5, 6],
                      parse_dates = ['datetime'], 
                      names=['CustomerID', 'datetime', 'Demand', 'EnergyCharge', 'DemandCharge', 'FacilityCharge', 'TotalCharge']) # add dtype conversions
                      
    foutLog.write('Number of interval records read: %d\n' %df1['Demand'].size)
    # df1['datetime'] = pd.to_datetime(df1['datetimestr'], format='%Y-%m-%d %H:%M')
    # df1.set_index(['datetime'], inplace=True)
    # df1.drop(['datetimestr'], axis=1, inplace=True) # drop redundant column
    # df1.sort_index(inplace=True) # sort on datetime
        
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
        ignoreIDs = [x.replace(" ", "") for x in ignoreIDs]
        
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
        considerIDs = [x.replace(" ", "") for x in considerIDs]
        considerIDs = list(set(considerIDs)-set(ignoreIDs))
        UniqueIDs = list(set(UniqueIDs).intersection(considerIDs))
    else:
        considerIDs = list(set(UniqueIDs)-set(ignoreIDs))
        UniqueIDs = list(set(UniqueIDs).intersection(considerIDs))

    foutLog.write('Number of customer IDs after consider/ignore: %d\n' %len(UniqueIDs))

    df1.set_index(['CustomerID', 'datetime'], inplace=True)
    df1.sort_index(inplace=True) # sorts on CustomerID, then datetime
    
    df1['fractionalday'] = df1.index.get_level_values(1).day.values-1. + df1.index.get_level_values(1).hour.values/24. + df1.index.get_level_values(1).minute.values/60./24.
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    i = 1
    idx = pd.IndexSlice
    for cID in UniqueIDs:
        print ('Processing %s (%d of %d)' %(cID, i, len(UniqueIDs)))
        i += 1
        df2 = df1.loc[idx[cID,:]] # df2 = df1[df1['CustomerID']==cID]
        outputBillingPage(pltPdf1, df2, fnamein+'/'+cID)

    #%% Closing plot files
    print("Closing plot files")
    pltPdf1.close()

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

if __name__ == "__main__":
    fnamebase = 'synthetic20'
    PlotBillingData(dirin='testdata/', fnamein=fnamebase+'.billing.csv', # '.csv',
                     dirout='testdata/', fnameout=fnamebase+'.billing.pdf',
                     dirlog='testdata/')
