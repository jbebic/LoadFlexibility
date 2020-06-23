# Load Flexibility Toolchain

## Introduction
This document is a user guide for various functions of *Load Flexibility Toochain*. It documents the input and output file formats and suggested file placement in directories. The rest of the document is organized as follows: The *Overview* section provides the complete view of the toolchain essentials, starting from interval meter data, to generating a set of constraints for use in production simulations. This is followed by documentation of individual functions - each is presented in its own section with subsections documenting the format and suggested location of input data, the meaning and intent of input parameters, the brief explanation of what the function does, and the format and suggested location of output data. Only the *top level* functions are discussed under these headings, the helper functions (called from within the top level functions) are presented last, under their own library's heading.

## Overview
The toolchain processes *homogeneous* collections of smart meter data to extract naturally occurring flexibility by study of load patterns. The term *homogeneous* in this context represents the utility loads sharing the same [NAICS code](https://www.census.gov/eos/www/naics/) and subscribed to the same time of use (TOU) rate. (An overview of Southern California Edison's (SCE) rates, including TOU rates, can be found [here](https://www.sce.com/regulatory/tariff-books/rates-pricing-choices "Regulatory Information > SCE Tariff Books > Rates & Pricing Choices").)

For example, a homogeneous group of customers are [grocery stores](https://www.census.gov/cgi-bin/sssd/naics/naicsrch?code=445110&search=2017%20NAICS%20Search "445110 Supermarkets and Other Grocery (except Convenience) Stores") on [TOU-GS3](https://library.sce.com/content/dam/sce-doclib/public/regulatory/tariff/electric/schedules/general-service-&-industrial-rates/ELECTRIC_SCHEDULES_TOU-GS-3.pdf "TIME-OF-USE - GENERAL SERVICE - DEMAND METERED"). Additional criteria is used to further enhance homogeneity of the groups - this will be discussed in the context of [CalculateGroups](#calculategroups) function.

## AnonymizeCIDs

## CalculateBilling

## CalculateGroups
```python
CalculateGroups(dirin='testdata/',
                fnamein="summary." + fnamebase+'.billing.csv',
                dirout='testdata/',
                dirplot='testdata/',
                fnamebase=fnamebase,
                dirlog='testdata/',  
                ignore1515=True,
                energyPercentiles = [5, 27.5,  50, 72.5, 95],
                chargeType="Total")
```

## GroupAnalysisMaster
```python
GroupAnalysisMaster(dirin_raw = 'input/', # folder where the raw data inputs are located  
                    dirout_data ='output/',  # folder where to save the ouput data
                    dirout_plots = 'plots/', # folder where to save the output figures
                    dirlog = 'output/', #  folder where to save the log file(s)
                    fnamebase = 'waterSupplyandIrrigationSystems', # file name base (usual by the type of building / NAICS)
                    fnamein = 'waterSupplyandIrrigationSystems.A.csv', # interval data
                    Ngroups = 2, # tells the function how many groups to iterate over
                    demandUnit = 'Wh' # unit of the raw interval data
                    )
```

##
