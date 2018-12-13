# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""
from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs, CalculateBilling, CalculateGroups
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves, PlotDurationCurveSequence
from NormalizeLoads import ReviewLoads, NormalizeLoads
from PlotHeatMaps import PlotHeatMaps, PlotHeatMapOfBilling
from GroupAnalysis import GroupAnalysisMaster, ShowWalk2DurationCurve, ShowFlexibilityOptions, SaveDeltaByMonth
from SupportFunctions import findMissingData


#%% Define Iterations
if True:
    fnamebase = 'synthetic10'
    ratein =  'SCE-TOU-PA-2-B.csv'

if False:
    fnamebase = 'waterSupplyandIrrigationSystems'
    ratein =  'SCE-TOU-PA-2-B.csv'

#%% Create profiles
if False: # GenerateSyntheticProfiles
    GenerateSyntheticProfiles(10, # number of profiles to create
                  '2017-01-01 00:00', # start date
                  '2017-12-31 23:45', # end date
                  IDlen=6,  # ID length
                  meMean=200,  #  monthly energy mean,
                  htllr=2.0, # high to low load ratio (peak day / low day)
                  dirout='testdata/', 
                  fnameout = fnamebase + '.csv', 
                  dirlog='testdata/')

#%% AnonymizeCIDs
if False: # AnonymizeCIDs
    AnonymizeCIDs(dirin='testdata/', 
                  fnamein=fnamebase+'.csv',
                  dirout='testdata/', 
                  fnameout='two_grocers_DST.anonymized.csv', 
                  fnameKeys='two_grocers_DST.lookup.csv',
                  dirlog='testdata/', 
                  fnameLog='AnonymizeCIDs.log',
                  IDlen=6)

#%% Fix DST
if False: # FixDST
    FixDST(dirin='testdata/', 
           fnamein='two_grocers_DST_test2.csv',
                   dirout='testdata/', 
                   fnameout='two_grocers2.csv',
                   dirlog='testdata/',
                   tzinput='America/Los_Angeles',
                   OutputFormat='SCE')

#%% Normalize profiles
if False: # NormalizeLoads
    NormalizeLoads(dirin='testdata/', 
                   fnamein=fnamebase+'.csv', 
                   dirout='testdata/', 
                   fnameout=fnamebase+'.normalized.csv',
                   dirlog='testdata/', 
                   InputFormat='SCE', 
                   normalizeBy='day')
    
if False: # format for billing calc
    NormalizeLoads(dirin='testdata/', 
                   fnamein=fnamebase+'.csv', 
                   dirout='testdata/', 
                   fnameout=fnamebase+'.4billing.csv',
                   dirlog='testdata/', 
                   InputFormat='SCE', 
                   normalizeBy='year', 
                   normalize=False)        
    
#%% Plot heatmaps
if False:  # PlotHeatMaps  
    PlotHeatMaps(dirin='testdata/', 
                 fnamein=fnamebase+'.normalized.csv', 
                 # considerCIDs=fnamebase+'.g1c.csv', 
                 # ignoreCIDs = fnamebase+'.g1i.csv',
                 dirout='testdata/', 
                 fnameout=fnamebase+'.HeatMaps.g1.pdf',
                 dirlog='testdata/')    
    
#%% Calculate Billing
if False: # CalculateBilling
    CalculateBilling(dirin='testdata/', 
                     fnamein=fnamebase+'.4billing.csv',
                     dirout='testdata/', 
                     fnameout=fnamebase+'.billing.csv',
                     fnameoutsummary ='summary.' + fnamebase + '.billing.csv',
                     dirlog='testdata/',
                     demandUnit='Wh',
                     dirrate='tou_data/',
                     ratein=ratein,
                     writeDataFile=True,
                     writeSummaryFile=True)   
    
##%% Plot heatmaps
#if False:    
#    PlotHeatMapOfBilling(dirin='testdata/', fnamein=fnamebase+'.billing.csv', # considerCIDs=fnamebase+'.g1c.csv', ignoreCIDs = fnamebase+'.g1i.csv',
#                 dirout='testdata/', fnameout=fnamebase+'.HeatMaps.BillingNew.pdf',
#                 dirlog='testdata/')    
    
#if False:
#    findMissingData(dirin='testdata/', fnamein=fnamebase+'.csv',
#                dirout='testdata/',fnameout=fnamebase + '.List.MissingData.csv', 
#                dirlog='testdata/', fnameLog='InitializeIgnoreList.log')
    
#%% Group Customers
if False: #  CalculateGroups
    CalculateGroups(dirin='testdata/', 
                    fnamein="summary." + fnamebase+'.billing.csv',
                    dirout='testdata/', 
                    dirplot='testdata/', 
                    fnamebase=fnamebase,
                    dirlog='testdata/',  
                    ignore1515=True,
                    energyPercentiles = [5, 27.5,  50, 72.5, 95], 
                    chargeType="Total")
        
#%% Analyze Groups & Calculate Flexibility      
# performs normalizing groups, delta between groups, plot delta by day, & plot delta summary
if True:  # full chain using synthetic data, e.g. for GE
    GroupAnalysisMaster(dirin_raw = 'testdata/', # folder where the raw data inputs are located  
                     dirout_data ='testdata/',  # folder where to save the ouput data
                     dirout_plots = 'testdata/', # folder where to save the output figures
                     dirlog = 'testdata/', # folder where the log file(s) are saved
                     fnamebase = fnamebase, # file name base (usual by the type of building / NAICS)
                     fnamein = fnamebase+'.4billing.csv', # interval data
                     Ngroups = 2, # tells the function how many groups to iterate over
                     threshold = 0.5, # sets the threshold for identifying multiple cycles per day
                     demandUnit = 'kWh' # unit of the raw interval data
                     )
    
if False:  # full chain using real data, e.g. for SCE
    GroupAnalysisMaster(dirin_raw = 'input/', # folder where the raw data inputs are located  
                     dirout_data ='output/',  # folder where to save the ouput data
                     dirout_plots = 'plots/', # folder where to save the output figures
                     dirlog = 'output/', #  folder where to save the log file(s)
                     fnamebase = 'waterSupplyandIrrigationSystems', # file name base (usual by the type of building / NAICS)
                     fnamein = 'waterSupplyandIrrigationSystems.A.csv', # interval data 
                     Ngroups = 2, # tells the function how many groups to iterate over
                     threshold = 0.5, # sets the threshold for identifying multiple cycles per day
                     demandUnit = 'Wh' # unit of the raw interval data
                     )
    
if False:  # part of chain using real data, e.g. for GE
    GroupAnalysisMaster(dirin_raw = 'input/', # folder where the raw data inputs are located  
                     dirout_data ='output/',  # folder where to save the ouput data
                     dirout_plots = 'plots/', # folder where to save the output figures
                     dirlog = 'output/', #  folder where to save the log file(s)
                     fnamebase = 'waterSupplyandIrrigationSystems', # file name base (usual by the type of building / NAICS)
                     fnamein = 'waterSupplyandIrrigationSystems.A.csv', # interval data 
                     Ngroups = 2, # tells the function how many groups to iterate over
                     threshold = 0.5, # sets the threshold for identifying multiple cycles per day
                     demandUnit = 'Wh', # unit of the raw interval data
                     steps=['Summary'] # which steps of the analysis to run, default is entire chain
                     )

#if False: # GroupAnalysisMaster - synthetic data
#    GroupAnalysisMaster(dirin_raw='testdata/', 
#                    dirout_data='output/', 
#                    dirout_plots='plots/',
#                    fnamebase='waterSupplyandIrrigationSystems',
#                    fnamein=fnamebase+'.4billing.csv',
#                    Ngroups=1, 
#                    threshold=0.1, 
#                    demandUnit='Wh',
#                     steps=['Summary'])     
#   
#if False: # GroupAnalysisMaster
#    GroupAnalysisMaster(dirin_raw='data/', 
#                    dirout_data='data/', 
#                    dirout_plots='plots/',
#                    fnamebase='largeOfficesAll',
#                    fnamein=fnamebase+'.4billing.csv',
#                    Ngroups=1, 
#                    threshold=0.1, 
#                    demandUnit='Wh',
#                    steps=['Summary'])    
    
if False:
    SaveDeltaByMonth(dirin_raw='data/', 
                    dirout='output/', 
                    fnamebase='largeOfficesAll',
                    fnameout = 'largeOfficesAll.DurationCurves.csv',
                    fnamein=fnamebase+'.4billing.csv',
                    Ngroups=4)
     
#%% Plot Duration Curves     
if False: # annual duration curve 
    PlotDurationCurves(dirin='testdata/', 
                       fnamein=fnamebase+'.normalized.csv',
                       dirout='testdata/', 
                       fnameout=fnamebase+'.DurationCurves.pdf',
                       dirlog='testdata/')
    
if False: # family of duration curves 
    PlotFamilyOfDurationCurves(dirin='testdata/', 
                               fnamein=fnamebase+'.normalized.csv',
                               dirout='testdata/', 
                               fnameout=fnamebase+'.FamilyOfDurationCurves.pdf',
                               dirlog='testdata/')
    
#%% Demonstration Figures
if False:
    
    n = 1        
    fnamebase = 'largeOfficesAll' #.g1L.energyOnly.A.normalized
    groupL = 'g' + str(n) + 'L'
    groupo = 'g' + str(n) + 'o'
    fnameout  = fnamebase+".delta." + groupL + "-" + groupo + ".csv"
    
    ShowFlexibilityOptions(dirin='data/', # outputs
               fnameinL=fnamebase+ "." + groupL + ".energyOnly.A.normalized.csv",
               fnameino=fnamebase+ "." + groupo + ".energyOnly.A.normalized.csv",
               dirout='data/', dirrate='tou_data/',ratein='SCE-TOU-GS3-B.csv',
               fnameout=fnameout.replace('.csv', '.flexibility.pdf'))       
    
    ShowWalk2DurationCurve(dirin='data/', # outputs
               fnamein  = fnamebase+".delta." + groupL + "." + groupo + ".csv",
               fnameinL=fnamebase+ "." + groupL + ".energyOnly.A.normalized.csv",
               fnameino=fnamebase+ "." + groupo + ".energyOnly.A.normalized.csv",
               dirout='data/', dirrate='tou_data/',ratein='SCE-TOU-GS3-B.csv',
               fnameout=fnameout.replace('.csv', '.durationWalk.pdf'))          