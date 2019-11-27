# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 10:42:46 2019

@author: jzb@achillearesearch.com
"""


# from GroupAnalysis import DeltaLoads, PlotDeltaByDay, PlotDeltaSummary, GroupAnalysisMaster, SaveDeltaByMonth
# from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs, CalculateBilling, CalculateGroups
# from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from NormalizeLoads import ConvertTo1515 # ReviewLoads, NormalizeLoads,  NormalizeGroup
# from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
# from PlotHeatMaps import PlotHeatMaps, PlotHeatMapOfBilling
# from PlotBilling import PlotBillingData


if True:
    fnamebase = 'largeOfficesAll' # Name your input files here

if False:
    ConvertTo1515(dirin='input/', fnamein = fnamebase + '.A.csv',
                  dirout='input/', fnameout= fnamebase + '.A.1515.pv.csv',
                  saveSummary = True, fnamesummary = fnamebase + '.A.summary.pv.csv',
                  considerCIDs = fnamebase + '.A.pv.csv',
                  dirlog='input/')

if True:
    ConvertTo1515(dirin='input/', fnamein = fnamebase + '.A.csv',
                  dirout='input/', fnameout= fnamebase + '.A.1515.all.csv',
                  saveSummary = True, fnamesummary = fnamebase + '.A.summary.all.csv',
                  ignoreCIDs = fnamebase + '.A.ignore.csv',
                  dirlog='input/')
