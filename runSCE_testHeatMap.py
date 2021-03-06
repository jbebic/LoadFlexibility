# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""
from GroupAnalysis import GroupAnalysisMaster, SaveDeltaByMonth
from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs, CalculateBilling, CalculateGroups
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from NormalizeLoads import ReviewLoads, NormalizeLoads
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from PlotHeatMaps import PlotHeatMaps
from PlotBilling import PlotBillingData
from CustomerReport import CreateCustomerReports

if True:
    fnamebase = 'waterSupplyandIrrigationSystems' # Name your input files here
    ratefile = 'SCE-TOU-PA-2-B.csv' # name of TOU rate profile

if False:
    fnamebase = 'largeOfficesAll' # Name your input files here
    ratefile = 'SCE-TOU-GS2-B.csv' # name of TOU rate profile
    ignoreCIDs_forGrouping = 'largeOfficesAll.A.ignore.csv' # the ignoreCIDs for grouping (e.g. sites with solarPV, etc)

#%% Create profiles
if False:
    GenerateSyntheticProfiles(10, # number of profiles to create
                              '2017-01-01 00:00', '2017-12-31 23:45', # timedate range
                              IDlen=6, meMean=200, htllr=2.0, # ID length, monthly energy mean, high to low load ratio (peak day / low day)
                              dirout='input/', fnameout=fnamebase + 'csv', 
                              dirlog='input/')

#%% Convert Feather file
if False:
    ConvertFeather(dirin='input/', fnamein=fnamebase + '.feather',
                   dirout='input/', fnameout=fnamebase + '.csv',
                   dirlog='input/',
                   renameDict={'DatePeriod':'datetimestr', 'Usage':'Demand'},
                   writeOutput = True)

#%% AnonymizeCIDs #CAREFULL when running this function - it overwrites existing CIDs completely and require to re-do all the steps.
if False:
    AnonymizeCIDs(dirin='private/', fnamein=fnamebase + '.csv', 
                  dirout='input/', fnameout=fnamebase + '.A.csv', fnameKeys=fnamebase + '.lookup.csv',
                  dirlog='private/', fnameLog='AnonymizeCIDs.log')#,IDlen=6)

#%% Manual steps:
#  1) Validate that the CustomerIDs have been anonymized: open the csv file in 
#     text editor (e.g. Notepad++) and review CustomerIDs
#  2) Copy the anonymized file from private to input directory

#%% Fix DST # Correct calculated billings to use DST adjusted times.
if False:
    FixDST(dirin='input/', fnamein=fnamebase + '.A.csv',
                   dirout='input/', fnameout=fnamebase + '.A.csv',
                   dirlog='input/',
                   tzinput = 'America/Los_Angeles',
                   OutputFormat = 'ISO')

#%% Review load profiles
if False:
    ReviewLoads(dirin='input/', fnamein=fnamebase + '.A.csv',
                   dirout='input/', fnameout=fnamebase+'A.summary.csv',
                   dirlog='input/')
#%% Normalize profiles
if False:
    NormalizeLoads(dirin='input/', fnamein=fnamebase + '.A.csv', #ignoreCIDs=fnamebase + '.A.ignore.csv',
                   dirout='output/', fnameout=fnamebase + '.A.normalized.csv',
                   dirlog='output/')
#%% Plot heatmaps, Re-define the ignore list(10-12-2018)
if False:    
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', #ignoreCIDs = fnamebase + '.A.ignore.csv',
                 #considerCIDs = 'largeOfficesConsider.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.pdf',
                 dirlog='plots/')
#%% Generate the heatmaps of the leaders
if False:
    for n in [1,2,3,4]:
        PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', 
                considerCIDs = 'g' + str(n) + 'L.'+ fnamebase + '.Energy.A.groups.csv',
                dirout='plots/', fnameout=fnamebase + ".g" + str(n) + 'L.A.HeatMaps.pdf',
                dirlog='plots/')
        
#%% Calculate Billing
if False:
    CalculateBilling(dirin='input/', fnamein=fnamebase + '.A.csv', #ignoreCIDs = ignoreCIDs_forGrouping, #considerCIDs ='purelyBundledCustomers.csv', #fnamebase + '.g1c.csv', 
                    dirrate = 'tou_data', ratein = ratefile, 
                   dirout='output/', fnameout=fnamebase + '.A.billing.csv',
                   dirlog='output/', writeDataFile=True)
    
#%% Plot Billing
if False:
    PlotBillingData(dirin='output/', fnamein=fnamebase + '.A.billing.csv', 
                   dirout='plots/', fnameout=fnamebase + '.A.billing.pdf',
                   dirlog='plots/')
    
#%% IMB: these are replaced by CreateReports
#if False:
#    PlotHeatMapOfBilling(dirin='output/', fnamein=fnamebase + '.A.billing.csv', 
#                   considerCIDs =   'g1L.'+ fnamebase + '.Energy.A.groups.csv',
#                   dirout='plots/', fnameout=fnamebase + '.A.billing.g1L.Heatmaps.pdf',
#                   dirlog='plots/')     
#    PlotHeatMapOfBilling(dirin='output/', fnamein=fnamebase + '.A.billing.csv', 
#                   considerCIDs =   'g1o.'+ fnamebase + '.Energy.A.groups.csv',
#                   dirout='plots/', fnameout=fnamebase + '.A.billing.g1o.Heatmaps.pdf',
#                   dirlog='plots/') 
    
#%% Grouping
if False: # by energy component of bill
    CalculateGroups(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', #ignoreCIDs = fnamebase + '.A.ignore.csv', #considerCIDs = fnamebase + '.g1c.csv',
                   plotGroups = True, chargeType='Energy', energyPercentiles = [0, 25, 50, 75, 100 ],
                   dirout='output/', fnameout=fnamebase + '.Energy.A.groups.csv',
                   dirlog='plots/', dirplot='plots/') 
    
if False: # by Total Bill
    CalculateGroups(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', #ignoreCIDs = fnamebase + '.A.ignore.csv', #considerCIDs = fnamebase + '.g1c.csv',
                   plotGroups = True, chargeType='Total', energyPercentiles = [10, 30, 50, 70, 90],
                   dirout='output/', fnameout=fnamebase + '.Total.A.groups.csv', 
                   dirlog='plots/', dirplot='plots/')
    
if False: # by demand component of bill   
    CalculateGroups(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', #ignoreCIDs = fnamebase + '.A.ignore.csv', #considerCIDs = fnamebase + '.g1c.csv',
                   plotGroups = True, chargeType='Demand', energyPercentiles = [10, 30, 50, 70, 90],
                   dirout='output/', fnameout=fnamebase + '.Demand.A.groups.csv',
                   dirlog='plots/', dirplot='plots/')  
    
#%% Group Analysis Functions
if False: # performs normalizing groups, delta between groups, plot delta by day, & plot delta summary (all in one function)
    GroupAnalysisMaster(dirin_raw='input/',
                        dirout_data='output/', 
                        dirout_plots='plots/', 
                        dirlog='output/',
                        fnamebase=fnamebase,
                        fnamein=fnamebase+'.A.csv',
                        Ngroups=2, threshold=0.5, demandUnit='Wh') 
    
#%% Save Duration to CSV
if False:# SaveDeltaByMonth
    SaveDeltaByMonth(dirin_raw='output/', 
                    dirout='output/', 
                    fnamebase=fnamebase,
                    Ngroups=2,
                    fnameout= fnamebase + '.durationcurves.csv',
                    dirlog='output/') 
    
#%% Calculate Billing of the Group of Others
if True:
    CalculateBilling(dirin='input/', 
                     fnamein=fnamebase + '.g1o.normalized.csv',
                     dirout='output/', 
                     fnameout=fnamebase + '.g1o.billing.csv',
                     fnameoutsummary ='summary.' + fnamebase + '.g1L.billing.csv',
                     dirlog='output/',
                     demandUnit='Wh',
                     dirrate='tou_data/',
                     varName='AvgDemand',
                     ratein=ratefile,
                     writeDataFile=True,
                     writeSummaryFile=False)    
    
#%% Create Report for Each Leader
if True:
    CreateCustomerReports(dirin='input/', 
                    fnamein=fnamebase + '.A.billing.csv', 
                    considerCIDs=fnamebase + 'g1L.Energy.A.groups.csv',
                    dirin_group='output/', 
                    fnamein_group = fnamebase + '.g1o.billing.csv', 
                    leaderFlag=True, 
                    dirout='output/') 
    
#%% IMB: these are all replace by GroupAnalysisMaster
#if False:
#    for groupName in [ 'g1L' , 'g1o', 'g2L', 'g2o', 'g3L', 'g3o', 'g4L', 'g4o'] :
#        NormalizeGroup(dirin='input/', fnamein=fnamebase + '.A.csv', dirconsider = 'output/', considerCIDs = groupName + '.'+ fnamebase + '.Energy.A.groups.csv',
#                   dirout='output/', fnameout=fnamebase + '.' + groupName + '.energyOnly.A.normalized.csv',
#                   groupName = groupName,
#                   dirlog='output/')
#if False:
#    for n in [1,2,3,4]:
#        
#        groupL = 'g' + str(n) + 'L'
#        groupo = 'g' + str(n) + 'o'
#        fnameout  = fnamebase+".delta." + groupL + "." + groupo + ".csv"
#    
#        DeltaLoads(dirin='output/', # outputs
#                   fnameinL=fnamebase + '.' + groupL + '.energyOnly.A.normalized.csv',
#                   fnameino=fnamebase + '.' + groupo + '.energyOnly.A.normalized.csv',
#                   dirout='output/', # outputs 
#                   fnameout=fnameout,
#                   dirlog='output/' # outputs
#                   ) 
#        
#        PlotDeltaByDay(dirin='output/',  # outputs
#                   fnameinL=fnamebase + "." + groupL +".energyOnly.A.normalized.csv", 
#                   fnameino=fnamebase + "." + groupo +".energyOnly.A.normalized.csv", 
#                  dirout='plots/',
#                  fnameout=fnamebase + ".loads.energyOnly." + groupL + "." + groupo + ".A.pdf",
#                  dirlog='plots/'
#                  ) 
#        
#        PlotDeltaSummary(dirin='output/',  # outputs
#                  fnamein=fnameout, 
#                  dirout='plots/', 
#                  fnameout=fnameout.replace('.csv', '.FullYear.pdf'),
#                  dirlog='plots/'
#                  )  
#        
#%% Export profiles (use this for troubleshooting)
if False:
    ExportLoadFiles(dirin='output/', fnamein =fnamebase + '.A.normalized.csv', explist=fnamebase + '.A.ignore.csv',
                   dirout='output/', 
                   dirlog='output/')
#%% Plot duration curves
if False:
    PlotDurationCurves(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', #ignoreCIDs = fnamebase + '.A.ignore.csv', 
                       #considerCIDs = 'largeOfficesConsider.csv',
                       byMonthFlag=True,
                       dirout='plots/', fnameout=fnamebase + '.A.duration.monthly.test.pdf',
                       dirlog='plots/')
if False:   
    PlotFamilyOfDurationCurves(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', #ignoreCIDs = fnamebase + '.A.ignore.csv',
                               dirout='plots/', fnameout=fnamebase + '.A.FamilyOfDurationCurves.pdf',
                               dirlog='plots/')
    