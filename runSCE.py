# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""

import numpy as np

from GroupAnalysis import PlotGroup, DeltaLoads, PlotDelta, PlotLoads, PlotPage
from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs, SplitToGroups, CalculateBilling, CalculateGroups
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from NormalizeLoads import ReviewLoads, NormalizeLoads,  NormalizeGroup
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from PlotHeatMaps import PlotHeatMaps
from PlotBilling import PlotBillingData

fnamebase = 'synthetic2' # Name your input files here
Ngroups = 10

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

#%% AnonymizeCIDs
if False:
    AnonymizeCIDs(dirin='private/', fnamein=fnamebase + '.csv', 
                  dirout='input/', fnameout=fnamebase + '.A.csv', fnameKeys=fnamebase + '.lookup.csv',
                  dirlog='private/', fnameLog='AnonymizeCIDs.log')#,IDlen=6)

#%% Manual steps:
#  1) Validate that the CustomerIDs have been anonymized: open the csv file in 
#     text editor (e.g. Notepad++) and review CustomerIDs
#  2) Copy the anonymized file from private to input directory

#%% Fix DST
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

#%% Manual steps:
#  1) Open  

#%% Calculate Billing
if False:
    CalculateBilling(dirin='input/', fnamein=fnamebase + '.A.csv', writeDataFile=True, #considerCIDs ='purelyBundledCustomers.csv', #fnamebase + '.g1c.csv', 
                   dirout='output/', fnameout=fnamebase + '.A.billing.csv',
                   dirlog='output/')
#%% Plot Billing
if False:
    PlotBillingData(dirin='output/', fnamein=fnamebase + '.A.billing.csv', #considerCIDs = 'purelyBundledCustomers.csv',#fnamebase + '.g1c.csv',
                   dirout='plots/', fnameout=fnamebase + '.A.billing.pdf',
                   dirlog='plots/')
#%% Grouping
if False:
    CalculateGroups(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', #considerCIDs = fnamebase + '.g1c.csv',
                   plotGroups = True, chargeType='Total', energyPercentiles = [10, 30, 50, 70, 90],
                   dirout='output/', fnameout=fnamebase + '.Total.A.groups.csv', 
                   dirlog='plots/', dirplot='plots/')
    CalculateGroups(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', #considerCIDs = fnamebase + '.g1c.csv',
                   plotGroups = True, chargeType='Energy', energyPercentiles = [10, 30, 50, 70, 90],
                   dirout='output/', fnameout=fnamebase + '.Energy.A.groups.csv',
                   dirlog='plots/', dirplot='plots/')   
    CalculateGroups(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', #considerCIDs = fnamebase + '.g1c.csv',
                   plotGroups = True, chargeType='Demand', energyPercentiles = [10, 30, 50, 70, 90],
                   dirout='output/', fnameout=fnamebase + '.Demand.A.groups.csv',
                   dirlog='plots/', dirplot='plots/')   
#%% Normalize profiles
if True:
    NormalizeLoads(dirin='input/', fnamein=fnamebase + '.A.csv', #ignoreCIDs=fnamebase + '.A.ignore.csv',
                   dirout='output/', fnameout=fnamebase + '.A.normalized.csv',
                   dirlog='output/')
#%% Normalize profiles
if False:
    for groupName in [ 'g1L' , 'g1o', 'g2L', 'g2o', 'g3L', 'g3o', 'g4L', 'g4o'] :
        NormalizeGroup(dirin='input/', fnamein=fnamebase + '.A.csv', dirconsider = 'output/', considerCIDs = groupName+ '.synthetic2.Energy.A.groups.csv',
                   dirout='output/', fnameout=fnamebase + '.' + groupName + '.energyOnly.A.normalized.csv',
                   groupName = groupName,
                   dirlog='output/')
if False:
    for n in [1,2,3,4]:
        
        groupL = 'g' + str(n) + 'L'
        groupo = 'g' + str(n) + 'o'
        fnameout  = fnamebase+".delta." + groupL + "." + groupo + ".csv"
    
        DeltaLoads(dirin='output/', # outputs
                   fnameinL=fnamebase + '.' + groupL + '.energyOnly.A.normalized.csv',
                   fnameino=fnamebase + '.' + groupo + '.energyOnly.A.normalized.csv',
                   dirout='output/', # outputs 
                   fnameout=fnameout,
                   dirlog='output/' # outputs
                   ) 
        
#        PlotDelta(dirin='output/',  # outputs
#                  fnamein=fnameout, 
#                  dirout='output/', # plots
#                  fnameout=fnameout.replace('.csv', '.pdf'),
#                  dirlog='output/' # outputs
#                  )  

        PlotLoads(dirin='output/',  # outputs
                   fnameinL=fnamebase + "." + groupL +".energyOnly.A.normalized.csv", 
                   fnameino=fnamebase + "." + groupo +".energyOnly.A.normalized.csv", 
                  dirout='plots/',
                  fnameout=fnamebase + ".loads.energyOnly." + groupL + "." + groupo + ".A.pdf",
                  dirlog='plots/'
                  ) 
        
        PlotPage(dirin='output/',  # outputs
                  fnamein=fnameout, 
                  dirout='plots/', 
                  fnameout=fnameout.replace('.csv', '.FullYear.pdf'),
                  dirlog='plots/'
                  )  
        
if False:
    groupName = 'g1L'
    PlotGroup(dirin='output/', 
                  fnamein= fnamebase+'.A.normalized.csv',
                  considerCIDs ='g1L.synthetic2.Total.A.groups.csv',
                  fnameGroup = fnamebase + '.g1L.A.normalized.csv',
                  dirout='output/', fnameout=fnamebase+'.GroupPlots.' + groupName + ".pdf",
                  dirlog='output/')    

#%% Normalize profiles
if False:
    ExportLoadFiles(dirin='testdata/', fnamein='two_grocers_modified.csv', explist='two_grocers.export.csv',
                   dirout='testdata/', 
                   dirlog='testdata/')

    
#%% Plot duration curves
if False:
    PlotDurationCurves(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', #ignoreCIDs = fnamebase + '.A.ignore.csv', #considerCIDs = fnamebase + '.g1c.csv',
                       byMonthFlag=True,
                       dirout='plots/', fnameout=fnamebase + '.A.duration.monthly.pdf',
                       dirlog='plots/')
if False:   
    PlotFamilyOfDurationCurves(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', ignoreCIDs = fnamebase + '.ignore.csv',
                               dirout='plots/', fnameout=fnamebase + '.A.FamilyOfDurationCurves.pdf',
                               dirlog='plots/')
#%% Plot heatmaps
if False:    
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', ignoreCIDs = fnamebase + '.ignore.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.pdf',
                 dirlog='plots/')

# Use this only if line#165 (block above) fails    
if False:
    SplitToGroups(Ngroups, 
                  dirin='output/', fnamein=fnamebase + '.A.normalized.csv', ignoreCIDs='', considerCIDs='',
                  dirout='output/', foutbase=fnamebase, # 
                  dirlog='output/', fnameLog='SplitToGroups.log')    
if False:
    for i in np.arange(1, Ngroups+1): #for i in np.arange(1, 2):
        PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', considerCIDs = fnamebase + '.g' + str(i) + 'c.csv', #ignoreCIDs = fnamebase + '.g' + str(i) + 'i.csv',
                     dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.g' + str(i) + '.pdf',
                     dirlog='plots/')
    