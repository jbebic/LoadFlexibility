# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 15:57:51 2018

@author: 200018380
"""
#%% Importing all the necessary Python packages
import pandas as pd # multidimensional data analysis
import numpy as np # vectorized calculations
from datetime import datetime # time stamps
import os # operating system interface
import matplotlib.pyplot as plt # plotting 
import matplotlib.backends.backend_pdf as dpdf # pdf output
from PyPDF2 import PdfFileReader, PdfFileWriter
import re

import warnings
warnings.filterwarnings("ignore")

#%% Importing supporting modules
from SupportFunctions import findUniqueIDs, getData, logTime, createLog,  assignDayType, getDataAndLabels, readHighlightIDs
#from UtilityFunctions import AssignRatePeriods, readTOURates
#from NormalizeLoads import NormalizeGroup
from PlotHeatMaps import outputThreeHeatmaps, outputThreeHeatmapsGroup

#%% Version and copyright info to record on the log file
codeName = 'CustomerReports.py'
codeVersion = '1.2'
codeCopyright = 'GNU General Public License v3.0' # 'Copyright (C) GE Global Research 2018'
codeAuthors = "Irene M. Berry, Jovan Z. Bebic, GE Global Research\n"

def getPrices(cid, foutLog, df1):
    # fetch data from input file
    PricesDict = {}
    return PricesDict
    
def PopulateLaTeX(dirin='testdata/', fnamein= 'summary.synthetic20.A.billing.csv', 
                  dirtex='report/', fnametex = 'report03t.tex', 
                  considerCIDs = '', 
                  dirout='testdata/', fnameout = '.report02.tex',
                  ReplaceDict = {},
                  dirlog='testdata/', fnameLog='PopulateLaTeX.log'):
    # Capture start time of code execution
    codeTstart = datetime.now()
    # open log file
    foutLog = createLog(codeName, "PopulateLaTeX", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    if considerCIDs != '':
        print('Reading: %s' %os.path.join(dirin,considerCIDs))
        foutLog.write('Reading: %s\n' %os.path.join(dirin,considerCIDs))
        df9 = pd.read_csv(os.path.join(dirin,considerCIDs), 
                          header = 0, 
                          usecols = [0],
                          comment = '#',
                          names=['CustomerID'],
                          dtype={'CustomerID':np.str})
        considerIDs = df9['CustomerID'].tolist()
        considerIDs = [x.replace(" ", "") for x in considerIDs]
    else:
        foutLog.write("\n*** considerCIDs must be specified")
        print("*** considerCIDs must be specified")

    # fetch data from input file
    df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                      skiprows = 3,
                      header = None,
                      # usecols = [0, 1, 2], 
                      # names=['datetimestr', 'Demand', 'CustomerID'],
                      # dtype={'datetimestr':np.str, 'Demand':np.float64, 'CustomerID':np.str}
                      )
    # UniqueIDs = df1[0].unique().tolist()

    print('Total number of records read: %d' %df1[0].size)
    foutLog.write('Total number of interval records read: %d\n' %df1[0].size)

    try: # Read in the LaTeX template file
        with open(os.path.join(dirtex, fnametex), 'r') as file :
            filetemplate = file.read()
    except:
        foutLog.write("\n*** Couldn't open %s" %(os.path.join(dirin,fnametex)))
        print("*** Couldn't open %s" %(os.path.join(dirin,fnametex)))
        
    # Replace the target strings
    for cid in considerIDs:
        try:
            foutLog.write("\nGenerating report for %s " %cid )
            print("Generating report for %s " %cid)
            filedata = filetemplate.replace('<CustomerID>', cid)

            for key in list(ReplaceDict.keys()):
                filedata = filedata.replace(key, ReplaceDict[key])

            ix_ad  = 1
            ix_adc = 2
            ix_aec = 3
            ix_afc = 4
            ix_atc = 5
            ix_mdc = 5+1*12+1 # monthly demand charges
            ix_mec = 5+2*12+1 # monthly energy charges
            ix_mfc = 5+3*12+1 # monthly facility charges
            ix_mtc = 5+4*12+1 # monthly total charges
    
            try:
                df2 = df1[df1[0]==cid]
                
                filedata = filedata.replace('<dmndpc>', '%.1f' %(df2.iloc[0,ix_adc]/df2.iloc[0,ix_atc]*100))
                
                filedata = filedata.replace('<facility>', '%.2f' %(df2.iloc[0,ix_afc]))
                filedata = filedata.replace('<energy>', '%.2f' %(df2.iloc[0,ix_aec]))
                filedata = filedata.replace('<demand>', '%.2f' %(df2.iloc[0,ix_adc]))
                filedata = filedata.replace('<total>', '%.2f' %(df2.iloc[0,ix_atc]))

                filedata = filedata.replace('<EnAvgAnnual>', '%.2f' %(df2.iloc[0,ix_aec]/12.))
                filedata = filedata.replace('<DmndAvgAnnual>', '%.2f' %(df2.iloc[0,ix_adc]/12.))
                
                x = range(1,13)
                y1 = df2.iloc[0,ix_mfc:ix_mfc+12].values
                y2 = df2.iloc[0,ix_mec:ix_mec+12].values
                y3 = df2.iloc[0,ix_mdc:ix_mdc+12].values
                for month in range(12):
                    filedata = filedata.replace('<EnAvg%02d>' %(x[month]), '%.2f' %(y2[month]))
                    filedata = filedata.replace('<DmndAvg%02d>' %(x[month]), '%.2f' %(y3[month]))
            except:
                foutLog.write("\n*** Unable to find billing data for %s " %cid )
                print("*** Unable to find billing data for %s " %cid)

            # Write the tex report file for this customer
            with open(os.path.join(dirout, cid+fnameout), 'w') as file:
              file.write(filedata)
        except:
            foutLog.write("\n*** Something failed for customer %s " %cid )
            print("*** Something failed for customer %s " %cid)

    return

def ExtractPlotsFromPDF(dirin='testdata/', fnamein= 'synthetic20.A.boxplots.pdf', 
                               considerCIDs = '', 
                               dirout='testdata/', 
                               fnameout = '.boxplot.pdf',
                               dirlog='testdata/',
                               fnameLog='ExtractPlotsFromPDF.log'):
    # Capture start time of code execution
    codeTstart = datetime.now()
    # open log file
    foutLog = createLog(codeName, "ExtractPlotsFromPDF", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    if considerCIDs != '':
        print('Reading: %s' %os.path.join(dirin,considerCIDs))
        foutLog.write('Reading: %s\n' %os.path.join(dirin,considerCIDs))
        df9 = pd.read_csv(os.path.join(dirin,considerCIDs), 
                          header = 0, 
                          usecols = [0],
                          comment = '#',
                          names=['CustomerID'],
                          dtype={'CustomerID':np.str})
        considerIDs = df9['CustomerID'].tolist()
        considerIDs = [x.replace(" ", "") for x in considerIDs]
    else:
        foutLog.write("\n*** considerCIDs must be specified")
        print("*** considerCIDs must be specified")
    
    # open pdf with figures
    print('Opening plot file: %s' %(os.path.join(dirin, fnamein)))
    foutLog.write('Opening plot file: %s\n' %(os.path.join(dirin, fnamein)))

    try:
        pltPdf1 = PdfFileReader(os.path.join(dirin, fnamein))
        NumPages = pltPdf1.getNumPages()

        for cid in considerIDs:
            try:
                for i in range(0, NumPages):
                    PageObj = pltPdf1.getPage(i)
                    Text = PageObj.extractText() 
                    # print(Text)
                    ResSearch = re.search(cid, Text)
                    if ResSearch != None:
                        foutLog.write("\nCustomer %s found on page %d" %(cid, i))
                        print("Customer %s found on page %d" %(cid, i))
                        pdf_writer = PdfFileWriter()
                        pdf_writer.addPage(pltPdf1.getPage(i))
                        with open(os.path.join(dirout, cid+fnameout), 'wb') as fout:
                            pdf_writer.write(fout)
            except:
                foutLog.write("\n*** Unable to find customer %s " %cid )
                print("*** Unable to find customer %s " %cid)
        
    except:
        foutLog.write("\n*** Unable to open plot file %s " %(os.path.join(dirin, fnamein)))
        print("*** Unable to open plot file %s " %(os.path.join(dirin, fnamein)))

    return

def PlotMonthlySummaries(dirin='testdata/', fnamein= 'summary.synthetic20.A.billing.csv', 
                               considerCIDs = '', 
                               ignoreCIDs = '', 
                               dirout='testdata/', 
                               fnameout='synthetic20.A.boxplots.pdf',
                               dirlog='testdata/',
                               fnameLog='PlotMonthlySummaries.log',
                               ymaxAll=False):

    # Capture start time of code execution
    codeTstart = datetime.now()
    # open log file
    foutLog = createLog(codeName, "PlotMonthlySummaries", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # fetch data from input file
    df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                      skiprows = 3,
                      header = None,
                      # usecols = [0, 1, 2], 
                      # names=['datetimestr', 'Demand', 'CustomerID'],
                      # dtype={'datetimestr':np.str, 'Demand':np.float64, 'CustomerID':np.str}
                      )
    UniqueIDs = df1[0].unique().tolist()

    print('Total number of records read: %d' %df1[0].size)
    foutLog.write('Total number of interval records read: %d\n' %df1[0].size)

    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs=ignoreCIDs, considerCIDs=considerCIDs)

    # open pdf for figures
    print('Opening plot file: %s' %(os.path.join(dirout, fnameout)))
    foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout)))
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    ix_mdc = 5+1*12+1 # monthly demand charges
    ix_mec = 5+2*12+1 # monthly energy charges
    ix_mfc = 5+3*12+1 # monthly facility charges
    ix_mtc = 5+4*12+1 # monthly total charges

    for cid in UniqueIDs:
        fig, (ax0) = plt.subplots(nrows=1, ncols=1, figsize=(8,6), sharex=True) 
        fig.suptitle(fnamein + "/" + cid)
        ax0.set_title('Monthly Charges')
        ax0.set_ylabel('Monthly Charges [$]')
        # ax0.set_xlim([0, 12])

        ymin = 0
        if ymaxAll:
            ymax = np.ceil(df1.iloc[:,ix_mtc:ix_mtc+12].max().max()*2)/2
        
        alpha = 1.0
        
        try:
            try:
                df2 = df1[df1[0]==cid]
                x = np.arange(1, 13)
                y1 = df2.iloc[0,ix_mfc:ix_mfc+12].values
                y2 = df2.iloc[0,ix_mec:ix_mec+12].values
                y3 = df2.iloc[0,ix_mdc:ix_mdc+12].values
                ax0.bar(x, y1, color='C2', label = 'Facility', alpha=alpha)
                ax0.bar(x, y2, color='C1', bottom = y1, label = 'Energy', alpha=alpha)
                ax0.bar(x, y3, color='C0', bottom = y1+y2, label = 'Demand', alpha=alpha, )
                if not ymaxAll:
                    ymax = (np.floor(df2.iloc[:,ix_mtc:ix_mtc+12].max().max()/500.)+1)*500
                ax0.set_ylim([ymin,ymax])
            except:
                foutLog.write("\n*** Unable to create box plot for %s " %cid )
                print("*** Unable to create box plot for %s " %cid)

            ax0.set_xticks(np.arange(1,13))
            handles, labels = ax0.get_legend_handles_labels()
            ax0.legend(reversed(handles), reversed(labels))
            
            pltPdf1.savefig() 
            plt.close()    
            
        except:
            
            foutLog.write("\n*** Unable to create box plot for %s " %cid )
            print("*** Unable to create box plot for %s " %cid)
            
            try:
                plt.close()    
            except:
                pass
    

    # Closing plot files
    print("Closing plot files")
    pltPdf1.close()

    # close log file
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    return

def PlotAnnualSummaries(dirin='testdata/', fnamein= 'summary.synthetic20.A.billing.csv', 
                               considerCIDs = '', 
                               ignoreCIDs = '', 
                               dirout='testdata/', 
                               fnameout='synthetic20.A.piecharts.pdf',
                               dirlog='testdata/',
                               fnameLog='PlotAnnualSummaries.log'):

    # Capture start time of code execution
    codeTstart = datetime.now()
    # open log file
    foutLog = createLog(codeName, "PlotAnnualSummaries", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # fetch data from input file
    df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                      skiprows = 3,
                      header = None,
                      # usecols = [0, 1, 2], 
                      # names=['datetimestr', 'Demand', 'CustomerID'],
                      # dtype={'datetimestr':np.str, 'Demand':np.float64, 'CustomerID':np.str}
                      )
    UniqueIDs = df1[0].unique().tolist()

    print('Total number of records read: %d' %df1[0].size)
    foutLog.write('Total number of interval records read: %d\n' %df1[0].size)

    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs=ignoreCIDs, considerCIDs=considerCIDs)

    # open pdf for figures
    print('Opening plot file: %s' %(os.path.join(dirout, fnameout)))
    foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout)))
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    for cid in UniqueIDs:
        fig, (ax0) = plt.subplots(nrows=1, ncols=1, figsize=(4,4)) 
        fig.suptitle(fnamein + "/" + cid)
        
        try:
            try:
                df2 = df1[df1[0]==cid]
                y = df2.iloc[0,2:5].values.tolist()
                ax0.pie(y, labels = ['Demand', 'Energy', 'Facility'], explode = [0.05, 0, 0], autopct='%1.1f%%', counterclock=False, startangle=90)
                ax0.axis('equal')
            except:
                pass
    
            pltPdf1.savefig() 
            plt.close()    
            
        except:
            
            foutLog.write("\n*** Unable to create box plot for %s " %cid )
            print("*** Unable to create box plot for %s " %cid)
            
            try:
                plt.close()    
            except:
                pass
    

    # Closing plot files
    print("Closing plot files")
    pltPdf1.close()

    # close log file
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    return

def PlotAnnualWhiskers(dirin='testdata/', fnamein= 'summary.synthetic20.A.billing.csv', 
                               highlightCIDs = '', 
                               considerCIDs = '', 
                               ignoreCIDs = '', 
                               dirout='testdata/', 
                               fnameout='synthetic20.A.piecharts.pdf',
                               dirlog='testdata/',
                               fnameLog='PlotAnnualWhiskers.log'):

    # Capture start time of code execution
    codeTstart = datetime.now()
    # open log file
    foutLog = createLog(codeName, "PlotAnnualWhiskers", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)
    
    # fetch data from input file
    df1 = pd.read_csv(os.path.join(dirin,fnamein), 
                      skiprows = 3,
                      header = None,
                      # usecols = [0, 1, 2], 
                      # names=['datetimestr', 'Demand', 'CustomerID'],
                      # dtype={'datetimestr':np.str, 'Demand':np.float64, 'CustomerID':np.str}
                      )
    UniqueIDs = df1[0].unique().tolist()

    print('Total number of records read: %d' %df1[0].size)
    foutLog.write('Total number of interval records read: %d\n' %df1[0].size)

    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs=ignoreCIDs, considerCIDs=considerCIDs)
    HighlightIDs, foutlog = readHighlightIDs(dirin, UniqueIDs, foutLog, highlightCIDs)

    # open pdf for figures
    print('Opening plot file: %s' %(os.path.join(dirout, fnameout)))
    foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout)))
    pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout))

    yb = df1.iloc[:,1].values # annual demand Wh
    y1 = df1.iloc[:,2].values # annual demand charges [$]
    y2 = df1.iloc[:,3].values # annual energy charges [$]
    y3 = df1.iloc[:,4].values # annual facility charges [$]
    y1n = y1/yb*100
    y2n = y2/yb*100
    y3n = y3/yb*100

    for cid in HighlightIDs:
        fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, ncols=1, figsize=(8,6)) # sharex=True
        fig.suptitle(fnamein + "/" + cid)
        fig.subplots_adjust(hspace=0.5)
        
        try:
            try:
                x1n = y1n[df1.index[df1[0]==cid]][0]
                x2n = y2n[df1.index[df1[0]==cid]][0]
                x3n = y3n[df1.index[df1[0]==cid]][0]
                ax0.boxplot(y1n, vert=False)
                ax0.plot(x1n,1,'d')
                ax1.boxplot(y2n, vert=False)
                ax1.plot(x2n,1,'d')
                ax2.boxplot(y3n, vert=False)
                ax2.plot(x3n,1,'d')
                ax0.set_title('Demand Charges [c/kWh]')
                ax1.set_title('Energy Charges [c/kWh]')
                ax2.set_title('Facility Charges [c/kWh]')
            except:
                pass
    
            pltPdf1.savefig() 
            plt.close()    
            
        except:
            
            foutLog.write("\n*** Unable to create whisker plot for %s " %cid )
            print("*** Unable to create whisker plot for %s " %cid)
            
            try:
                plt.close()    
            except:
                pass
    

    # Closing plot files
    print("Closing plot files")
    pltPdf1.close()

    # close log file
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
    return


#%% Create Reports by considerCIDs list
def CreateCustomerReports(dirin='./', 
                    fnamein='IntervalData.normalized.csv', 
                    considerCIDs='', # this list of customers to generate a report on
                    dirin_group='./', 
                    fnamein_group = 'GroupData.normalized.csv', # the group to compare against
                    leaderFlag=True,  # if the consider list is of leaders
                    dirout='./', 
                    fnameout='CustomerReport.pdf', 
                    dirlog='./', 
                    fnameLog='CreateCustomerReport.log'):

    # Capture start time of code execution
    codeTstart = datetime.now()
    
    # open log file
    foutLog = createLog(codeName, "CreateCustomerReports", codeVersion, codeCopyright, codeAuthors, dirlog, fnameLog, codeTstart)

    # load data from file, find initial list of unique IDs. Update log file    
    df1, UniqueIDs, foutLog = getDataAndLabels(dirin,  fnamein, foutLog, datetimeIndex=True)
    df1['day'] = df1.index.dayofyear
    df1['hour'] = df1.index.hour + df1.index.minute/60.
    df1['EnergyCost'] = df1['EnergyCharge'].values / df1['Demand'].values * 100

    # apply ignore and consider CIDs to the list of UniqueIDs. Update log file.
    UniqueIDs, foutLog = findUniqueIDs(dirin, UniqueIDs, foutLog, ignoreCIDs='', considerCIDs=considerCIDs)
    
    # load GROUP data from file, find initial list of unique IDs. Update log file    
    df_group, UniqueIDs_group, foutLog = getDataAndLabels(dirin_group,  fnamein_group, foutLog, datetimeIndex=True)
    df_group['day'] = df_group.index.dayofyear
    df_group['hour'] = df_group.index.hour + df_group.index.minute/60.
    df_group['EnergyCost'] = df_group['EnergyCharge'].values / df_group['Demand'].values * 100

    if not(leaderFlag):
        groupName='Average Leader'
    else:
        groupName='Others'
    

    # loop over each CID
    for cid in UniqueIDs:

        print('Opening plot file: %s' %(os.path.join(dirout, fnameout.replace('.pdf', '_' + cid + '.pdf'))))
        foutLog.write('Opening plot file: %s\n' %(os.path.join(dirout, fnameout.replace('.pdf', '_' + cid + '.pdf'))))
        pltPdf1  = dpdf.PdfPages(os.path.join(dirout, fnameout.replace('.pdf', '_' + cid + '.pdf')))
        
        # heatmaps of rate, demand, and total charge for this customer
        outputThreeHeatmaps(pltPdf1, df1=df1,  title=cid, cid=cid, foutLog=foutLog)
        
        # for the group it should be compared against
        outputThreeHeatmapsGroup(pltPdf1, df0=df1, df1=df_group, title=groupName, cid=groupName, foutLog=foutLog)
        
        # showing what would happen if the others behaved as leaders
        # or how much better the leaders are than the others
        
        # Closing plot files
        print('Closing plot files')
        foutLog.write('Closing plot files\n')
        pltPdf1.close()
    
    logTime(foutLog, '\nRunFinished at: ', codeTstart)
        
    return 