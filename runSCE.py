# -*- coding: utf-8 -*-
"""
Created on Mon May 28 09:28:36 2018

@author: jbebic
"""

from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from NormalizeLoads import ReviewLoads, NormalizeLoads
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from PlotHeatMaps import PlotHeatMaps

fnamebase = 'synthetic2'

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
                  dirout='private/', fnameout=fnamebase + '.A.csv', fnameKeys=fnamebase + '.lookup.csv',
                  dirlog='private/', fnameLog='AnonymizeCIDs.log',
                  IDlen=6)

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
if True:
    ReviewLoads(dirin='input/', fnamein=fnamebase + '.A.csv',
                   dirout='input/', fnameout=fnamebase+'A.summary.csv',
                   dirlog='input/')

#%% Manual steps:
#  1) Open  


#%% Normalize profiles
if False:
    NormalizeLoads(dirin='input/', fnamein=fnamebase + '.A.csv', ignorein=fnamebase + '.A.ignore.csv',
                   dirout='output/', fnameout=fnamebase + '.A.normalized.csv',
                   dirlog='output/')

#%% Normalize profiles
if False:
    ExportLoadFiles(dirin='testdata/', fnamein='two_grocers_modified.csv', explist='two_grocers.export.csv',
                   dirout='testdata/', 
                   dirlog='testdata/')

    
#%% Plot duration curves
if False:
    PlotDurationCurves(dirin='output/', fnamein=fnamebase + '.A.normalized.csv',
                       dirout='plots/', fnameout=fnamebase + '.A.duration.pdf',
                       dirlog='plots/')
    
    PlotFamilyOfDurationCurves(dirin='output/', fnamein=fnamebase + '.A.normalized.csv',
                               dirout='plots/', fnameout=fnamebase + '.A.FamilyOfDurationCurves.pdf',
                               dirlog='plots/')

#%% Plot heatmaps
if False:    
    PlotHeatMaps(dirin='output/', fnamein=fnamebase + '.A.normalized.csv',
                 dirout='plots/', fnameout=fnamebase + '.A.HeatMaps.pdf',
                 dirlog='plots/')
