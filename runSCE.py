# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""
from GroupAnalysis import DeltaLoads, PlotDeltaByDay, PlotDeltaSummary, GroupAnalysisMaster
from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs, CalculateBilling, CalculateGroups
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from NormalizeLoads import ReviewLoads, NormalizeLoads,  NormalizeGroup
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from PlotHeatMaps import PlotHeatMaps, PlotHeatMapOfBilling
from PlotBilling import PlotBillingData
from CustomerReport import PlotMonthlySummaries, PlotAnnualSummaries, PlotAnnualWhiskers, ExtractPlotsFromPDF, PopulateLaTeX, CompileLaTeX, PurgeLaTeX

if False:
    fnamebase = 'waterSupplyandIrrigationSystems' # Name your input files here
    ratefile = 'SCE-TOU-PA-2-B.csv' # name of TOU rate profile

if False:
    fnamebase = 'largeOfficesAll' # Name your input files here
    ratefile = 'SCE-TOU-GS2-B.csv' # name of TOU rate profile
    ignoreCIDs_forGrouping = 'largeOfficesAll.A.ignore.csv' # the ignoreCIDs for grouping (e.g. sites with solarPV, etc)
    considerfname = 'largeOffices_CustomerI.csv'

if True:
    fnamebase = 'synthetic2_old' # Name your input files here
    ratefile = 'SCE-TOU-GS3-B.csv' # name of TOU rate profile
    considerfname = 'groceryStores_CustomerI.csv'

# =============================================================================
# #%% Create profiles
# if False:
#     GenerateSyntheticProfiles(10, # number of profiles to create
#                               '2017-01-01 00:00', '2017-12-31 23:45', # timedate range
#                               IDlen=6, meMean=200, htllr=2.0, # ID length, monthly energy mean, high to low load ratio (peak day / low day)
#                               dirout='input/', fnameout=fnamebase + 'csv', 
#                               dirlog='input/')
# 
# =============================================================================
# =============================================================================
# #%% Convert Feather file
# if False:
#     ConvertFeather(dirin='input/', fnamein=fnamebase + '.feather',
#                    dirout='input/', fnameout=fnamebase + '.csv',
#                    dirlog='input/',
#                    renameDict={'DatePeriod':'datetimestr', 'Usage':'Demand'},
#                    writeOutput = True)
# =============================================================================

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
    ReviewLoads(dirin='input/', fnamein=fnamebase + '.A.csv', considerCIDs ='troubleShootCIDs.csv',
                   dirout='input/', fnameout=fnamebase+'A.summary.csv',
                   dirlog='input/')
#%% Normalize profiles
if False:
    NormalizeLoads(dirin='input/', fnamein=fnamebase + '.A.csv', #ignoreCIDs=fnamebase + '.A.ignore.csv',
                   dirout='output/', fnameout=fnamebase + '.A.normalized.csv',
                   dirlog='output/')
#%% Plot heatmaps, Re-define the ignore list(10-12-2018)
if True:    
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', #ignoreCIDs = fnamebase + '.A.ignore.csv',
                 considerCIDs = considerfname,
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.pdf',
                 dirlog='plots/')
# =============================================================================
# #%% Generate the heatmaps of the leaders
# if False:
#     for n in [1,2,3,4]:
#         PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', 
#                 considerCIDs = 'g' + str(n) + 'L.'+ fnamebase + '.Energy.A.groups.csv',
#                 dirout='plots/', fnameout=fnamebase + ".g" + str(n) + 'L.A.HeatMaps.pdf',
#                 dirlog='plots/')
# =============================================================================
#%% Calculate Billing
if False:
    CalculateBilling(dirin='input/', fnamein=fnamebase + '.A.csv', #ignoreCIDs = ignoreCIDs_forGrouping, #considerCIDs ='purelyBundledCustomers.csv', #fnamebase + '.g1c.csv', 
                    dirrate = 'tou_data', ratein = ratefile, 
                   dirout='output/', fnameout=fnamebase + '.A.billing.csv',
                   dirlog='output/', writeDataFile=True)
    
#%% Plot Billing (optional)
if False:
    PlotBillingData(dirin='output/', fnamein=fnamebase + '.A.billing.csv', 
                   dirout='plots/', fnameout=fnamebase + '.A.billing.pdf',
                   dirlog='plots/')
    
#%% Plot heatmap of TOU Price
if True:
    PlotHeatMapOfBilling(dirin='output/', fnamein=fnamebase + '.A.billing.csv',
                         considerCIDs = considerfname,
                         dirout='plots/', fnameout=fnamebase + '.A.billing.Heatmaps.pdf',
                         dirlog='plots/')
    
#%% Plot Billing Heatmaps (after calculate groups)
if False:
    PlotHeatMapOfBilling(dirin='output/', fnamein=fnamebase + '.A.billing.csv', 
                   considerCIDs =   'g1L.'+ fnamebase + '.Energy.A.groups.csv',
                   dirout='plots/', fnameout=fnamebase + '.A.billing.g1L.Heatmaps.pdf',
                   dirlog='plots/')     
    PlotHeatMapOfBilling(dirin='output/', fnamein=fnamebase + '.A.billing.csv', 
                   considerCIDs =   'g1o.'+ fnamebase + '.Energy.A.groups.csv',
                   dirout='plots/', fnameout=fnamebase + '.A.billing.g1o.Heatmaps.pdf',
                   dirlog='plots/') 
    
#%% Grouping
if False: # by energy component of bill
    CalculateGroups(dirin='output/', 
                    fnamein="summary." + fnamebase+'.A.billing.csv',
                    highlightCIDs = 'largeOffices_CustomerI.csv',
                    #considerCIDs = 'groceryStores_CustomerM.csv', 
                    dirout='output/', 
                    fnamebase="largeOffices_CustomerI.csv.Energy." + fnamebase,
                    dirlog='plots/',  
                    ignore1515=True,
                    energyPercentiles = [0, 5, 27.5, 50, 77.5, 95, 100], 
                    chargeType="Energy")

  
#if False: # by Total Bill
#    CalculateGroups(dirin='output/', 
#                    fnamein="summary." + fnamebase+'.A.billing.csv',
#                    dirout='output/', 
#                    fnamebase=fnamebase,
#                    dirlog='plots/',  
#                    ignore1515=False,
#                    energyPercentiles = [5, 27.5,  50, 72.5, 95], 
#                    chargeType="Total")
    
if False: # by demand component of bill   
    CalculateGroups(dirin='output/', 
                    fnamein="summary." + fnamebase+'.A.billing.csv',
                    highlightCIDs = 'largeOffices_CustomerI.csv',
                    #considerCIDs = 'groceryStores_CustomerM.csv', 
                    dirout='output/', 
                    fnamebase="largeOffices_CustomerI.csv.Demand." + fnamebase,
                    dirlog='plots/',
                    ignore1515=True,
                    energyPercentiles = [0, 25, 50, 75, 100], 
                    chargeType="Demand")

if False: # performs normalizing groups, delta between groups, plot delta by day, & plot delta summary (all in one function)
    GroupAnalysisMaster(dirin_raw='input/',
                        dirin_data = 'output/',
                        dirout_plots='plots/', dirlog='output/',
                        fnamebase=fnamebase,
                        fnamein=fnamebase+'.A.csv',
                        Ngroups=2, threshold=0.5, demandUnit='Wh') 

##%% This entire block of code is replaced by GrupAnalysisMaster (above)
##%% Normalize profiles
#if True:
#    for groupName in [ 'g1L' , 'g1o', 'g2L', 'g2o', 'g3L', 'g3o', 'g4L', 'g4o'] :
#        NormalizeGroup(dirin='input/', fnamein=fnamebase + '.A.csv', dirconsider = 'output/', considerCIDs = groupName + '.'+ fnamebase + '.Energy.A.groups.csv',
#                   dirout='output/', fnameout=fnamebase + '.' + groupName + '.energyOnly.A.normalized.csv',
#                   groupName = groupName,
#                   dirlog='output/')
#if True:
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
        
#%% Export profiles (use this for troubleshooting)
if False:
    ExportLoadFiles(dirin='output/', fnamein =fnamebase + '.A.normalized.csv', explist=fnamebase + '.A.ignore.csv',
                   dirout='output/', 
                   dirlog='output/')
#%% Plot duration curves
if True:
    PlotDurationCurves(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', #ignoreCIDs = fnamebase + '.A.ignore.csv', 
                       considerCIDs = considerfname,
                       byMonthFlag=True, withDailyProfiles=True, 
                       dirout='plots/', fnameout=fnamebase + '.A.duration.monthly.test.pdf',
                       dirlog='plots/')
#%% Export profiles (use this for troubleshooting)
if False:
    ExportLoadFiles(dirin='output/', fnamein =fnamebase + '.A.normalized.csv', explist= 'troubleShootCIDs.csv', #fnamebase + '.A.ignore.csv',
                   dirout='output/', 
                   dirlog='output/') 

#%% Plot charts for customer reports
if True:   
    PlotFamilyOfDurationCurves(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', 
                               #ignoreCIDs = fnamebase + '.A.ignore.csv',
                               dirout='plots/', fnameout=fnamebase + '.A.FamilyOfDurationCurves.pdf', 
                               byMonthFlag=True, 
                               highlightCIDs = considerfname,
                               dirlog='plots/')
if True:
    PlotMonthlySummaries(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', 
                         considerCIDs = considerfname, #ignoreCIDs = fnamebase + '.A.ignore.csv',
                         dirout='plots/', fnameout=fnamebase + '.A.boxplots.pdf',
                         dirlog='plots/')

if True:
    PlotAnnualSummaries(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', 
                        considerCIDs = considerfname, #ignoreCIDs = fnamebase + '.A.ignore.csv',
                        dirout='plots/', fnameout=fnamebase + '.A.piecharts.pdf',
                        dirlog='plots/')

if True:
    PlotAnnualWhiskers(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', 
                       considerCIDs = considerfname, #ignoreCIDs = fnamebase + '.A.ignore.csv',
                       dirout='plots/', fnameout=fnamebase + '.A.whiskercharts.pdf', highlightCIDs = considerfname,
                       dirlog='plots/') # to plot fewer groups, use 'consderCIDs'

#%% Extracting relevant plot pages for custoemrs listed in considerIDs
if True:
    ExtractPlotsFromPDF(dirin='plots/', fnamein= fnamebase + '.A.piecharts.pdf',
                        considerCIDs = considerfname,
                        dirout='report/visuals/', fnameout = '.piechart.pdf',
                        dirlog='output/')
if True:
    ExtractPlotsFromPDF(dirin='plots/', fnamein= fnamebase + '.A.boxplots.pdf',
                        considerCIDs = considerfname,
                        dirout='report/visuals/', fnameout = '.boxplot.pdf',
                        dirlog='output/')
if True:
    ExtractPlotsFromPDF(dirin='plots/', fnamein= fnamebase + '.A.whiskercharts.pdf',
                        considerCIDs = considerfname,
                        dirout='report/visuals/', fnameout = '.whiskerchart.pdf',
                        dirlog='output/')
if True:
    ExtractPlotsFromPDF(dirin='plots/', fnamein= fnamebase + '.A.heatmaps.pdf',
                        considerCIDs = considerfname,
                        dirout='report/visuals/', fnameout = '.heatmap.pdf',
                        dirlog='output/')
if True:
    ExtractPlotsFromPDF(dirin='plots/', fnamein= fnamebase + '.A.duration.monthly.test.pdf',
                        considerCIDs = considerfname, 
                        dirout='report/visuals/', fnameout = '.duration.monthly.test.pdf',
                        dirlog='output/')
    
if True:
    ExtractPlotsFromPDF(dirin='plots/', fnamein= fnamebase + '.A.billing.Heatmaps.pdf',
                        considerCIDs = considerfname, 
                        dirout='report/visuals/', fnameout = '.billing.Heatmap.pdf',
                        dirlog='output/')


#%% Generating LaTeX files for customers listed in considerIDs using latex template file as input
ReplaceDict = {'<RateCode>':'TOU-GS3-B'}
if True:
    PopulateLaTeX(dirin='output/', fnamein= 'summary.'+ fnamebase + '.A.billing.csv', 
                  dirtex = 'report/templates/', fnametex = 'report05t.tex', 
                  considerCIDs = considerfname,
                  dirout='report/', fnameout = '.report05t.tex',
                  ReplaceDict = ReplaceDict,
                  dirlog='report/')

if True:
    CompileLaTeX(dirin='output/', considerCIDs = considerfname,
                 dirtex = 'report/', texext='.report05t.tex',
                 dirout='report/',
                 dirlog='report/')
    CompileLaTeX(dirin='output/', considerCIDs = considerfname,
                 dirtex = 'report/', texext='.report05t.tex',
                 dirout='report/',
                 dirlog='report/')

if False:
    PurgeLaTeX(dirin='output/', considerCIDs = considerfname,
               dirtex = 'report/', 
               dirlog = 'report/')