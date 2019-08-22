# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 12:52:38 2019

@author: 200010679
"""

from NormalizeLoads import NormalizeLoads, NormalizeGroup # ReviewLoads

if True:
    fnamebase = 'synthetic2_old' # Name your input files here
    ratefile = 'SCE-TOU-GS3-B.csv' # name of TOU rate profile
    considerfname = 'groceryStores_CustomerI.csv'

if False:
    NormalizeLoads(dirin='input/', fnamein=fnamebase + '.A.csv', considerCIDs=considerfname, #ignoreCIDs=fnamebase + '.A.ignore.csv',
                   dirout='eduardo/', fnameout=fnamebase + '.A.normalized.csv',
                   dirlog='eduardo/')

if True:
    groupName='g1L'
    NormalizeGroup(dirin='input/', fnamein=fnamebase + '.A.csv',
                           considerCIDs='groceryStores_CustomerI' + '.' + fnamebase + "." + groupName + ".groupIDs.csv",
                           demandUnit='kW',
                           dirout='eduardo/', fnameout=fnamebase + "." + groupName +  '.normalized.csv',
                           dirlog='eduardo/')    
