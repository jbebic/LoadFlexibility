# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 10:43:24 2019

@author: jzb@achillearesearch.com
"""

from GroupAnalysis import DeltaLoads, PlotDeltaByDay, PlotDeltaSummary, GroupAnalysisMaster, SaveDeltaByMonth
from UtilityFunctions import ConvertFeather, FixDST, ExportLoadFiles, AnonymizeCIDs, CalculateBilling, CalculateGroups
from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from NormalizeLoads import ReviewLoads, NormalizeLoads,  NormalizeGroup
from PlotDurationCurves import PlotDurationCurves, PlotFamilyOfDurationCurves
from PlotHeatMaps import PlotHeatMaps, PlotHeatMapOfBilling
from PlotBilling import PlotBillingData

steps = ['All']
# steps = ['CalculateBilling']
# steps = ['CalculateGroups']
# steps = ['GroupAnalysisMaster']
# steps = ['SaveDeltaByMonth']

if True:
    fnamebase = 'waterSupplyandIrrigationSystems' # Name your input files here
    ratefile = 'SCE-TOU-PA-2-B.csv' # name of TOU rate profile
    ignoreCIDs_forGrouping = 'waterSupplyandIrrigationSystems.A.ignore.csv' # the ignoreCIDs for grouping (e.g. sites with solarPV, etc)
    # considerfname = 'largeOffices_CustomerI.csv'

#%% Calculate Billing
if ('CalculateBilling' in steps) or ('All' in steps):
    CalculateBilling(dirin='output3/', fnamein=fnamebase + '.A.csv', #'input/',
                    ignoreCIDs = ignoreCIDs_forGrouping, #considerCIDs ='purelyBundledCustomers.csv', #fnamebase + '.g1c.csv', 
                    dirrate = 'tou_data/', ratein = ratefile, 
                    dirout='output3/', fnameout=fnamebase + '.A.billing.csv',
                    dirlog='output3/', writeDataFile=True)


#%% Grouping
if ('CalculateGroups' in steps) or ('All' in steps): # by energy component of bill
    CalculateGroups(dirin='output3/', 
                    fnamein="summary." + fnamebase+'.A.billing.csv',
                    # highlightCIDs = 'largeOffices_CustomerI.csv',
                    # considerCIDs = 'groceryStores_CustomerM.csv', 
                    dirout='output3/', 
                    fnamebase=fnamebase,
                    dirlog='output3/',
                    ignore1515=False,
                    #energyPercentiles = [0, 5, 27.5, 50, 77.5, 95, 100], 
                    energyPercentiles = [0, 25, 50, 75, 100],
                    chargeType="Energy")

if ('GroupAnalysisMaster' in steps) or ('All' in steps): # performs normalizing groups, delta between groups, plot delta by day, & plot delta summary (all in one function)
    GroupAnalysisMaster(dirin_raw='output3/', #'input/',
                        dirout_data = 'output3/',
                        dirout_plots='plots3/', dirlog='output3/',
                        fnamebase=fnamebase,
                        fnamein=fnamebase+'.A.csv',
                        Ngroups=4, 
                        threshold=0.5,
                        demandUnit='Wh',
                        steps=['NormalizeGroup', 'DeltaLoads', 'PlotDeltaSummary','SaveDeltaSummary'])
                        #steps=['NormalizeGroup', 'DeltaLoads', 'PlotDeltaByDayWithDuration', 'PlotDeltaSummary', 'SaveDeltaSummary']) 

#if ('SaveDeltaByMonth' in steps) or ('All' in steps):
# This can be run after NormalizedGroup step in GroupAnalysisMaster   
#    SaveDeltaByMonth(dirin_raw='output3/', 
#                     dirout='output3/', 
#                     fnamebase=fnamebase,
#                     Ngroups=4,
#                     fnameout= fnamebase + '.DurationCurves.csv',
#                     dirlog='output3/')
