# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""

from UtilityFunctions import ConvertFeather
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
if True:
    ConvertFeather(dirin='input/', fnamein='GroceryTOU_GS3B_Q1O15_152017.feather',
                   dirout='output/', fnameout='GroceryTOU_GS3B_Q1O15_152017.csv',
                   dirlog='output/',
                   renameDict={'DatePeriod':'datetimestr', 'Usage':'Demand'},
                   writeOutput = True)

#%% Review load profiles
if False:
    ReviewLoads(dirin='input/', fnamein='synthetic2.csv',
                   dirout='output/', fnameout='synthetic2.summary.csv',
                   dirlog='output/')

#%% Normalize profiles
if False:
    NormalizeLoads(dirin='input/', fnamein='synthetic2.csv',
                   dirout='output/', fnameout='synthetic2.normalized.csv',
                   dirlog='output/')
    
#%% Plot duration curves
if False:
    PlotDurationCurves(dirin='output/', fnamein='synthetic2.normalized.csv',
                       dirout='plots/', fnameout='DurationCurves.synthetic2.pdf',
                       dirlog='output/')
    
    PlotFamilyOfDurationCurves(dirin='output/', fnamein='synthetic2.normalized.csv',
                               dirout='plots/', fnameout='FamilyOfDurationCurves.synthetic2.pdf',
                               dirlog='output/')

#%% Plot heatmaps
if False:    
    PlotHeatMaps(dirin='output/', fnamein='synthetic2.normalized.csv',
                 dirout='plots/', fnameout='HeatMaps.synthetic2.pdf',
                 dirlog='output/')
