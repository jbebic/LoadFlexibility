# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 11:51:10 2018

@author: berryi
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
from SupportFunctions import getData, logTime, createLog,  assignDayType, getDataAndLabels
from UtilityFunctions import AssignRatePeriods, readTOURates
from NormalizeLoads import NormalizeGroup

#%% Version and copyright info to record on the log file
codeName = 'GroupAnalysis.py'
codeVersion = '1.8'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Irene Berry, GE Global Research\n"

# %% Basic Function Definitions
def deltaLoadsFunction(df1, df2):
    
    """ take leader and other dateframes and calculate deltas into third dataframe """
    
    #copy dataframe
    df3 = df2.copy()
    # calculate normalized and absolute delta
    df3['NormDelta']   = df1['NormDmnd'] - df2['NormDmnd']
    df3['AbsDelta']    = df3['NormDelta'] * ( df2['DailyAverage']  )
    
    # assign leaders & others to new dataframe
    df3['Leaders']     = df1['Demand'].copy()
    df3['Others']      = df2['Demand'].copy()
    
    # assign leaders & others daily averages to new data frame
    df3['DailyAvgLeaders']     = df1['DailyAverage'] .copy()
    df3['DailyAvgOthers']      = df2['DailyAverage'] .copy()
    
    # assign normalized leaders & others to new dataframe
    df3['NormLeaders'] = df1['NormDmnd'].copy()
    df3['NormOthers']  = df2['NormDmnd'].copy()
    
    # return only the new dataframe
    return df3

def findShiftingEvents(df0, threshold=0.1):
    
    """ searches in a normalized segment of data for charge/discharge cycles & adds to the dataframe """
    
    # copy dataframe
    df = df0.copy()
    
    # idendify modes
    mode = np.asarray(['0' for x in range(0, len(df),1)])
    charge = df['NormDelta']>0
    mode[charge] = 'c' 
    discharge = df['NormDelta']<0
    mode[discharge] = 'd' 
    df = df.assign(mode=mode)
    rawmode = mode.copy()
    gaps = np.where(mode=='0')[0]
    for ig in range(0, len(gaps)):
        v0 = [x for x in range(0, gaps[ig]) if not(x in gaps)]
        v1 = [x for x in range(gaps[ig], len(mode)) if not(x in gaps)]
        if len(v0)<1:
            v0 = v1
        if len(v1)<1:
            v1 = v0
        if len(v1)>0:
            before = mode[ v0[-1] ]
            after = mode[v1[0]]
            if before==after:
                mode[gaps[ig]]=before
    
    # identify transitions
    rawtransitions = np.asarray( np.where( (rawmode[:-1] != rawmode[1:])  )[0])
    rawCycle = np.asarray([ 0 for x in range(0, len(charge)) ])
    if len(rawtransitions) > 1:
        for i in range(1, len(rawtransitions),1):
            rawCycle[rawtransitions[i-1]+1:rawtransitions[i]+1 ] = i
    df = df.assign(rawCycle=rawCycle)
    
    energy = df.groupby(['rawCycle'])['NormDelta'].cumsum()
    totalEnergy = np.cumsum( df['NormDelta'].values)
    totalEnergy = totalEnergy - np.min(totalEnergy)
    
    rawtransitions0 = np.asarray( np.where( (mode[:-1] != mode[1:]) & (mode[:-1]!='0')  )[0])
    deltaEnergy = energy[rawtransitions0].values
    deltaEnergy = np.nan_to_num(deltaEnergy)
    rawdischarges = rawtransitions0[ deltaEnergy<-np.max(totalEnergy)*threshold ] 
    rawcharges = rawtransitions0[ deltaEnergy>np.max(totalEnergy)*threshold ]
    
    chargeTransitions = []
    dischargeTransitions = []
    for i in range(1, len(rawdischarges),1):
        c = [ x for x in rawcharges if x > rawdischarges[i-1] and x < rawdischarges[i] ]
        if len(c)>0:
            if abs(energy.values[c[0]]) < abs(energy.values[rawdischarges[i]]):
                chargeTransitions.append(c[0])
            else:
                dischargeTransitions.append(rawdischarges[i])

    transitions = []
    for x in chargeTransitions:
        try:
            i0 = np.max(np.where( mode[:x]!='c'  )[0] )+1
            e0 = totalEnergy[i0-1]
            i1 = i0 + np.min(np.where( totalEnergy[i0:]<e0  )[0]) 
            transitions.append(i0)
            transitions.append(i1)
        except:
            pass
        
    for x in dischargeTransitions:
        
        try:
            i0 = np.max(np.where( mode[:x]!='d'  )[0] )+1
            e0 = totalEnergy[i0-1]
            i1 = i0 + np.min(np.where( totalEnergy[i0:]>e0  )[0]) 
            transitions.append(i0)
            transitions.append(i1)
        except:
            pass
        
    # create cycle count vector
    cycle = np.asarray([ 0 for x in range(0, len(charge)) ])
    if len(transitions)>1:
        for i in range(1, len(transitions),1):
            cycle[ transitions[i-1]:transitions[i] ] = i
          
    # assign to dataframe
    df = df.assign(cycle=cycle)
    
    return df

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

def plotDailyDeltaLoad(ax0, df0, lw=1, c='b', ls='-', fillFlag=True, shiftFlag=False):
    
    """ adds specific day's power & energy deltas to axis """
    
    df = df0.copy()
    df = df.sort_values(by='datetime', ascending=True)    
    ax0.set_ylabel('Delta in Loads [pu]')
    ax0.set_xlabel('Hour of the Day [h]')
    ax0.set_xlim([0,df.shape[0]])
    ix = np.max(df.loc[df['NormDelta']<0].index)
    L = len( df.loc[ix:])    
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    y = [yy for yy in range(-80, 81,1)]
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

def plotDailyDeltaEnergy(ax0, df0, lw=1, c='b', ls='-'):
    
    """ adds specific day's power & energy deltas to axis """
    
    df = df0.copy()
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
    cycle = df['cycle'].values
    transitions = np.where( (cycle[:-1] != cycle[1:]) )[0]

    # print cycle transitions
    for ix in transitions:
        ax0.plot([ix,ix], [0, 100], lw=1.5, color='orangered')

    return ax0, np.max(y)

def plotHistogram(ax2, dailyEnergy, shiftedEnergy):
    
    """ adds histogram of daily shifted energy """
    
    y = np.asarray(shiftedEnergy)/np.asarray(dailyEnergy)*100
    yMax = np.ceil(np.max(y))
    ax2.hist(y,bins='auto', color='purple', lw=0, alpha=0.5)   
    ax2.set_xlabel('Shiftable Energy [% of Daily]')
    ax2.set_ylabel('Number of Days')
    ax2.set_xlim([0,yMax])  
    ax2.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
    ax2.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)
                   
    return ax2

def plotDeltaDuration(ax0, df, lineWidth=1, lineColor ='steelblue', lineStyle='-', lineAlpha=1.0,  addText=False, varType='Norm', threshold=0.1):
    
    """ adds specific day's duration curve to axis """   
    cm = pylab.get_cmap('jet')
    
    # calculate # data points per hour
    Ns = 60 / (df.index[1].minute - df.index[0].minute)
        
    # switch between three options 
    if varType in ['Percentage', '%', 'Percent', 'percent', 'percentage']:
          varName='AbsDelta'
    elif varType in ['Norm', 'norm', 'pu']:
        varName='NormDelta'
    else:
        varName = 'AbsDelta'
        
    charge = df.loc[df[varName]>0]
    discharge = df.loc[df[varName]<0]    
    charge = charge.sort_values(varName, ascending=True)
    discharge = discharge.sort_values(varName, ascending=False)   
    x_raw = np.asarray( np.sort( list( -1.*np.arange(charge.shape[0]) / Ns ) + list( np.arange(discharge.shape[0]) /Ns)) )
    y_raw = np.flipud( np.asarray( np.sort(  list(charge[varName].values/np.max(df['Others'].values) ) +  list( discharge[varName].values /np.max(df['Others'].values)  )   )))
    x_out = np.asarray( np.sort( list([ x/Ns for x in range(-int(24*Ns),1, 1) ]  ) + list([ x/Ns for x in range(0,int(24*Ns+1), 1) ]  ) ))
    
    y_out = []
    for i in range(0,len(x_out),1):
        ix = np.where( x_out[i] == x_raw)[0]
        if len(ix)>0:
            y_out.append(y_raw[ix][0])
        else:
            y_out.append(np.nan)
    
    # sort dataframe & extract charge / discharge vectors
    Nevents = np.max(df['cycle'])
    for n in range(0, Nevents+1,1):  
        if Nevents>0 and n>0:
            lineColor = cm(1.*n/Nevents)
        else:
            lineColor='steelblue'
        df1 = df.loc[df['cycle']==n].copy()

        charge = df1.loc[df1[varName]>0]
        discharge = df1.loc[df1[varName]<0]    
        charge = charge.sort_values(varName, ascending=True)
        discharge = discharge.sort_values(varName, ascending=False)   
        
        # format x and y ticks and labels
        x = [ x for x in range(-int(df.shape[0]),int(df.shape[0])+int(df.shape[0]/(24/Ns)), int(df.shape[0]/(24/Ns))) ]
        ax0.set_xticks(x)
        ax0.set_xticklabels([str(np.abs(x)) for x in range(-24, 28,int(Ns))])  
        ax0.set_xlim([-int(df.shape[0]*20/24),  int(df.shape[0]*20/24) ])   
                
        if varType in ['Percentage', '%', 'Percent', 'percent', 'percentage']:
            """ PERCENTAGE OF DAILY MAX """
            # plot charge & discharge
            ax0.step(-1.*np.arange(charge.shape[0]), charge[varName] /np.max(df['Others']) *100,  lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)
            ax0.step(np.arange(discharge.shape[0]), discharge[varName] /np.max(df['Others']) *100,  lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)
            # calculate min / max values
            ymax = np.max([ np.max(abs(charge[varName]) /np.max(df['Others']) *100 ), np.max(abs(discharge[varName])/np.max(df['Others'])*100)  ])
            ymaxC = np.max(charge[varName]) /np.max(df['Others']) *100 
            ymaxD = np.min(discharge[varName]) /np.max(df['Others']) *100 
            # set y-label
            ax0.set_ylabel('Shfitable Load [%]')
            
        elif varType in ['Norm', 'norm', 'pu']:
            """ NORMALIZED DELTA """
            # plot charge & discharge
            ax0.step(-1.*np.arange(charge.shape[0]), charge[varName]    , lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)
            ax0.step( np.arange(discharge.shape[0]), discharge[varName] , lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)            
            # calculate min / max values
            ymax = np.max([ np.max(abs(charge[varName])) , np.max(abs(discharge[varName]))  ])    
            ymaxC = np.max(charge[varName]) * Ns
            ymaxD = np.min(discharge[varName]) * Ns
            # set y-label
            ax0.set_ylabel('Shfitable Load [pu]')
            # plot horizontal lines at the threshold
            ax0.plot( [-int(df.shape[0]*24/24),  int(df.shape[0]*24/24)], [threshold,  threshold ], "--", lw=1, color='gray', alpha=0.5)
            ax0.plot( [-int(df.shape[0]*24/24),  int(df.shape[0]*24/24)], [-threshold, -threshold],  "--",  lw=1, color='gray', alpha=0.5) 
        
        else:
            """ ABSOLUTE DELTA of the OTHERS """
            # plot charge & discharge
            ax0.step(-1.*np.arange(charge.shape[0]), charge[varName] * Ns ,  lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)
            ax0.step(np.arange(discharge.shape[0]), discharge[varName]* Ns ,  lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)
                        
            # calculate min / max values
            ymax = np.max([ np.max(abs(charge[varName])) , np.max(abs(discharge[varName]))  ])  * Ns  
            ymaxC = np.max(charge[varName]) * Ns
            ymaxD = np.min(discharge[varName]) * Ns
            
            # set y-label
            ax0.set_ylabel('Shfitable Load [MW]')
            
        # add gridlines & x-label
        ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
        ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
        ax0.set_xlabel('Duration [h]')
        
    return ax0, ymax, ymaxC, ymaxD, x_out, y_out

def plotShiftedEnergy(ax0, df, lw=1, c='b', ls='-',a=1.0, showCycles=False):
    
    """ adds specific day's shifted energy to axis """
    df = df.sort_values(by='datetime', ascending=True)                  
    y = np.cumsum(df['NormDelta'])
    y = y - np.min(y)  
    ax0.plot(np.arange(df.shape[0]), y, ls, lw=lw, c=c, alpha=a)
    ax0.set_xlim([0,df.shape[0]])
    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
    
    # print cycle transitions
    if showCycles:
        cycle = df['cycle'].values
        transitions = np.where( (cycle[:-1] != cycle[1:]) )[0]
        for ix in transitions:
            ax0.plot([ix,ix], [0, np.max(y)], lw=1, color='orangered')
    
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
def annualSummaryPage(pltPdf1, df1, fnamein, normalized=False, threshold=0.1):
    
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
            df1x = findShiftingEvents(df1.loc[relevant], threshold=threshold)
            
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                pass
            else:
                dailyEnergy.append( np.sum( df1x['Others'].values) )
                ax1, ymax = plotShiftedEnergy(ax1, df1x, c='purple', a=0.1)
                yMax  = np.max([yMax, ymax])
                shiftedEnergy.append(ymax)
            
            if df1x['DayType'][0] in ['we','h']:
                pass
            else:
                ax0, ymax, ymaxC, ymaxD, x0, y0 = plotDeltaDuration(ax0, df1x, lineAlpha=0.1, addText=False, varType='Abs', threshold=threshold) 
                yMaxD = np.max([yMaxD , ymax])
                yMaxD_C = np.max([yMaxD_C , ymaxC]) 
                yMaxD_D = np.min([yMaxD_D , ymaxD])
                
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                pass
            else:
                ax2, ymax, ymaxC, ymaxD, x0, y0= plotDeltaDuration(ax2, df1x, lineAlpha=0.1, addText=False, varType='%', threshold=threshold) 
                yMaxP = np.max([yMaxP , ymax])
                                
        yMax = np.ceil(yMax)
        ax1.set_ylim([0,yMax])
        ax0.set_ylim([-yMaxD*1.15 , yMaxD*1.15 ])
        yMaxP_C = np.max([yMaxP_C , ymaxC]) 
        yMaxP_D = np.min([yMaxP_D , ymaxD])
        ax2.plot( [-int(df1.shape[0]*24/24),  int(df1.shape[0]*24/24)], [threshold*100,  threshold*100 ], "--", lw=1, color='gray', alpha=0.5)
        ax2.plot( [-int(df1.shape[0]*24/24),  int(df1.shape[0]*24/24)], [-threshold*100, -threshold*100],  "--",  lw=1, color='gray', alpha=0.5) 
        ax2.set_ylim([-yMaxP*1.15 , yMaxP*1.15 ])
        
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
               fontsize=8)
    
    ax0.text(s=str(round(yMaxD_D,1)) + ' MW',
               x=12*4, y=yMaxD_D,
               verticalalignment="top",horizontalalignment="center",
               fontsize=8)
    
    ax2.text(s=str(round(yMaxP_C,1)) + '%',
               x=-12*4, y=yMaxP_C,
               verticalalignment="bottom",horizontalalignment="center",
               fontsize=8)
    
    ax2.text(s=str(round(yMaxP_D,1)) + '%',
               x=12*4, y=yMaxP_D,
               verticalalignment="top",horizontalalignment="center",
               fontsize=8)   
    
    # save to pdf
    pltPdf1.savefig() 
    plt.close() 
        
    return pltPdf1, yMax, yMaxD, yMaxP, yMaxH, xMaxH, yMaxD_C, yMaxD_D

def monthlySummaryPages(pltPdf1, df1, fnamein,  yMaxE, yMaxD, yMaxP, yMaxH, xMaxH, normalized=False, saveAllDurationCurves=False, threshold=0.1):
    
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
            df1x = findShiftingEvents(df1.loc[relevant], threshold=threshold)
            
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                ax1,ymax0 = plotShiftedEnergy(ax1, df1x, c='gray', a=0.2)
            else:
                dailyEnergy.append( np.sum( df1x['Others'].values) )
                ax1,ymax0 = plotShiftedEnergy(ax1, df1x, c='purple', a=0.5)
                shiftedEnergy.append(ymax0)               
        
            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
                ax0, ymax1, temp0, temp1, x0, y  = plotDeltaDuration(ax0, df1x, lineColor='gray', lineAlpha=0.2, addText=False, varType='Abs', threshold=threshold)
            else:
                ax0, ymax1 , temp0, temp1, x, y = plotDeltaDuration(ax0, df1x, lineAlpha=0.5, addText=False, varType='Abs', threshold=threshold)
            if df1x['DayType'][0] in ['we','h']:
                ax2, ymax, temp0, temp1 , x0, y0 = plotDeltaDuration(ax2, df1x, lineColor='gray', lineAlpha=0.2, addText=False, varType='%', threshold=threshold ) 
            else:
                ax2, ymax, temp0, temp1, x0, y0  = plotDeltaDuration(ax2, df1x, lineAlpha=0.5, addText=False,varType='%', threshold=threshold)            
        
        ax1.set_ylim([0,yMaxE])
        ax1.set_xlabel('Shiftable Energy [MWh]')        
        ax0.set_ylim([-yMaxD*1.15, yMaxD*1.15])
        
        ax2.plot( [-int(df1.shape[0]*24/24), int(df1.shape[0]*24/24)], [threshold*100,  threshold*100 ], "--", lw=1, color='gray', alpha=0.5)
        ax2.plot( [-int(df1.shape[0]*24/24), int(df1.shape[0]*24/24)], [-threshold*100, -threshold*100],  "--",  lw=1, color='gray', alpha=0.5) 
        ax2.set_ylim([-yMaxP*1.15, yMaxP*1.15])
        
        # plot histogram
        ax3 = plotHistogram(ax3, dailyEnergy, shiftedEnergy)             
        ax3.set_ylim([0.0, yMaxH ])        
        ax3.set_xlim([0.0, xMaxH ])                    
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
    
    """ calculates delta between leaders & others in a group and saves to csv """
    
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
    df3.to_csv( os.path.join(dirout,fnameout), 
               columns=['CustomerID', 'datetime', 'NormDelta','AbsDelta', 'Leaders', 'Others',  'NormLeaders', 'NormOthers', 'DailyAvgLeaders', 'DailyAvgOthers'], 
               float_format='%.5f', date_format='%Y-%m-%d %H:%M', index=False) # this is a multiindexed dataframe, so only the data column is written

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

def PlotDeltaByDay(dirin='./', fnameinL='leaders.csv',   fnameino='others.csv', 
                  dirout='./', fnameout='delta.csv', 
                  dirlog='./', fnameLog='PlotDeltaByDay.log', 
                  threshold = 0.1,withDuration=True):
    
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
            df3x = findShiftingEvents(df3.loc[relevant], threshold=threshold)
            
            # initialize figure
            if withDuration:
                fig = plt.figure(figsize=(8,6))
                plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
                ax0 = plt.subplot2grid((3, 2), (0, 0),   fig=fig)
                ax1 = plt.subplot2grid((3, 2), (1, 0),  fig=fig)
                ax2 = plt.subplot2grid((3, 2), (2, 0),   fig=fig)
                ax3 = plt.subplot2grid((3, 2), (0, 1), rowspan=3, fig=fig)
                fig.suptitle(  date(2016, m,1).strftime('%B')  + " / " + str(int(d)) +  " / " + df1.loc[relevant, 'DayType'][0])   
            else:
                fig, ax = plt.subplots(nrows=3, ncols=1,figsize=(8,6),sharex=True)
                ax0=ax[0]
                ax1=ax[1]
                ax2=ax[2]
                fig.suptitle( fnameinL + " / " +  date(2016, m,1).strftime('%B')  + " / " + str(int(d)) +  " / " + df1.loc[relevant, 'DayType'][0])   
                plt.subplots_adjust(wspace=0.4,hspace=0.4 )  
            
            # plot loads of leaders & others 
            ax0 = plotDailyLoads(ax0, df1.loc[relevant], c='b', lw=1, label='leaders')
            ax0 = plotDailyLoads(ax0, df2.loc[relevant], c='k', lw=1, label='others')
            ax0.set_ylim([0.0,ymax])
            ax0.legend()
            
            # plot delta between leaders & others - in POWER
            ax1,temp = plotDailyDeltaLoad(ax1, df3x)
            ax1.set_ylim([-yLim,yLim])
            
            # plot delta between leaders & others - in ENERGY
            ax2,temp = plotDailyDeltaEnergy(ax2, df3x)
            ax2.set_ylim([0,ymaxDelta])
            
            if withDuration:
                # plot duration curve of the load DELTA
                ax3, temp0, temp1, temp2, x0, y0 = plotDeltaDuration(ax3, df3x, addText=True, varType='pu', threshold=threshold)
                ax3.set_ylim([-yLim, yLim])
                    
            # add to pdf
            pltPdf1.savefig() 
            plt.close()   
                
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
    pltPdf1.close()

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return



def SaveDeltaByMonth(dirin_raw = './', 
                    dirout = './', 
                    fnamebase = 'fnamebase',
                    fnameout = 'duration.csv', 
                    Ngroups=1,
                    dirlog='./', 
                    fnameLog='SaveDeltaByMonth.log' ):
    
    """ Creates pdf with 365 pages showing the leader and other loads & the delta for each day of the year"""
    
    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "PlotDeltaByDay", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    months = [ date(2016, m,1).strftime('%B') for m in range(1, 13,1)]
    durations_we = pd.DataFrame(columns=months)
    durations    = pd.DataFrame(columns=months)
    
    # iterate over each month of the year
    print("Calculating Average Delta for")
    for m in range(1, 13,1):
        print('\n%s' %(date(2016, m,1).strftime('%B')))
        
        for n in range(1,Ngroups+1,1): 
            groupL = 'g' + str(n) + 'L'
            groupo = 'g' + str(n) + 'o'
            fnameinL=fnamebase+ "." + groupL + ".normalized.csv"
            fnameino=fnamebase+ "." + groupo + ".normalized.csv"

            # load time-series data for leaders & others
            dfL, UniqueIDs, foutLog = getDataAndLabels( dirin_raw, fnameinL, foutLog, datetimeIndex=True )
            dfo, UniqueIDs, foutLog = getDataAndLabels( dirin_raw, fnameino, foutLog, datetimeIndex=True )
    
            # calculate # data points per hour
            Ns = 60 / ( dfL.index[1].minute - dfL.index[0].minute )
            v = [ x/Ns for x in range(0, int(24*Ns),1) ]
            
            leaders_we = pd.DataFrame( index=v )
            others_we = pd.DataFrame( index=v )
            leaders = pd.DataFrame( index=v )
            others = pd.DataFrame( index=v )
            
            # assign season & day type
            dfL = assignDayType( dfL, datetimeIndex=True )
            dfo = assignDayType( dfo, datetimeIndex=True )
            monthL = dfL.index.month
            dayL = dfL.index.day
            montho = dfo.index.month
            dayo = dfo.index.day
            
            # iterate over each day of the month
            days = list(set(dfL.loc[(monthL==m)].index.day))
            for d in days:
                relevantL = (monthL==m) & (dayL==d)
                relevanto = (montho==m) & (dayo==d)
                
                if dfL.loc[relevantL, 'DayType'][0] in ['we','h']:
                    # find this day in the data
                    try:
                        leaders_we[d] = dfL.loc[relevantL,'Demand'].values
                        others_we[d]  = dfo.loc[relevanto,'Demand'].values
                    except:
                        pass
                    
                else:
                    # find this day in the data
                    try:
                        leaders[d] = dfL.loc[relevantL,'Demand'].values
                        others[d]  = dfo.loc[relevanto,'Demand'].values
                    except:
                        pass
                    
            # sum & normalize the leaders 
            leaders = leaders.T
            avgLeaders = leaders.mean(axis=0).values
            normLeaders = avgLeaders / np.mean(avgLeaders)
            
            # sum & normalize the others
            others = others.T
            avgOthers = others.mean(axis=0).values
            normOthers = avgOthers / np.mean(avgOthers)
            
            # delta between leaders and others
            normDelta = np.flipud( np.sort((normLeaders - normOthers)) )
            durations[(date(2016, m,1).strftime('%B'))] = normDelta  #*np.mean(avgOthers)
            
            # sum & normalize the leaders 
            leaders_we = leaders_we.T
            avgLeaders_we = leaders.mean(axis=0).values
            normLeaders_we = avgLeaders / np.mean(avgLeaders_we)
            
            # sum & normalize the others
            others_we = others_we.T
            avgOthers_we = others_we.mean(axis=0).values
            normOthers_we = avgOthers_we / np.mean(avgOthers_we)
            
            # delta between leaders and others
            normDelta_we = np.flipud( np.sort((normLeaders_we - normOthers_we)) )
            durations_we[(date(2016, m,1).strftime('%B'))] = normDelta_we # *np.mean(avgOthers_we)
            
    print('\nWriting: %s' %os.path.join(os.path.join(dirout, fnameout.replace('.csv',  ".Weekdays.csv" ))))
    durations = durations.T
    durations.to_csv(dirout + "/" + fnameout.replace('csv',  ".Weekdays.csv" ))     
    
    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout.replace('.csv',  ".Weekends.csv" ))))
    durations_we = durations_we.T
    durations_we.to_csv(dirout + "/" + fnameout.replace('.csv',  ".Weekends.csv" ))        

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return

def PlotDeltaSummary(dirin='./', fnamein='delta.csv', 
                 dirout_plots='plots/', fnameout_plots='DurationCurves.pdf', 
                 normalized=False, threshold=0.1,
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
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout_plots, fnameout_plots))

    # create annual summary of shifted energy & load duration
    foutLog.write("Creating annual figure" )
    print("Creating annual figure" )
    pltPdf1, yMaxE, yMaxD, yMaxP, yMaxH, xMaxH, yMaxD_C, yMaxD_D = annualSummaryPage(pltPdf1, df1, fnamein, normalized,threshold=threshold)       
    
    # create monthly summaries of shifted energy & load duration
    foutLog.write("\nCreating monthly figures" )
    print("Creating monthly figures" )
    pltPdf1 = monthlySummaryPages(pltPdf1, df1, fnamein, yMaxE, yMaxD, yMaxP, yMaxH, xMaxH, normalized,threshold=threshold)  
        
    # write results for user
    print('\tMaximum Shiftable Load, Charging is ' + str(round(yMaxD_C,2) ) + ' MW')
    foutLog.write('\n\tMaximum Shiftable Load, Charging is ' + str(round(yMaxD_C,2) ) + ' MW')
    print('\tMaximum Shiftable Load, Disharging is ' + str(round(yMaxD_D,2) ) + ' MW')
    foutLog.write('\n\tMaximum Shiftable Load, Disharging is ' + str(round(yMaxD_D,2) ) + ' MW')
    
    # Closing plot files
    print('Writing output file: %s' %os.path.join(os.path.join(dirout_plots, fnameout_plots)))
    foutLog.write('\n\nWriting: %s' %os.path.join(dirout_plots, fnameout_plots))
    pltPdf1.close()

    # finish log with run time
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    
    return



def GroupAnalysisMaster(dirin_raw='./',  dirout_data='./', dirout_plots='./',
                        fnamebase='NAICS', fnamegroup = 'NAICS.groups.csv', 
                        fnamein='IntervalData.csv',  
                        Ngroups=4, threshold=1.0, demandUnit='Wh',
                        dirlog='./', fnameLog='GroupAnalysisMaster.log',
                        steps=['NormalizeGroup', 'DeltaLoads', 'PlotDeltaByDayWithDuration', 'PlotDeltaSummary']):

    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLogMaster = createLog(codeName, "GroupAnalysisMaster", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
                        
    for n in range(1,Ngroups+1,1): 
        
        # write to log and print about the master loop
        foutLogMaster.write('\n********************************************************')        
        print('\n********************************************************')
        codeTstartx = datetime.now()
        foutLogMaster.write('\nAnalyzing group #' + str(n) + ' : ' + str(datetime.now()-codeTstartx) )
        
        print('\nAnalyzing group #' + str(n) + ' : ' + str(datetime.now()-codeTstartx) )
        groupL = 'g' + str(n) + 'L'
        groupo = 'g' + str(n) + 'o'
        fnameinL=fnamebase+ "." + groupL + ".normalized.csv"
        fnameino=fnamebase+ "." + groupo + ".normalized.csv"
        fnameout_raw  = fnamebase+".delta." + groupL + "-" + groupo 
        
        if ('Normalize' in steps) or ('NormalizeGroup' in steps):
            
            # normalize leaders
            NormalizeGroup(dirin=dirin_raw, 
                           fnamein=fnamein, 
                           groupName=groupL,
                           considerCIDs=fnamebase + "." + groupL+ ".groupIDs.csv",
                           demandUnit=demandUnit,
                           dirout=dirout_data, fnameout=fnamebase + "." + groupL +  '.normalized.csv',
                           dirlog=dirlog)                        
            foutLogMaster.write('\n\tNormalized ' + groupL + ' : ' + str(datetime.now()-codeTstartx) )
            print('\n\tNormalized ' + groupL + ' : ' + str(datetime.now()-codeTstartx) )
            
            # normalize others
            NormalizeGroup(dirin=dirin_raw, fnamein=fnamein,groupName=groupo ,
                           considerCIDs= fnamebase + "." + groupo + ".groupIDs.csv",
                           demandUnit=demandUnit,
                           dirout=dirout_data, fnameout=fnamebase + "." + groupo +  '.normalized.csv',
                           dirlog=dirlog)           
            foutLogMaster.write('\n\tNormalized ' + groupo + ' : ' + str(datetime.now()-codeTstartx) )
            print('\n\tNormalized ' + groupo + ' : ' + str(datetime.now()-codeTstartx) )
        
        if ('Delta' in steps) or ('DeltaLoads' in steps):
            # calculate detla between normalized loads
            DeltaLoads(dirin=dirout_data, dirout=dirout_data, dirlog=dirlog,
                       fnameinL=fnameinL, fnameino=fnameino,
                       fnameout= fnameout_raw + ".csv" )    
            foutLogMaster.write('\n\tCalculated delta ' + groupL + '-' + groupo +' : ' + str(datetime.now()-codeTstartx) )
            print('\n\tCalculated delta ' + groupL + '-' + groupo +' : ' + str(datetime.now()-codeTstartx) )
        
        if ('PlotDeltaByDay' in steps) or ('DeltaByDay' in steps) or ('ByDay' in steps):
            # plot deltas between loads for each day
            PlotDeltaByDay(dirin=dirout_data, 
                       dirout=dirout_plots, 
                       dirlog=dirlog,
                       fnameinL=fnameinL, 
                       fnameino=fnameino,
                       threshold=threshold,
                       withDuration=False,
                       fnameout= fnameout_raw + ".pdf")  
            foutLogMaster.write('\n\tPlotted deltas by day : '  + str(datetime.now()-codeTstartx))
            print('\n\tPlotted deltas by day : '  + str(datetime.now()-codeTstartx))
        
        if ('PlotDeltaByDayWithDuration' in steps) or ('DeltaByDayWithDuration' in steps) or ('ByDayWithDuration' in steps):
            # plot deltas between loads for each day
            PlotDeltaByDay(dirin=dirout_data, 
                       dirout=dirout_plots, 
                       dirlog=dirlog,
                       fnameinL=fnameinL, 
                       fnameino=fnameino,
                       threshold=threshold, 
                       withDuration=True,
                       fnameout= fnameout_raw + "_wDuration.pdf" ,
                       fnameLog='PlotDeltaByDayWithDuration.log',)  
            foutLogMaster.write('\n\tPlotted deltas by day with Duration : '  + str(datetime.now()-codeTstartx))
            print('\n\tPlotted deltas by day with Duration : '  + str(datetime.now()-codeTstartx))
        
        if ('PlotDeltaSummary' in steps) or ('DeltaSummary' in steps) or ('Summary' in steps):
            # plot annual & monthly summary of load flexibility 
            PlotDeltaSummary(dirin=dirout_data, 
                       fnamein=fnameout_raw  + ".csv",
                       dirout_plots=dirout_plots, 
                       fnameout_plots=fnameout_raw + '.Summary.pdf',
                       threshold=threshold,
                       dirlog=dirlog)
            foutLogMaster.write('\n\tPlotted load flexibility summary : '  + str(datetime.now()-codeTstartx))
            print('\n\tPlotted load flexibility summary : '  + str(datetime.now()-codeTstartx))
            
        foutLogMaster.write('\nDone with group #' + str(n) + ' : ' + str(datetime.now()-codeTstartx) )
        print('\nDone with group #' + str(n) + ' : ' + str(datetime.now()-codeTstartx) )
        
    # finish log with run time
    logTime(foutLogMaster, '\n\nAll groups finished at: ', codeTstart)
    
    return 

#%% Show the Process & Illustrative Examples
def ShowFlexibilityOptions(dirin='./', fnameinL='leaders.csv', fnameino='others.csv', 
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


def ShowWalk2DurationCurve(dirin='./',fnamein='file.csv', fnameinL='leaders.csv', fnameino='others.csv', 
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

#%% Unused / Old
def PlotDeltaSummaryByDay(dirin='./', fnamein='IntervalData.normalized.csv', 
                 dirout='plots/', fnameout='DurationCurves.pdf', 
                 normalized=False, threshold=0.1,
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
    pltPdf1, yMaxE, yMaxD, yMaxP, yMaxH, xMaxH, yMaxD_C, yMaxD_D = annualSummaryPageByDay(pltPdf1, df1, dirout, fnamein, normalized,threshold=threshold)       
    
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
def annualSummaryPageByDay(pltPdf1, df1, dirout, fnamein, normalized=False, threshold=0.1):
    
    """ create page summary for specific month & add to pdf """

    # initialize variables
    month = df1.index.month
    day = df1.index.day
    
    # iterate over each month
    dailyEnergy = []
    shiftedEnergy = []
    for m in range(1,13,1):
        days = list(set(df1.loc[(month==m)].index.day))
        X = []
        Y = []
        
        # plot shifted energy
        for d in days:
            relevant = (month==m) & (day==d)
            
            # initialize figure
            fig = plt.figure(figsize=(8,6))
            fig.suptitle(  date(2016, m,1).strftime('%B')  + " / " + str(int(d)) +  " / " + df1.loc[relevant, 'DayType'][0])   
            plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
            ax0 = plt.subplot2grid((2, 2), (0, 0),  fig=fig)
            ax1 = plt.subplot2grid((2, 2), (0, 1),  fig=fig)
            ax2 = plt.subplot2grid((2, 2), (1, 0),  fig=fig)
            
            ymax = 0
            yMax = 0
            yMaxD = 0.0
            yMaxP = 0.0
            yMaxD_D = 0.0
            yMaxD_C = 0.0
            yMaxP_D = 0.0
            yMaxP_C = 0.0            
            
            df1x = findShiftingEvents(df1.loc[relevant], threshold=threshold)
            
            dailyEnergy.append( np.sum( df1.loc[relevant,'Others'].values) )
            ax1, ymax = plotShiftedEnergy(ax1, df1x, c='purple', a=0.8)
            yMax = np.max([yMax, ymax])
            shiftedEnergy.append(ymax)
            
            # plot load-duration
            ax0, ymax, ymaxC, ymaxD, x, y = plotDeltaDuration(ax0, df1x, lineAlpha=0.8, addText=False, varType='Abs', threshold=threshold) 
            yMaxD = np.max([yMaxD , ymax])
            yMaxD_C = np.max([yMaxD_C , ymaxC]) 
            yMaxD_D = np.min([yMaxD_D , ymaxD])
            
            X.append(x)
            Y.append(y)
                
            ax2, ymax, ymaxC, ymaxD, x0, y0 = plotDeltaDuration(ax2, df1x, lineAlpha=0.8, addText=False, varType='%', threshold=threshold) 
            yMaxP = np.max([yMaxP , ymax])
            yMaxP_C = np.max([yMaxP_C , ymaxC]) 
            yMaxP_D = np.min([yMaxP_D , ymaxD])
            ax2.plot( [-int(df1.shape[0]*24/24),  int(df1.shape[0]*24/24)], [threshold*100,  threshold*100 ], "--", lw=1, color='gray', alpha=0.5)
            ax2.plot( [-int(df1.shape[0]*24/24),  int(df1.shape[0]*24/24)], [-threshold*100, -threshold*100], "--", lw=1, color='gray', alpha=0.5) 

            formatShiftedEnergy(ax1)
            ax0.text(s=str(round(yMaxD_C,2)) + ' MW',
                       x=-12*4, y=yMaxD_C,
                       verticalalignment="bottom",horizontalalignment="center",
                       fontsize=8)
            
            ax0.text(s=str(round(yMaxD_D,1)) + ' MW',
                       x=12*4, y=yMaxD_D,
                       verticalalignment="top",horizontalalignment="center",
                       fontsize=8)
            
            ax2.text(s=str(round(yMaxP_C,1)) + '%',
                       x=-12*4, y=yMaxP_C,
                       verticalalignment="bottom",horizontalalignment="center",
                       fontsize=8)
            
            ax2.text(s=str(round(yMaxP_D,1)) + '%',
                       x=12*4, y=yMaxP_D,
                       verticalalignment="top",horizontalalignment="center",
                       fontsize=8)   
        
            # save to pdf
            pltPdf1.savefig() 
            plt.close() 
        
        output = pd.DataFrame(Y, columns=x)
        output.to_csv(dirout + "/" + fnamein.replace('delta.', '').replace('csv', date(2016, m,1).strftime('%B') + ".csv" ))
        
    return pltPdf1, yMax, yMaxD, yMaxP, 0, 0, yMaxD_C, yMaxD_D

    
#def plotDeltaDurationX(ax0, df, lineWidth=1, lineColor ='steelblue', lineStyle='-', lineAlpha=1.0, threshold=0.1,  addText=False, varType='Norm'):
#    
#    """ adds specific day's duration curve to axis """
#    
#    # calculate # data points per hour
#    Ns = 60 / (df.index[1].minute - df.index[0].minute)
#    
#    # find shifting events
#    df = findShiftingEvents(df, threshold=threshold)
#    
#    # switch between three options 
#    if varType in ['Percentage', '%', 'Percent', 'percent', 'percentage']:
#          varName='AbsDelta'
#    elif varType in ['Norm', 'norm', 'pu']:
#        varName='NormDelta'
#    else:
#        varName = 'AbsDelta'
#        
#    # sort dataframe & extract charge / discharge vectors
#    df = df.sort_values(by='datetime', ascending=True)
#    
#    df1 = df.copy()
#    charge = df1.loc[df1[varName]>0]
#    discharge = df1.loc[df1[varName]<0]    
#    charge = charge.sort_values(varName, ascending=True)
#    discharge = discharge.sort_values(varName, ascending=False)   
#    
#    # format x and y ticks and labels
#    x = [x for x in range(-int(df.shape[0]),int(df.shape[0])+int(df.shape[0]/(24/Ns)), int(df.shape[0]/(24/Ns)))]
#    ax0.set_xticks(x)
#    ax0.set_xticklabels([str(np.abs(x)) for x in range(-24, 28,int(Ns))])  
#    ax0.set_xlim([-int(df.shape[0]*20/24),  int(df.shape[0]*20/24) ])   
#    
#    if varType in ['Percentage', '%', 'Percent', 'percent', 'percentage']:
#        """ PERCENTAGE OF DAILY AVERAGE """
#        # plot charge & discharge
#        ax0.step(-1.*np.arange(charge.shape[0]), charge[varName] /np.mean(df1['DailyAvgOthers']) *100,  lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)
#        ax0.step(np.arange(discharge.shape[0]), discharge[varName] /np.mean(df1['DailyAvgOthers']) *100,  lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)
#        # calculate min / max values
#        ymax = np.max([ np.max(abs(charge[varName]) /np.mean(df1['DailyAvgOthers']) *100 ), np.max(abs(discharge[varName])/np.mean(df1['DailyAvgOthers']) *100)  ])
#        ymaxC = np.max(charge[varName]) /np.mean(df1['DailyAvgOthers']) *100 
#        ymaxD = np.min(discharge[varName]) /np.mean(df1['DailyAvgOthers']) *100 
#        # set y-label
#        ax0.set_ylabel('Shfitable Load [%]')
#        
#    elif varType in ['Norm', 'norm', 'pu']:
#        """ NORMALIZED DELTA """
#        # plot charge & discharge
#        ax0.step(-1.*np.arange(charge.shape[0]), charge[varName]  ,  lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)
#        ax0.step(np.arange(discharge.shape[0]), discharge[varName] ,  lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)
#        # calculate min / max values
#        ymax = np.max([ np.max(abs(charge[varName])) , np.max(abs(discharge[varName]))  ])    
#        ymaxC = np.max(charge[varName]) * Ns
#        ymaxD = np.min(discharge[varName]) * Ns
#        # set y-label
#        ax0.set_ylabel('Shfitable Load [pu]')
#        # plot horizontal lines at the threshold
#        ax0.plot( [-int(df.shape[0]*24/24),  int(df.shape[0]*24/24)], [threshold,  threshold ], "--", lw=1, color='gray', alpha=0.5)
#        ax0.plot( [-int(df.shape[0]*24/24),  int(df.shape[0]*24/24)], [-threshold, -threshold],  "--",  lw=1, color='gray', alpha=0.5) 
#    
#    else:
#        """ ABSOLUTE DELTA of the OTHERS """
#        # plot charge & discharge
#        ax0.step(-1.*np.arange(charge.shape[0]), charge[varName] * Ns ,  lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)
#        ax0.step(np.arange(discharge.shape[0]), discharge[varName]* Ns ,  lineStyle, lw=lineWidth, c=lineColor, alpha=lineAlpha)
#        # calculate min / max values
#        ymax = np.max([ np.max(abs(charge[varName])) , np.max(abs(discharge[varName]))  ])  * Ns  
#        ymaxC = np.max(charge[varName]) * Ns
#        ymaxD = np.min(discharge[varName]) * Ns
#        # set y-label
#        ax0.set_ylabel('Shfitable Load [MW]')
#        # plot horizontal lines at the threshold
#        ax0.plot( [-int(df.shape[0]*24/24),  int(df.shape[0]*24/24)], [threshold*100*np.mean(df1['Others'])* Ns,  threshold*100*np.mean(df1['Others'])* 4.0 ]  , "--", lw=1, color='gray', alpha=0.5)
#        ax0.plot( [-int(df.shape[0]*24/24),  int(df.shape[0]*24/24)], [-threshold*100*np.mean(df1['Others'])* Ns, -threshold*100*np.mean(df1['Others'])* 4.0] ,  "--",  lw=1, color='gray', alpha=0.5) 
#        
#    # add gridlines & x-label
#    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
#    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
#    ax0.set_xlabel('Duration [h]')
#    
##    if addText:
##        
##        # calculate variable crossing points
##        chargeCrossing = -1 * len( charge[charge['NormDelta'] <threshold] )
##        disCrossing = len( discharge[discharge['NormDelta'] >-threshold] )
##        
##        # calculate hours of charging and discharging beyond threshold
##        chargeHours = len(charge[charge['NormDelta'] >threshold] ) / Ns
##        dischargeHours =  len(discharge[discharge['NormDelta'] <-threshold] ) / Ns
##        
##        # plot verical lines at crossing points
##        ax0.plot([chargeCrossing , chargeCrossing ], [-100, 100], "--", lw=1, color='gray', alpha=0.5)
##        ax0.plot([disCrossing , disCrossing ], [-100, 100], "--", lw=1, color='gray', alpha=0.5)
##        
##        # add text label of CHARGE HOURS
##        ax0.text(s=str(int(round(chargeHours,0))) + 'hr',
##                   x=-1.*charge.shape[0], y= np.max(charge[varName] ),
##                   verticalalignment="bottom",horizontalalignment="center",
##                   fontsize=8, fontweight='bold')
##        
##        # add text label of DISCHARGE HOURS
##        ax0.text(s=str(int(round(dischargeHours,0)) )+ 'hr',
##                   x=discharge.shape[0], y= np.min(discharge[varName] ),
##                   verticalalignment="top",horizontalalignment="center",
##                   fontsize=8, fontweight='bold')
##        
##        # add text label of GAP HOURS
##        ax0.text(s=str(int(round((disCrossing-chargeCrossing)/Ns,0)) )+ 'hr',
##                   x=(disCrossing+chargeCrossing)/2, y= 0.1,
##                   verticalalignment="bottom",horizontalalignment="center",
##                   fontsize=8, fontweight='bold') 
#    
#    return ax0, ymax, ymaxC, ymaxD    
#def xPlotDeltaByDayWithDuration(dirin='./', fnameinL='leaders.csv',   fnameino='others.csv', 
#                  dirout='./', fnameout='delta.csv',
#                  dirlog='./', fnameLog='PlotDeltaByDayWithDuration.log', 
#                  threshold = 0.1):
#    
#    """ Creates pdf with 365 pages showing the leader and other loads & the delta for each day of the year"""
#    
#    # Capture start time of code execution
#    codeTstart = datetime.now()
#    
#    # open log file
#    foutLog = createLog(codeName, "PlotDeltaByDayWithDuration", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
#
#    # load time-series data for leaders & others
#    df1, UniqueIDs, foutLog = getDataAndLabels(dirin, fnameinL, foutLog, datetimeIndex=True)
#    df2, UniqueIDs, foutLog = getDataAndLabels(dirin, fnameino, foutLog, datetimeIndex=True)
#
#    # assign season & day type
#    df1 = assignDayType(df1, datetimeIndex=True)
#    df2 = assignDayType(df2, datetimeIndex=True)
#    month = df1.index.month
#    day = df1.index.day
#    
#    # calculate delta
#    df3 = deltaLoadsFunction(df1, df2)
#        
#    # open pdf for figures
#    print("Opening plot files")
#    pltPdf1 = dpdf.PdfPages(os.path.join(dirout, fnameout))
#    
#    # find max y limits
#    ymax = np.ceil(np.max([ df1['NormDmnd'].max() *2  , df2['NormDmnd'].max()*2  ])) / 2
#    ymaxDelta = 1.0
#    yLim =  np.ceil(np.max([ df3['NormDelta'].max() *2  ,  abs(df3['NormDelta'].min() *2)    ])) / 2
#    for m in range(1, 13,1):
#        days = list(set(df1.loc[(month==m)].index.day))  
#        for d in days:
#            relevant = (month==m) & (day==d)
#            y = np.cumsum(df3.loc[relevant,'NormDelta'])/4
#            y = y - np.min(y)
#            ymaxDelta = np.max([ ymaxDelta, np.max(y) ])
#    ymaxDelta = np.ceil( ymaxDelta * 2.0 ) / 2.0
#    
#    # iterate over each month of the year
#    print("Creating plots for")
#    for m in range(1, 13,1):
#        print('\t%s' %(date(2016, m,1).strftime('%B')))
#        
#        # iterate over each day of the month
#        days = list(set(df1.loc[(month==m)].index.day))  
#        for d in days:
#
#            # find this day in the data
#            relevant = (month==m) & (day==d)
#            df3x = findShiftingEvents(df3.loc[relevant], threshold=threshold)
#            
#            # initialize figure
#            fig = plt.figure(figsize=(8,6))
#            plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
#            ax0 = plt.subplot2grid((3, 2), (0, 0),   fig=fig)
#            ax1 = plt.subplot2grid((3, 2), (1, 0),  fig=fig)
#            ax2 = plt.subplot2grid((3, 2), (2, 0),   fig=fig)
#            ax3 = plt.subplot2grid((3, 2), (0, 1), rowspan=3, fig=fig)
#            fig.suptitle(  date(2016, m,1).strftime('%B')  + " / " + str(int(d)) +  " / " + df1.loc[relevant, 'DayType'][0])   
#            
#            # plot loads of leaders & others 
#            ax0 = plotDailyLoads(ax0, df1.loc[relevant], c='b', lw=1, label='leaders')
#            ax0 = plotDailyLoads(ax0, df2.loc[relevant], c='k', lw=1, label='others')
#            ax0.set_ylim([0.0,ymax])
#            ax0.set_xlabel('')
#            
#            # plot delta between leaders & others - in POWER
#            ax1,temp = plotDailyDeltaLoad(ax1, df3x)
#            ax1.set_ylim([-yLim,yLim])
#            ax1.set_xlabel('')
#            
#            # plot shifted energy: delta between leaders & others - in ENERGY
#            ax2,temp = plotDailyDeltaEnergy(ax2, df3x)
#            ax2.set_ylim([0,ymaxDelta])
#            
#            # plot duration curve of the load DELTA
#            ax3, temp0, temp1, temp2 = plotDeltaDuration(ax3, df3x, addText=True, varType='pu', threshold=threshold)
#            ax3.set_ylim([-yLim, yLim])
#            
#            # add to pdf
#            pltPdf1.savefig() 
#            plt.close()   
#                
#    print('Writing: %s' %os.path.join(os.path.join(dirout, fnameout)))
#    pltPdf1.close()
#
#    # finish log with run time
#    logTime(foutLog, '\nRunFinished at: ', codeTstart)
#    
#    return    
#    
    
#def plotLoadDuration(ax0, df, lw=1, c='b', ls='-', a=1.0):
#    
#    """ adds specific day's duration curve to axis """
#    df = df.sort_values(by='datetime', ascending=True)
#    ax0.set_xlabel('Duration [h]')
#    x = [x for x in range(0,int(df.shape[0])+int(df.shape[0]/(24/4)), int(df.shape[0]/(24/4)))]
#    ax0.set_xticks(x)
#    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
#    ax0.set_xlim([0,  int(df.shape[0]*24/24) ])   
#       
#    df1 = df.copy()
#    df1 = df1.sort_values('Others', ascending=False)
#    ax0.step(np.arange(df1.shape[0]), df1['Others'] * 4.0,  ls, lw=lw, c=c, alpha=a)
#    
#    e = np.sum( df1['Others'].values)
#    ymax = np.max([  np.max(abs(df1['Others'])) * 4.0 ])
#    if np.isnan(ymax) or np.isinf(ymax):
#        ymax = 0.0
#    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
#    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
#    
#    return ax0, ymax, e
#def plotDeltaDuration_v2(ax0, df, lw=1, c='b', ls='-', a=1.0):
#    """ adds specific day's duration curve to axis """
#    # sort data
#    df = df.sort_values(by='datetime', ascending=True)
#    # format axis
#    ax0.set_xlabel('Duration [h]')
#    x = [x for x in range(-int(df.shape[0]),int(df.shape[0])+int(df.shape[0]/(24/4)), int(df.shape[0]/(24/4)))]
#    ax0.set_xticks(x)
#    ax0.set_xticklabels([str(np.abs(x)) for x in range(-24, 28,4)])  
#    ax0.set_xlim([-int(df.shape[0]*16/24),  int(df.shape[0]*16/24) ])   
#    # separate charge & discharge
#    df1 = df.copy()
#    charge = df1.loc[df1['NormDmnd']>0]
#    discharge = df1.loc[df1['NormDmnd']<0]      
#    # sort charge & discharge
#    charge = charge.sort_values('NormDmnd', ascending=True)
#    discharge = discharge.sort_values('NormDmnd', ascending=False)
#    # plot charge & discharge  
#    ax0.step(-1.*np.arange(charge.shape[0]), charge['NormDmnd'] * 4.0 ,  ls, lw=lw, c=c, alpha=a)
#    ax0.step(np.arange(discharge.shape[0]), discharge['NormDmnd'] * 4.0,  ls, lw=lw, c=c, alpha=a)
#    # find maximum values
#    ymax = np.max([ np.max(abs(charge['NormDmnd'])) * 4.0 , np.max(abs(discharge['NormDmnd'])) * 4.0 ])
#    ymaxC = np.max(charge['NormDmnd']) * 4.0
#    ymaxD = np.min(discharge['NormDmnd']) * 4.0
#    # format gridlines
#    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
#    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
#    # assign output
#    return ax0, ymax, ymaxC, ymaxD
#
#def plotDeltaDurationPercentage_v2(ax0, df, lw=1, c='b', ls='-', a=1.0):
#    
#    """ adds specific day's duration curve to axis """
#    df = df.sort_values(by='datetime', ascending=True)
#    ax0.set_xlabel('Duration [h]')
#    x = [x for x in range(-int(df.shape[0]),int(df.shape[0])+int(df.shape[0]/(24/4)), int(df.shape[0]/(24/4)))]
#    ax0.set_xticks(x)
#    ax0.set_xticklabels([str(np.abs(x)) for x in range(-24, 28,4)])  
#    ax0.set_xlim([-int(df.shape[0]*16/24),  int(df.shape[0]*16/24) ])   
#       
#    df1 = df.copy()
#    charge = df1.loc[df1['NormDmnd']>0]
#    discharge = df1.loc[df1['NormDmnd']<0]      
#    
#    charge = charge.sort_values('NormDmnd', ascending=True)
#    discharge = discharge.sort_values('NormDmnd', ascending=False)
#    
#    ax0.step(-1.*np.arange(charge.shape[0]), charge['NormDmnd'] /np.max(df1['Others']) *100,  ls, lw=lw, c=c, alpha=a)
#    ax0.step(np.arange(discharge.shape[0]), discharge['NormDmnd'] /np.max(df1['Others']) *100,  ls, lw=lw, c=c, alpha=a)
#    
#    ymax = np.max([ np.max(abs(charge['NormDmnd']) /np.max(df1['Others']) *100 ), np.max(abs(discharge['NormDmnd'])/np.max(df1['Others']) *100)  ])
#    ymaxC = np.max(charge['NormDmnd']) /np.max(df1['Others']) *100 
#    ymaxD = np.min(discharge['NormDmnd']) /np.max(df1['Others']) *100 
#
#    ax0.xaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5)    
#    ax0.yaxis.grid(which="major", color='#A9A9A9', linestyle='-', linewidth=0.5) 
#
#    return ax0, ymax, ymaxC, ymaxD    
#    
#def PlotDurationSummary(dirin='./', fnamein='IntervalData.normalized.csv', 
#                 dirout='plots/', fnameout='DurationCurves.pdf', 
#                 normalized=False,
#                 dirlog='./', fnameLog='PlotDeltaSummary.log'):
#    
#    """Creates pdf with 13 pages: 1 page summary of entire year followed by monthly. Each page shows shifted energy & duration curves """
#    
#    # Capture start time of code execution
#    codeTstart = datetime.now()
#    
#    # open log file
#    foutLog = createLog(codeName, "PlotDurationSummary", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
#    
##    # load data from file, find initial list of unique IDs. Update log file
##    if normalized:
##        df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog,  varName=['NormDmnd', 'AbsDemand', 'Leaders', 'Others'], usecols=[0,1,2])
##    else:
##        df1, UniqueIDs, foutLog = getData(dirin, fnamein, foutLog, varName=[ 'NormDmnd', 'Leaders', 'Others'], usecols=[0,1,3, 4, 5])
#    
#    # load data from file, find initial list of unique IDs. Update log file    
#    df1, UniqueIDs, foutLog = getDataAndLabels(dirin,  fnamein, foutLog, datetimeIndex=True)
#    if not('Others' in df1.columns):
#        df1['Others'] = df1['Demand']
#    if not('NormDmnd' in df1.columns):
#        df1['NormDmnd'] = df1['NormDelta']
#    
#    # add season & day type
#    df1 = assignDayType(df1)
#
#    # open pdf for figures
#    print("Opening plot files")
#    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))
#
#    # create annual summary of shifted energy & load duration
#    foutLog.write("Creating annual figure" )
#    print("Creating annual figure" )
#    pltPdf1,  yMaxD = annualDurationSummaryPage(pltPdf1, df1, fnamein, normalized)
#    
#    # create monthly summaries of shifted energy & load duration
#    foutLog.write("Creating monthly figures" )
#    print("Creating monthly figures" )
#    pltPdf1 = monthlyDurationSummaryPages(pltPdf1, df1, fnamein,  yMaxD, normalized)  
#    
#    # Closing plot files
#    print('Writing output file: %s' %os.path.join(os.path.join(dirout, fnameout)))
#    foutLog.write('\n\nWriting: %s' %os.path.join(dirout, fnameout))
#    pltPdf1.close()
#
#    # finish log with run time
#    logTime(foutLog, '\nRunFinished at: ', codeTstart)
#    
#    return
#
#
#
#def plotDailyDeltas(ax0, df, lw=1, c='b', ls='-'):
#    
#    """ adds specific day's power & energy deltas to axis """
#    df = df.sort_values(by='datetime', ascending=True)
#    ax0.set_ylabel('Delta')
#    ax0.set_xlabel('Hour of the Day [h]')
#    ax0.set_xlim([0,df.shape[0]])
#    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
#    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
#    y = [yy for yy in range(-40, 41,1)]
#    ax0.set_yticks(y)  
#    ax0.xaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5)    
#    ax0.yaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5) 
#    y = np.cumsum(df['NormDelta'])/4
#    y = y - np.min(y)
#    ax0.fill_between(np.arange(df.shape[0]), 0,  df['NormDelta'],  label='Load [pu]')      
#    ax0.plot(np.arange(df.shape[0]), y, ls, lw=lw*2, c='purple', label='Energy [pu-h]')    
#    return ax0, np.max(y)
#
#
#
#
#
#
#def plotDailyRate(ax0, df, lw=1, c='b', ls='-'):
#    """ adds specific day's power & energy deltas to axis """
#    df = df.sort_values(by='datetime', ascending=True)
#    ax0.set_ylabel('Energy Cost [$/kWh]')
#    ax0.set_xlabel('Hour of the Day [h]')
#    ax0.set_xlim([0,df.shape[0]])
#    ax0.set_xticks([x for x in range(0, int(df.shape[0])+int(df.shape[0]/(24/4)),int(df.shape[0]/(24/4)))])
#    ax0.set_xticklabels([str(x) for x in range(0, 28,4)])  
#    ax0.xaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5)    
#    ax0.yaxis.grid(which="major", color='#cbcbcb', linestyle='-', linewidth=0.5) 
#    ax0.plot(np.arange(df.shape[0]),   df['EnergyCost'],  label='Load [pu]')  
#    
#    return ax0, np.max(df['EnergyCost'])
#
#
#
#def annualDurationSummaryPage(pltPdf1, df1, fnamein, normalized=False):
#    """ create page summary for specific month & add to pdf """
#    
#    # initialize figure
#    #fig, ax = plt.subplots(nrows=1, ncols=2,figsize=(8,6),sharex=False)
#    #ax1 = ax[1]
#    #ax0 = ax[0]
#    fig = plt.figure(figsize=(8,6))
#    plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
#    ax1 = plt.subplot2grid((1, 2), (0, 0),  fig=fig)
#    ax2 = plt.subplot2grid((1, 2), (0, 1),  fig=fig)
#    fig.suptitle(fnamein + " / entire year" )  
#    
#    # initialize variables
#    month = df1.index.month
#    day = df1.index.day
#    ymax = 0
#    yMaxD = 1.0
#    yMaxP = 0.0
#    
#    for m in range(1, 13,1):
#        days = list(set(df1.loc[(month==m)].index.day))
#           
#            
#        # plot load-duration
#        ax1.set_title( "Flexibility")
#        # iterate for each day in month
#        for d in days:
#            relevant = (month==m) & (day==d)
#            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
#                pass
#            else:
#                ax1, ymax = plotDeltaDuration_v2(ax1, df1.loc[relevant], c='steelblue', a=0.1) 
#                yMaxD = np.max([yMaxD , ymax])
#        if normalized:
#            ax1.set_ylabel('Shiftable Load [p.u.]')
#        else:
#            ax1.set_ylabel('Shiftable Load [MW]')
#        ax1.set_ylim([-yMaxD , yMaxD ])
#        
#        
#        # plot load-duration as percentage
#        ax2.set_title( "Percent of Daily Peak")
#        # iterate for each day in month
#        for d in days:
#            relevant = (month==m) & (day==d)
#            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
#                pass
#            else:
#                ax2, ymax, temp0, temp1 = plotDeltaDurationPercentage_v2(ax2, df1.loc[relevant], c='steelblue', a=0.1) 
#                yMaxP = np.max([yMaxP , ymax])
#        ax2.set_ylabel('Shiftable Load [%]')
#        ax2.set_ylim([-100 , 100 ])        
#    
#    # save to pdf
#    pltPdf1.savefig() 
#    plt.close() 
#        
#    return pltPdf1, yMaxD
#
#def monthlyDurationSummaryPages(pltPdf1, df1, fnamein, yMaxD, normalized=False):
#    """ create page summary for specific month & add to pdf"""
#    
#    month = df1.index.month
#    day = df1.index.day
#    
#    # iterate over each month
#    for m in range(1, 13,1):
#        days = list(set(df1.loc[(month==m)].index.day))
#        
#
#        fig = plt.figure(figsize=(8,6))
#        plt.subplots_adjust(wspace=0.3,hspace=0.3 )    
#        ax1 = plt.subplot2grid((1, 2), (0, 0),  fig=fig)
#        ax2 = plt.subplot2grid((1, 2), (0, 1),  fig=fig)
#        fig.suptitle(fnamein  + " / " + date(2016, m,1).strftime('%B') )   
#
#        # plot load-duration
#        ax1.set_title( "Flexibility")  
#        
#        # iterate for each day of the month
#        for d in days:
#            relevant =  (month==m) & (day==d)
#            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
#                ax1, ymax1 = plotDeltaDuration_v2(ax1, df1.loc[relevant], c='gray', a=0.2)
#            else:
#                ax1, ymax1 = plotDeltaDuration_v2(ax1, df1.loc[relevant], c='steelblue', a=0.5)
#        ax1.set_ylim([-yMaxD, yMaxD])
#        ax1.set_ylabel('Shiftable Load [MW]')
#            
#            
#        # plot load-duration
#        ax2.set_title( "Percentage of Daily Peak")  
#        
#        # iterate for each day of the month
#        for d in days:
#            relevant =  (month==m) & (day==d)
#            if df1.loc[relevant, 'DayType'][0] in ['we','h']:
#                ax2, ymax1, ymax2, ymax3 = plotDeltaDurationPercentage_v2(ax2, df1.loc[relevant], c='gray', a=0.2)
#            else:
#                ax2, ymax1, ymax2, ymax3 = plotDeltaDurationPercentage_v2(ax2, df1.loc[relevant], c='steelblue', a=0.5)
#        ax2.set_ylim([-100,100])
#        ax2.set_ylabel('Shiftable Load [%]')
#        
#        # save figure to pdf
#        pltPdf1.savefig() 
#        plt.close()  
#        
#    return pltPdf1
