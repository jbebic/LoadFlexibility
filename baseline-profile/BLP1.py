# -*- coding: utf-8 -*-
"""
BLP1.py

Created on June 8th, 2018

@author: Jerome Carman

Use customer load data to calculate an estimated average load baseline
Uses the N-day simple average with morning adjustment method (BLP1) as described in Coughlin et al., 2008.
  - This method is also that described in Section 4.13.4.1 in the CAISO conformed tariff, if a 10-day average is used.
Applies to:
  Reliability Demand Response Resources (RDRR) offering uncommitted capacity as energy in the real time market
    - DR events are a minumum of 1 hour, and can be up to 48 hours in length. Maximum of 15 events per term.
    - There are two terms: June - Sept, Oct - May
  Proxy Demand Resource (PDR)
  

"""
#define this as a function to be called by another .py script
  #required user inputs into the function
    #N = number of business days to average (CAISO Section 4.13.4.1 uses 10 for business days, and 4 for non-business days)
    #businessDays = vector of numerical representation of days of the week that are considered business days (1=Mon, 7=Sun). Script assumes numbers NOT included here are non-business days
    #realCustomerData = data frame of actual customer load data
    #DREvent = data frame of information on the DR event that is reflected in the customer load data
      #date
      #deployment hour
      #normal op hour (hour returning to normal operations)

#define the date and hour of a fictitious DR event. If spanning multiple hours, the start and end hours of the DR event need to be specified

#determine if DR event is on a business day or non-business day

#pull historic customer load data from which baseline estimate will be calculated (positive value means consumed demand from the grid by the customer)
  #if business day DR event, load the last 10 business days immediately prior to the DR event day
  #if non-business day DR event, load the last 4 non-business days immediately prior to the DR event day

#create an hourly average 1-day profile. This is the baseline load

#calculate the ratio used to quantify the amount of demand provided
  #numerator = for each hour of the DR event, average load of the DR-day second, third, and fourth hours preceding the hour of the DR event
  #denominator = for each hour of the DR event, average load of the baseline second, third, and fourth hours preceding the hour of the DR event
  #ratio = numerator / denominator for each hour of the DR event
  #Check ratio values and cap if needed
    #If any value is greater than 1.2, cap at 1.2
    #If any value is less than 0.8, cap at 0.8
    
#multiple each hour of the DR event by the corresponding ratio for that hour. This gives kW and kWh
