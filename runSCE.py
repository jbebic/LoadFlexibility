# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""

import numpy as np

from GroupAnalysis import PlotGroup, DeltaLoads, PlotDelta
from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs, SplitToGroups, CalculateBilling, CalculateGroups
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from NormalizeLoads import ReviewLoads, NormalizeLoads,  NormalizeGroup
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from PlotHeatMaps import PlotHeatMaps
from PlotBilling import PlotBillingData

fnamebase = 'synthetic2'
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
if True:
    AnonymizeCIDs(dirin='private/', fnamein=fnamebase + '.csv', 
                  dirout='private/', fnameout=fnamebase + '.A.csv', fnameKeys=fnamebase + '.lookup.csv',
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
    CalculateBilling(dirin='input/', fnamein=fnamebase + '.A.csv', writeDataFile=True, considerCIDs ='purelyBundledCustomers.csv', #fnamebase + '.g1c.csv', 
                   dirout='output/', fnameout=fnamebase + '.A.billing.csv',
                   dirlog='output/')
#%% Plot Billing
if False:
    PlotBillingData(dirin='output/', fnamein=fnamebase + '.A.billing.csv', considerCIDs = 'purelyBundledCustomers.csv',#fnamebase + '.g1c.csv',
                   dirout='plots/', fnameout=fnamebase + '.A.billing.pdf',
                   dirlog='plots/')
#%% Grouping
if False:
    CalculateGroups(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', #considerCIDs = fnamebase + '.g1c.csv',
                   plotGroups = True, chargeType='Total', energyPercentiles = [10, 30, 50, 70, 90],
                   dirout='plots/', fnameout=fnamebase + '.Total.A.groups.csv',
                   dirlog='plots/')
    CalculateGroups(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', #considerCIDs = fnamebase + '.g1c.csv',
                   plotGroups = True, chargeType='Energy', energyPercentiles = [10, 30, 50, 70, 90],
                   dirout='plots/', fnameout=fnamebase + '.Energy.A.groups.csv',
                   dirlog='plots/')   
    CalculateGroups(dirin='output/', fnamein= 'summary.' + fnamebase + '.A.billing.csv', #considerCIDs = fnamebase + '.g1c.csv',
                   plotGroups = True, chargeType='Demand', energyPercentiles = [10, 30, 50, 70, 90],
                   dirout='plots/', fnameout=fnamebase + '.Demand.A.groups.csv',
                   dirlog='plots/')   
#%% Normalize profiles
if False:
    NormalizeLoads(dirin='input/', fnamein=fnamebase + '.A.csv', ignoreCIDs=fnamebase + '.A.ignore.csv',
                   dirout='output/', fnameout=fnamebase + '.A.normalized.csv',
                   dirlog='output/')
#%% Normalize profiles
if False:
    for groupName in [ 'g1L' , 'g1o', 'g2L', 'g2o', 'g3L', 'g3o', 'g4L', 'g4o'] :
        NormalizeGroup(dirin='input/', fnamein=fnamebase + '.A.csv', considerCIDs = groupName+ '.synthetic2.Energy.A.groups.csv',
                   dirout='output/', fnameout=fnamebase + '.' + groupName + '.energyOnly.A.normalized.csv',
                   groupName = groupName,
                   dirlog='output/')
if False:
    for n in [1,2,3,4]:
        
        groupL = 'g' + str(n) + 'L'
        groupo = 'g' + str(n) + 'o'
        fnameout  = fnamebase+".delta." + groupL + "." + groupo + ".csv"
    
        DeltaLoads(dirin='output/', # outputs
                   fnameinL=fnamebase + '.' + groupL + '.A.normalized.csv',
                   fnameino=fnamebase + '.' + groupo + '.A.normalized.csv',
                   dirout='output/', # outputs 
                   fnameout=fnameout,
                   dirlog='output/' # outputs
                   ) 
        
        PlotDelta(dirin='output/',  # outputs
                  fnamein=fnameout, 
                  dirout='output/', # plots
                  fnameout=fnameout.replace('.csv', '.pdf'),
                  dirlog='output/' # outputs
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
    PlotDurationCurves(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', ignoreCIDs = fnamebase + '.A.ignore.csv', #considerCIDs = fnamebase + '.g1c.csv',
                       byMonthFlag=True,
                       dirout='plots/', fnameout=fnamebase + '.A.duration.pdf',
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
    
if False:    
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', considerCIDs = 'Group1.csv', #ignoreCIDs = 'ignore.G1.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.G1.pdf',
                 dirlog='plots/')
    
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', considerCIDs = 'Group2.csv', #ignoreCIDs = 'ignore.G1.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.G2.pdf',
                 dirlog='plots/')
    
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', considerCIDs = 'Group3.csv', #ignoreCIDs = 'ignore.G1.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.G3.pdf',
                 dirlog='plots/')
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', considerCIDs = 'Group4.csv', #ignoreCIDs = 'ignore.G1.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.G4.pdf',
                 dirlog='plots/')
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', considerCIDs = 'Group5.csv', #ignoreCIDs = 'ignore.G1.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.G5.pdf',
                 dirlog='plots/')
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', considerCIDs = 'Group6.csv', #ignoreCIDs = 'ignore.G1.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.G6.pdf',
                 dirlog='plots/')
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', considerCIDs = 'Group7.csv', #ignoreCIDs = 'ignore.G1.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.G7.pdf',
                 dirlog='plots/')
    
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', considerCIDs = 'Group8.csv', #ignoreCIDs = 'ignore.G1.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.G8.pdf',
                 dirlog='plots/')
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', considerCIDs = 'Group9.csv', #ignoreCIDs = 'ignore.G1.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.G9.pdf',
                 dirlog='plots/')
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv', considerCIDs = 'Group10.csv', #ignoreCIDs = 'ignore.G1.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.G10.pdf',
                 dirlog='plots/')


