# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""
from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs, CalculateBilling, CalculateGroups
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves, PlotDurationCurveSequence
from NormalizeLoads import ReviewLoads, NormalizeLoads, NormalizeGroup
from PlotHeatMaps import PlotHeatMaps, PlotHeatMapOfBilling
from GroupAnalysis import GroupAnalysisMaster, DeltaLoads,  PlotDeltaByDay, PlotDeltaSummary,  ShowWalk2DurationCurve, ShowFlexibilityOptions
from SupportFunctions import findMissingData

fnamebase = 'synthetic10'

initialize = False # create data, anonymize,  normalize
calculate = False # plot heatmaps & calculate billing
group = False# create groups
analyze = False # analyze
plot = False # plot duration plots

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
    AnonymizeCIDs(dirin='testdata/', fnamein=fnamebase+'.csv',
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
    
    
#%% Calculate Billing
if False:
    CalculateBilling(dirin='testdata/', fnamein=fnamebase+'.4billing.csv',
                     dirout='testdata/', fnameout=fnamebase+'.billing.csv',
                     fnameoutsummary ='summary.' + fnamebase + '.billing.csv',
                     dirlog='testdata/',
                     demandUnit='Wh',dirrate='tou_data/',ratein='SCE-TOU-PA-2-B.csv',
                     writeDataFile=True,
                     writeSummaryFile=True)   
    
#%% Plot heatmaps
if False:    
    PlotHeatMapOfBilling(dirin='testdata/', fnamein=fnamebase+'.billing.csv', # considerCIDs=fnamebase+'.g1c.csv', ignoreCIDs = fnamebase+'.g1i.csv',
                 dirout='testdata/', fnameout=fnamebase+'.HeatMaps.BillingNew.pdf',
                 dirlog='testdata/')    
    
if False:
    findMissingData(dirin='testdata/', fnamein=fnamebase+'.csv',
                dirout='testdata/',fnameout=fnamebase + '.List.MissingData.csv', 
                dirlog='testdata/', fnameLog='InitializeIgnoreList.log')
    
#%% Group Customers
if False:
    CalculateGroups(dirin='testdata/', 
                    fnamein="summary." + fnamebase+'.billing.csv',
                    dirout='testdata/', 
                    dirplot='testdata/', 
                    fnamebase=fnamebase,
                    dirlog='testdata/',  
                    ignore1515=True,
                    energyPercentiles = [5, 27.5,  50, 72.5, 95], 
                    chargeType="Total")
    
    
#%% RUN ENTIRE GROUP ANALYSIS
if True:
     GroupAnalysisMaster(dirin='testdata/', dirout='testdata/', dirlog='testdata/',
                     fnamebase=fnamebase,
                     fnamein=fnamebase+'.4billing.csv',
                     Ngroups=1, threshold=0.5, demandUnit='kWh'),
#                     steps=[ 'Summary'])
##                     steps=['DeltaByDayWithDuration']) #
##                    steps=['NormalizeGroup', 'DeltaLoads', 'DeltaByDay', 'DeltaByDayWithDuration', 'Summary'])
     
if False:
     GroupAnalysisMaster(dirin='data/', dirout='data/', dirlog='data/',
                     fnamebase='waterSupplyandIrrigationSystems',
                     fnamein=fnamebase+'.4billing.csv',
                     Ngroups=1, threshold=0.25, demandUnit='kWh',
                     steps=[ 'DeltaByDayWithDuration'])     
     
   
#if False:
#    for n in [1]:
#        fnamebase = 'largeOfficesAll' #.g1L.energyOnly.A.normalized
#        groupL = 'g' + str(n) + 'L'
#        groupo = 'g' + str(n) + 'o'
#        fnameout  = fnamebase+".delta." + groupL + "." + groupo + ".csv"
#        ShowFlexibilityOptions(dirin='data/', # outputs
#                   fnameinL=fnamebase+ "." + groupL + ".energyOnly.A.normalized.csv",
#                   fnameino=fnamebase+ "." + groupo + ".energyOnly.A.normalized.csv",
#                   dirout='data/', dirrate='tou_data/',ratein='SCE-TOU-GS3-B.csv',
#                   fnameout=fnameout.replace('.csv', '.flexibility.pdf'))       
        
#        ShowWalk2DurationCurve(dirin='data/', # outputs
#                   fnamein  = fnamebase+".delta." + groupL + "." + groupo + ".csv",
#                   fnameinL=fnamebase+ "." + groupL + ".energyOnly.A.normalized.csv",
#                   fnameino=fnamebase+ "." + groupo + ".energyOnly.A.normalized.csv",
#                   dirout='data/', dirrate='tou_data/',ratein='SCE-TOU-GS3-B.csv',
#                   fnameout=fnameout.replace('.csv', '.durationWalk.pdf'))       
        
            
#%% Plot Duration Curves
        
if plot: # annual duration curve 
    PlotDurationCurves(dirin='testdata/', fnamein=fnamebase+'.normalized.csv',
                       dirout='testdata/', fnameout=fnamebase+'.DurationCurves.pdf',
                       dirlog='testdata/')
    
#if plot: # monthly duration curve showing entire year with duration for each month
if plot: # family of duration curves on one plot
    PlotFamilyOfDurationCurves(dirin='testdata/', fnamein=fnamebase+'.normalized.csv',
                               dirout='testdata/', fnameout=fnamebase+'.FamilyOfDurationCurves.pdf',
                               dirlog='testdata/')

#%% Plot heatmaps
if False:    
    PlotHeatMaps(dirin='testdata/', fnamein=fnamebase+'.normalized.csv', # considerCIDs=fnamebase+'.g1c.csv', ignoreCIDs = fnamebase+'.g1i.csv',
                 dirout='testdata/', fnameout=fnamebase+'.HeatMaps.g1.pdf',
                 dirlog='testdata/')