# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""

from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs, CalculateBilling
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from NormalizeLoads import ReviewLoads, NormalizeLoads
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from PlotHeatMaps import PlotHeatMaps
from PlotBilling import PlotBillingData

fnamebase = 'synthetic20'

#%% Create profiles
if False:
    GenerateSyntheticProfiles(20, # number of profiles to create
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
                   tzinput = 'America/Los_Angeles',
                   OutputFormat = 'ISO')

#%% Review load profiles
if False:
    ReviewLoads(dirin='testdata/', fnamein=fnamebase+'.csv',
                   dirout='testdata/', fnameout=fnamebase+'.summary.csv',
                   dirlog='testdata/',
                   InputFormat = 'SCE')

#%% Calculate Billing
if True:
    CalculateBilling(dirin='testdata/', fnamein=fnamebase+'.normalized.csv', # '.csv',
                     dirout='testdata/', fnameout=fnamebase+'.billing.csv',
                     writeDataFile = True,
                     dirlog='testdata/')

#%% Plot Billing
if True:
    PlotBillingData(dirin='testdata/', fnamein=fnamebase+'.billing.csv', # '.csv',
                     dirout='testdata/', fnameout=fnamebase+'.billing.pdf',
                     dirlog='testdata/')

#%% Normalize profiles
if False:
    NormalizeLoads(dirin='testdata/', fnamein=fnamebase+'.csv', 
                   dirout='testdata/', fnameout=fnamebase+'.normalized.csv',
                   dirlog='testdata/', 
                   InputFormat='SCE')

#%% Normalize profiles
if False:
    ExportLoadFiles(dirin='testdata/', fnamein=fnamebase+'.csv', explist=fnamebase+'.export.csv',
                   dirout='testdata/', 
                   dirlog='testdata/')

    
#%% Plot duration curves
if False:
    PlotDurationCurves(dirin='testdata/', fnamein=fnamebase+'.normalized.csv',
                       dirout='testdata/', fnameout=fnamebase+'.DurationCurves.pdf',
                       dirlog='testdata/')
    
    PlotFamilyOfDurationCurves(dirin='testdata/', fnamein=fnamebase+'.normalized.csv',
                               dirout='testdata/', fnameout=fnamebase+'.FamilyOfDurationCurves.pdf',
                               dirlog='testdata/')

#%% Plot heatmaps
if False:    
    PlotHeatMaps(dirin='testdata/', fnamein=fnamebase+'.normalized.csv', considerCIDs=fnamebase+'.g1c.csv', ignoreCIDs = fnamebase+'.g1i.csv',
                 dirout='testdata/', fnameout=fnamebase+'.HeatMaps.g1.pdf',
                 dirlog='testdata/')
