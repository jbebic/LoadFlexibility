# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 15:57:51 2018

@author: 200018380
"""
#%% Importing all the necessary Python packages
import pandas as pd # multidimensional data analysis
import numpy as np # vectorized calculations
from datetime import datetime # time stamps
from datetime import date # date
import os # operating system interface
import matplotlib.pyplot as plt # plotting 
import matplotlib.backends.backend_pdf as dpdf # pdf output
from copy import copy as copy
import pylab
import warnings
warnings.filterwarnings("ignore")

#%% Importing supporting modules
from SupportFunctions import findUniqueIDs, getData, logTime, createLog,  assignDayType, getDataAndLabels
#from UtilityFunctions import AssignRatePeriods, readTOURates
#from NormalizeLoads import NormalizeGroup
from PlotHeatMaps import outputThreeHeatmaps, outputThreeHeatmapsGroup

#%% Version and copyright info to record on the log file
codeName = 'CustomerReport.py'
codeVersion = '1.0'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Irene Berry, GE Global Research\n"


#%% Individual Report
#def singleReport()


#%% Create Reports by considerCIDs list
def CreateCustomerReports(dirin='./', fnamein='IntervalData.normalized.csv', considerCIDs='',
                    dirin_group='./', fnamein_group = 'GroupData.normalized.csv', leaderFlag=True, 
                    dirout='./', fnameout='CustomerReport.pdf', 
                    dirlog='./', fnameLog='CreateCustomerReport.log'):

    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "CreateCustomerReports", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    # load data from file, find initial list of unique IDs. Update log file    
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin,  fnamein, foutLog, datetimeIndex=True)
    df1['day'] = df1.index.dayofyear
    df1['hour'] = df1.index.hour + df1.index.minute/60.
    df1['EnergyCost'] = df1['EnergyCharge'].values / df1['Demand'].values * 100

    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs='', considerCIDs=considerCIDs)
    
    # load GROUP data from file, find initial list of unique IDs. Update log file    
    df_group, UniqueIDs_group, foutLog = getDataAndLabels(dirin_group,  fnamein_group, foutLog, datetimeIndex=True)
    df_group['day'] = df_group.index.dayofyear
    df_group['hour'] = df_group.index.hour + df_group.index.minute/60.
    df_group['EnergyCost'] = df_group['EnergyCharge'].values / df_group['Demand'].values * 100

    if not(leaderFlag):
        groupName='Average Leader'
    else:
        groupName='Others'
    

    # loop over each CID
    for cid in UniqueIDs:

        print('Opening plot file: %s' %(os.path.join(dirout, fnameout.replace('.pdf', '_' + cid + '.pdf'))))
        foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout.replace('.pdf', '_' + cid + '.pdf'))))
        pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout.replace('.pdf', '_' + cid + '.pdf')))
        
        
        outputThreeHeatmaps(pltPdf1, df1=df1,  title=cid, cid=cid, foutLog=foutLog)
        
        outputThreeHeatmapsGroup(pltPdf1, df0=df1, df1=df_group, title=groupName, cid=groupName, foutLog=foutLog)
        
        # Closing plot files
        print('Closing plot files')
        foutLog.write('Closing plot files\n')
        pltPdf1.close()
    
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
        
    return 