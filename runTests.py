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
    ConvertFeather(dirin='testdata/', fnamein='GroceryTOU_GS3B_Q1O15_152017.feather',
                   dirout='testdata/', fnameout='GroceryTOU_GS3B_Q1O15_152017.csv',
                   dirlog='testdata/',
                   renameDict={'DatePeriod':'datetimestr', 'Usage':'Demand'},
                   writeOutput = True)

#%% Fix DST
if False:
    FixDST(dirin='testdata/', fnamein='two_grocers_DST_test.csv',
                   dirout='testdata/', fnameout='two_grocers.csv',
                   dirlog='testdata/',
                   tzinput = 'America/Los_Angeles',
                   OutputFormat = 'SCE')

#%% Review load profiles
if False:
    ReviewLoads(dirin='testdata/', fnamein='two_grocers_modified.csv',
                   dirout='testdata/', fnameout='two_grocers_modified.summary.csv',
                   dirlog='testdata/')

#%% Normalize profiles
if False:
    NormalizeLoads(dirin='testdata/', fnamein='two_grocers_modified.csv', ignorein='two_grocers.ignore.csv',
                   dirout='testdata/', fnameout='two_grocers_modified.normalized.csv',
                   dirlog='testdata/')

#%% Normalize profiles
if True:
    ExportLoadFiles(dirin='testdata/', fnamein='two_grocers_modified.csv', explist='two_grocers.export.csv',
                   dirout='testdata/', 
                   dirlog='testdata/')

    
#%% Plot duration curves
if False:
    PlotDurationCurves(dirin='testdata/', fnamein='two_grocers_modified.normalized.csv',
                       dirout='testdata/', fnameout='DurationCurves.two_grocers_modified.pdf',
                       dirlog='testdata/')
    
    PlotFamilyOfDurationCurves(dirin='testdata/', fnamein='two_grocers_modified.normalized.csv',
                               dirout='testdata/', fnameout='FamilyOfDurationCurves.two_grocers_modified.pdf',
                               dirlog='testdata/')

#%% Plot heatmaps
if False:    
    PlotHeatMaps(dirin='testdata/', fnamein='two_grocers_modified.normalized.csv',
                 dirout='testdata/', fnameout='HeatMaps.two_grocers_modified.pdf',
                 dirlog='testdata/')
