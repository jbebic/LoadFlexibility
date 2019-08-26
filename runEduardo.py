# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 12:52:38 2019

@author: 200010679
"""

from GenerateSyntheticProfiles import GenerateSyntheticProfiles
from OutputsForMAPS import AggregateLoadsForMAPS

if True:
    fnamebase = 'synthetic2.A' # Name your input files here
    # ratefile = 'SCE-TOU-GS3-B.csv' # name of TOU rate profile
    # considerfname = 'groceryStores_CustomerI.csv'

if False:
    GenerateSyntheticProfiles(10, # number of profiles to create
                              '2017-01-01 00:00', '2017-12-31 23:45', # timedate range
                              IDlen=6, meMean=200, htllr=2.0, # ID length, monthly energy mean, high to low load ratio (peak day / low day)
                              dirout='input/', fnameout=fnamebase + '.csv', 
                              dirlog='input/', 
                              outfmt='ISO')
    
if True:
    groupName='all'
    AggregateLoadsForMAPS(dirin='input/', fnamein=fnamebase + '.csv',
                           # considerCIDs='groceryStores_CustomerI' + '.' + fnamebase + "." + groupName + ".groupIDs.csv",
                           demandUnit='Wh',
                           dirout='eduardo/', fnameout=fnamebase + "." + groupName +  '.aggregate.csv',
                           dirlog='eduardo/', 
                           normalizeBy="all")