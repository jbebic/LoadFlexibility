# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 11:51:10 2018

@author: berryi
"""
#%% Importing all the necessary Python packages
import pandas as pd # multidimensional data analysis
import numpy as np # vectorized calculations
from datetime import datetime # time stamps
from datetime import date
import os # operating system interface
import matplotlib.pyplot as plt # plotting 
import matplotlib.backends.backend_pdf as dpdf # pdf output
from copy import copy as copy

#%% Importing supporting modules
from SupportFunctions import getData, logTime, createLog,  assignDayType, getDataAndLabels
from UtilityFunctions import AssignRatePeriods, readTOURates
from NormalizeLoads import NormalizeGroup

#%% Version and copyright info to record on the log file
codeName = 'GroupAnalysis.py'
codeVersion = '1.7'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Irene Berry, GE Global Research\n"

# %% Basic Function Definitions
def deltaLoadsFunction(df1, df2):
    df3 = df2.copy()
    df3['NormDelta'] = df1['NormDmnd'] - df2['NormDmnd']
    df3['AbsDelta']  = df3['NormDelta'] * ( df2['DailyAverage']  )
    df3['Leaders'] = df1['Demand'].copy()
    df3['Others'] = df2['Demand'].copy()
    return df3

#%% Add Individual Lines or Figures
def plotDailyLoads(ax0, df, lw=1, c='b', ls='-', label=''):
    """ adds specific day's load curve to axis """
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Normalized Load [pu]')
    ax0.set_xlabel('Hour of the Day [h]')
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    y = [yy for yy in range(-40, 41,1)]
    ax0.set_yticks(y )  
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    ax0.plot(np.arange(df.shape[0]), df['NormDmnd'], ls,  lw=2, c=c, label=label)
    return ax0

def plotDailyDeltaLoad(ax0, df, lw=1, c='b', ls='-', fillFlag=True, shiftFlag=False):
    
    """ adds specific day's power & energy deltas to axis """
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Delta in Loads [pu]')
    ax0.set_xlabel('Hour of the Day [h]')
    ax0.set_xlim([0,df.shape[0]])
    ix = np.max(df.loc[df['NormDelta']<0].index)
    L = len( df.loc[ix:])    
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    y = [yy/2 for yy in range(-80, 81,1)]
    ax0.set_yticks(y)  
    ax0.xaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5) 
    if shiftFlag:
        X = [x-L/4 for x in range(0, 28,4)]
        x2 = []
        for x in X:
            if x>24:  
                x2.append( str(int(x-24)) )
            elif x<0:
                x2.append( str(int(24+x)) )
            else:
                x2.append( str(int(x)  )) 
        ax0.set_xticklabels(x2)  
        ax0.plot(np.arange(df.shape[0]),   np.roll(df['NormDelta'],L),  label='Load [pu]')     
    else:
        ax0.set_xticklabels([str(x) for x in range(0, 28,4)])          
        if fillFlag:
            ax0.fill_between(np.arange(df.shape[0]), 0,  df['NormDelta'],  label='Load [pu]')   
        else:
            ax0.plot(np.arange(df.shape[0]),   df['NormDelta'],  label='Load [pu]')      
    ax0.plot([0 , df.shape[0] ], [0.0, 0.0], lw=1, color='gray', alpha=1.0)
    return ax0, np.max(y)

def plotDailyDeltaEnergy(ax0, df, lw=1, c='b', ls='-'):
    
    """ adds specific day's power & energy deltas to axis """    
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Delta in Energy [puh]')
    ax0.set_xlabel('Hour of the Day [h]')
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    y = [yy for yy in range(-40, 41,1)]
    ax0.set_yticks(y)  
    ax0.xaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5) 
    y = np.cumsum(df['NormDelta'])/4
    y = y - np.min(y)
    ax0.plot(np.arange(df.shape[0]), y, ls, lw=lw*2, c='purple', label='Energy [pu-h]')
    return ax0, np.max(y)

def plotHistogram(ax2, dailyEnergy, shiftedEnergy):
    """ adds histogram of daily shifted energy """
    y = np.asarray(shiftedEnergy)/np.asarray(dailyEnergy)*100
    yMax = np.ceil(np.max(y))
    ax2.hist(y,bins='auto', color='purple', lw=0, alpha=0.5)   
    ax2.set_xlabel('Shiftable Energy [% of Daily Energy]')
    ax2.set_ylabel('Number of Days')
    ax2.set_xlim([0,yMax])  
    ax2.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax2.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    return ax2

def plotDeltaDuration(ax0, df, lw=1, c='steelblue', ls='-', a=1.0, varName='AbsDelta', addText=False, asPercentage=False):
    """ adds specific day's duration curve to axis """
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_xlabel('Duration [h]')
    x = [x for x in range(-int(df.shape[0]),int(df.shape[0])+int(df.shape[0]/(24/4)), int(df.shape[0]/(24/4)))]
    ax0.set_xticks(x)
    ax0.set_xticklabels([str(np.abs(x)) for x in range(-24, 28,4)])  
    ax0.set_xlim([-int(df.shape[0]*20/24),  int(df.shape[0]*20/24) ])   
    df1 = df.copy()
    charge = df1.loc[df1[varName]>0]
    discharge = df1.loc[df1[varName]<0]    
    charge = charge.sort_values(varName, ascending=True)
    discharge = discharge.sort_values(varName, ascending=False)   
    
    if asPercentage:
        
        ax0.step(-1.*np.arange(charge.shape[0]), charge[varName] /np.max(df1['Others']) *100,  ls, lw=lw, c=c, alpha=a)
        ax0.step(np.arange(discharge.shape[0]), discharge[varName] /np.max(df1['Others']) *100,  ls, lw=lw, c=c, alpha=a)
        ymax = np.max([ np.max(abs(charge[varName]) /np.max(df1['Others']) *100 ), np.max(abs(discharge['NormDelta'])/np.max(df1['Others']) *100)  ])
        ymaxC = np.max(charge[varName]) /np.max(df1['Others']) *100 
        ymaxD = np.min(discharge[varName]) /np.max(df1['Others']) *100 
        ax0.set_ylabel('Shfitable Load [%]')
        
    else:
        
        ax0.step(-1.*np.arange(charge.shape[0]), charge[varName]  ,  ls, lw=lw, c=c, alpha=a)
        ax0.step(np.arange(discharge.shape[0]), discharge[varName] ,  ls, lw=lw, c=c, alpha=a)
        ymax = np.max([ np.max(abs(charge[varName])) , np.max(abs(discharge[varName]))  ])    
        ymaxC = np.max(charge[varName]) * 4.0
        ymaxD = np.min(discharge[varName]) * 4.0
        ax0.set_ylabel('Shfitable Load [MW]')
        
    # add gridlines
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    
    if addText:
        
        ax0.plot( [-int(df.shape[0]*24/24),  int(df.shape[0]*24/24)], [ 0.1,  0.1 ], "--", lw=1, color='gray', alpha=0.5)
        ax0.plot( [-int(df.shape[0]*24/24),  int(df.shape[0]*24/24)], [-0.1, -0.1],  "--",  lw=1, color='gray', alpha=0.5) 
        chargeCrossing = -1 * len( charge[charge[varName] <0.1] )
        disCrossing = len( discharge[discharge[varName] >-0.1] )
        chargeHours = len(charge[charge[varName] >0.1] ) /4
        dischargeHours =  len(discharge[discharge[varName] <-0.1] ) /4
        ax0.plot([chargeCrossing , chargeCrossing ], [-5.0, 5.0], "--", lw=1, color='gray', alpha=0.5)
        ax0.plot([disCrossing , disCrossing ], [-5.0, 5.0], "--", lw=1, color='gray', alpha=0.5)
        
        # add text label of CHARGE HOURS
        ax0.text(s=str(int(round(chargeHours,0))) + 'hr',
                   x=-1.*charge.shape[0], y= np.max(charge[varName] ),
                   verticalalignment="bottom",horizontalalignment="center",
                   fontsize=8, fontweight='bold')
        
        # add text label of DISCHARGE HOURS
        ax0.text(s=str(int(round(dischargeHours,0)) )+ 'hr',
                   x=discharge.shape[0], y= np.min(discharge[varName] ),
                   verticalalignment="top",horizontalalignment="center",
                   fontsize=8, fontweight='bold')
        
        # add text label of GAP HOURS
        ax0.text(s=str(int(round((disCrossing-chargeCrossing)/4,0)) )+ 'hr',
                   x=(disCrossing+chargeCrossing)/2, y= 0.1,
                   verticalalignment="bottom",horizontalalignment="center",
                   fontsize=8, fontweight='bold') 
    
    return ax0, ymax, ymaxC, ymaxD

def plotShiftedEnergy(ax0, df, lw=1, c='b', ls='-',a=1.0):
    """ adds specific day's shifted energy to axis """
    df = df.sort_values(by='datetime', ascending=True)                  
    y = np.cumsum(df['NormDelta'])
    y = y - np.min(y)  
    ax0.plot(np.arange(df.shape[0]), y, ls, lw=lw, c=c, alpha=a)
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    return ax0, np.max(y)

def formatShiftedEnergy(ax0):
    """ formats the axis on which shifted energy is plotted """
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    ax0.set_ylabel('Shiftable Energy [MWh]')
    ax0.set_xlabel('Hour of the Day')
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])
    return

#%% Create Entire Page of Figures
def annualSummaryPage(pltPdf1, df1, fnamein, normalized=False):
    
    """ create page summary for specific month & add to pdf """
    
    # initialize figure
    fig = plt.figure(figsize=(8,6))
    fig.suptitle(fnamein + " / entire year" )  
    plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
    ax0 = plt.subplot2grid((2, 2), (0, 0),  fig=fig)
    ax1 = plt.subplot2grid((2, 2), (0, 1),  fig=fig)
    ax2 = plt.subplot2grid((2, 2), (1, 0),  fig=fig)
    ax3 = plt.subplot2grid((2, 2), (1, 1),  fig=fig)
    
    # initialize variables
    month = df1.index.month
    day = df1.index.day
    ymax = 0
    yMax = 0
    yMaxD = 0.0
    yMaxP = 0.0
    yMaxD_D = 0.0
    yMaxD_C = 0.0
    yMaxP_D = 0.0
    yMaxP_C = 0.0
    
    # iterate over each month
    dailyEnergy = []
    shiftedEnergy = []
    for m in range(1, 13,1):
        days = list(set(df1.loc[(month==m)].index.day))
        
        # plot shifted energy
        for d in days:
            relevant = (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                pass
            else:
                dailyEnergy.append( np.sum( df1.loc[relevant,'Others'].values) )
                ax1, ymax = plotShiftedEnergy(ax1, df1.loc[relevant], c='purple', a=0.1)
                yMax  = np.max([yMax, ymax])
                shiftedEnergy.append(ymax)
        yMax = np.ceil(yMax)
        ax1.set_ylim([0,yMax])
        ax1.set_ylabel('Shiftable Energy [MWh]')
            
        # plot load-duration
        for d in days:
            relevant = (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                pass
            else:
                ax0, ymax, ymaxC, ymaxD = plotDeltaDuration(ax0, df1.loc[relevant], c='steelblue', a=0.1, addText=False) 
                yMaxD = np.max([yMaxD , ymax])
                yMaxD_C = np.max([yMaxD_C , ymaxC]) 
                yMaxD_D = np.min([yMaxD_D , ymaxD])
        ax0.set_ylim([-yMaxD , yMaxD ])
        
        # iterate for each day in month
        for d in days:
            relevant = (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                pass
            else:
                ax2, ymax, ymaxC, ymaxD = plotDeltaDuration(ax2, df1.loc[relevant], c='steelblue', a=0.1, addText=False, asPercentage=True) 
        yMaxP_C = np.max([yMaxP_C , ymaxC]) 
        yMaxP_D = np.min([yMaxP_D , ymaxD])

    # plot histogram
    ax3 = plotHistogram(ax3, dailyEnergy, shiftedEnergy) 
    ymax = ax3.get_ylim()
    xmax = ax3.get_xlim()
    yMaxH = ymax[1]
    xMaxH = xmax[1]
    
    formatShiftedEnergy(ax1)
    ax0.text(s=str(round(yMaxD_C,2)) + ' MW',
               x=-12*4, y=yMaxD_C,
               verticalalignment="bottom",horizontalalignment="center",
               fontsize=8#, fontweight='bold'
            )
    ax0.text(s=str(round(yMaxD_D,1)) + ' MW',
               x=12*4, y=yMaxD_D,
               verticalalignment="top",horizontalalignment="center",
               fontsize=8#, fontweight='bold'
            )
    
    ax2.text(s=str(round(yMaxP_C,1)) + '%',
               x=-12*4, y=yMaxP_C,
               verticalalignment="bottom",horizontalalignment="center",
               fontsize=8#, fontweight='bold'
            )
    ax2.text(s=str(round(yMaxP_D,1)) + '%',
               x=12*4, y=yMaxP_D,
               verticalalignment="top",horizontalalignment="center",
               fontsize=8#, fontweight='bold'
            )   
    # save to pdf
    pltPdf1.savefig() 
    plt.close() 
        
    return pltPdf1, yMax, yMaxD, yMaxP, yMaxH, xMaxH, yMaxD_C, yMaxD_D

def monthlySummaryPages(pltPdf1, df1, fnamein, yMaxE, yMaxD, yMaxP, yMaxH, xMaxH, normalized=False):
    """ create page summary for specific month & add to pdf"""
    
    month = df1.index.month
    day = df1.index.day
    
    # iterate over each month
    for m in range(1, 13,1):
        days = list(set(df1.loc[(month==m)].index.day))
        
        # initialize figure
        fig = plt.figure(figsize=(8,6))
        fig.suptitle(fnamein + " / entire year" )  
        plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
        ax0 = plt.subplot2grid((2, 2), (0, 0),  fig=fig)
        ax1 = plt.subplot2grid((2, 2), (0, 1),  fig=fig)
        ax2 = plt.subplot2grid((2, 2), (1, 0),  fig=fig)
        ax3 = plt.subplot2grid((2, 2), (1, 1),  fig=fig)
        fig.suptitle(fnamein  + " / " + date(2016, m,1).strftime('%B') )   
        
        # plot shifted energy
        dailyEnergy = []
        shiftedEnergy = []
        for d in days:
            relevant =  (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                ax1,ymax0 = plotShiftedEnergy(ax1, df1.loc[relevant], c='gray', a=0.2)
            else:
                dailyEnergy.append( np.sum( df1.loc[relevant,'Others'].values) )
                ax1,ymax0 = plotShiftedEnergy(ax1, df1.loc[relevant], c='purple', a=0.5)
                shiftedEnergy.append(ymax0)
                
        ax1.set_ylim([0,yMaxE])
        ax1.set_ylabel('Shifted Energy [MWh]')
            
        # plot load-duration
        for d in days:
            relevant =  (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                ax0, ymax1, temp0, temp1  = plotDeltaDuration(ax0, df1.loc[relevant], c='gray', a=0.2, addText=False, asPercentage=False)
            else:
                ax0, ymax1 , temp0, temp1 = plotDeltaDuration(ax0, df1.loc[relevant], c='steelblue', a=0.5, addText=False, asPercentage=False)
        ax0.set_ylim([-yMaxD, yMaxD])
        
        # iterate for each day in month
        for d in days:
            relevant = (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                ax2, ymax, temp0, temp1 = plotDeltaDuration(ax2, df1.loc[relevant], c='gray', a=0.2, addText=False, asPercentage=True ) 
            else:
                ax2, ymax, temp0, temp1 = plotDeltaDuration(ax2, df1.loc[relevant], c='steelblue', a=0.5, addText=False, asPercentage=True) 
#        ax2.set_ylim([-100 , 100 ]) 
            
            
       # plot duration curve
#        for d in days:
#            relevant = (month==m) & (day==d)
#            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
#                pass
#                ax3, ymax2, emax = plotLoadDuration(ax3, df1.loc[relevant], c='gray', a=0.2) 
#            else:
#                ax3, ymax2, emax = plotLoadDuration(ax3, df1.loc[relevant], c='steelblue', a=0.5) 
#                dailyEnergy.append(emax)
#        ax3.set_ylabel('Load [MW]')
#        ax3.set_ylim([0.0, yMaxP ])        
        
        # plot histogram
        ax3 = plotHistogram(ax3, dailyEnergy, shiftedEnergy)             
        ax3.set_ylim([0.0, yMaxH ])        
        ax3.set_xlim([0.0, xMaxH ])        
        ax3.set_xlabel('Shiftable Energy [% of Daily]')
        
        ax1.set_xlabel('Shiftable Energy [MWh]')
            
        formatShiftedEnergy(ax1)
        
        # save figure to pdf
        pltPdf1.savefig() 
        plt.close()  
        
    return pltPdf1




# %% Externally-Facing Function Definitions
def DeltaLoads(dirin='./', fnameinL='groups.csv',   fnameino='groups.csv', 
               dirout='./', fnameout='delta.csv',
               dirlog='./', fnameLog='DeltaLoads.log',
               dataName = 'delta'):
    
    """ calculates delta between leaders & others in a group """
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "DeltaLoads", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
       
    # load time-series data for leaders & others
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin, fnameinL, foutLog, datetimeIndex=False)
    df2, UniqueIDs, foutLog = getDataAndLabels(dirin, fnameino, foutLog, datetimeIndex=False)
    
    # calculate delta
    df3 = deltaLoadsFunction(df1, df2)
    
    # asign cid as CustomerID
    cid = np.asarray([ dataName for i in range(0,len(df3),1)])
    df3 = df3.assign(CustomerID=pd.Series(cid,index=df3.index))
    
    # write to file
    print('Writing output file: %s' %os.path.join(dirout,fnameout))
    foutLog.write('Writing: %s\n' %os.path.join(dirout,fnameout))
    df3.to_csv( os.path.join(dirout,fnameout), columns=['CustomerID', 'datetime', 'NormDelta','AbsDelta', 'Leaders', 'Others'], float_format='%.5f', date_format='%Y-%m-%d %H:%M', index=False) # this is a multiindexed dataframe, so only the data column is written

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

def PlotDeltaSummary(dirin='./', fnamein='IntervalData.normalized.csv', 
                 dirout='plots/', fnameout='DurationCurves.pdf', normalized=False,
                 dirlog='./', fnameLog='PlotDeltaSummary.log'):
    
    """Creates pdf with 13 pages: 1 page summary of entire year followed by monthly. Each page shows shifted energy & duration curves """
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "PlotDeltaSummary", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # load data from file, find initial list of unique IDs. Update log file    
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin,  fnamein, foutLog, datetimeIndex=True)
    
    # add season & day type
    df1 = assignDayType(df1)

    # open pdf for figures
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    # create annual summary of shifted energy & load duration
    foutLog.write("Creating annual figure" )
    print("Creating annual figure" )
    pltPdf1, yMaxE, yMaxD, yMaxP, yMaxH, xMaxH, yMaxD_C, yMaxD_D = annualSummaryPage(pltPdf1, df1, fnamein, normalized)       
    
    # create monthly summaries of shifted energy & load duration
    foutLog.write("\nCreating monthly figures" )
    print("Creating monthly figures" )
    pltPdf1 = monthlySummaryPages(pltPdf1, df1, fnamein, yMaxE, yMaxD, yMaxP, yMaxH, xMaxH, normalized)  
    
    # write results for user
    print('\tMaximum Shiftable Load, Charging is ' + str(round(yMaxD_C,2) ) + ' MW')
    foutLog.write('\n\tMaximum Shiftable Load, Charging is ' + str(round(yMaxD_C,2) ) + ' MW')
    print('\tMaximum Shiftable Load, Disharging is ' + str(round(yMaxD_D,2) ) + ' MW')
    foutLog.write('\n\tMaximum Shiftable Load, Disharging is ' + str(round(yMaxD_D,2) ) + ' MW')
    
    # Closing plot files
    print('Writing output file: %s' %os.path.join(os.path.join(dirout, fnameout)))
    foutLog.write('\n\nWriting: %s' %os.path.join(dirout, fnameout))
    pltPdf1.close()

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return


def PlotDeltaByDay(dirin='./', fnameinL='leaders.csv',   fnameino='others.csv', 
                   dirrate = './', ratein='SCE-TOU-GS3-B.csv', 
                  dirout='./', fnameout='delta.csv',
                  dirlog='./', fnameLog='PlotDeltaByDay.log'):
    
    """ Creates pdf with 365 pages showing the leader and other loads & the delta for each day of the year"""
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "PlotDeltaByDay", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    # load time-series data for leaders & others
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin, fnameinL, foutLog, datetimeIndex=True)
    df2, UniqueIDs, foutLog = getDataAndLabels(dirin, fnameino, foutLog, datetimeIndex=True)
    
    # assign season & day type
    df1 = assignDayType(df1, datetimeIndex=True)
    df2 = assignDayType(df2, datetimeIndex=True)
    
    month = df1.index.month
    day = df1.index.day
    
    # calculate delta
    df3 = deltaLoadsFunction(df1, df2)
    
    # open pdf for figures
    print("Opening plot files")
    pltPdf1 = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    # find max y limits
    ymax = np.ceil(np.max([ df1['NormDmnd'].max() *2  , df2['NormDmnd'].max()*2  ])) / 2
    yLim =  np.ceil(np.max([ df3['NormDelta'].max() *2  ,  abs(df3['NormDelta'].min() *2)    ])) / 2
    ymaxDelta = 1.0
    for m in range(1, 13,1):
        days = list(set(df1.loc[(month==m)].index.day))  
        for d in days:
            relevant = (month==m) & (day==d)
            y = np.cumsum(df3.loc[relevant,'NormDelta'])/4
            y = y - np.min(y)
            ymaxDelta = np.max([ ymaxDelta, np.max(y) ])
    ymaxDelta = np.ceil( ymaxDelta * 2.0 ) / 2.0
    
    # iterate over each month of the year
    print("Creating plots for")
    for m in range(1, 13,1):
        print('\t%s' %(date(2016, m,1).strftime('%B')))
        
        # iterate over each day of the month
        days = list(set(df1.loc[(month==m)].index.day))  
        for d in days:
            
            # find this day in the data
            relevant = (month==m) & (day==d)
            
            # initialize figure
            fig, ax = plt.subplots(nrows=3, ncols=1,figsize=(8,6),sharex=True)
            fig.suptitle( fnameinL + " / " +  date(2016, m,1).strftime('%B')  + " / " + str(int(d)) +  " / " + df1.loc[relevant, 'DayType'][0])   
            plt.subplots_adjust(wspace=0.4,hspace=0.4 )  
            
            # plot loads of leaders & others 
            ax0=ax[0]
            ax0 = plotDailyLoads(ax0, df1.loc[relevant], c='b', lw=1, label='leaders')
            ax0 = plotDailyLoads(ax0, df2.loc[relevant], c='k', lw=1, label='others')
            ax0.set_ylim([0.0,ymax])
            ax0.legend()
            
            # plot delta between leaders & others 
            ax1=ax[1]
            ax1,temp = plotDailyDeltaLoad(ax1, df3.loc[relevant])
            ax1.set_ylim([-yLim,yLim])
            
            ax2=ax[2]
            ax2,temp = plotDailyDeltaEnergy(ax2, df3.loc[relevant])
            ax2.set_ylim([0,ymaxDelta])

            # add to pdf
            pltPdf1.savefig() 
            plt.close()   
                
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    pltPdf1.close()

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return


def PlotDeltaByDayWithDuration(dirin='./', fnameinL='leaders.csv',   fnameino='others.csv', 
                   dirrate = './', ratein='SCE-TOU-GS3-B.csv', 
                  dirout='./', fnameout='delta.csv',
                  dirlog='./', fnameLog='PlotDeltaByDay.log', yLim =2):
    
    """ Creates pdf with 365 pages showing the leader and other loads & the delta for each day of the year"""
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "PlotDeltaByDayWithDuration", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    # load time-series data for leaders & others
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin, fnameinL, foutLog, datetimeIndex=True)
    df2, UniqueIDs, foutLog = getDataAndLabels(dirin, fnameino, foutLog, datetimeIndex=True)

    # assign season & day type
    df1 = assignDayType(df1, datetimeIndex=True)
    df2 = assignDayType(df2, datetimeIndex=True)
    month = df1.index.month
    day = df1.index.day
    
    # calculate delta
    df3 = deltaLoadsFunction(df1, df2)
    
    # open pdf for figures
    print("Opening plot files")
    pltPdf1 = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    # find max y limits
    ymax = np.ceil(np.max([ df1['NormDmnd'].max() *2  , df2['NormDmnd'].max()*2  ])) / 2
    ymaxDelta = 1.0
    yLim =  np.ceil(np.max([ df3['NormDelta'].max() *2  ,  abs(df3['NormDelta'].min() *2)    ])) / 2
    for m in range(1, 13,1):
        days = list(set(df1.loc[(month==m)].index.day))  
        for d in days:
            relevant = (month==m) & (day==d)
            y = np.cumsum(df3.loc[relevant,'NormDelta'])/4
            y = y - np.min(y)
            ymaxDelta = np.max([ ymaxDelta, np.max(y) ])
    ymaxDelta = np.ceil( ymaxDelta * 2.0 ) / 2.0
    
    # iterate over each month of the year
    print("Creating plots for")
    for m in range(1, 13,1):
        print('\t%s' %(date(2016, m,1).strftime('%B')))
        
        # iterate over each day of the month
        days = list(set(df1.loc[(month==m)].index.day))  
        for d in days:
            
            # find this day in the data
            relevant = (month==m) & (day==d)
            
            # initialize figure
            fig = plt.figure(figsize=(8,6))
            plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
            ax0 = plt.subplot2grid((3, 2), (0, 0),   fig=fig)
            ax1 = plt.subplot2grid((3, 2), (1, 0),  fig=fig)
            ax2 = plt.subplot2grid((3, 2), (2, 0),   fig=fig)
            ax3 = plt.subplot2grid((3, 2), (0, 1), rowspan=3, fig=fig)
            fig.suptitle(  date(2016, m,1).strftime('%B')  + " / " + str(int(d)) +  " / " + df1.loc[relevant, 'DayType'][0])   
            
            # plot loads of leaders & others 
            ax0 = plotDailyLoads(ax0, df1.loc[relevant], c='b', lw=1, label='leaders')
            ax0 = plotDailyLoads(ax0, df2.loc[relevant], c='k', lw=1, label='others')
            ax0.set_ylim([0.0,ymax])
            ax0.set_xlabel('')
            
            # plot delta between leaders & others 
            ax1,temp = plotDailyDeltaLoad(ax1, df3.loc[relevant])
            ax1.set_ylim([-yLim,yLim])
            ax1.set_xlabel('')
            
            # plot shifted energy
            ax2,temp = plotDailyDeltaEnergy(ax2, df3.loc[relevant])
            ax2.set_ylim([0,ymaxDelta])
            
            # plot duration curve
            ax3, temp0, temp1, temp2 = plotDeltaDuration(ax3, df3.loc[relevant], addText=True, varName='NormDelta')
            ax3.set_ylim([-yLim, yLim])
            ax3.set_ylabel('Shfitable Load [pu]')     
            
            # add to pdf
            pltPdf1.savefig() 
            plt.close()   
                
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    pltPdf1.close()

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return
def GroupAnalysisMaster(dirin='./', dirout='./', 
                        fnamebase='NAICS', fnamegroup = 'NAICS.groups.csv', 
                        fnamein='IntervalData.csv',  N=4, 
                        dirlog='./', fnameLog='GroupAnalysisMaster.log',
                        steps=['NormalizeGroup', 'DeltaLoads', 'PlotDeltaByDay', 'PlotDeltaByDayWithDuration', 'PlotDeltaSummary']):

    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "GroupAnalysisMaster", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
                        
    for n in range(1,N+1,1):  
        foutLog.write('\n********************************************************')        
        print('\n********************************************************')
        codeTstartx = datetime.now()
        foutLog.write('\nAnalyzing group #' + str(n) + ' : ' + str(datetime.now()-codeTstartx) )
        print('\nAnalyzing group #' + str(n) + ' : ' + str(datetime.now()-codeTstartx) )
        groupL = 'g' + str(n) + 'L'
        groupo = 'g' + str(n) + 'o'
        fnameinL=fnamebase+ "." + groupL + ".normalized.csv"
        fnameino=fnamebase+ "." + groupo + ".normalized.csv"
        fnameout_raw  = fnamebase+".delta." + groupL + "-" + groupo 
        
        if ('Normalize' in steps) or ('NormalizeGroup' in steps):
            # normalize leaders
            NormalizeGroup(dirin=dirin, fnamein=fnamein, groupName=groupL,
                           considerCIDs= groupL + "." + fnamebase + ".groups.csv",
                           dirout=dirout, fnameout=fnamebase + "." + groupL +  '.normalized.csv',
                           dirlog=dirlog)                        
            foutLog.write('\n\tNormalized ' + groupL + ' : ' + str(datetime.now()-codeTstartx) )
            print('\n\tNormalized ' + groupL + ' : ' + str(datetime.now()-codeTstartx) )
            
            # normalize others
            NormalizeGroup(dirin=dirin, fnamein=fnamein,groupName=groupo ,
                           considerCIDs= groupo + "." + fnamebase + ".groups.csv",
                           dirout=dirout, fnameout=fnamebase + "." + groupo +  '.normalized.csv',
                           dirlog=dirlog)           
            foutLog.write('\n\tNormalized ' + groupo + ' : ' + str(datetime.now()-codeTstartx) )
            print('\n\tNormalized ' + groupo + ' : ' + str(datetime.now()-codeTstartx) )
        
        
        if ('Delta' in steps) or ('DeltaLoads' in steps):
            # calculate detla between normalized loads
            DeltaLoads(dirin=dirin, dirout=dirout, dirlog=dirlog,
                       fnameinL=fnameinL, fnameino=fnameino,
                       fnameout= fnameout_raw + ".csv" )    
            foutLog.write('\n\tCalculated delta ' + groupL + '-' + groupo +' : ' + str(datetime.now()-codeTstartx) )
            print('\n\tCalculated delta ' + groupL + '-' + groupo +' : ' + str(datetime.now()-codeTstartx) )
        
        if ('PlotDeltaByDay' in steps) or ('DeltaByDay' in steps) or ('ByDay' in steps):
            # plot deltas between loads for each day
            PlotDeltaByDay(dirin=dirin, dirout=dirout, dirlog=dirlog,
                       fnameinL=fnameinL, fnameino=fnameino,
                       fnameout= fnameout_raw + ".pdf")  
            foutLog.write('\n\tPlotted deltas by day : '  + str(datetime.now()-codeTstartx))
            print('\n\tPlotted deltas by day : '  + str(datetime.now()-codeTstartx))
        
        if ('PlotDeltaByDayWithDuration' in steps) or ('DeltaByDayWithDuration' in steps) or ('ByDayWithDuration' in steps):
            # plot deltas between loads for each day
            PlotDeltaByDayWithDuration(dirin=dirin, dirout=dirout, dirlog=dirlog,
                       fnameinL=fnameinL, fnameino=fnameino,
                       fnameout= fnameout_raw + "_wDuration.pdf" )  
            foutLog.write('\n\tPlotted deltas by day with Duration : '  + str(datetime.now()-codeTstartx))
            print('\n\tPlotted deltas by day with Duration : '  + str(datetime.now()-codeTstartx))
        
        if ('PlotDeltaSummary' in steps) or ('DeltaSummary' in steps) or ('Summary' in steps):
            # plot annual & monthly summary of load flexibility 
            PlotDeltaSummary(dirin=dirin, fnamein=fnameout_raw  + ".csv",
                       dirout=dirout, fnameout=fnameout_raw + '.Summary.pdf',
                       dirlog=dirlog)
            foutLog.write('\n\tPlotted load flexibility summary : '  + str(datetime.now()-codeTstartx))
            print('\n\tPlotted load flexibility summary : '  + str(datetime.now()-codeTstartx))
        
    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
        
    return 

#%% **Show the Process & Illustrative Examples
def PlotFlexibilityOptions(dirin='./', fnameinL='leaders.csv', fnameino='others.csv', 
                  dirout='./', fnameout='delta.csv',
                  m = 6, d = 21,dirrate = './', ratein='SCE-TOU-GS3-B.csv',
                  dirlog='./', fnameLog='PlotDeltaByDay.log'):
    
    """ Creates pdf with 365 pages showing the leader and other loads & the delta for each day of the year"""
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "PlotFlexibilityOptions", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    # load time-series data for leaders & others
    df1raw, UniqueIDs, foutLog = getData(dirin, fnameinL, foutLog, varName=['NormDmnd'],usecols=[0,1,2])
    df2raw, UniqueIDs, foutLog = getData(dirin, fnameino, foutLog, varName=['NormDmnd'],usecols=[0,1,2])

    # reading TOU rates
    rate = readTOURates(dirrate, ratein)

    # assign season & day type
    df1 = AssignRatePeriods(df1raw, rate, addRate=True, datetimeIndex=True)
    df2 = AssignRatePeriods(df2raw, rate, addRate=True, datetimeIndex=True)
    
    month = df1.index.month
    day = df1.index.day
    
    # find this day in the data
    relevant = (month==m) & (day==d)
    df2 = df2[relevant]
    df1 = df1[relevant]
    
    # calculate delta
    df3 = deltaLoadsFunction(df1, df2)

    # open pdf for figures
    print("Opening plot files")
    pltPdf1 = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    # find max y limits
    ymax = np.ceil(np.max([ df1['NormDmnd'].max() *2  , df2['NormDmnd'].max()*2  ])) / 2 +0.5

    # find min / max for delta figure
    ymaxDelta = 1.0
    y = np.cumsum(df3['NormDmnd'])/4
    y = y - np.min(y)
    ymaxDelta = np.max([ ymaxDelta, np.max(y) ])
    ymaxDelta = np.ceil( ymaxDelta * 2.0 ) / 2.0
    
    # iterate over each month of the year
    print('Plotting daily loads & deltas for %s' %(date(2016, m,1).strftime('%B')))
    
    # initialize figure
    fig, ax = plt.subplots(nrows=3, ncols=1,figsize=(8,6),sharex=True)
    plt.subplots_adjust(wspace=0.4,hspace=0.4 )    
    fig.suptitle('Raw Data')
    
    # plot loads of leaders & others 
    ax0=ax[0]
    ax0 = plotDailyLoads(ax0, df1, c='b', lw=1, label='leaders')
    ax0 = plotDailyLoads(ax0, df2, c='k', lw=1, label='others')
    ax0.set_ylim([0.0,ymax])
    ax0.legend()
    
    # plot delta between leaders & others 
    ax1=ax[1]
    ax1,temp = plotDailyDeltaLoad(ax1, df3)
    ax1.set_ylim([-1,1])
    
    # plot shifted energy
    ax2=ax[2]
    ax2,temp = plotDailyDeltaEnergy(ax2, df3)
    ax2.set_ylim([0,ymaxDelta])

    pltPdf1.savefig() 
    plt.close()  
    
    charge = df3['NormDmnd']>0
    discharge = df3['NormDmnd']<0
    
    # aligned to rates    
    df3x = df3.copy(deep=True)
    df3x[ 'NormDmnd'] = 0.0
    onpeak  = df3x['EnergyCost']==np.max(df3x['EnergyCost'])
    offpeak = df3x['EnergyCost']==np.min(df3x['EnergyCost'])
    midpeak = (df3x['EnergyCost']>np.min(df3x['EnergyCost'])) & (df3x['EnergyCost']<np.max(df3x['EnergyCost']))
    
    chargeDeltas    = np.sort(np.asarray( df3.loc[charge, 'NormDmnd'].values ))
    dischargeDeltas = np.sort(np.asarray(df3.loc[discharge, 'NormDmnd'].values))
    
    onpeakDeltas = copy(dischargeDeltas[:sum(onpeak)])
    onpeakDeltasx = copy(onpeakDeltas[1:])
    arrangedOnPeakDeltas = np.asarray(list(np.flipud(copy(onpeakDeltas[::2]))) + copy(list(onpeakDeltasx[::2]) ))
    
    midpeakDeltas = dischargeDeltas[sum(onpeak)+1:]
    midpeakDeltasx = copy(midpeakDeltas[1:])
    arrangedMidPeakDeltas = np.asarray(list(np.flipud(copy(midpeakDeltas[::2]))) + copy(list(midpeakDeltasx[::2]) ))
    if sum(midpeak)> len(arrangedMidPeakDeltas):
        missing = sum(midpeak) - len(arrangedMidPeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        arrangedMidPeakDeltas = np.asarray( list(addZeros[:np.int(np.floor(len(addZeros)/2))]) + list(arrangedMidPeakDeltas) +  list(addZeros[np.int(np.floor(len(addZeros)/2)):]) )

    df3x.loc[midpeak, 'NormDmnd'] = arrangedMidPeakDeltas
    df3x.loc[onpeak, 'NormDmnd'] = arrangedOnPeakDeltas
    
    offpeak = df3x[ 'NormDmnd']>=0.0
    offpeakDeltas = np.flipud(chargeDeltas[:sum(offpeak)-1])
    if sum(offpeak)> len(offpeakDeltas):
        missing = sum(offpeak) - len(offpeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        offpeakDeltas = np.asarray( list(offpeakDeltas) + list(addZeros) )
    offpeakDeltasx = copy(offpeakDeltas[1:])
    arrangedOffPeakDeltas = np.asarray(list(copy(offpeakDeltas[::2])) + copy(list(np.flipud(offpeakDeltasx[::2]) )))
        
    stop1 = offpeak.idxmin()
    start2 = offpeak[stop1:].idxmax()
    
    circlen = len(offpeak[start2:])
    
    arrangedOffPeakDeltas =np.roll( arrangedOffPeakDeltas,circlen)
    
    df3x.loc[offpeak, 'NormDmnd'] = arrangedOffPeakDeltas
    df1x = df1.copy()
    df1x['NormDmnd'] = df2['NormDmnd'] + df3x['NormDmnd']
    
    fig, ax = plt.subplots(nrows=3, ncols=1,figsize=(8,6),sharex=True)
    plt.subplots_adjust(wspace=0.4,hspace=0.4 )    
    ax0=ax[0]
    ax0 = plotDailyLoads(ax0, df1x, c='b', lw=1, label='leaders')
    ax0 = plotDailyLoads(ax0, df2, c='k', lw=1, label='others')
    ax0.set_ylim([0.0,ymax])
    ax0.legend()
    
    ax1=ax[1]
    ax1,temp = plotDailyDeltaLoad(ax1, df3x)
    ax1.set_ylim([-1,1])
    
    ax2=ax[2]
    ax2,temp = plotDailyDeltaEnergy(ax2, df3x)
    ax2.set_ylim([0,ymaxDelta])
            
    pltPdf1.savefig() 
    plt.close()      
    
    "aligned to artifical rates  "
    rate = readTOURates(dirrate, ratein='TOU-Fake.csv')
    df1 = AssignRatePeriods(df1raw, rate, addRate=True, datetimeIndex=True)
    df2 = AssignRatePeriods(df2raw, rate, addRate=True, datetimeIndex=True)
    df2 = df2[relevant]
    df1 = df1[relevant]
    
    # calculate delta
    df3 = df2.copy()
    df3['NormDmnd'] = df1['NormDmnd'] - df2['NormDmnd']

    df3x = df3.copy(deep=True)
    df3x[ 'NormDmnd'] = 0.0
    onpeak  = df3x['EnergyCost']==np.max(df3x['EnergyCost'])
    offpeak = df3x['EnergyCost']==np.min(df3x['EnergyCost'])
    midpeak = (df3x['EnergyCost']>np.min(df3x['EnergyCost'])) & (df3x['EnergyCost']<np.max(df3x['EnergyCost']))
    
    chargeDeltas    = np.sort(np.asarray( df3.loc[charge, 'NormDmnd'].values ))
    dischargeDeltas = np.sort(np.asarray(df3.loc[discharge, 'NormDmnd'].values))
    
    onpeakDeltas = copy(dischargeDeltas[:sum(onpeak)])
    onpeakDeltasx = copy(onpeakDeltas[1:])
    arrangedOnPeakDeltas = np.asarray(list(np.flipud(copy(onpeakDeltas[::2]))) + copy(list(onpeakDeltasx[::2]) ))
    
    midpeakDeltas = dischargeDeltas[sum(onpeak)+1:]
    midpeakDeltasx = copy(midpeakDeltas[1:])
    arrangedMidPeakDeltas = np.asarray(list(np.flipud(copy(midpeakDeltas[::2]))) + copy(list(midpeakDeltasx[::2]) ))
    if sum(midpeak)> len(arrangedMidPeakDeltas):
        missing = sum(midpeak) - len(arrangedMidPeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        arrangedMidPeakDeltas = np.asarray( list(addZeros[:np.int(np.floor(len(addZeros)/2))]) + list(arrangedMidPeakDeltas) +  list(addZeros[np.int(np.floor(len(addZeros)/2)):]) )

    if len(arrangedMidPeakDeltas)>0 and np.sum(midpeak)>0:
        df3x.loc[midpeak, 'NormDmnd'] = arrangedMidPeakDeltas[:np.sum(midpeak)]
    df3x.loc[onpeak, 'NormDmnd'] = arrangedOnPeakDeltas
    
    offpeak = df3x[ 'NormDmnd']>=0.0
    offpeakDeltas = np.flipud(chargeDeltas[:sum(offpeak)])
    if sum(offpeak)> len(offpeakDeltas):
        missing = sum(offpeak) - len(offpeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        offpeakDeltas = np.asarray( list(offpeakDeltas) + list(addZeros) )
    offpeakDeltasx = copy(offpeakDeltas[1:])
    arrangedOffPeakDeltas = np.asarray(list(np.flipud(copy(offpeakDeltas[::2]))) + copy(list(offpeakDeltasx[::2]) ))
    
    df3x.loc[offpeak, 'NormDmnd'] = arrangedOffPeakDeltas
    df1x = df1.copy()
    df1x['NormDmnd'] = df2['NormDmnd'] + df3x['NormDmnd']
    
    fig, ax = plt.subplots(nrows=3, ncols=1,figsize=(8,6),sharex=True)
    plt.subplots_adjust(wspace=0.4,hspace=0.4 )    
    ax0=ax[0]
    ax0 = plotDailyLoads(ax0, df1x, c='b', lw=1, label='leaders')
    ax0 = plotDailyLoads(ax0, df2, c='k', lw=1, label='others')
    ax0.set_ylim([0.0,ymax])
    ax0.legend()
    
    ax1=ax[1]
    ax1,temp = plotDailyDeltaLoad(ax1, df3x)
    ax1.set_ylim([-1,1])
    
    ax2=ax[2]
    ax2,temp = plotDailyDeltaEnergy(ax2, df3x)
    ax2.set_ylim([0,ymaxDelta])
        
    pltPdf1.savefig() 
    plt.close()      
    
    
    "aligned to artifical rates with two cycles "
    rate = readTOURates(dirrate, ratein='TOU-Fake-2.csv')
    df1 = AssignRatePeriods(df1raw, rate, addRate=True, datetimeIndex=True)
    df2 = AssignRatePeriods(df2raw, rate, addRate=True, datetimeIndex=True)
    df2 = df2[relevant]
    df1 = df1[relevant]
    
    # calculate delta
    df3 = df2.copy()
    df3['NormDmnd'] = df1['NormDmnd'] - df2['NormDmnd']

    df3x = df3.copy(deep=True)
    df3x['NormDmnd'] = 0.0
    onpeak  = df3x['EnergyCost']==np.max(df3x['EnergyCost'])
    offpeak = df3x['EnergyCost']==np.min(df3x['EnergyCost'])
    midpeak = (df3x['EnergyCost']>np.min(df3x['EnergyCost'])) & (df3x['EnergyCost']<np.max(df3x['EnergyCost']))
    
    chargeDeltas    = np.sort(np.asarray( df3.loc[charge, 'NormDmnd'].values ))
    chargeDeltasx = chargeDeltas[1:]
    charge1Deltas = chargeDeltas[::2]
    charge2Deltas = chargeDeltasx[::2] 
    
    dischargeDeltas = np.sort(np.asarray(df3.loc[discharge, 'NormDmnd'].values))
    dischargeDeltasx = dischargeDeltas[1:]
    discharge1Deltas = dischargeDeltas[::2]
    discharge2Deltas = dischargeDeltasx[::2]
    
    onpeakDeltas = copy(discharge1Deltas[:sum(onpeak)])
    onpeakDeltasx = copy(onpeakDeltas[1:])
    arrangedOnPeakDeltas = np.asarray(list(np.flipud(copy(onpeakDeltas[::2]))) + copy(list(onpeakDeltasx[::2]) ))
    
    midpeakDeltas = copy(discharge2Deltas[:sum(midpeak)])
    midpeakDeltasx = copy(midpeakDeltas[1:])
    arrangedMidPeakDeltas = np.asarray(list(np.flipud(copy(midpeakDeltas[::2]))) + copy(list(midpeakDeltasx[::2]) ))
    if sum(midpeak)> len(arrangedMidPeakDeltas):
        missing = sum(midpeak) - len(arrangedMidPeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        arrangedMidPeakDeltas = np.asarray( list(addZeros[:np.int(np.floor(len(addZeros)/2))]) + list(arrangedMidPeakDeltas) +  list(addZeros[np.int(np.floor(len(addZeros)/2)):]) )

    if len(arrangedMidPeakDeltas)>0 and np.sum(midpeak)>0:
        df3x.loc[midpeak, 'NormDmnd'] = arrangedMidPeakDeltas[:np.sum(midpeak)]
    df3x.loc[onpeak, 'NormDmnd'] = arrangedOnPeakDeltas
    
    offpeak = df3x[ 'NormDmnd']>=0.0
    stopD = []
    startD = []
    for ix in range(0, len(df3x)-1,1):
        if offpeak.iloc[ix] and ( onpeak.iloc[ix+1] or midpeak.iloc[ix+1] ):
            stopD.append(ix)
        if offpeak.iloc[ix+1] and ( onpeak.iloc[ix] or midpeak.iloc[ix] ):
            startD.append(ix)
    
    offpeak1  = copy(offpeak)
    offpeak1.iloc[stopD[0]:startD[1]] = False
    
    offpeak2 = copy(offpeak)
    offpeak2.iloc[:startD[0]] = False
    offpeak2.iloc[stopD[1]:] = False
    
    offpeakDeltas = np.flipud(charge2Deltas[:sum(offpeak2)])
    if sum(offpeak2)> len(offpeakDeltas):
        missing = sum(offpeak2) - len(offpeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        offpeakDeltas = np.asarray( list(offpeakDeltas) + list(addZeros) )
    offpeakDeltasx = copy(offpeakDeltas[1:])
    arrangedOffPeakDeltas = np.asarray(list(np.flipud(copy(offpeakDeltas[::2]))) + copy(list(offpeakDeltasx[::2]) ))
    df3x.loc[offpeak2, 'NormDmnd'] = arrangedOffPeakDeltas


    offpeakDeltas = np.flipud(charge1Deltas[:sum(offpeak1)])
    if sum(offpeak1)> len(offpeakDeltas):
        missing = sum(offpeak1) - len(offpeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        offpeakDeltas = np.asarray( list(offpeakDeltas) + list(addZeros) )
    offpeakDeltasx = copy(offpeakDeltas[1:])
    arrangedOffPeakDeltas = np.asarray(list(np.flipud(copy(offpeakDeltas[::2]))) + copy(list((offpeakDeltasx[::2]) )))
    circlen = len(offpeak[startD[1]:])
    arrangedOffPeakDeltas =np.roll( arrangedOffPeakDeltas,-circlen)
    df3x.loc[offpeak1, 'NormDmnd'] = arrangedOffPeakDeltas    
    
    df1x = df1.copy()
    df1x['NormDmnd'] = df2['NormDmnd'] + df3x['NormDmnd']
    
    fig, ax = plt.subplots(nrows=3, ncols=1,figsize=(8,6),sharex=True)
    plt.subplots_adjust(wspace=0.4,hspace=0.4 )    
    ax0=ax[0]
    ax0 = plotDailyLoads(ax0, df1x, c='b', lw=1, label='leaders')
    ax0 = plotDailyLoads(ax0, df2, c='k', lw=1, label='others')
    ax0.set_ylim([0.0,ymax])
    ax0.legend()
    
    ax1=ax[1]
    ax1,temp = plotDailyDeltaLoad(ax1, df3x)
    ax1.set_ylim([-1,1])
    
    ax2=ax[2]
    ax2,temp = plotDailyDeltaEnergy(ax2, df3x)
    ax2.set_ylim([0,ymaxDelta])
        
    pltPdf1.savefig() 
    plt.close()          
    
    
    "aligned to artifical rates with two cycles "
    rate = readTOURates(dirrate, ratein='TOU-Fake-2.csv')
    df1 = AssignRatePeriods(df1raw, rate, addRate=True, datetimeIndex=True)
    df2 = AssignRatePeriods(df2raw, rate, addRate=True, datetimeIndex=True)
    df2 = df2[relevant]
    df1 = df1[relevant]
    
    # calculate delta
    df3 = df2.copy()
    df3['NormDmnd'] = df1['NormDmnd'] - df2['NormDmnd']

    df3x = df3.copy(deep=True)
    df3x['NormDmnd'] = 0.0
    onpeak  = df3x['EnergyCost']==np.max(df3x['EnergyCost'])
    offpeak = df3x['EnergyCost']==np.min(df3x['EnergyCost'])
    midpeak = (df3x['EnergyCost']>np.min(df3x['EnergyCost'])) & (df3x['EnergyCost']<np.max(df3x['EnergyCost']))
    
    chargeDeltas    = np.sort(np.asarray( df3.loc[charge, 'NormDmnd'].values ))
    charge1Deltas = chargeDeltas[:np.int(np.floor(len(chargeDeltas)/2))]
    charge2Deltas = chargeDeltas[np.int(np.floor(len(chargeDeltas)/2)):] 

    dischargeDeltas = np.sort(np.asarray(df3.loc[discharge, 'NormDmnd'].values))
    discharge1Deltas = dischargeDeltas[:np.int(np.floor(len(dischargeDeltas)/2))]
    discharge2Deltas = dischargeDeltas[np.int(np.floor(len(dischargeDeltas)/2)):] 

    
    onpeakDeltas = copy(discharge1Deltas[:sum(onpeak)])
    onpeakDeltasx = copy(onpeakDeltas[1:])
    arrangedOnPeakDeltas = np.asarray(list(np.flipud(copy(onpeakDeltas[::2]))) + copy(list(onpeakDeltasx[::2]) ))
    
    midpeakDeltas = copy(discharge2Deltas[:sum(midpeak)])
    midpeakDeltasx = copy(midpeakDeltas[1:])
    arrangedMidPeakDeltas = np.asarray(list(np.flipud(copy(midpeakDeltas[::2]))) + copy(list(midpeakDeltasx[::2]) ))
    if sum(midpeak)> len(arrangedMidPeakDeltas):
        missing = sum(midpeak) - len(arrangedMidPeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        arrangedMidPeakDeltas = np.asarray( list(addZeros[:np.int(np.floor(len(addZeros)/2))]) + list(arrangedMidPeakDeltas) +  list(addZeros[np.int(np.floor(len(addZeros)/2)):]) )

    if len(arrangedMidPeakDeltas)>0 and np.sum(midpeak)>0:
        df3x.loc[midpeak, 'NormDmnd'] = arrangedMidPeakDeltas[:np.sum(midpeak)]
    df3x.loc[onpeak, 'NormDmnd'] = arrangedOnPeakDeltas
    
    offpeak = df3x[ 'NormDmnd']>=0.0
    stopD = []
    startD = []
    for ix in range(0, len(df3x)-1,1):
        if offpeak.iloc[ix] and ( onpeak.iloc[ix+1] or midpeak.iloc[ix+1] ):
            stopD.append(ix)
        if offpeak.iloc[ix+1] and ( onpeak.iloc[ix] or midpeak.iloc[ix] ):
            startD.append(ix)
    
    offpeak1  = copy(offpeak)
    offpeak1.iloc[stopD[0]:startD[1]] = False
    
    offpeak2 = copy(offpeak)
    offpeak2.iloc[:startD[0]] = False
    offpeak2.iloc[stopD[1]:] = False
    offpeakDeltas = np.flipud(charge2Deltas[:sum(offpeak2)])
    if np.sum(offpeak2)> len(offpeakDeltas):
        missing = sum(offpeak2) - len(offpeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        offpeakDeltas = np.asarray( list(offpeakDeltas) + list(addZeros) )
    offpeakDeltasx = copy(offpeakDeltas[1:])
    arrangedOffPeakDeltas = np.asarray(list(np.flipud(copy(offpeakDeltas[::2]))) + copy(list(offpeakDeltasx[::2]) ))
    df3x.loc[offpeak2, 'NormDmnd'] = arrangedOffPeakDeltas

    offpeakDeltas = np.flipud(charge1Deltas[:sum(offpeak1)])
    if sum(offpeak1)> len(offpeakDeltas):
        missing = sum(offpeak1) - len(offpeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        offpeakDeltas = np.asarray( list(offpeakDeltas) + list(addZeros) )
    offpeakDeltasx = copy(offpeakDeltas[1:])
    arrangedOffPeakDeltas = np.asarray(list(np.flipud(copy(offpeakDeltas[::2]))) + copy(list((offpeakDeltasx[::2]) )))
    circlen = len(offpeak[startD[1]:])
    arrangedOffPeakDeltas =np.roll( arrangedOffPeakDeltas,-circlen)
    df3x.loc[offpeak1, 'NormDmnd'] = arrangedOffPeakDeltas    
    
    df1x = df1.copy()
    df1x['NormDmnd'] = df2['NormDmnd'] + df3x['NormDmnd']
    
    fig, ax = plt.subplots(nrows=3, ncols=1,figsize=(8,6),sharex=True)
    plt.subplots_adjust(wspace=0.4,hspace=0.4 )    
    ax0=ax[0]
    ax0 = plotDailyLoads(ax0, df1x, c='b', lw=1, label='leaders')
    ax0 = plotDailyLoads(ax0, df2, c='k', lw=1, label='others')
    ax0.set_ylim([0.0,ymax])
    ax0.legend()
    
    ax1=ax[1]
    ax1,temp = plotDailyDeltaLoad(ax1, df3x)
    ax1.set_ylim([-1,1])
    
    ax2=ax[2]
    ax2,temp = plotDailyDeltaEnergy(ax2, df3x)
    ax2.set_ylim([0,ymaxDelta])
        
    pltPdf1.savefig() 
    plt.close()         
    
    "aligned to artifical rates with two cycles & WRONG ordering"
    rate = readTOURates(dirrate, ratein='TOU-Fake-2.csv')
    df1 = AssignRatePeriods(df1raw, rate, addRate=True, datetimeIndex=True)
    df2 = AssignRatePeriods(df2raw, rate, addRate=True, datetimeIndex=True)
    df2 = df2[relevant]
    df1 = df1[relevant]
    
    # calculate delta
    df3 = df2.copy()
    df3['NormDmnd'] = df1['NormDmnd'] - df2['NormDmnd']

    df3x = df3.copy(deep=True)
    df3x['NormDmnd'] = 0.0
    onpeak  = df3x['EnergyCost']==np.max(df3x['EnergyCost'])
    offpeak = df3x['EnergyCost']==np.min(df3x['EnergyCost'])
    midpeak = (df3x['EnergyCost']>np.min(df3x['EnergyCost'])) & (df3x['EnergyCost']<np.max(df3x['EnergyCost']))
    
    chargeDeltas    = np.sort(np.asarray( df3.loc[charge, 'NormDmnd'].values ))
    chargeDeltasx = chargeDeltas[1:]
    charge1Deltas = chargeDeltas[::2]
    charge2Deltas = chargeDeltasx[::2] 
    
    dischargeDeltas = np.sort(np.asarray(df3.loc[discharge, 'NormDmnd'].values))
    dischargeDeltasx = dischargeDeltas[1:]
    discharge1Deltas = dischargeDeltas[::2]
    discharge2Deltas = dischargeDeltasx[::2]
    
    onpeakDeltas = copy(discharge1Deltas[:sum(onpeak)])
    onpeakDeltasx = copy(onpeakDeltas[1:])
    arrangedOnPeakDeltas = np.asarray(list((copy(onpeakDeltas[::2]))) + copy(list(np.flipud(onpeakDeltasx[::2]) )))
    
    midpeakDeltas = copy(discharge2Deltas[:sum(midpeak)])
    midpeakDeltasx = copy(midpeakDeltas[1:])
    arrangedMidPeakDeltas = np.asarray(list((copy(midpeakDeltas[::2]))) + copy(list(np.flipud(midpeakDeltasx[::2]) )))
    if sum(midpeak)> len(arrangedMidPeakDeltas):
        missing = sum(midpeak) - len(arrangedMidPeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        arrangedMidPeakDeltas = np.asarray( list(addZeros[:np.int(np.floor(len(addZeros)/2))]) + list(arrangedMidPeakDeltas) +  list(addZeros[np.int(np.floor(len(addZeros)/2)):]) )

    if len(arrangedMidPeakDeltas)>0 and np.sum(midpeak)>0:
        df3x.loc[midpeak, 'NormDmnd'] = arrangedMidPeakDeltas[:np.sum(midpeak)]
    df3x.loc[onpeak, 'NormDmnd'] = arrangedOnPeakDeltas
    
    offpeak = df3x[ 'NormDmnd']>=0.0
    stopD = []
    startD = []
    for ix in range(0, len(df3x)-1,1):
        if offpeak.iloc[ix] and ( onpeak.iloc[ix+1] or midpeak.iloc[ix+1] ):
            stopD.append(ix)
        if offpeak.iloc[ix+1] and ( onpeak.iloc[ix] or midpeak.iloc[ix] ):
            startD.append(ix)
    
    offpeak1  = copy(offpeak)
    offpeak1.iloc[stopD[0]:startD[1]] = False
    
    offpeak2 = copy(offpeak)
    offpeak2.iloc[:startD[0]] = False
    offpeak2.iloc[stopD[1]:] = False
    
    offpeakDeltas = np.flipud(charge2Deltas[:sum(offpeak2)])
    if sum(offpeak2)> len(offpeakDeltas):
        missing = sum(offpeak2) - len(offpeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        offpeakDeltas = np.asarray( list(offpeakDeltas) + list(addZeros) )
    offpeakDeltasx = copy(offpeakDeltas[1:])
    arrangedOffPeakDeltas = np.asarray(list((copy(offpeakDeltas[::2]))) + copy(list(np.flipud(offpeakDeltasx[::2]) )))
    df3x.loc[offpeak2, 'NormDmnd'] = arrangedOffPeakDeltas


    offpeakDeltas = np.flipud(charge1Deltas[:sum(offpeak1)])
    if sum(offpeak1)> len(offpeakDeltas):
        missing = sum(offpeak1) - len(offpeakDeltas) 
        addZeros = [0 for x in range(0, missing,1)]
        offpeakDeltas = np.asarray( list(offpeakDeltas) + list(addZeros) )
    offpeakDeltasx = copy(offpeakDeltas[1:])
    arrangedOffPeakDeltas = np.asarray(list((copy(offpeakDeltas[::2]))) + copy(list(np.flipud(offpeakDeltasx[::2]) )))
    circlen = len(offpeak[startD[1]:])
    arrangedOffPeakDeltas =np.roll( arrangedOffPeakDeltas,-circlen)
    df3x.loc[offpeak1, 'NormDmnd'] = arrangedOffPeakDeltas    
    
    df1x = df1.copy()
    df1x['NormDmnd'] = df2['NormDmnd'] + df3x['NormDmnd']
    
    fig, ax = plt.subplots(nrows=3, ncols=1,figsize=(8,6),sharex=True)
    plt.subplots_adjust(wspace=0.4,hspace=0.4 )    
    ax0=ax[0]
    ax0 = plotDailyLoads(ax0, df1x, c='b', lw=1, label='leaders')
    ax0 = plotDailyLoads(ax0, df2, c='k', lw=1, label='others')
    ax0.set_ylim([0.0,ymax])
    ax0.legend()
    
    ax1=ax[1]
    ax1,temp = plotDailyDeltaLoad(ax1, df3x)
    ax1.set_ylim([-1,1])
    
    ax2=ax[2]
    ax2,temp = plotDailyDeltaEnergy(ax2, df3x)
    ax2.set_ylim([0,ymaxDelta])
        
    pltPdf1.savefig() 
    plt.close()          
            
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    pltPdf1.close()

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return


def PlotWalk2DurationCurve(dirin='./',fnamein='file.csv', fnameinL='leaders.csv', fnameino='others.csv', 
                  dirout='./', fnameout='delta.csv',
                  m = 6, d = 21,dirrate = './', ratein='SCE-TOU-GS3-B.csv',
                  dirlog='./', fnameLog='PlotDeltaByDay.log'):
    
    """ Creates pdf with 365 pages showing the leader and other loads & the delta for each day of the year"""
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "PlotWalk2DurationCurve", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    # load time-series data for leaders & others
    df1raw, UniqueIDs, foutLog = getData(dirin, fnameinL, foutLog, varName='NormDmnd',usecols=[0,1,2])
    df2raw, UniqueIDs, foutLog = getData(dirin, fnameino, foutLog, varName='NormDmnd',usecols=[0,1,2])
    dfDelta, UniqueIDsGroup, foutLog = getData(dirin, fnamein, foutLog, varName=[ 'NormDmnd', 'Leaders', 'Others'], usecols=[0,1,3, 4, 5])
    
    # reading TOU rates
    rate = readTOURates(dirrate, ratein)

    # assign season & day type
    df1 = AssignRatePeriods(df1raw, rate, addRate=True, datetimeIndex=True)
    df2 = AssignRatePeriods(df2raw, rate, addRate=True, datetimeIndex=True)
    
    month = df1.index.month
    day = df1.index.day
    
    # find this day in the data
    relevant = (month==m) & (day==d)
    df2 = df2[relevant]
    df1 = df1[relevant]
    
    # calculate delta
    df3 = deltaLoadsFunction(df1, df2)
    
    # open pdf for figures
    print("Opening plot files")
    pltPdf1 = dpdf.PdfPages(os.path.join(dirout, fnameout))
    
    # find max y limits
    ymax = np.ceil(np.max([ df1['NormDmnd'].max() *2  , df2['NormDmnd'].max()*2  ])) / 2 +0.5

    # find min / max for delta figure
    ymaxDelta = 1.0
    y = np.cumsum(df3['NormDmnd'])/4
    y = y - np.min(y)
    ymaxDelta = np.max([ ymaxDelta, np.max(y) ])
    ymaxDelta = np.ceil( ymaxDelta * 2.0 ) / 2.0
    
    # iterate over each month of the year
    print('Plotting daily loads & deltas for %s' %(date(2016, m,1).strftime('%B')))
    
    # initialize figure
    fig, ax = plt.subplots(nrows=2, ncols=3,figsize=(8,6),sharex=False, sharey=True)
    plt.subplots_adjust(wspace=0.4,hspace=0.4 )    
    
    # plot delta between leaders & others 
    ax1=ax[0,0]
    ax1,temp = plotDailyDeltaLoad(ax1, df3, fillFlag=False, lw=3)
    ax1.set_ylim([-1,1])
    
    ax11=ax[0,1]
    ax11,temp = plotDailyDeltaLoad(ax11, df3, fillFlag=False, shiftFlag=True, lw=3)
    ax11.set_ylim([-1,1])
    
    ax2=ax[0,2]

    
    ax2, ymax = plotDeltaDuration(ax2, df3, c='steelblue', a=1.0, lw=1.5) 
    ax2.set_ylabel('Delta in Load [pu]]')
    
    pltPdf1.savefig() 
    plt.close()  
    
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    pltPdf1.close()

#%% **Unused
def xplotLoadDuration(ax0, df, lw=1, c='b', ls='-', a=1.0):
    
    """ adds specific day's duration curve to axis """
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_xlabel('Duration [h]')
    x = [x for x in range(0,int(df.shape[0])+int(df.shape[0]/(24/4)), int(df.shape[0]/(24/4)))]
    ax0.set_xticks(x)
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    ax0.set_xlim([0,  int(df.shape[0]*24/24) ])   
       
    df1 = df.copy()
    df1 = df1.sort_values('Others', ascending=False)
    ax0.step(np.arange(df1.shape[0]), df1['Others'] * 4.0,  ls, lw=lw, c=c, alpha=a)
    
    e = np.sum( df1['Others'].values)
    ymax = np.max([  np.max(abs(df1['Others'])) * 4.0 ])
    if np.isnan(ymax) or np.isinf(ymax):
        ymax = 0.0
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    
    return ax0, ymax, e
def xplotDeltaDuration_v2(ax0, df, lw=1, c='b', ls='-', a=1.0):
    """ adds specific day's duration curve to axis """
    # sort data
    df = df.sort_values(by='datetime', ascending=True)
    # format axis
    ax0.set_xlabel('Duration [h]')
    x = [x for x in range(-int(df.shape[0]),int(df.shape[0])+int(df.shape[0]/(24/4)), int(df.shape[0]/(24/4)))]
    ax0.set_xticks(x)
    ax0.set_xticklabels([str(np.abs(x)) for x in range(-24, 28,4)])  
    ax0.set_xlim([-int(df.shape[0]*16/24),  int(df.shape[0]*16/24) ])   
    # separate charge & discharge
    df1 = df.copy()
    charge = df1.loc[df1['NormDmnd']>0]
    discharge = df1.loc[df1['NormDmnd']<0]      
    # sort charge & discharge
    charge = charge.sort_values('NormDmnd', ascending=True)
    discharge = discharge.sort_values('NormDmnd', ascending=False)
    # plot charge & discharge  
    ax0.step(-1.*np.arange(charge.shape[0]), charge['NormDmnd'] * 4.0 ,  ls, lw=lw, c=c, alpha=a)
    ax0.step(np.arange(discharge.shape[0]), discharge['NormDmnd'] * 4.0,  ls, lw=lw, c=c, alpha=a)
    # find maximum values
    ymax = np.max([ np.max(abs(charge['NormDmnd'])) * 4.0 , np.max(abs(discharge['NormDmnd'])) * 4.0 ])
    ymaxC = np.max(charge['NormDmnd']) * 4.0
    ymaxD = np.min(discharge['NormDmnd']) * 4.0
    # format gridlines
    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
    # assign output
    return ax0, ymax, ymaxC, ymaxD

def xplotDeltaDurationPercentage_v2(ax0, df, lw=1, c='b', ls='-', a=1.0):
    
    """ adds specific day's duration curve to axis """
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_xlabel('Duration [h]')
    x = [x for x in range(-int(df.shape[0]),int(df.shape[0])+int(df.shape[0]/(24/4)), int(df.shape[0]/(24/4)))]
    ax0.set_xticks(x)
    ax0.set_xticklabels([str(np.abs(x)) for x in range(-24, 28,4)])  
    ax0.set_xlim([-int(df.shape[0]*16/24),  int(df.shape[0]*16/24) ])   
       
    df1 = df.copy()
    charge = df1.loc[df1['NormDmnd']>0]
    discharge = df1.loc[df1['NormDmnd']<0]      
    
    charge = charge.sort_values('NormDmnd', ascending=True)
    discharge = discharge.sort_values('NormDmnd', ascending=False)
    
    ax0.step(-1.*np.arange(charge.shape[0]), charge['NormDmnd'] /np.max(df1['Others']) *100,  ls, lw=lw, c=c, alpha=a)
    ax0.step(np.arange(discharge.shape[0]), discharge['NormDmnd'] /np.max(df1['Others']) *100,  ls, lw=lw, c=c, alpha=a)
    
    ymax = np.max([ np.max(abs(charge['NormDmnd']) /np.max(df1['Others']) *100 ), np.max(abs(discharge['NormDmnd'])/np.max(df1['Others']) *100)  ])
    ymaxC = np.max(charge['NormDmnd']) /np.max(df1['Others']) *100 
    ymaxD = np.min(discharge['NormDmnd']) /np.max(df1['Others']) *100 

    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 

    return ax0, ymax, ymaxC, ymaxD    
    
def xPlotDurationSummary(dirin='./', fnamein='IntervalData.normalized.csv', 
                 dirout='plots/', fnameout='DurationCurves.pdf', 
                 normalized=False,
                 dirlog='./', fnameLog='PlotDeltaSummary.log'):
    
    """Creates pdf with 13 pages: 1 page summary of entire year followed by monthly. Each page shows shifted energy & duration curves """
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "PlotDurationSummary", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
#    # load data from file, find initial list of unique IDs. Update log file
#    if normalized:
#        df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog,  varName=['NormDmnd', 'AbsDemand', 'Leaders', 'Others'], usecols=[0,1,2])
#    else:
#        df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog, varName=[ 'NormDmnd', 'Leaders', 'Others'], usecols=[0,1,3, 4, 5])
    
    # load data from file, find initial list of unique IDs. Update log file    
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin,  fnamein, foutLog, datetimeIndex=True)
    if not('Others' in df1.columns):
        df1['Others'] = df1['Demand']
    if not('NormDmnd' in df1.columns):
        df1['NormDmnd'] = df1['NormDelta']
    
    # add season & day type
    df1 = assignDayType(df1)

    # open pdf for figures
    print("Opening plot files")
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    # create annual summary of shifted energy & load duration
    foutLog.write("Creating annual figure" )
    print("Creating annual figure" )
    pltPdf1,  yMaxD = annualDurationSummaryPage(pltPdf1, df1, fnamein, normalized)
    
    # create monthly summaries of shifted energy & load duration
    foutLog.write("Creating monthly figures" )
    print("Creating monthly figures" )
    pltPdf1 = monthlyDurationSummaryPages(pltPdf1, df1, fnamein,  yMaxD, normalized)  
    
    # Closing plot files
    print('Writing output file: %s' %os.path.join(os.path.join(dirout, fnameout)))
    foutLog.write('\n\nWriting: %s' %os.path.join(dirout, fnameout))
    pltPdf1.close()

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return



def xplotDailyDeltas(ax0, df, lw=1, c='b', ls='-'):
    
    """ adds specific day's power & energy deltas to axis """
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Delta')
    ax0.set_xlabel('Hour of the Day [h]')
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    y = [yy for yy in range(-40, 41,1)]
    ax0.set_yticks(y)  
    ax0.xaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5) 
    y = np.cumsum(df['NormDelta'])/4
    y = y - np.min(y)
    ax0.fill_between(np.arange(df.shape[0]), 0,  df['NormDelta'],  label='Load [pu]')      
    ax0.plot(np.arange(df.shape[0]), y, ls, lw=lw*2, c='purple', label='Energy [pu-h]')    
    return ax0, np.max(y)






def xplotDailyRate(ax0, df, lw=1, c='b', ls='-'):
    """ adds specific day's power & energy deltas to axis """
    df = df.sort_values(by='datetime', ascending=True)
    ax0.set_ylabel('Energy Cost [$/kWh]')
    ax0.set_xlabel('Hour of the Day [h]')
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
    ax0.xaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5)    
    ax0.yaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5) 
    ax0.plot(np.arange(df.shape[0]),   df['EnergyCost'],  label='Load [pu]')  
    
    return ax0, np.max(df['EnergyCost'])



def xannualDurationSummaryPage(pltPdf1, df1, fnamein, normalized=False):
    """ create page summary for specific month & add to pdf """
    
    # initialize figure
    #fig, ax = plt.subplots(nrows=1, ncols=2,figsize=(8,6),sharex=False)
    #ax1 = ax[1]
    #ax0 = ax[0]
    fig = plt.figure(figsize=(8,6))
    plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
    ax1 = plt.subplot2grid((1, 2), (0, 0),  fig=fig)
    ax2 = plt.subplot2grid((1, 2), (0, 1),  fig=fig)
    fig.suptitle(fnamein + " / entire year" )  
    
    # initialize variables
    month = df1.index.month
    day = df1.index.day
    ymax = 0
    yMaxD = 1.0
    yMaxP = 0.0
    
    for m in range(1, 13,1):
        days = list(set(df1.loc[(month==m)].index.day))
           
            
        # plot load-duration
        ax1.set_title( "Flexibility")
        # iterate for each day in month
        for d in days:
            relevant = (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                pass
            else:
                ax1, ymax = plotDeltaDuration_v2(ax1, df1.loc[relevant], c='steelblue', a=0.1) 
                yMaxD = np.max([yMaxD , ymax])
        if normalized:
            ax1.set_ylabel('Shiftable Load [p.u.]')
        else:
            ax1.set_ylabel('Shiftable Load [MW]')
        ax1.set_ylim([-yMaxD , yMaxD ])
        
        
        # plot load-duration as percentage
        ax2.set_title( "Percent of Daily Peak")
        # iterate for each day in month
        for d in days:
            relevant = (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                pass
            else:
                ax2, ymax, temp0, temp1 = plotDeltaDurationPercentage_v2(ax2, df1.loc[relevant], c='steelblue', a=0.1) 
                yMaxP = np.max([yMaxP , ymax])
        ax2.set_ylabel('Shiftable Load [%]')
        ax2.set_ylim([-100 , 100 ])        
    
    # save to pdf
    pltPdf1.savefig() 
    plt.close() 
        
    return pltPdf1, yMaxD

def xmonthlyDurationSummaryPages(pltPdf1, df1, fnamein, yMaxD, normalized=False):
    """ create page summary for specific month & add to pdf"""
    
    month = df1.index.month
    day = df1.index.day
    
    # iterate over each month
    for m in range(1, 13,1):
        days = list(set(df1.loc[(month==m)].index.day))
        

        fig = plt.figure(figsize=(8,6))
        plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
        ax1 = plt.subplot2grid((1, 2), (0, 0),  fig=fig)
        ax2 = plt.subplot2grid((1, 2), (0, 1),  fig=fig)
        fig.suptitle(fnamein  + " / " + date(2016, m,1).strftime('%B') )   

        # plot load-duration
        ax1.set_title( "Flexibility")  
        
        # iterate for each day of the month
        for d in days:
            relevant =  (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                ax1, ymax1 = plotDeltaDuration_v2(ax1, df1.loc[relevant], c='gray', a=0.2)
            else:
                ax1, ymax1 = plotDeltaDuration_v2(ax1, df1.loc[relevant], c='steelblue', a=0.5)
        ax1.set_ylim([-yMaxD, yMaxD])
        ax1.set_ylabel('Shiftable Load [MW]')
            
            
        # plot load-duration
        ax2.set_title( "Percentage of Daily Peak")  
        
        # iterate for each day of the month
        for d in days:
            relevant =  (month==m) & (day==d)
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                ax2, ymax1, ymax2, ymax3 = plotDeltaDurationPercentage_v2(ax2, df1.loc[relevant], c='gray', a=0.2)
            else:
                ax2, ymax1, ymax2, ymax3 = plotDeltaDurationPercentage_v2(ax2, df1.loc[relevant], c='steelblue', a=0.5)
        ax2.set_ylim([-100,100])
        ax2.set_ylabel('Shiftable Load [%]')
        
        # save figure to pdf
        pltPdf1.savefig() 
        plt.close()  
        
    return pltPdf1
