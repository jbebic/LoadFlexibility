# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 10:43:24 2019

@author: jzb@achillearesearch.com
"""

from GroupAnalysis import DeltaLoads, PlotDeltaByDay, PlotDeltaSummary, GroupAnalysisMaster, SaveDeltaByMonth
from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs, CalculateBilling, CalculateGroups, CalculateCorrelation
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from NormalizeLoads import ReviewLoads, NormalizeLoads,  NormalizeGroup
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from PlotHeatMaps import PlotHeatMaps, PlotHeatMapOfBilling
from PlotBilling import PlotBillingData

# steps = ['All']
steps = ['CalculateCorrelation']
# steps = ['CalculateGroups']
# steps = ['GroupAnalysisMaster']
# steps = ['SaveDeltaByMonth']

if True:
    fnamebase = 'GroceryStores' # Name your input files here
    ratefile = 'SCE-TOU-GS3-B.csv' # name of TOU rate profile
    ignoreCIDs_forGrouping = 'GroceryStores.A.ignore.csv' # the ignoreCIDs for grouping (e.g. sites with solarPV, etc)
    # considerfname = 'largeOffices_CustomerI.csv'

#%% CalcualteCorrelation
if ('CalculateCorrelation' in steps) or ('All' in steps):
    CalculateCorrelation(dirin='output2/', fnamein=fnamebase + '.A.csv', 
                         ignoreCIDs = ignoreCIDs_forGrouping, #considerCIDs ='purelyBundledCustomers.csv', #fnamebase + '.g1c.csv', 
                         dirprice  = 'tou_data/', pricein='20170101-20171231_CAISO_Average_Price.csv',
                         dirout='output2/', fnameout=fnamebase + '.A.billing.csv', 
                         dirlog='output2/', fnameLog='CalculateCorrelation.log')


#%% Grouping
if ('CalculateGroups' in steps) or ('All' in steps): # by energy component of bill
    CalculateGroups(dirin='output2/', 
                    fnamein="summary." + fnamebase+'.A.billing.csv',
                    # highlightCIDs = 'largeOffices_CustomerI.csv',
                    # considerCIDs = 'groceryStores_CustomerM.csv', 
                    dirout='output2/', 
                    fnamebase=fnamebase,
                    dirlog='output2/',
                    ignore1515=False,
                    #energyPercentiles = [0, 5, 27.5, 50, 77.5, 95, 100], 
                    energyPercentiles = [0, 25, 50, 75, 100],
                    chargeType="Energy")

if ('GroupAnalysisMaster' in steps) or ('All' in steps): # performs normalizing groups, delta between groups, plot delta by day, & plot delta summary (all in one function)
    GroupAnalysisMaster(dirin_raw='output2/', #'input/',
                        dirout_data = 'output2/',
                        dirout_plots='plots2/', dirlog='output2/',
                        fnamebase=fnamebase,
                        fnamein=fnamebase+'.A.csv',
                        Ngroups=4, 
                        threshold=0.5,
                        demandUnit='Wh',
                        steps=['NormalizeGroup', 'DeltaLoads', 'PlotDeltaSummary','SaveDeltaSummary'])
                        #steps=['NormalizeGroup', 'DeltaLoads', 'PlotDeltaByDayWithDuration', 'PlotDeltaSummary', 'SaveDeltaSummary']) 

#if ('SaveDeltaByMonth' in steps) or ('All' in steps):
# This can be run after NormalizedGroup step in GroupAnalysisMaster   
#    SaveDeltaByMonth(dirin_raw='output2/', 
#                     dirout='output2/', 
#                     fnamebase=fnamebase,
#                     Ngroups=4,
#                     fnameout= fnamebase + '.DurationCurves.csv',
#                     dirlog='output2/')
