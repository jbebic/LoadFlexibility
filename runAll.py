# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""

from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from NormalizeLoads import ReviewLoads, NormalizeLoads
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from PlotHeatMaps import PlotHeatMaps

#%% Create profiles
if False:
    GenerateSyntheticProfiles(10, # number of profiles to create
                              '2017-01-01 00:00', '2017-12-31 23:45', # date range
                              IDlen=6, meMean=200, htllr=2.0, # ID length, monthly energy mean, high to low load ratio (peak day / low day)
                              dirout='input/', fnameout='synthetic2.csv', 
                              dirlog='output/')

#%% Convert Feather file
if False:
    ConvertFeather(dirin='input/', fnamein='GroceryTOU_GS3B_Q1O15_152017.feather',
                   dirout='output/', fnameout='GroceryTOU_GS3B_Q1O15_152017.csv',
                   dirlog='output/',
                   renameDict={'DatePeriod':'datetimestr', 'Usage':'Demand'},
                   writeOutput = True)
    
 #%% Fix the Datlight savings time   
if False:
    FixDST(dirin='input/', fnamein='synthetic2.csv', 
                   dirout='output/', fnameout='synthetic2.csv', 
                   dirlog='output/', fnameLog='FixDST.log',
                   tzinput = 'America/Los_Angeles',
                   OutputFormat = 'SCE')
if False:
    FixDST(dirin='input/', fnamein='two_grocers_DST_test.csv', 
                   dirout='output/', fnameout='two_grocers_test.csv', 
                   dirlog='output/', fnameLog='FixDST.log',
                   tzinput = 'America/Los_Angeles',
                   OutputFormat = 'SCE')

#%% Review load profiles
if False:
    ReviewLoads(dirin='output/', fnamein='synthetic2.csv',
                   dirout='output/', fnameout='synthetic2.summary.csv',
                   dirlog='output/')
#%% Export the defected
if False:   
    ExportLoadFiles(dirin='output/', fnamein='synthetic2.csv', explist='ExportCIDs.csv',
                   dirout='output/', # fnameout derived from customer IDs
                   dirlog='output/')

if True:   
    ExportLoadFiles(dirin='input/', fnamein='synthetic2.csv', explist='ExportCIDs.csv',
                   dirout='input/', # fnameout derived from customer IDs
                   dirlog='input/')
#%% Normalize profiles
if False:
    NormalizeLoads(dirin='output/', fnamein='synthetic2.csv', ignorein='synthetic2.ignore.csv',
                   dirout='output/', fnameout='synthetic2.normalized.csv',
                   dirlog='output/')
if False:
    NormalizeLoads(dirin='output/', fnamein='21861.csv', ignorein='ignore.none.csv',
                   dirout='output/', fnameout='21861.normalized.csv',
                   dirlog='output/')
#%% Plot duration curves
if False:
    PlotDurationCurves(dirin='output/', fnamein='two_grocers_test.csv',
                       dirout='plots/', fnameout='DurationCurves.synthetic2.pdf',
                       dirlog='output/')
    
    PlotFamilyOfDurationCurves(dirin='output/', fnamein='two_grocers_test.csv',
                               dirout='plots/', fnameout='FamilyOfDurationCurves.synthetic2.pdf',
                               dirlog='output/')

#%% Plot heatmaps
if False:    
    PlotHeatMaps(dirin='output/', fnamein='two_grocers_test.csv',
                 dirout='plots/', fnameout='HeatMaps.synthetic2.pdf',
                 dirlog='output/')
