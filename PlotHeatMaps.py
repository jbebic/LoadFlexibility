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
from SupportFunctions import getData, logTime, createLog, findUniqueIDs, getDataAndLabels

#%% Version and copyright info to record on the log file
codeName = 'PlotHeatMaps.py'
codeVersion = '1.5'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Jovan Bebic & Irene Berry, GE Global Research\n"

#%% Internal-Facing Function Definitions
def outputLoadHeatmap(pltPdf, df1,  title, cid, foutLog, weeklyBox=True, varName='NormDmnd'):
    """ creates an annual heatmap with daily bar charts for a single customer"""
    
    df2 = df1[df1['CustomerID']==cid]
    
    fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1,figsize=(8,6),sharex=False)
    fig.suptitle(title) # This titles the figure
    plt.subplots_adjust(wspace=0.3,hspace=0.3 )   
    
    ax0.set_title('Load [pu]') 
    ax0.set_ylabel('Hour')
    ax0.set_xlabel('Day of Year')
    ax0.set_xlim([0,365])
    ax0.set_ylim([0,24*4])
    ax0.set_yticks(np.linspace(0, 96, num=5).tolist())
    ax0.set_yticklabels(np.linspace(0, 24, num=5, dtype=np.int16).tolist())
    ax0.set_yticklabels(['0', '6', '12', '18', '24'])        

    cmin = 0.0
    ax1.set_ylabel('Load [pu]')
    if weeklyBox:
        ax1.set_xlabel('Week')
        ax1.set_xlim([0,52])
        ax1.set_xticks(np.arange(0, 52, step=5).tolist())
    else:
        ax1.set_xlabel('Day')
        ax1.set_xlim([0,365])
        ax1.set_xticks(np.arange(0, 365, step=50).tolist())
    
    df3 = pd.DataFrame(index=np.arange(0, 24, 0.25), columns=np.arange(0,367))
    df3.iloc[:] = np.nan # resetting all values to nan to prevent backfilling from other customers
    
    df2 = df2.assign(week =pd.Series(df2.index.week,index=df2.index))
    
    if weeklyBox:
        weeklyData = []
        for wk in list(set(df2['week'])):    
            weeklyData.append(df2.loc[df2['week']==wk,varName].values)
        
    try:
        
        if np.min(df2[varName])<-0.01:
            print('creating delta heatmap')
            # delta plot
            df3 = df2.pivot(index='hour', columns='day', values=varName) 
            cmax = np.ceil( df3.max().max() * 4 ) / 4
            im0 = ax0.imshow(df3.iloc[:,:], interpolation='none', #'nearest'
                                                  cmap='Spectral_r', 
                                                  origin='lower', 
                                                  vmin = -cmax, 
                                                  vmax = cmax)
            
            if weeklyBox:
                ax1.boxplot(weeklyData, manage_xticks = False)
            else:
                ax1.boxplot(df3.values, manage_xticks = False)
            ax1.set_ylim([-cmax,cmax]) 
            ax0.set_aspect('auto')
            ax1.set_aspect('auto')
            fig.colorbar(im0, ax=[ax0,ax1])
            
        else:
            # min of zero
            df3 = df2.pivot(index='hour', columns='day', values=varName) 
            cmax = np.ceil( df3.max().max() * 4 ) / 4
            im0 = ax0.imshow(df3.iloc[:,:], interpolation='none', #'nearest'
                                                  cmap='viridis', 
                                                  origin='lower', 
                                                  vmin = cmin, 
                                                  vmax = cmax)
            
            if weeklyBox:
                ax1.boxplot(weeklyData, manage_xticks = False)
            else:
                ax1.boxplot(df3.values, manage_xticks = False)
            ax1.set_ylim([0,cmax]) 
            ax0.set_aspect('auto')
            ax1.set_aspect('auto')
            fig.colorbar(im0, ax=[ax0,ax1])
        
        pltPdf.savefig() # Saves fig to pdf
        plt.close() # Closes fig to clean up memory
        successFlag = True
        
    except:
        
        successFlag = False
        foutLog.write("\n*** Unable to create duration plot for %s " %cid )
        print("*** Unable to create duration plot for %s " %cid)
        
        try:
            plt.close()    
        except:
            pass
    
    return successFlag


def outputBillingHeatmap(pltPdf, df1,  title, cid, foutLog):
    """ creates an annual heatmap with daily bar charts for a single customer"""
    
    df2 = df1[df1['CustomerID']==cid]
    
    # figure creation & formatting
    fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1,figsize=(8,6),sharex=False)
    fig.suptitle(title) # This titles the figure
    plt.subplots_adjust(wspace=0.3,hspace=0.3 )   
    
    # formatting for upper plot
    ax0.set_title('Energy Cost [c/kWh]') 
    ax0.set_ylabel('Hour')
    ax1.set_xlabel('Day of Year')
    ax1.set_xlim([0,365])
    ax0.set_ylim([0,24*4])
    ax0.set_yticks(np.linspace(0, 96, num=5).tolist())
    ax0.set_yticklabels(np.linspace(0, 24, num=5, dtype=np.int16).tolist())
    ax0.set_yticklabels(['0', '6', '12', '18', '24'])     
    
    # formatting for lower plot
    ax1.set_title('Energy Charge [$]') 
    ax1.set_ylabel('Hour')
    ax1.set_xlabel('Day of Year')
    ax1.set_xlim([0,365])
    ax1.set_ylim([0,24*4])
    ax1.set_yticks(np.linspace(0, 96, num=5).tolist())
    ax1.set_yticklabels(np.linspace(0, 24, num=5, dtype=np.int16).tolist())
    ax1.set_yticklabels(['0', '6', '12', '18', '24'])        

    cmin = 0.0
    df3 = pd.DataFrame(index=np.arange(0, 24, 0.25), columns=np.arange(0,367))
    df3.iloc[:] = np.nan # resetting all values to nan to prevent backfilling from other customers
    try:
        df3 = df2.pivot(index='hour', columns='day', values="EnergyCost") 
        df3 = df3.fillna(method='ffill')
        df3 = df3.fillna(method='bfill')
        cmax = np.ceil( df3.max().max() * 4 ) / 4
        im0 = ax0.imshow(df3.iloc[:,:], interpolation='none', #'nearest'
                                              cmap= 'viridis',  
                                              origin='lower', 
                                              vmin = cmin, 
                                              vmax = cmax)
        
        ax0.set_aspect('auto')
        fig.colorbar(im0, ax=[ax0])
        
        df4 = df2.pivot(index='hour', columns='day', values="EnergyCharge") 
        cmax = np.ceil( df4.max().max() * 4 ) / 4
        im0 = ax1.imshow(df4.iloc[:,:], interpolation='none', #'nearest'
                                              cmap='viridis',  
                                              origin='lower', 
                                              vmin = cmin, 
                                              vmax = cmax)
        
        ax1.set_aspect('auto')
        fig.colorbar(im0, ax=[ax1])        
        pltPdf.savefig() # Saves fig to pdf
        plt.close() # Closes fig to clean up memory
        successFlag = True
        
        
    except:
        successFlag = False
        foutLog.write("\n*** Unable to create duration plot for %s " %cid )
        print("*** Unable to create duration plot for %s " %cid)
        
        try:
            plt.close()    
        except:
            pass
    
    return successFlag



def outputThreeHeatmaps(pltPdf, df1,  title, cid, foutLog):
    """ creates an annual heatmap with daily bar charts for a single customer"""
    
    if len(set(df1['CustomerID']))>1:
        df2 = df1[df1['CustomerID']==cid]
    else:
        df2 = df1.copy()
    
    # figure creation & formatting
    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, ncols=1,figsize=(8,6),sharex=True)
    fig.suptitle(title) # This titles the figure
    plt.subplots_adjust(wspace=0.25,hspace=0.5, left=0.1, right = 0.75 )   
    
    # formatting for upper plot
    ax0.set_title('Price [c/kWh]') 
    ax0.set_ylabel('Hour')
    ax0.set_ylim([0,24*4])
    ax0.set_yticks(np.linspace(0, 96, num=5).tolist())
    ax0.set_yticklabels(np.linspace(0, 24, num=5, dtype=np.int16).tolist())
    ax0.set_yticklabels(['0', '6', '12', '18', '24'])     
    ax0.set_xlim([0,365])
    
    # formatting for upper plot
    ax1.set_title('Demand [MWh]') 
    ax1.set_ylabel('Hour')
    ax1.set_ylim([0,24*4])
    ax1.set_yticks(np.linspace(0, 96, num=5).tolist())
    ax1.set_yticklabels(np.linspace(0, 24, num=5, dtype=np.int16).tolist())
    ax1.set_yticklabels(['0', '6', '12', '18', '24'])     
    ax1.set_xlim([0,365])
    
    # formatting for lower plot
    ax2.set_title('Energy Charge [$]') 
    ax2.set_ylabel('Hour')
    ax2.set_ylim([0,24*4])
    ax2.set_yticks(np.linspace(0, 96, num=5).tolist())
    ax2.set_yticklabels(np.linspace(0, 24, num=5, dtype=np.int16).tolist())
    ax2.set_yticklabels(['0', '6', '12', '18', '24'])        
    ax2.set_xlabel('Day of Year')
    ax2.set_xlim([0,365])
    
    cmin = 0.0
    df3 = pd.DataFrame(index=np.arange(0, 24, 0.25), columns=np.arange(0,367))
    df3.iloc[:] = np.nan # resetting all values to nan to prevent backfilling from other customers
    
    try:
        
        # cost from TOU
        df3 = df2.pivot(index='hour', columns='day', values="EnergyCost") 
        df3 = df3.fillna(method='ffill')
        df3 = df3.fillna(method='bfill')
        cmax = np.ceil( df3.max().max()  ) 
        im0 = ax0.imshow(df3.iloc[:,:], interpolation='none', #'nearest'
                                              cmap= 'viridis',  
                                              origin='lower', 
                                              vmin = cmin, 
                                              vmax = cmax)
        ax0.set_aspect('auto')
        fig.colorbar(im0, ax=[ax0])       
        
        
        # total demand
        df5 = df2.pivot(index='hour', columns='day', values="Demand") 
        cmax = np.ceil( df5.max().max() * 4 ) / 4
        im0 = ax1.imshow(df5.iloc[:,:], interpolation='none', #'nearest'
                                              cmap='viridis',  
                                              origin='lower', 
                                              vmin = cmin, 
                                              vmax = cmax)
        
        ax1.set_aspect('auto')
        fig.colorbar(im0, ax=[ax1]) 
        ax1.text(s=str(round(np.sum(df5.values)/1000,1) ) ,
                   x=365*0.9/0.6, y=96*0.55,verticalalignment="bottom",horizontalalignment="center",fontsize=30)      
        ax1.text(s='GWh',
                   x=365*0.9/0.6, y=96*0.54,verticalalignment="top",horizontalalignment="center",fontsize=12)      
        
        
        # total charge
        df4 = df2.pivot(index='hour', columns='day', values="EnergyCharge") 
        cmax = np.ceil( df4.max().max() * 4 ) / 4
        im0 = ax2.imshow(df4.iloc[:,:], interpolation='none', #'nearest'
                                              cmap='viridis',  
                                              origin='lower', 
                                              vmin = cmin, 
                                              vmax = cmax)
        
        ax2.set_aspect('auto')
        fig.colorbar(im0, ax=[ax2]) 
        ax2.text(s="$" + "{:,}".format(int(round(np.sum(df4.values),0))),
                   x=365*0.9/0.6, y=96*0.55,verticalalignment="bottom",horizontalalignment="center",fontsize=30)      



        ax0.text(s=str(round(np.sum(df4.values)/np.sum(df5.values)*100,1)),
                   x=365*0.9/0.6, y=96*0.55,verticalalignment="bottom",horizontalalignment="center",fontsize=30)      
        ax0.text(s='₵/kWh',
                   x=365*0.9/0.6, y=96*0.55,verticalalignment="top",horizontalalignment="center",fontsize=12)      
        
        pltPdf.savefig() # Saves fig to pdf
        plt.close() # Closes fig to clean up memory
        successFlag = True
        
    except:
        successFlag = False
        foutLog.write("\n*** Unable to create heat map for %s " %cid )
        print("*** Unable to create heat map for %s " %cid)
        
        try:
            plt.close()    
        except:
            pass
    
    return successFlag

def outputThreeHeatmapsGroup(pltPdf,df0,  df1,  title, cid, foutLog):
    """ creates an annual heatmap with daily bar charts for a single customer"""
    
    cids = list(set(df0['CustomerID']))
    df0 = df0[df0['CustomerID']==cids[0]]
    df2 = df1.copy()
    
    # figure creation & formatting
    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, ncols=1,figsize=(8,6),sharex=True)
    fig.suptitle(title) # This titles the figure
    plt.subplots_adjust(wspace=0.25,hspace=0.5, left=0.1, right = 0.75 )   
        
    # formatting for upper plot
    ax0.set_title('Price [c/kWh]') 
    ax0.set_ylabel('Hour')
    ax0.set_ylim([0,24*4])
    ax0.set_yticks(np.linspace(0, 96, num=5).tolist())
    ax0.set_yticklabels(np.linspace(0, 24, num=5, dtype=np.int16).tolist())
    ax0.set_yticklabels(['0', '6', '12', '18', '24'])     
    ax0.set_xlim([0,365])
    
    # formatting for upper plot
    ax1.set_title('Demand [MWh]') 
    ax1.set_ylabel('Hour')
    ax1.set_ylim([0,24*4])
    ax1.set_yticks(np.linspace(0, 96, num=5).tolist())
    ax1.set_yticklabels(np.linspace(0, 24, num=5, dtype=np.int16).tolist())
    ax1.set_yticklabels(['0', '6', '12', '18', '24'])     
    ax1.set_xlim([0,365])
    
    # formatting for lower plot
    ax2.set_title('Energy Charge [$]') 
    ax2.set_ylabel('Hour')
    ax2.set_ylim([0,24*4])
    ax2.set_yticks(np.linspace(0, 96, num=5).tolist())
    ax2.set_yticklabels(np.linspace(0, 24, num=5, dtype=np.int16).tolist())
    ax2.set_yticklabels(['0', '6', '12', '18', '24'])        
    ax2.set_xlabel('Day of Year')
    ax2.set_xlim([0,365])
    
    cmin = 0.0
    df3 = pd.DataFrame(index=np.arange(0, 24, 0.25), columns=np.arange(0,367))
    df3.iloc[:] = np.nan # resetting all values to nan to prevent backfilling from other customers
    try:
        
        # cost from TOU
        df3 = df0.pivot(index='hour', columns='day', values="EnergyCost") 
        df3 = df3.fillna(method='ffill')
        df3 = df3.fillna(method='bfill')
        cmax = np.ceil( df3.max().max()  ) 
        im0 = ax0.imshow(df3.iloc[:,:], interpolation = 'none', #'nearest'
                                              cmap = 'viridis',  
                                              origin = 'lower', 
                                              vmin = cmin, 
                                              vmax = cmax)
        ax0.set_aspect('auto')
        fig.colorbar(im0, ax=[ax0]) 
        
        # total charge
        df5 = df2.pivot(index='hour', columns='day', values="Demand") 
        cmax = np.ceil( df5.max().max() * 4 ) / 4
        im0 = ax1.imshow(df5.iloc[:,:], interpolation = 'none', #'nearest'
                                              cmap = 'viridis',  
                                              origin = 'lower', 
                                              vmin = cmin, 
                                              vmax = cmax)
        ax1.set_aspect('auto')
        fig.colorbar(im0, ax=[ax1])         
        ax1.text(s=str(round(np.sum(df5.values)/1000,1) ) ,
                   x=365*0.9/0.6, y=96*0.55,verticalalignment="bottom",horizontalalignment="center",fontsize=30)      
        ax1.text(s='GWh',
                   x=365*0.9/0.6, y=96*0.54,verticalalignment="top",horizontalalignment="center",fontsize=12)      

        # total charge
        df4 = df2.pivot(index='hour', columns='day', values="EnergyCharge") 
        cmax = np.ceil( df4.max().max() * 4 ) / 4
        im0 = ax2.imshow(df4.iloc[:,:], interpolation = 'none', #'nearest'
                                              cmap = 'viridis',  
                                              origin = 'lower', 
                                              vmin = cmin, 
                                              vmax = cmax)
        ax2.set_aspect('auto')
        fig.colorbar(im0, ax=[ax2])  
        ax2.text(s="$" + "{:,}".format(int(round(np.sum(df4.values),0))),
                   x=365*0.9/0.6, y=96*0.55,verticalalignment="bottom",horizontalalignment="center",fontsize=30)      
        ax0.text(s=str(round(np.sum(df4.values)/np.sum(df5.values)*100,1)),
                   x=365*0.9/0.6, y=96*0.55,verticalalignment="bottom",horizontalalignment="center",fontsize=30)      
        ax0.text(s='₵/kWh',
                   x=365*0.9/0.6, y=96*0.55,verticalalignment="top",horizontalalignment="center",fontsize=12)      
        
        
        pltPdf.savefig() # Saves fig to pdf
        plt.close() # Closes fig to clean up memory
        successFlag = True
        
    except:
        successFlag = False
        foutLog.write("\n*** Unable to create heat map for %s " %cid )
        print("*** Unable to create heat map for %s " %cid)
        try:
            plt.close()    
        except:
            pass
    
    return successFlag

#%% External-Facing Fuctions Definitions
def PlotHeatMaps(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='./', fnameout='HeatMaps.pdf', 
                 dirlog='./', fnameLog='PlotHeatMaps.log',
                 weeklyBox = True, varName='NormDmnd', column=2):    
    
    """ Create pdf with one page per customer showing heat map of demand and weekly (or daily) box plots """

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, 'PlotHeatMaps', codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # load data from file, find initial list of unique IDs. Update log file
#    df1, UniqueIDs, foutLog = getDataWithLabels(dirin, fnamein, foutLog, varName=varName, usecols=[0,1,column])
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin, fnamein, foutLog)
    df1['day'] = df1.index.dayofyear
    df1['hour'] = df1.index.hour + df1.index.minute/60.

    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs, considerCIDs)

    print('Opening plot file: %s' %(os.path.join(dirout, fnameout)))
    foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout)))
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    i = 1
    figN = 0
    for cID in sorted(list(set(UniqueIDs))):
        print ('Processing %s (%d of %d) ' %(cID, i, len(UniqueIDs)))
        i += 1
        successFlag = outputLoadHeatmap(pltPdf1, df1,  fnamein+'/'+cID, cID, foutLog, weeklyBox=weeklyBox, varName=varName)
        if successFlag:
            figN += 1
            
    foutLog.write('\nNumber of customer IDs for which figures were generated: %d\n' % figN)
    print('Number of customer IDs for which figures were generated: ' + str( figN))

    # Closing plot files
    print('Closing plot files')
    foutLog.write('Closing plot files\n')
    pltPdf1.close()

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

def Plot3HeatMaps(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='./', fnameout='ThreeHeatMaps.pdf', 
                 dirlog='./', fnameLog='Plot3HeatMaps.log'):    
    
    """ Create pdf with one page per customer showing three heat maps: rate, demand, charge """

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, "Plot3HeatMaps", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin, fnamein, foutLog) #, varName=["Demand", "EnergyCharge"], usecols=[0,1,2,3])
    df1['day'] = df1.index.dayofyear
    df1['hour'] = df1.index.hour + df1.index.minute/60.
    df1['EnergyCost'] = df1['EnergyCharge'].values / df1['Demand'].values * 100
    
    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs, considerCIDs)

    print('Opening plot file: %s' %(os.path.join(dirout, fnameout)))
    foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout)))
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    i = 1
    figN = 0
    for cID in sorted(list(set(UniqueIDs))):
        print ('Processing %s (%d of %d) ' %(cID, i, len(UniqueIDs)))
        i += 1
        successFlag = outputThreeHeatmaps(pltPdf1, df1,  fnamein+'/'+cID, cID, foutLog)
        if successFlag:
            figN += 1
            
    foutLog.write('\nNumber of customer IDs for which figures were generated: %d\n' % figN)
    print('Number of customer IDs for which figures were generated: ' + str( figN))

    # Closing plot files
    print('Closing plot files')
    foutLog.write('Closing plot files\n')
    pltPdf1.close()

    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

def PlotHeatMapOfBilling(dirin='./', fnamein='IntervalData.normalized.csv', ignoreCIDs='', considerCIDs='',
                 dirout='./', fnameout='HeatMaps.pdf', 
                 dirlog='./', fnameLog='PlotHeatMapsOfBilling.log'):    
    
    """ Create pdf with one page per customer showing heat map of demand and weekly (or daily) box plots """

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = createLog(codeName, "PlotHeatMapOfBilling", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # load data from file, find initial list of unique IDs. Update log file
    df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog, varName=["Demand", "EnergyCharge"], usecols=[0,1,2,3])
    df1['day'] = df1.index.dayofyear
    df1['hour'] = df1.index.hour + df1.index.minute/60.
    df1['EnergyCost'] = df1['EnergyCharge'] / df1['Demand'] * 100
    
    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs, considerCIDs)

    print('Opening plot file: %s' %(os.path.join(dirout, fnameout)))
    foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout)))
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    i = 1
    figN = 0
    for cID in sorted(list(set(UniqueIDs))):
        print ('Processing %s (%d of %d) ' %(cID, i, len(UniqueIDs)))
        i += 1
        successFlag = outputBillingHeatmap(pltPdf1, df1,  fnamein+'/'+cID, cID, foutLog)
        if successFlag:
            figN += 1
            
    foutLog.write('\nNumber of customer IDs for which figures were generated: %d\n' % figN)
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