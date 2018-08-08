# -*- coding: utf-8 -*-
"""
Created on Tues Aug 07 16:40:06 2018

@author: Anh Bui

Load smoothing algorithm
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
import sys
import datetime as dt
from pytz import timezone
from functools import reduce
import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='output/loadreduction_281.log',level=logging.DEBUG)
with open('output/loadreduction_281.log', 'w'):
    pass
pd.options.mode.chained_assignment = None  # default='warn' 
%matplotlib inline

#Set user input variables
#Required directory structure
#  input data directory = workingDir/input/load_smoothing_algorithm/
#  output data directory = workingDir/output/load_smoothing_algorithm/

workingDir = os.path.dirname('C:/Users/apb38/Documents/GitHub/LoadFlexibility/') #set your working directory
c = 2 #number of customerid
k = 300001 #number of smoothing iteration
g = 10000 #iteration number at which data will be logged into csv file
n = 5 #number of 15-min intervals around the peak (plus the peak) to which the shaved kW is re-distributed
DA_Customer = 0 #Used for calculating bill. 0 = non-direct access customer, 1 = direct access customer

#if using two-grocers Enernoc modified file EnerNoc data ('SCE-format-data-two-grocers.csv') use this code other wise comment out this chunk of code
#change the file to GE-SCE format datetime
rng = pd.date_range(pd.Timestamp("2012-01-01 00:00"),periods=35136, freq='15Min')
rng = rng.strftime('%d%b%Y:%H:%M') #same datetimestr format as in SCE bill
rng = rng.tolist()
datetime = list(map(str.upper, rng))
datetime = pd.DataFrame(datetime)
GE_date = pd.concat([datetime]*d, ignore_index=True) #amount of CustomerID
GE_date.columns=['datetimestr']
Enernoc_data= pd.read_csv(os.path.join(workingDir, 'testdata/SCE-format-data-two-grocers.csv'))
del Enernoc_data ['Unnamed: 0']
del Enernoc_data ['DateTime']
Enernoc_data.rename(columns ={'Usage_KWH':'Base Usage kWh'},inplace =True)
consumption_raw_data = pd.merge(GE_date,Enernoc_data,left_index=True, right_index = True)
consumption_raw_data.to_csv(os.path.join(workingDir, 'output/load-smoothing-algorithm/GE_UTconsumption.csv'))

# Read in input data located in workingDir/input/load-smoothing-algorithm/bill_calc
# These are the files uploaded by SCE in SCE/Input Data for Calculate bill components/
# energy charges
energy_charges_input = pd.read_csv(os.path.join(workingDir,'input/load-smoothing-algorithm/bill_calc/TOU_GS3_B_Energy.csv'))
# energy charges for DA customers
energy_charges_input_DA = pd.read_csv(os.path.join(workingDir,'input/load-smoothing-algorithm/bill_calc/TOU_GS3_B_Energy_DA.csv'))
# demand charges
demand_charges_input = pd.read_csv(os.path.join(workingDir,'input/load-smoothing-algorithm/bill_calc/TOU_GS3_B_Demand.csv'))
# demand charges for DA customers
demand_charges_input_DA = pd.read_csv(os.path.join(workingDir,'input/load-smoothing-algorithm/bill_calc/TOU_GS3_B_Demand_DA.csv'))
# UT hourly time periods
UT_hourly_time_periods_input = pd.read_csv(os.path.join(workingDir,'input/load-smoothing-algorithm/bill_calc/TOU_GS3_B_Seasonal_TimePeriods_DST.csv'))
# change column names
energy_charges_input = energy_charges_input.rename(columns={'TOU-GS3-B':'TOU Energy Charges Rate ($/kWh)','Number':'Rate Periods'})
demand_charges_input = demand_charges_input.rename(columns={'TOU-GS3-B':'TOU Demand Charges Rate ($/kW)','Number':'Rate Periods'})
UT_hourly_time_periods_input = UT_hourly_time_periods_input.rename(columns={'TOU-GS3-B':'Rate Periods'})

# choose correct demand and energy charges based on whether customer is a DA customer or not
if DA_Customer == 0:
    demand_charges = demand_charges_input
    energy_charges = energy_charges_input
    DA_CRS_DWR_bond = 0
else:
    demand_charges = demand_charges_input_DA
    energy_charges = energy_charges_input_DA
    DA_CRS_DWR_bond = 0.00549

#####################
#define functions
def monthlyOnPeakMaxDemand(df):
    # filtering out summer on-peak periods
    dfSummerOnPeakDemand = df[df['Rate Periods'] == 1] #$20.01/KW   
    # calculating maximum on-peak demand for each month
    mthOPD_Summer = dfSummerOnPeakDemand.groupby(["month"]).apply(lambda x: x.sort_values(["Base Usage kWh"], ascending = False)) #sort values
    mthOPD_Summer = mthOPD_Summer.reset_index(level=1).groupby('month').first() #choose the highest value each month
    # calculating max on-peak demand charge
    mthOPD_Summer['TOU Demand Charges ($)'] = mthOPD_Summer['TOU Demand Charges Rate ($/kW)'] * mthOPD_Summer ['Usage kW'] 
    mthOPD_Summer['TOU Demand Charges ($)'] = mthOPD_Summer['TOU Demand Charges ($)'].round(2)
    return mthOPD_Summer

def monthlyMidPeakMaxDemand(df):
    # filtering out Summer and Winter mid-peak periods
    dfSummerMidPeakDemand = df[df['Rate Periods'] == 2] #$3.95/KW
    dfWinterMidPeakDemand = df[df['Rate Periods'] == 5] #$0.00/KW
    # calculating maximum on peak demand for each month
    mthMidD_Summer = dfSummerMidPeakDemand.groupby(["month"]).apply(lambda x: x.sort_values(["Base Usage kWh"], ascending = False)) #sort values
    mthMidD_Summer = mthMidD_Summer.reset_index(level=1).groupby('month').first() #choose the highest value each month
    mthMidD_Summer['TOU Demand Charges ($)'] = mthMidD_Summer['TOU Demand Charges Rate ($/kW)'] *  mthMidD_Summer ['Usage kW']
    mthMidD_Winter = dfWinterMidPeakDemand.groupby(["month"]).apply(lambda x: x.sort_values(["Base Usage kWh"], ascending = False)) #sort values
    mthMidD_Winter = mthMidD_Winter.reset_index(level=1).groupby('month').first()
    mthMidD_Winter['TOU Demand Charges ($)'] = mthMidD_Winter['TOU Demand Charges Rate ($/kW)'] * mthMidD_Winter['Usage kW'] 
    # concatenate summer and winter off peak
    mthMidD = pd.concat([mthMidD_Summer, mthMidD_Winter])
    mthMidD['TOU Demand Charges ($)'] = mthMidD['TOU Demand Charges ($)'].round(2)
    return mthMidD

def monthlyOffPeakMaxDemand(df): #it is $0.00 on off - peak demand bill for non-DA customer
    # filtering out Summer and Winter off-peak periods
    dfSummerOffPeakDemand = df[df['Rate Periods'] == 3] #$0.00/KW
    dfWinterOffPeakDemand = df[df['Rate Periods'] == 6] #$0.00/KW
    # calculating maximum on peak demand for each month
    mthOffD_Summer = dfSummerOffPeakDemand.groupby(["month"]).apply(lambda x: x.sort_values(["Base Usage kWh"], ascending = False)) #sort values
    mthOffD_Summer = mthOffD_Summer.reset_index(level=1).groupby('month').first() #choose the highest value each month
    mthOffD_Summer['TOU Demand Charges ($)'] = mthOffD_Summer['TOU Demand Charges Rate ($/kW)'] *  mthOffD_Summer ['Usage kW']
    mthOffD_Winter = dfWinterOffPeakDemand.groupby(["month"]).apply(lambda x: x.sort_values(["Base Usage kWh"], ascending = False)) #sort values
    mthOffD_Winter = mthOffD_Winter.reset_index(level=1).groupby('month').first()
    mthOffD_Winter['TOU Demand Charges ($)'] = mthOffD_Winter['TOU Demand Charges Rate ($/kW)'] * mthOffD_Winter['Usage kW']
    # concatenate summer and winter off peak
    mthOffD = pd.concat([mthOffD_Summer, mthOffD_Winter])
    mthOffD['TOU Demand Charges ($)'] = mthOffD['TOU Demand Charges ($)'].round(2)
    return mthOffD

def DemandFacilityCharge(df):
    # define demand facility charge rate
    DemandFacilityCharge = 17.81    
    # calculate monthly demand
    mthFacilityDemand = df.groupby(["month"]).apply(lambda x: x.sort_values(["Base Usage kWh"], ascending = False)) #sort values
    mthFacilityDemand = mthFacilityDemand.reset_index(level=1).groupby('month').first() 
    mthFacilityDemand['Facility_Demand Charges ($)'] = DemandFacilityCharge * mthFacilityDemand['Usage kW'] 
    mthFacilityDemand['Facility_Demand Charges ($)'] = mthFacilityDemand['Facility_Demand Charges ($)'].round(2)
    return mthFacilityDemand

def monthlyOnPeakEnergy(df):
    # filtering out summer on-peak periods
    dfSummerEnergyOnPeak = df[df['Rate Periods'] == 1].copy()
    # calculating on-peak energy for each month
    dfSummerEnergyOnPeak['TOU Energy Charges ($)'] = dfSummerEnergyOnPeak['TOU Energy Charges Rate ($/kWh)'] * dfSummerEnergyOnPeak['Base Usage kWh']
    mthOPE_Summer = dfSummerEnergyOnPeak.groupby(['CustomerID','month','Rate Periods'], as_index = False)['Base Usage kWh','TOU Energy Charges ($)'].sum()
    mthOPE_Summer['TOU Energy Charges ($)'] = mthOPE_Summer['TOU Energy Charges ($)'].round(2)
    mthOPE_Summer = mthOPE_Summer.groupby(['month','CustomerID'],as_index = False)['TOU Energy Charges ($)'].sum()
    return mthOPE_Summer

def monthlyOffPeakEnergy(df):
    # filtering out Summer off-peak periods
    dfSummerEnergyOffPeak = df[df['Rate Periods'] == 3].copy()
    # calculating Summer off-peak energy for each month
    dfSummerEnergyOffPeak['TOU Energy Charges ($)'] = dfSummerEnergyOffPeak['TOU Energy Charges Rate ($/kWh)'] * dfSummerEnergyOffPeak['Base Usage kWh']
    mthOffE_Summer = dfSummerEnergyOffPeak.groupby(['CustomerID','month','Rate Periods'], as_index = False)['Base Usage kWh','TOU Energy Charges ($)'].sum()
    # filtering out winter off-peak periods
    dfWinterEnergyOffPeak = df[df['Rate Periods'] == 6].copy()
    # calculating Winter off-peak energy for each month
    dfWinterEnergyOffPeak['TOU Energy Charges ($)'] = dfWinterEnergyOffPeak['TOU Energy Charges Rate ($/kWh)'] * dfWinterEnergyOffPeak['Base Usage kWh']
    mthOffE_Winter = dfWinterEnergyOffPeak.groupby(['CustomerID','month','Rate Periods'], as_index = False)['Base Usage kWh','TOU Energy Charges ($)'].sum()
    # concatenate Summer and Winter off-peak energy
    mthOffE = pd.concat([mthOffE_Summer, mthOffE_Winter])
    mthOffE['TOU Energy Charges ($)'] = mthOffE['TOU Energy Charges ($)'].round(2)
    #sort by Month, and rename the columns
    mthOffE = mthOffE.groupby(['month','CustomerID'],as_index = False)['TOU Energy Charges ($)'].sum()
    return mthOffE

def monthlyMidPeakEnergy(df):
    # filtering out Summer Mid-peak periods
    dfSummerEnergyMidPeak = df[df['Rate Periods'] == 2].copy()
    # calculating Summer Mid-peak energy for each month
    dfSummerEnergyMidPeak['TOU Energy Charges ($)'] = dfSummerEnergyMidPeak['TOU Energy Charges Rate ($/kWh)'] * dfSummerEnergyMidPeak['Base Usage kWh']
    mthMidE_Summer = dfSummerEnergyMidPeak.groupby(['CustomerID','month','Rate Periods'], as_index = False)['Base Usage kWh','TOU Energy Charges ($)'].sum()
    # filtering out Winter Mid-peak periods
    dfWinterEnergyMidPeak = df[df['Rate Periods'] == 5].copy()
    # calculating Winter Mid-peak energy for each month
    dfWinterEnergyMidPeak['TOU Energy Charges ($)'] = dfWinterEnergyMidPeak['TOU Energy Charges Rate ($/kWh)'] * dfWinterEnergyMidPeak['Base Usage kWh']
    mthMidE_Winter = dfWinterEnergyMidPeak.groupby(['CustomerID','month','Rate Periods'], as_index = False)['Base Usage kWh','TOU Energy Charges ($)'].sum()
    # concatenate Summer and Winter Mid-peak energy
    mthMidE = pd.concat([mthMidE_Summer, mthMidE_Winter])
    mthMidE['TOU Energy Charges ($)'] = mthMidE['TOU Energy Charges ($)'].round(2)
    # sort by Month and rename the columns
    mthMidE = mthMidE.groupby(['month','CustomerID'],as_index = False)['TOU Energy Charges ($)'].sum()
    return mthMidE

def add_iteration_bill(df,a): #put iteration as the first column
    new_df = pd.DataFrame([df])
    new_df['Iteration']= '%d' % (a)
    cols = list(new_df)
    cols.insert(0, cols.pop(cols.index('Iteration')))
    new_df = new_df.ix[:, cols]
    return new_df

def logTime(foutLog, logMsg, tbase):
    codeTnow = datetime.now()
    foutLog.write('%s%s\n' %(logMsg, str(codeTnow)))
    codeTdelta = codeTnow - tbase
    foutLog.write('Time delta since start: %.3f seconds\n' %((codeTdelta.seconds+codeTdelta.microseconds/1.e6)))

######################
#Jovan's code to make sure it is in the right SCE DST format
from datetime import datetime
def FixDST(dirin='./', fnamein='IntervalDataDST.csv', 
           dirout='./', fnameout='IntervalData.csv', 
           dirlog='./', fnameLog='FixDST.log',
           tzinput = 'America/Los_Angeles',
           OutputFormat = 'SCE'):
    #%% Version and copyright info to record on the log file
    codeName = 'FixDST.py'
    codeVersion = '1.0'
    codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
    codeAuthors = "Jovan Bebic GE Global Research\n"

    # Capture start time of code execution and open log file
    codeTstart = datetime.now()
    foutLog = open(os.path.join(dirlog, fnameLog), 'w')

    print('\nThis is: %s, Version: %s' %(codeName, codeVersion))
    foutLog.write('This is: %s, Version: %s\n' %(codeName, codeVersion))
    foutLog.write('%s\n' %(codeCopyright))
    foutLog.write('%s\n' %(codeAuthors))
    foutLog.write('Run started on: %s\n\n' %(str(codeTstart)))

    # Output file information to log file
    print('Reading: %s' %os.path.join(dirin,fnamein))
    foutLog.write('Reading: %s\n' %os.path.join(dirin,fnamein))

    df1 = pd.read_csv(os.path.join(dirin,fnamein))
    foutLog.write('Read %d records\n' %df1.shape[0])
    foutLog.write('Columns are: %s\n' %' '.join(str(x) for x in df1.columns.tolist()))

    print('Processing customers')
    uniqueCIDs = df1['CustomerID'].unique()
    print('Number of unique customer IDs in the file: %d' %uniqueCIDs.size)
    foutLog.write('Number of unique customer IDs in the file: %d\n' %uniqueCIDs.size)
    i = 1
    for cid in uniqueCIDs:
        print('Processing time records for: %s (%d of %d)' %(str(cid), i, uniqueCIDs.size))
        foutLog.write('Processing time records for: %s\n' %(str(cid)))
        i += 1
        
        dstr = df1[df1['CustomerID'] == cid]['datetimestr'].str.split(':').str[0]
        # print(dstr.head())
        hstr = df1[df1['CustomerID'] == cid]['datetimestr'].str.split(':').str[1]
        # print(tstr.head())
        mstr = df1[df1['CustomerID'] == cid]['datetimestr'].str.split(':').str[2]
        # sstr = df1['datetimestr'].str.split(':').str[3]
        temp = dstr + ' ' + hstr + ':' + mstr
        df1.loc[(df1['CustomerID'] == cid), 'datetime'] = pd.to_datetime(temp, format='%d%b%Y %H:%M')

        if df1[df1['CustomerID'] == cid]['datetime'].dt.strftime('%Y').unique().size > 1:
            print('  Time records contain more than one year of data - aborting\n')
            foutLog.write('\n  Time records contain more than one year of data - aborting\n')
            logTime(foutLog, '\nRunFinished at: ', codeTstart)
            return
            
    if OutputFormat == 'SCE':
        print('\nWriting: %s in %s format' %(os.path.join(dirout,fnameout), OutputFormat))
        foutLog.write('Writing: %s in %s format\n' %(os.path.join(dirout,fnameout), OutputFormat))
        df1.sort_values(by=['CustomerID', 'datetimestr'], inplace = True)
        df1.to_csv(os.path.join(dirout,fnameout), index=False, )
    elif OutputFormat == 'ISO':
        print('\nWriting: %s in %s format' %(os.path.join(dirout,fnameout), OutputFormat))
        foutLog.write('Writing: %s in %s format\n' %(os.path.join(dirout,fnameout), OutputFormat))
        df1.set_index(['CustomerID', 'datetime'], inplace=True)
        df1.sort_index(inplace=True) # need to sort on datetime **TODO: Check if this is robust
        # df1.drop(['datetimestr'], axis=1, inplace=True) # drop redundant column
        df1.to_csv(os.path.join(dirout,fnameout), index=True, float_format='%.1f', date_format='%Y-%m-%d %H:%M', columns=['Demand'])
    else:
        print('\nUnrecognized output format, writing in %s in SCE format' %os.path.join(dirout,fnameout))
        foutLog.write('\nUnrecognized output format, writing in %s in SCE format\n' %os.path.join(dirout,fnameout))
        df1.sort_values(by=['CustomerID', 'datetimestr'], inplace = True)
        df1.to_csv(os.path.join(dirout,fnameout), index=False, float_format='%.1f', columns=['datetimestr', 'Demand', 'CustomerID'])
        
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    print('Finished\n')
    
if __name__ == "__main__":

    FixDST(dirin='output/load-smoothing-algorithm/', fnamein='GE_UTconsumption.csv', 
                   dirout='output/load-smoothing-algorithm/', fnameout='GE_UTconsumption_DST.csv', 
                   dirlog='output/load-smoothing-algorithm/', fnameLog='FixDST.log',
                   tzinput = 'America/Los_Angeles',
                   OutputFormat = 'SCE')

    
################# 
# input data processing

# input data with add in columns month, day, hour, minutes, dayofyear, year
consumption_raw_data_input = pd.read_csv(os.path.join(workingDir, 'output/load-smoothing-algorithm/GE_UTconsumption_DST.csv'))
del consumption_raw_data_input ['Unnamed: 0']
consumption_raw_data_input['datetime']=pd.to_datetime(consumption_raw_data_input['datetime'])
consumption_raw_data_input.index = consumption_raw_data_input['datetime']
month = consumption_raw_data_input['datetime'].dt.month
day = consumption_raw_data_input['datetime'].dt.day
hour = consumption_raw_data_input['datetime'].dt.hour
minute = consumption_raw_data_input['datetime'].dt.minute
day_of_year = consumption_raw_data_input['datetime'].dt.dayofyear
year = consumption_raw_data_input['datetime'].dt.year
del consumption_raw_data_input['datetime']
consumption_data_input = pd.concat([consumption_raw_data_input, month, day, hour, minute, day_of_year, year], axis=1)
consumption_data_input.columns = ['datetimestr','Base Usage kWh','CustomerID','month','day', 'hour', 'minute', 'day_of_year', 'year']

#normalizing data
norm_k = lambda x: x/x.mean()
consumption_data_input['Norm kWh']= consumption_data_input.groupby(['CustomerID', 'month'])['Base Usage kWh'].transform(norm_k)

#merging data with demand and energy rate
UTdemandCharges = pd.merge(UT_hourly_time_periods_input, demand_charges, how='left', on=['Rate Periods'])
UTdemandCharges = UTdemandCharges[UTdemandCharges.index % 4 == 0] #only keep one column out of 4 repeated column for the hour
UTdemandCharges.reset_index(inplace=True,drop=True)
UTdemandConsumption = pd.merge(consumption_data_input, UTdemandCharges, how='left', on=['month','day','hour'])
UTConsumption = pd.merge(UTdemandConsumption,energy_charges, how='left', on=['Rate Periods','Season','Hour'])
UTConsumption = UTConsumption.rename(columns ={'Hour': 'Peak periods'})
UTConsumption['Usage kW'] = UTConsumption['Base Usage kWh'] / 0.25 #add in the kW column

#reorder all the metrics
UTConsumption = UTConsumption[['CustomerID','datetimestr','year', 'day_of_year','month','day','hour','minute','Base Usage kWh','Usage kW','Norm kWh','Rate Periods','Season','Peak periods','TOU Demand Charges Rate ($/kW)','TOU Energy Charges Rate ($/kWh)']]

##################
#load smoothing algorithm - choosing one customerid
df1 = UTConsumption.loc[(UTConsumption['CustomerID'] == 281)] #281 is customer ID in the EnerNoc data
# make empty data frame
delta_max_norm = []
Total_Demand_Charges = pd.DataFrame()
Total_Energy_Charges = pd.DataFrame()
Total_Bill = pd.DataFrame()
TOU_demand_bill = pd.DataFrame()
merge_TOU_demand = pd.DataFrame()
merge_bill = pd.DataFrame()
dfNorm =[]

for x in range(1,k): #number of smoothing iteration
    #Finding the indexes which are the highest point in "Base Usage KWh" per month and find the indexes of these peak_load
    peak_load = df1.groupby(["month"],as_index=False)['Base Usage kWh'].idxmax()
    indexes = np.array(peak_load)
    #logging.debug('indexes:{}'.format(indexes))
    
    # find the average normalized in the hour and sort from high to low Norm
    df2 = df1.groupby(df1.index // 4).mean().reset_index(drop=True)
    df2 = df2[['month','day','hour','Norm kWh']]
    df2 = df2.sort_values('Norm kWh',ascending=False).reset_index(drop=True)
    
    #find the highest Norm in the 15 min data
    df3 = df1.sort_values('Norm kWh',ascending=False).reset_index(drop=True)
    
    #find the distance from highest Norm to norm = 1:
    delta_max_to_1 = df3['Norm kWh'].max()-1
    print (delta_max_to_1)
    delta_max_to_1 = delta_max_to_1.round(2)
    delta_max_norm = np.append(delta_max_norm,delta_max_to_1) #keep track of delta_max_to_1
    
    if x == 1:
        delta_stop_to_1= (0.25* delta_max_to_1)
        min_check = delta_max_to_1.round(2)
        print ('delta_stop_to_1:{}'.format(delta_stop_to_1))
    
    # Break loop
    if delta_max_to_1 < delta_stop_to_1:
        break 
    
    # logging in delta_max_to_1.round(2) as it decreases
    if x == 1 or x % (g) == 0 or (min_check > delta_max_to_1):
        #Total Bill
        #make sure sum kWh stay the same after all iterations
        sum_kWh = df1['Base Usage kWh'].sum()
        #logging.debug('Total kWh Usage:{}'.format(sum_kWh)) 

        # June-September $ per kW during max On-Peak and Mid-Peak and Off-Peak each month 
        mthOPD_Summer= monthlyOnPeakMaxDemand(df1)
        mthOPD_Summer_bill = mthOPD_Summer['TOU Demand Charges ($)'].sum()

        mthMidD = monthlyMidPeakMaxDemand(df1)
        mthMidD_bill = mthMidD ['TOU Demand Charges ($)'].sum()

        mthOffD = monthlyOffPeakMaxDemand(df1) 
        mthOffD_bill = mthOffD ['TOU Demand Charges ($)'].sum()

        # facilities demand charge: Year-round $ per maximum kW during the entire month
        mthFacilityDemand = DemandFacilityCharge(df1)
        mthFacilityDemand = mthFacilityDemand[['CustomerID','datetimestr','Facility_Demand Charges ($)']]
        mthFacilityDemand_bill = mthFacilityDemand['Facility_Demand Charges ($)'].sum()
        #logging.debug("Facilities Demand charges: {}".format(mthFacilityDemand_bill))

        #energy bill
        mthOPE_Summer = monthlyOnPeakEnergy(df1)
        mthOPE_Summer_bill = mthOPE_Summer['TOU Energy Charges ($)'].sum()
        mthOffE = monthlyOffPeakEnergy(df1)
        mthOffE_bill = mthOffE ['TOU Energy Charges ($)'].sum()
        mthMidE = monthlyMidPeakEnergy(df1)
        mthMidE_bill = mthMidE['TOU Energy Charges ($)'].sum()
        #logging.debug("On: %d Mid: %d Off: %d" % (mthOPD_Summer_bill, mthMidD_bill, mthOffD_bill))
        
        TOU_demand_charges = mthOPD_Summer_bill + mthMidD_bill + mthOffD_bill
        #logging.debug("TOU Demand charges: {}".format(TOU_demand_charges))

        #total energy charge
        total_energy_charges = mthOPE_Summer_bill + mthOffE_bill + mthMidE_bill
        Total_Energy_Charges= Total_Energy_Charges.append(add_iteration_bill(total_energy_charges,x))
        #logging.debug("Energy charges: {}".format(total_energy_charges))

        #total demand charge
        total_demand_charges = TOU_demand_charges + mthFacilityDemand_bill
        Total_Demand_Charges = Total_Demand_Charges.append(add_iteration_bill(total_demand_charges,x))
        #logging.debug("Demand charges: {}".format(total_demand_charges))

        #total bill
        total_bill = total_demand_charges + total_energy_charges
        
        #Update new minimum
        min_check = delta_max_to_1
        logging.debug ('delta_norm:{}, iteration:{}, total_bill_($):{}'.format(delta_max_to_1,x,total_bill))
        
        #merge all the bill into df1 with desired columns and total bill
        if x == 1 or x % (g) == 0:
            TOU_demand_bill= pd.concat([mthOPD_Summer,mthMidD,mthOffD])
            TOU_demand_bill = TOU_demand_bill[['CustomerID','datetimestr','TOU Demand Charges ($)']]
            merge_TOU_demand = pd.merge(df1,TOU_demand_bill, on=['CustomerID','datetimestr'],how='left')
            merge_bill = pd.merge(merge_TOU_demand,mthFacilityDemand, on=['CustomerID','datetimestr'],how='left')
            merge_bill['TOU Energy Bill ($)'] = merge_bill['Base Usage kWh'] * merge_bill['TOU Energy Charges Rate ($/kWh)']
            merge_bill = merge_bill.fillna(0)
            merge_bill.to_csv(os.path.join(workingDir, 'output/load-smoothing-algorithm/', str(281)+ '_%d_iteration.csv') %x)
            #total bill
            Total_Bill = Total_Bill.append(add_iteration_bill(total_bill,x))

            #graph normalized curve 
            df2time = list(range(1,1001)) #choose the first 200 hours
            dfNorm.append(df2['Norm kWh'][0:1000].values)
            newNorm = np.array(dfNorm)
            colors = mpl.cm.rainbow(np.linspace(0,1,n))
            fig, ax = plt.subplots(figsize = (15,20))
            fig.suptitle(str(281), fontsize=20)
            plt.xlabel('hours')
            plt.ylabel('Normalized kWh')
            for color, y in zip(colors, newNorm):
                ax.plot(df2time, y, color=color)
            plt.show()    

    # show change in base usage kWh and normalized data
    for i in indexes:
        average_twoloadsNorm = (df1.loc[i-1,:]['Norm kWh'] + df1.loc[i+1,:]['Norm kWh'])/2
        deltaNorm = df1.loc[i,:]['Norm kWh'] - average_twoloadsNorm #find the delta to the average norm data
        deltaNorm = deltaNorm/n #the load that will be added on loads surrounding peak load
        df1.loc[i,'Norm kWh'] = average_twoloadsNorm + deltaNorm

        average_twoloadsKWH = (df1.loc[i-1,:]['Base Usage kWh'] + df1.loc[i+1,:]['Base Usage kWh'])/2
        deltaKWH = df1.loc[i,:]['Base Usage kWh'] - average_twoloadsKWH
        deltaKWH = deltaKWH /n

        df1.loc[i, 'Base Usage kWh'] = average_twoloadsKWH + deltaKWH

        #sum discharge
        for a in range(1,(n-1)//2+1):
            #smoothen the curve out to the both side of peak load
            df1.loc[i-a,'Base Usage kWh'] = df1.loc[i-a,'Base Usage kWh'] + deltaKWH
            df1.loc[i+a,'Base Usage kWh'] = df1.loc[i+a,'Base Usage kWh'] + deltaKWH

            df1.loc[i-a,'Norm kWh'] = df1.loc[i-a,'Norm kWh'] + deltaNorm
            df1.loc[i+a,'Norm kWh'] = df1.loc[i+a,'Norm kWh'] + deltaNorm
    
    #print iteration
    if x% 100 == 0:
        print ('%d' %(x))
