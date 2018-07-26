
# coding: utf-8

# ## Calculate and show bill components - energy and demand charges-public version



import pandas as pd
import datetime as dt
import numpy as np
from ggplot import *
import matplotlib.pyplot as plt
import matplotlib as mpl
# if DA customers = 1, 0 for non-DA customers
DA_Customer = 0
# Read in input tables 
# energy charges
energy_charges_input = pd.read_csv('C:/Users/leed2/TOU_GS3_B_Energy.csv')
# energy charges for DA customers
energy_charges_input_DA = pd.read_csv('C:/Users/leed2/TOU_GS3_B_Energy_DA.csv')
# demand charges
demand_charges_input = pd.read_csv('C:/Users/leed2/TOU_GS3_B_Demand.csv')
# demand charges for DA customers
demand_charges_input_DA = pd.read_csv('C:/Users/leed2/TOU_GS3_B_Demand_DA.csv')
# UT hourly time periods
UT_hourly_time_periods_input = pd.read_csv('C:/Users/leed2/TOU_GS3_B_Seasonal_TimePeriods.csv')




energy_charges_input.head(n=10)



# rename the columns
energy_charges_input = energy_charges_input.rename(columns={'TOU-GS3-B':'Charges ($/kWh)'})
energy_charges_input = energy_charges_input.rename(columns={'Number':'Rate Periods'})
energy_charges_input.head(n=10)




energy_charges_input_DA




# rename the columns of energy charge rate tables
energy_charges_input_DA = energy_charges_input_DA.rename(columns={'TOU-GS3-B':'Charges ($/kWh)'})
energy_charges_input_DA = energy_charges_input_DA.rename(columns={'Number':'Rate Periods'})
energy_charges_input_DA.head(n=10)





demand_charges_input.head(n=6)




# rename the columns of demand charge rate tables
demand_charges_input = demand_charges_input.rename(columns={'TOU-GS3-B':'Charges ($/kW)'})
demand_charges_input = demand_charges_input.rename(columns={'Number':'Rate Periods'})
demand_charges_input.head(n=10)


demand_charges_input_DA



# rename the columns of demand charge rate tables with DA option
demand_charges_input_DA = demand_charges_input_DA.rename(columns={'TOU-GS3-B':'Charges ($/kW)'})
demand_charges_input_DA = demand_charges_input_DA.rename(columns={'Number':'Rate Periods'})
demand_charges_input_DA.head(n=10)



UT_hourly_time_periods_input.head()



# renmae the columns
UT_hourly_time_periods_input = UT_hourly_time_periods_input.rename(columns={'TOU-GS3-B':'Rate Periods'})
UT_hourly_time_periods_input.head()



# Read in consumption data
consumption_raw_data_input = pd.read_csv('file_name.csv')



consumption_raw_data_input.head()




# format datetime column and create additional datetime columns
consumption_raw_data_input['DateTime']=pd.to_datetime(consumption_raw_data_input['DateTime'], format='%m/%d/%Y %H:%M')
consumption_raw_data_input.index = consumption_raw_data_input['DateTime']

day = consumption_raw_data_input['DateTime'].dt.day
month = consumption_raw_data_input['DateTime'].dt.month
hour = consumption_raw_data_input['DateTime'].dt.hour
minute = consumption_raw_data_input['DateTime'].dt.minute
day_of_year = consumption_raw_data_input['DateTime'].dt.dayofyear
year = consumption_raw_data_input['DateTime'].dt.year

del consumption_raw_data_input['DateTime']

consumption_data_input = pd.concat([month, day, hour, minute, day_of_year, year, consumption_raw_data_input], axis=1)
consumption_data_input.columns = ['month', 'day', 'hour', 'minutes', 'day_of_year', 'year', 'Base Usage kWh']



consumption_data_input.head()




if DA_Customer == 0:
    demand_charges = demand_charges_input
    energy_charges = energy_charges_input
    DA_CRS_DWR_bond = 0
else:
    demand_charges = demand_charges_input_DA
    energy_charges = energy_charges_input_DA
    DA_CRS_DWR_bond = 0.00549




# Join 'UT_hourly_time_periods_input' with demand charges
UTdemandCharges = pd.merge(UT_hourly_time_periods_input, demand_charges, how='left', on=['Rate Periods'])
UTdemandCharges.head(n=10)



UTdemandConsumption = pd.merge(consumption_data_input, UTdemandCharges, on=['month','day','hour'])
UTdemandConsumption.tail(n=10)



# Calculate monthly on-, off- and mid-peak demands


# calculating only summer on-peak demand (winter on-peak rate is zero)
def monthlyOnPeakMaxDemand(df):
    # filtering out summer on-peak periods
    dfSummerOnPeakDemand = df[df['Rate Periods'] == 1] 
    # calculating maximum on-peak demand for each month
    mthOPD_Summer = dfSummerOnPeakDemand.groupby(['month','Season','Hour', 'Rate Periods','Charges ($/kW)'], as_index = False)['Base Usage kWh'].max()
    # calculating max on-peak demand charge
    mthOPD_Summer['On-Peak Demand Charges ($)'] = mthOPD_Summer['Charges ($/kW)'] * mthOPD_Summer['Base Usage kWh'] * 4
    mthOPD_Summer['On-Peak Demand Charges ($)'] = mthOPD_Summer['On-Peak Demand Charges ($)'].round(2)
    # drop unnecessary columns and sort by month
    mthOPD_Summer = mthOPD_Summer.drop(['Hour', 'Rate Periods', 'Charges ($/kW)'], axis=1)
    mthOPD_Summer = mthOPD_Summer.sort_values(['month'], ascending=[True])
    mthOPD_Summer = mthOPD_Summer.rename(columns={'Base Usage kWh':'On-Peak Demand (kW)'})
    return mthOPD_Summer
mthOPD_Summer = monthlyOnPeakMaxDemand(UTdemandConsumption) 
mthOPD_Summer.head(n=20)



# calculating only off-peak demand for Summer and Winter
def monthlyOffPeakMaxDemand(df):
    # filtering out Summer and Winter off-peak periods
    dfSummerOffPeakDemand = df[df['Rate Periods'] == 3]
    dfWinterOffPeakDemand = df[df['Rate Periods'] == 6]
    # calculating maximum on peak demand for each month
    mthOffD_Summer = dfSummerOffPeakDemand.groupby(['month','Season','Hour','Rate Periods','Charges ($/kW)'], as_index = False)['Base Usage kWh'].max()
    mthOffD_Summer['Off-Peak Demand Charges ($)'] = mthOffD_Summer['Charges ($/kW)'] * mthOffD_Summer['Base Usage kWh'] *4   
    mthOffD_Winter = dfWinterOffPeakDemand.groupby(['month', 'Season','Hour','Rate Periods','Charges ($/kW)'], as_index = False)['Base Usage kWh'].max()
    mthOffD_Winter['Off-Peak Demand Charges ($)'] = mthOffD_Winter['Charges ($/kW)'] * mthOffD_Winter['Base Usage kWh'] * 4    
    # concatenate summer and winter off peak
    mthOffD = pd.concat([mthOffD_Summer, mthOffD_Winter])
    mthOffD['Off-Peak Demand Charges ($)'] = mthOffD['Off-Peak Demand Charges ($)'].round(2)
    # drop unnecessary columns and sort by month
    mthOffD = mthOffD.drop(['Hour', 'Rate Periods', 'Charges ($/kW)'], axis=1)
    mthOffD = mthOffD.sort_values(['month'], ascending=[True])
    mthOffD = mthOffD.rename(columns={'Base Usage kWh':'Off-Peak Demand (kW)'})
    return  mthOffD
mthOffD = monthlyOffPeakMaxDemand(UTdemandConsumption)
mthOffD.head(n=10)



# calculating only mid-peak demand for Summer and Winter
def monthlyMidPeakMaxDemand(df):
    df = UTdemandConsumption
    # filtering out Summer and Winter mid-peak periods
    dfSummerMidPeakDemand = df[df['Rate Periods'] == 2]
    dfWinterMidPeakDemand = df[df['Rate Periods'] == 5]
    # calculating maximum on peak demand for each month
    mthMidD_Summer = dfSummerMidPeakDemand.groupby(['month','Season','Hour','Rate Periods', 'Charges ($/kW)'], as_index = False)['Base Usage kWh'].max()
    mthMidD_Summer['Mid-Peak Demand Charges ($)'] = mthMidD_Summer['Charges ($/kW)'] * mthMidD_Summer['Base Usage kWh'] *4    
    mthMidD_Winter = dfWinterMidPeakDemand.groupby(['month', 'Season','Hour','Rate Periods', 'Charges ($/kW)'], as_index = False)['Base Usage kWh'].max()
    mthMidD_Winter['Mid-Peak Demand Charges ($)'] = mthMidD_Winter['Charges ($/kW)'] * mthMidD_Winter['Base Usage kWh'] *4
    # concatenate summer and winter off peak
    mthMidD = pd.concat([mthMidD_Summer, mthMidD_Winter])
    mthMidD = mthMidD.sort_values(['month'], ascending=[True])
    mthMidD['Mid-Peak Demand Charges ($)'] = mthMidD['Mid-Peak Demand Charges ($)'].round(2)
    # drop unnecessary columns and renmae the columns
    mthMidD = mthMidD.drop(['Hour', 'Rate Periods', 'Charges ($/kW)'], axis=1)
    mthMidD = mthMidD.rename(columns={'Base Usage kWh':'Mid-Peak Demand (kW)'})    
    return  mthMidD
mthMidD = monthlyMidPeakMaxDemand(UTdemandConsumption)
mthMidD.head(n=100)



# profiling dataframe for processing
consumption_data_input.head()



#Calculate hourly sum for every for energy calculation
consumption_data_input_hourly = consumption_data_input.groupby(['month','day','hour'], as_index = False)['Base Usage kWh'].sum()
consumption_data_input_hourly.head()



# calculate hourly rates for 'UT_hourly_time_periods_input'
UT_hourly_time_periods_input_hourly = UT_hourly_time_periods_input.groupby(['month','day','hour'],as_index=False)['Rate Periods'].mean()
UT_hourly_time_periods_input_hourly.head()



energy_charges_input



# join 'UT_hourly_time_periods_input_hourly' with energy charge rates
UTenergyCharges = pd.merge(UT_hourly_time_periods_input_hourly, energy_charges, how='left', on=['Rate Periods'])
UTenergyCharges.head()



# join 'UTenergyCharges' with hourly consumption data
UTenergyConsumption = pd.merge(UTenergyCharges, consumption_data_input_hourly, on=['month','day','hour'])
UTenergyConsumption.head()



# calculate only summer on-peak energy
def monthlyOnPeakEnergy(df):
    df = UTenergyConsumption
    # filtering out summer on-peak periods
    dfSummerEnergyOnPeak = df[df['Rate Periods'] == 1].copy()
    # calculating on-peak energy for each month
    dfSummerEnergyOnPeak['On-Peak Energy Charges ($)'] = dfSummerEnergyOnPeak['Charges ($/kWh)'] * dfSummerEnergyOnPeak['Base Usage kWh']
    mthOPE_Summer = dfSummerEnergyOnPeak.groupby(['month','Season','Hour','Rate Periods'], as_index = False)['Base Usage kWh','On-Peak Energy Charges ($)'].sum()
    mthOPE_Summer['On-Peak Energy Charges ($)'] = mthOPE_Summer['On-Peak Energy Charges ($)'].round(2)
    # drop unnecessary columns and rename the columns
    mthOPE_Summer = mthOPE_Summer.drop(['Hour', 'Rate Periods'], axis=1)
    mthOPE_Summer = mthOPE_Summer.rename(columns={'Base Usage kWh':'On-Peak Energy (kWh)'}) 
    return mthOPE_Summer
mthOPE_Summer = monthlyOnPeakEnergy(UTenergyConsumption)
mthOPE_Summer.head(n=20)



# calculate only summer and winter off-peak energy
def monthlyOffPeakEnergy(df):
    df = UTenergyConsumption
    # filtering out Summer off-peak periods
    dfSummerEnergyOffPeak = df[df['Rate Periods'] == 3].copy()
    # calculating Summer off-peak energy for each month
    dfSummerEnergyOffPeak['Off-Peak Energy Charges ($)'] = dfSummerEnergyOffPeak['Charges ($/kWh)'] * dfSummerEnergyOffPeak['Base Usage kWh']
    mthOffE_Summer = dfSummerEnergyOffPeak.groupby(['month','Season','Hour','Rate Periods'], as_index = False)['Base Usage kWh','Off-Peak Energy Charges ($)'].sum()
    # filtering out winter off-peak periods
    dfWinterEnergyOffPeak = df[df['Rate Periods'] == 6].copy()
    # calculating Winter off-peak energy for each month
    dfWinterEnergyOffPeak['Off-Peak Energy Charges ($)'] = dfWinterEnergyOffPeak['Charges ($/kWh)'] * dfWinterEnergyOffPeak['Base Usage kWh']
    mthOffE_Winter = dfWinterEnergyOffPeak.groupby(['month','Season','Hour','Rate Periods'], as_index = False)['Base Usage kWh','Off-Peak Energy Charges ($)'].sum()    
    # concatenate Summer and Winter off-peak energy
    mthOffE = pd.concat([mthOffE_Summer, mthOffE_Winter])
    mthOffE['Off-Peak Energy Charges ($)'] = mthOffE['Off-Peak Energy Charges ($)'].round(2)
    # drop unnecessary columns, sort by Month, and rename the columns
    mthOffE = mthOffE.drop(['Hour', 'Rate Periods'], axis=1)
    mthOffE = mthOffE.sort_values(['month'], ascending=[True])
    mthOffE = mthOffE.rename(columns={'Base Usage kWh':'Off-Peak Energy (kWh)'}) 
    
    return mthOffE
        
mthOffE = monthlyOffPeakEnergy(UTenergyConsumption)
mthOffE.head(n=20)



# calculate only summer and winter Mid-peak energy
def monthlyMidPeakEnergy(df):
    df = UTenergyConsumption
    # filtering out Summer Mid-peak periods
    dfSummerEnergyMidPeak = df[df['Rate Periods'] == 2].copy()
    # calculating Summer Mid-peak energy for each month
    dfSummerEnergyMidPeak['Mid-Peak Energy Charges ($)'] = dfSummerEnergyMidPeak['Charges ($/kWh)'] * dfSummerEnergyMidPeak['Base Usage kWh']
    mthMidE_Summer = dfSummerEnergyMidPeak.groupby(['month','Season','Hour','Rate Periods'], as_index = False)['Base Usage kWh','Mid-Peak Energy Charges ($)'].sum()
    # filtering out Winter Mid-peak periods
    dfWinterEnergyMidPeak = df[df['Rate Periods'] == 5].copy()
    # calculating Winter Mid-peak energy for each month
    dfWinterEnergyMidPeak['Mid-Peak Energy Charges ($)'] = dfWinterEnergyMidPeak['Charges ($/kWh)'] * dfWinterEnergyMidPeak['Base Usage kWh']
    mthMidE_Winter = dfWinterEnergyMidPeak.groupby(['month','Season','Hour','Rate Periods'], as_index = False)['Base Usage kWh','Mid-Peak Energy Charges ($)'].sum()
    # concatenate Summer and Winter Mid-peak energy
    mthMidE = pd.concat([mthMidE_Summer, mthMidE_Winter])
    mthMidE['Mid-Peak Energy Charges ($)'] = mthMidE['Mid-Peak Energy Charges ($)'].round(2)
    # drop unnecessary columns, sort by Month and rename the columns
    mthMidE = mthMidE.drop(['Hour', 'Rate Periods'], axis=1)
    mthMidE = mthMidE.sort_values(['month'], ascending=[True])
    mthMidE = mthMidE.rename(columns={'Base Usage kWh':'Mid-Peak Energy (kWh)'})
    return mthMidE
        
mthMidE = monthlyMidPeakEnergy(UTenergyConsumption)
mthMidE.head(n=20)



UTdemandConsumption.head(n=11)



# calculate facility related demand charges
def DemandFacilityCharge(df):
    df = UTdemandConsumption
    # define demand facility charge rate
    DemandFacilityCharge = 17.81
    # calculate monthly demand
    mthFacilityDemand = df.groupby(['month', 'Season'], as_index = False)['Base Usage kWh'].max()
    mthFacilityDemand['Facility_Demand Charges ($)'] = mthFacilityDemand['Base Usage kWh'] * DemandFacilityCharge * 4
    # rename the columns
    mthFacilityDemand = mthFacilityDemand.rename(columns={'Base Usage kWh':'Monthly Max kWh'})
    mthFacilityDemand['Facility_Demand Charges ($)'] = mthFacilityDemand['Facility_Demand Charges ($)'].round(2)
    mthFacilityDemand = mthFacilityDemand.rename(columns={'Monthly Max kWh':'Facility Related Demand (kW)'})
    return mthFacilityDemand
mthFacilityDemand = DemandFacilityCharge(UTdemandConsumption)
mthFacilityDemand


# create output summary table
def createTotalDataFrame():
    # merge monthly Summer On-peak demand with monthly Off-peak demand charges 
    mthOffandOPdemand = mthOffD.merge(mthOPD_Summer, how='left', left_on=['month','Season'], right_on=['month','Season'],sort=True)
    # merge above with Mid-peak demand
    TotDemandCharges = mthOffandOPdemand.merge(mthMidD, how='left', left_on=['month','Season'],right_on=['month','Season'],sort=True)
    # Merge above with monthly Summer On-peak energy charge
    ToTDemandAndOpEnergy=TotDemandCharges.merge(mthOPE_Summer, how='left', left_on=['month','Season'],right_on=['month','Season'],sort=True)
    # merge above with monthly Off-peak energy charge
    TotDandOnMidEnergy = ToTDemandAndOpEnergy.merge(mthOffE, how='left', left_on=['month','Season'],right_on=['month','Season'],sort=True)
    # merge above with monthly Mid-peak energy charge
    TotalTable = TotDandOnMidEnergy.merge(mthMidE, how='left', left_on=['month','Season'],right_on=['month','Season'],sort=True)
    # merge above with monthly facility-related demand charge
    grandTotalTable = TotalTable.merge(mthFacilityDemand, how='left', left_on=['month','Season'],right_on=['month','Season'],sort=True)
    # convert 'month' to integers
    grandTotalTable['month'] = grandTotalTable['month'].astype(int)
    #replcace 'NaN' with 0
    grandTotalTable = grandTotalTable.fillna(0)
    
    # calculate monthly total energy (kWh)
    grandTotalTable['Grand Total Energy (kWh)'] = grandTotalTable['On-Peak Energy (kWh)'] + grandTotalTable['Off-Peak Energy (kWh)'] + grandTotalTable['Mid-Peak Energy (kWh)']
    # calculate monthly DA CRS DWR bond   
    grandTotalTable['DA CRS DWR Bond Charge ($)'] = grandTotalTable['Grand Total Energy (kWh)'] * DA_CRS_DWR_bond
    # calculate monthly total demand charge
    # define the column list
    Demand_col_list = ['Off-Peak Demand Charges ($)','On-Peak Demand Charges ($)','Mid-Peak Demand Charges ($)','Facility_Demand Charges ($)']
    Energy_col_list = ['On-Peak Energy Charges ($)','Off-Peak Energy Charges ($)','Mid-Peak Energy Charges ($)']
    # calculate demand charge total and energy charge totals
    grandTotalTable['Total Demand Charges ($)'] = grandTotalTable[Demand_col_list].sum(axis=1)
    grandTotalTable['Total Energy Charges ($)'] = grandTotalTable[Energy_col_list].sum(axis=1)
    # calculate grand total charges
    grandTotalTable['Grand Total Charges ($)'] = grandTotalTable['Total Demand Charges ($)'] + grandTotalTable['Total Energy Charges ($)'] + grandTotalTable['DA CRS DWR Bond Charge ($)']
    # calculate dollar($)/kWh
    grandTotalTable['Dollar ($)/kWh'] = grandTotalTable['Grand Total Charges ($)'] / grandTotalTable['Grand Total Energy (kWh)']
    
    return grandTotalTable
TotalTable = createTotalDataFrame ()
TotalTable


# generate plots from TotalTable
def plotGenerator():
    # call 'createTotalDataFrame ()' function
    createTotalDataFrame ().plot(x='month', y = ['Total Demand Charges ($)', 'Total Energy Charges ($)','Grand Total Charges ($)'],style='-')
    # define the size of plot
    plt.rcParams['figure.figsize'] = [12, 8]
    # define the x-axis ticks
    x = [1,2,3,4,5,6,7,8,9,10,11,12]
    plt.xticks(np.arange(min(x), max(x)+1, 1.0))
    # name titel,xlabel and ylabels
    plt.title('Demand and Energy Charges vs Total Charges(Company #7: Leader)',fontsize=18)
    plt.xlabel('Month', fontsize=18)
    plt.ylabel('Dollars($)',fontsize=18)
    # define the grid mark
    plt.grid(which='major',axis='both')
    # locate the legend box
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()
    
    # call 'createTotalDataFrame ()' function
    createTotalDataFrame ().plot(x='month', y = ['Off-Peak Demand Charges ($)','On-Peak Demand Charges ($)', 'Mid-Peak Demand Charges ($)', 'On-Peak Energy Charges ($)', 'Off-Peak Energy Charges ($)', 'On-Peak Energy Charges ($)','Off-Peak Energy Charges ($)','Mid-Peak Energy Charges ($)','Facility_Demand Charges ($)','Grand Total Charges ($)'],style='-')
    # define the size of plot
    plt.rcParams['figure.figsize'] = [12, 8]
    # define the x-axis ticks
    x = [1,2,3,4,5,6,7,8,9,10,11,12]
    plt.xticks(np.arange(min(x), max(x)+1, 1.0))
    # define title, xlabel and ylabels
    plt.title('Bill Components vs Total Charges(Company #7: Leader)',fontsize=20)
    plt.xlabel('Month', fontsize=18)
    plt.ylabel('Dollars($)',fontsize=18)
    # define the grid mark
    plt.grid(which='major',axis='both')
    # locate the legend box
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()
    
plotGenerator()



# traspose the totalTable
def grandTotalTableTransposed ():
    grandTotalTableTransposed = createTotalDataFrame().transpose()
    return (grandTotalTableTransposed)

grandTotalTableTransposed ()

