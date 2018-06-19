# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 14:24:41 2018

@author: apb38
"""
import pandas as pd
import os

os.chdir('C:/Users/apb38/Desktop/DR/datasets/enernoc-comm/enernoc-comm/enernoc-comm/csv')
df1=pd.read_csv('site_281.csv')
df1.columns=['Index','datetimestr','Demand','CustomerID' ]
del df1['Index']

dstr = df1['datetimestr'].str.split('').str[0]
# print(dstr.head())
hstr = df1['datetimestr'].str.split(':').str[1]
# print(tstr.head())
mstr = df1['datetimestr'].str.split(':').str[2]
# sstr = df1['datetimestr'].str.split(':').str[3]
temp = dstr + ' ' + hstr + ':' + mstr
df1['datetime'] = pd.to_datetime(temp, format='%d%b%Y %H:%M')

uniqueCIDs = df1.index.get_level_values('CustomerID').unique().values