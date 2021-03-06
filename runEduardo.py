# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 12:52:38 2019

@author: 200010679
"""

from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from OutputsForMAPS import AggregateLoadsForMAPS
from PlotHeatMaps import PlotHeatMaps

if True:
    # fnamebase = 'synthetic2' # Name your input files here
    fnamebase = 'largeOfficesAll' # Name your input files here
    # ratefile = 'SCE-TOU-GS3-B.csv' # name of TOU rate profile
    # considerfname = 'groceryStores_CustomerI.csv'

if False:
    GenerateSyntheticProfiles(10, # number of profiles to create
                              '2017-01-01 00:00', '2017-12-31 23:45', # timedate range
                              IDlen=6, meMean=200, htllr=2.0, # ID length, monthly energy mean, high to low load ratio (peak day / low day)
                              dirout='input/', fnameout=fnamebase + '.csv', 
                              dirlog='input/', 
                              outfmt='ISO')
    
if False:
    groupName='all'
    AggregateLoadsForMAPS(dirin='input/', fnamein=fnamebase + '.A.csv',
                           # considerCIDs='groceryStores_CustomerI' + '.' + fnamebase + "." + groupName + ".groupIDs.csv",
                           demandUnit='Wh',
                           dirout='eduardo/', fnameout=fnamebase + "." + groupName +  '.aggregate.csv',
                           dirlog='eduardo/', 
                           normalizeBy="all")

if False:
    for groupName in ['g1L', 'g1o']:
        AggregateLoadsForMAPS(dirin='input/', fnamein=fnamebase + '.A.csv',
                              dirconsider='output/',
                              considerCIDs = groupName +  '.' + fnamebase + '.Energy.A.groups.csv',
                              demandUnit='W',
                              dirout='eduardo/', fnameout=fnamebase + "." + groupName +  '.aggregate.csv',
                              dirlog='eduardo/', 
                              normalizeBy="all")

if False:
    ConsiderList = ['g1L.synthetic2.Energy.A.groups.csv', 
                    'g1o.synthetic2.Energy.A.groups.csv',
                    'g2L.synthetic2.Energy.A.groups.csv', 
                    'g2o.synthetic2.Energy.A.groups.csv',
                    'g3L.synthetic2.Energy.A.groups.csv', 
                    'g3o.synthetic2.Energy.A.groups.csv', 
                    'g4L.synthetic2.Energy.A.groups.csv', 
                    'g4o.synthetic2.Energy.A.groups.csv',
                    '']

    AggregateLoadsForMAPS(dirin='private/', fnamein=fnamebase + '.A.csv',
                          dirconsider='output/',
                          considerCIDs = ConsiderList,
                          demandUnit='kWh',
                          dirout='eduardo/', fnameout= 'aggregate.csv',
                          dirlog='eduardo/', 
                          normalizeBy="all")

if False:
    ConsiderList = ['g1L.largeOfficesAll.Energy.A.groups.csv',
                    'g1o.largeOfficesAll.Energy.A.groups.csv',
                    'g2L.largeOfficesAll.Energy.A.groups.csv',
                    'g2o.largeOfficesAll.Energy.A.groups.csv',
                    'g3L.largeOfficesAll.Energy.A.groups.csv',
                    'g3o.largeOfficesAll.Energy.A.groups.csv',
                    'g4L.largeOfficesAll.Energy.A.groups.csv',
                    'g4o.largeOfficesAll.Energy.A.groups.csv',
                    '']

    AggregateLoadsForMAPS(dirin='input/', fnamein=fnamebase + '.A.csv', ignoreCIDs='largeOfficesAll.A.ignore.csv',
                          dirconsider='output/',
                          considerCIDs = ConsiderList,
                          demandUnit='kWh',
                          dirout='eduardo/', fnameout= 'aggregate.csv',
                          dirlog='eduardo/', 
                          normalizeBy="all")

if False:
   PlotHeatMaps(dirin='eduardo/', fnamein='g1L.' + fnamebase + '.Energy.A.groups.csv.aggregate.csv',
                dirout='eduardo/', fnameout='g1L.' + fnamebase + '.aggregate.HeatMaps.pdf',
                dirlog='eduardo/')

if True:
    for groupName in ['g1L', 'g1o', 'g2L', 'g2o', 'g3L', 'g3o', 'g4L', 'g4o']:
        PlotHeatMaps(dirin='eduardo/', fnamein=groupName + '.' + fnamebase + '.Energy.A.groups.csv.aggregate.csv',
                     dirout='eduardo/', fnameout=groupName  + '.' + fnamebase + '.aggregate.HeatMaps.pdf',
                     dirlog='eduardo/')

if False:
   PlotHeatMaps(dirin='eduardo/', fnamein='all.' + fnamebase + '.aggregate.csv',
                dirout='eduardo/', fnameout='all.' + fnamebase + '.aggregate.HeatMaps.pdf',
                dirlog='eduardo/')
