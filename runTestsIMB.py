# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""
from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs, CalculateBilling, CalculateGroups
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from NormalizeLoads import ReviewLoads, NormalizeLoads, NormalizeGroup
from PlotHeatMaps import PlotHeatMaps
from GroupAnalysis import DeltaLoads,  PlotDeltaByDay, PlotDeltaSummary

fnamebase = 'synthetic10'

#%% Create profiles
if False:
    GenerateSyntheticProfiles(10, # number of profiles to create
                              '2017-01-01 00:00', '2017-12-31 23:45', # date range
                              IDlen=6, meMean=200, htllr=2.0, # ID length, monthly energy mean, high to low load ratio (peak day / low day)
                              dirout='testdata/', fnameout = fnamebase + '.csv', 
                              dirlog='testdata/')

#%% Convert Feather file
if False:
    ConvertFeather(dirin='testdata/', fnamein='GroceryTOU_GS3B_Q1O15_152017.feather',
                   dirout='testdata/', fnameout='GroceryTOU_GS3B_Q1O15_152017.csv',
                   dirlog='testdata/',
                   renameDict={'DatePeriod':'datetimestr', 'Usage':'Demand'},
                   writeOutput = True)

#%% AnonymizeCIDs
if False:
    AnonymizeCIDs(dirin='testdata/', fnamein='two_grocers_DST.csv', 
                  dirout='testdata/', fnameout='two_grocers_DST.anonymized.csv', fnameKeys='two_grocers_DST.lookup.csv',
                  dirlog='testdata/', fnameLog='AnonymizeCIDs.log',
                  IDlen=6)

#%% Fix DST
if False:
    FixDST(dirin='testdata/', fnamein='two_grocers_DST_test2.csv',
                   dirout='testdata/', fnameout='two_grocers2.csv',
                   dirlog='testdata/',
                   tzinput='America/Los_Angeles',
                   OutputFormat='SCE')

#%% Review load profiles
if False:
    ReviewLoads(dirin='testdata/', fnamein=fnamebase+'.csv',
                   dirout='testdata/', fnameout=fnamebase+'.summary.csv',
                   dirlog='testdata/',
                   InputFormat = 'SCE')

#%% Normalize profiles
if False:
    NormalizeLoads(dirin='testdata/', fnamein=fnamebase+'.csv', 
                   dirout='testdata/', fnameout=fnamebase+'.normalized.csv',
                   dirlog='testdata/', 
                   InputFormat='SCE', 
                   normalizeBy='day')
    
#%% Create data with right format for billing calc
if False:
    NormalizeLoads(dirin='testdata/', fnamein=fnamebase+'.csv', 
                   dirout='testdata/', fnameout=fnamebase+'.4billing.csv',
                   dirlog='testdata/', 
                   InputFormat='SCE', 
                   normalizeBy='year', normalize=False)    
    
#%% Export Load Files
if False:
    ExportLoadFiles(dirin='testdata/', fnamein=fnamebase+'.csv', 
                    explist=fnamebase+'.export.csv',
                    dirout='testdata/', 
                   dirlog='testdata/')
    
#%% Calculate Billing
if False:
    CalculateBilling(dirin='testdata/', fnamein=fnamebase+'.4billing.csv',
                     dirout='testdata/', fnameout=fnamebase+'.billing.csv',
                     fnameoutsummary ='summary.' + fnamebase + '.billing.csv',
                     dirlog='testdata/',
                     demandUnit='Wh',dirrate='tou_data/',ratein='SCE-TOU-GS2-B.csv',
                     writeDataFile=False,
                     writeSummaryFile=True)   
    
#%% Group Customers
if True:
    CalculateGroups(dirin='testdata/', # outputs
                    fnamein="summary." + fnamebase+'.billing.csv',
                     dirout='testdata/', # outputs
                     dirplot='testdata/', # plots
                     fnameout=fnamebase+'.groups.csv',
                     dirlog='testdata/', 
                     energyPercentiles = [5, 27.5,  50, 72.5, 95], 
                     chargeType="Total")
    
    
#%% Normalize & Plot
if False:
    for groupName in [ 'g1L' , 'g1o', 'g2L', 'g2o', 'g3L', 'g3o', 'g4L', 'g4o']:
        NormalizeGroup(dirin='testdata/', # inputs
                       fnamein=fnamebase+'.4billing.csv', 
                       considerCIDs= groupName + "." + fnamebase + ".groups.csv",
                       dirout='testdata/', # outputs
                       fnameout=fnamebase+'.normalized.'+ groupName +  '.csv',
                       dirlog='testdata/', 
                       groupName=groupName)
        
#%% Compare Normalized Groups
if False:
    for n in [1,2,3,4]:
        
        groupL = 'g' + str(n) + 'L'
        groupo = 'g' + str(n) + 'o'
        fnameout  = fnamebase+".delta." + groupL + "." + groupo + ".csv"
    
        DeltaLoads(dirin='testdata/', # outputs
                   fnameinL=fnamebase+".normalized." + groupL + ".csv",
                   fnameino=fnamebase+".normalized." + groupo + ".csv",
                   dirout='testdata/', # outputs 
                   fnameout=fnameout,
                   dirlog='testdata/' # outputs
                   ) 
        
        PlotDelta(dirin='testdata/',  # outputs
                  fnamein=fnameout, 
                  dirout='testdata/', # plots
                  fnameout=fnameout.replace('.csv', '.pdf'),
                  dirlog='testdata/' # outputs
                  )  
        
            
#%% Plot Duration Curves
if False: # annual duration curve 
    PlotDurationCurves(dirin='testdata/', fnamein=fnamebase+'.normalized.csv',
                       dirout='testdata/', fnameout=fnamebase+'.DurationCurves.pdf',
                       dirlog='testdata/')
    
if False: # monthly duration curve showing entire year with duration for each month
    PlotDurationCurves(dirin='testdata/', fnamein=fnamebase+'.normalized.g1O.csv',
                       considerCIDs= groupName + ".synthetic10.groups.csv",
                       dirout='testdata/', fnameout=fnamebase+'.DurationCurvesByMonth.pdf',
                       dirlog='testdata/',
                       byMonthFlag = True)    
    
if False: # family of duration curves on one plot
    PlotFamilyOfDurationCurves(dirin='testdata/', fnamein=fnamebase+'.normalized.csv',
                               dirout='testdata/', fnameout=fnamebase+'.FamilyOfDurationCurves.pdf',
                               dirlog='testdata/')

#%% Plot heatmaps
if False:    
    PlotHeatMaps(dirin='testdata/', fnamein=fnamebase+'.normalized.csv', # considerCIDs=fnamebase+'.g1c.csv', ignoreCIDs = fnamebase+'.g1i.csv',
                 dirout='testdata/', fnameout=fnamebase+'.HeatMaps.g1.pdf',
                 dirlog='testdata/')
    