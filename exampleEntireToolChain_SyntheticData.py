# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""
from UtilityFunctions import FixDST, AnonymizeCIDs, CalculateBilling, CalculateGroups
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from NormalizeLoads import NormalizeLoads
from PlotHeatMaps import PlotHeatMaps
from GroupAnalysis import GroupAnalysisMaster, ShowWalk2DurationCurve, ShowFlexibilityOptions, SaveDeltaByMonth
from CustomerReport import CreateCustomerReports

#%% Define Iterations
fnamebase = 'synthetic30'
ratein =  'SCE-TOU-PA-2-B.csv'


#%% Create profiles
if False: # GenerateSyntheticProfiles
    GenerateSyntheticProfiles(30, # number of profiles to create
                  '2017-01-01 00:00', # start date
                  '2017-12-31 23:45', # end date
                  IDlen=6,  # ID length
                  meMean=200,  #  monthly energy mean,
                  htllr=2.0, # high to low load ratio (peak day / low day)
                  dirout='testdata/', 
                  fnameout = fnamebase + '.csv', 
                  dirlog='testdata/')
# example ouput:
    # "testdata/synthetic30.csv"

#%% AnonymizeCIDs - not relevant for synthetic data
if False: # AnonymizeCIDs
    AnonymizeCIDs(dirin='testdata/', 
                  fnamein=fnamebase+'.csv',
                  dirout='testdata/', 
                  fnameout='two_grocers_DST.anonymized.csv', 
                  fnameKeys='two_grocers_DST.lookup.csv',
                  dirlog='testdata/', 
                  fnameLog='AnonymizeCIDs.log',
                  IDlen=6)

#%% Fix DST- not relevant for synthetic data
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
# example input:
    # testdata/synthetic30.csv    
# example output:
    # "testdata/synthetic30.normalized.csv"
    
#%% Plot heatmaps
if False:  # PlotHeatMaps  
    PlotHeatMaps(dirin='testdata/', 
                 fnamein=fnamebase+'.normalized.csv', 
                 # considerCIDs=fnamebase+'.g1c.csv', 
                 # ignoreCIDs = fnamebase+'.g1i.csv',
                 dirout='testdata/', 
                 fnameout=fnamebase+'.HeatMaps.pdf',
                 dirlog='testdata/')  
# example input:
    # testdata/synthetic30.normalized.csv    
# example output:
    # testdata/synthetic30.HeatMaps.pdf
    
#%% Calculate Billing
if False: # CalculateBilling
    CalculateBilling(dirin='testdata/', 
                     fnamein=fnamebase+'.csv',
                     dirout='testdata/', 
                     fnameout=fnamebase+'.billing.csv',
                     fnameoutsummary ='summary.' + fnamebase + '.billing.csv',
                     dirlog='testdata/',
                     demandUnit='Wh',
                     dirrate='tou_data/',
                     ratein=ratein,
                     writeDataFile=True,
                     writeSummaryFile=True) 
# example inputs:
    # testdata/synthetic30.csv    
    # tou_rates/TOU-GS3-B.csv
    
# example outputs:
    # testdata/synthetic30.billing.csv
    # testdata/summary.synthetic30.billing.csv
    
#%% Group Customers
if False: #  CalculateGroups
    CalculateGroups(dirin='testdata/', 
                    fnamein="summary." + fnamebase+'.billing.csv',
                    dirout='testdata/', 
                    dirplot='testdata/', 
                    fnamebase=fnamebase,
                    dirlog='testdata/',  
                    ignore1515=True,
                    energyPercentiles = [0, 100], # this creates only one group, but [0, 50, 100] would create two groups
                    chargeType="Energy")

# example input:
    # testdata/summary.synthetic30.billing.csv  
    
# example output:
    # testdata/synthetic30.groups.pdf
    # testdata/synthetic10.g1L.groupIDs.csv
    # testdata/synthetic10.g1o.groupIDs.csv
        
#%% Analyze Groups & Calculate Flexibility      
# performs normalizing groups, delta between groups, plot delta by day, & plot delta summary
if False:  # full chain using synthetic data, e.g. for GE
    GroupAnalysisMaster(dirin_raw = 'testdata/', # folder where the raw data inputs are located  
                     dirout_data = 'testdata/',  # folder where to save the ouput data
                     dirout_plots = 'testdata/', # folder where to save the output figures
                     dirlog = 'testdata/', # folder where the log file(s) are saved
                     fnamebase = fnamebase, # file name base (usual by the type of building / NAICS)
                     fnamein = fnamebase+'.csv', # interval data
                     Ngroups = 1, # tells the function how many groups to iterate over
                     threshold = 0.5, # sets the threshold for identifying multiple cycles per day
                     demandUnit = 'Wh' # unit of the raw interval data
                     )
 # example inputs:    
     # testdata/synthetic30.csv
    # testdata/synthetic30.g1L.groupIDs.csv
    # testdata/synthetic30.g1o.groupIDs.csv"
# see example outputs:
# from step #1: Normalize Leaders of each group
    # testdata/synthetic30.g1L.normalized.csv
# from step #2: Normalize Others of each group
    # testdata/synthetic30.g1o.normalized.csv
# from step #3: Calculate Delta between Leaders & Others of each group
    # testdata/synthetic30.delta.g1L-g1o.csv    
# from step #4: Create PDF of Deltas by Day for each group: 365 pages
    #  testdata/synthetic30.delta.g1L-g1o.ByDay.pdf    
# from step #5: Create PDF of Load Flexibility Summary for each group: 13 pages
    # testdata/synthetic30.delta.g1L-g1o.Summary.pdf
    
#%% Calculate Billing for a leader / others group
if False: # CalculateBilling
    CalculateBilling(dirin='testdata/', 
                     fnamein='synthetic30.g1L.normalized.csv',
                     dirout='testdata/', 
                     fnameout='synthetic30.g1L.billing.csv',
                     fnameoutsummary ='summary.synthetic30.g1L.billing.csv',
                     dirlog='testdata/',
                     demandUnit='Wh',
                     dirrate='tou_data/',
                     varName='AvgDemand',
                     ratein=ratein,
                     writeDataFile=True,
                     writeSummaryFile=False) 
# example input:    
    # testdata/synthetic30.g1L.normalized.csv
# see example output:
    # testdata/synthetic30.g1L.billing.csv
    
#%% Customer Report vs the leaders/others
if True:
    CreateCustomerReports(dirin='testdata/', 
                    fnamein='synthetic30.billing.csv', 
                    considerCIDs='synthetic30.g1o.groupIDs.csv',
                    dirin_group='testdata/', 
                    fnamein_group = 'synthetic30.g1L.billing.csv', 
                    leaderFlag=False, 
                    dirout='testdata/')
# example inputs:    
    # testdata/synthetic30.billing.csv
    # testdata/synthetic30.g1o.groupIDs.csv
    # testdata/synthetic30.g1L.billing.csv
    
# see example pdfs, one for each customer:
    # e.g., testdata/CustomerReport_GJI1PT.pdf
    
#%% Save Duration to CSV
if False:# SaveDeltaByMonth
    SaveDeltaByMonth(dirin_raw = 'testdata/', 
                    dirout ='testdata/', 
                    fnamebase=fnamebase,
                    Ngroups=1,
                    fnameout=fnamebase + '.DurationCurves.csv',
                    dirlog='output/')
    
    
# example inputs:
    # testdata/synthetic30.g1L.normalized.csv
    # testdata/synthetic30.g1o.normalized.csv
# see example outputs:
    # testdata/synthetic30.DurationCurves.csv     
    
#%% Plot heatmaps of a delta
if False:  # PlotHeatMaps  
    PlotHeatMaps(dirin='testdata/', 
                 fnamein= fnamebase + '.delta.g1L-g1o.csv', 
                 varName = 'AbsDelta', 
                 dirout = 'plots/', 
                 fnameout = fnamebase + '.delta.g1L-g1o.HeatMap.pdf',
                 dirlog = 'output/',
                 ) 
# example inputs:
    # testdata/synthetic30.delta.g1L-g1o.csv
# see example output:
    #   testdata/synthetic30.delta.g1L-g1o.HeatMap.pdf
    
#%% Plot Duration Curves     
if True: # annual duration curve 
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