# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""
from UtilityFunctions import FixDST, AnonymizeCIDs, CalculateBilling, CalculateGroups
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from NormalizeLoads import NormalizeLoads
from PlotHeatMaps import PlotHeatMaps, Plot3HeatMaps
from GroupAnalysis import GroupAnalysisMaster, ShowWalk2DurationCurve, ShowFlexibilityOptions, SaveDeltaByMonth
from SupportFunctions import findMissingData

#%% Define Iterations
if True: # synthetic10
    fnamebase = 'synthetic10'
    ratein =  'SCE-TOU-PA-2-B.csv'

if False: #waterSupplyandIrrigationSystems
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
# see example ouputs:
    # 


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
# see example outputs:
    #   two_grocers_DST.lookup.csv
    #


#%% Fix DST
if False: # FixDST
    FixDST(dirin='testdata/', 
           fnamein='two_grocers_DST_test2.csv',
                   dirout='testdata/', 
                   fnameout='two_grocers2.csv',
                   dirlog='testdata/',
                   tzinput='America/Los_Angeles',
                   OutputFormat='SCE')

# see example output: examples/fnameout.csv
    # 

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
    
# see example outputs:
    #    
    #
    
#%% Plot heatmaps
if False:  # PlotHeatMaps  
    PlotHeatMaps(dirin='testdata/', 
                 fnamein=fnamebase+'.normalized.csv', 
                 # considerCIDs=fnamebase+'.g1c.csv', 
                 # ignoreCIDs = fnamebase+'.g1i.csv',
                 dirout='testdata/', 
                 fnameout=fnamebase+'.HeatMaps.g1.pdf',
                 dirlog='testdata/')    

# see example outputs:
    #    
    
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

# see example outputs:
    #    
    
if True:# Heatmap of Billing
    Plot3HeatMaps(dirin='testdata/', 
                  fnamein=fnamebase+'.billing.csv', # considerCIDs=fnamebase+'.g1c.csv', ignoreCIDs = fnamebase+'.g1i.csv',
                  dirout='testdata/', 
                  fnameout=fnamebase+'.HeatMaps.BillingNew.pdf',
                  dirlog='testdata/')    

# see example outputs:
    #    
    
if False: #findMissingData: creates csv of customers with missing data, to use as ignoreCID
    findMissingData(dirin='testdata/', 
                    fnamein=fnamebase+'.csv',
                    dirout='testdata/',
                    fnameout=fnamebase + '.List.MissingData.csv', 
                    dirlog='testdata/', 
                    fnameLog='InitializeIgnoreList.log')

# see example outputs:
    #    
    
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

# see example outputs:
    #    
        
#%% Analyze Groups & Calculate Flexibility      
# performs normalizing groups, delta between groups, plot delta by day, & plot delta summary
if False:  # full chain using synthetic data, e.g. for GE
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
                     demandUnit = 'Wh' # unit of the raw interval data
                     )
    
if False:  # part of chain using real data, e.g. for GE
    GroupAnalysisMaster(dirin_raw = 'input/', # folder where the raw data inputs are located  
                     dirout_data ='output/',  # folder where to save the ouput data
                     dirout_plots = 'plots/', # folder where to save the output figures
                     dirlog = 'output/', #  folder where to save the log file(s)
                     fnamebase = 'waterSupplyandIrrigationSystems', # file name base (usual by the type of building / NAICS)
                     fnamein = 'waterSupplyandIrrigationSystems.A.csv', # interval data 
                     Ngroups = 1, # tells the function how many groups to iterate over
                     demandUnit = 'Wh', # unit of the raw interval data
                     steps=['DeltaByDayWithDuration'] # which steps of the analysis to run, default is entire chain
                     )  
    
if False:  # part of chain using real data, e.g. for GE
    GroupAnalysisMaster(dirin_raw = 'input/', # folder where the raw data inputs are located  
                     dirout_data ='output/',  # folder where to save the ouput data
                     dirout_plots = 'plots/', # folder where to save the output figures
                     dirlog = 'output/', #  folder where to save the log file(s)
                     fnamebase = 'LargeOfficesAll', # file name base (usual by the type of building / NAICS)
                     fnamein = 'LargeOfficesAll.A.csv', # interval data 
                     Ngroups = 2, # tells the function how many groups to iterate over
                     demandUnit = 'Wh', # unit of the raw interval data
                     steps=['Summary'] # which steps of the analysis to run, default is entire chain
                     )

# see example outputs:
    #    
     
#%% Plot heatmaps
if False:  # PlotHeatMaps  
    PlotHeatMaps(dirin='output/', 
                 fnamein='largeOfficesAll.delta.g1L-g1o.csv', 
                 # considerCIDs=fnamebase+'.g1c.csv', 
                 # ignoreCIDs = fnamebase+'.g1i.csv',
                 varName='AbsDelta', 
                 dirout='plots/', 
                 fnameout='largeOfficesAll.delta.g1L-g1o.HeatMap.pdf',
                 dirlog='output/',
                 )    
# see example outputs:
    #    

#%% Save Duration to CSV
if False:# SaveDeltaByMonth
    SaveDeltaByMonth(dirin_raw='data/', 
                    fnamein=fnamebase+'.4billing.csv',
                    dirout='output/', 
                    fnamebase='largeOfficesAll',
                    Ngroups=4,
                    fnameout='largeOfficesAll.DurationCurves.csv',
                    dirlog='output/')
# see example outputs:
    #      
    
    
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
    
    groupL = 'g1L'
    groupo = 'g1o'
    fnameout  = fnamebase+".delta." + groupL + "-" + groupo + ".csv"
    
    ShowFlexibilityOptions(dirin='data/',
               fnameinL = fnamebase+ "." + groupL + ".normalized.csv",
               fnameino = fnamebase+ "." + groupo + ".normalized.csv",
               dirout = 'data/', 
               dirrate = 'tou_data/',
               ratein = 'SCE-TOU-GS3-B.csv',
               fnameout = fnameout.replace('.csv', '.flexibility.pdf'))       
    
    ShowWalk2DurationCurve(dirin='data/',
               fnamein = fnamebase+".delta." + groupL + "." + groupo + ".csv",
               fnameinL = fnamebase+ "." + groupL + ".normalized.csv",
               fnameino = fnamebase+ "." + groupo + ".normalized.csv",
               dirout = 'data/', 
               dirrate = 'tou_data/',
               ratein = 'SCE-TOU-GS3-B.csv',
               fnameout = fnameout.replace('.csv', '.durationWalk.pdf'))          