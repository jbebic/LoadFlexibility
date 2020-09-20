JZB20180907
Setting up an environment for use with LoadFlexibility tool chain.

# Background
The LoadFlexibility tool-chain makes extensive use of numerical and plotting libraries and parts of the code have proven to be sensitive to the version of these libraries. To ensure correct execution across multiple computers, it is necessary to control the execution environment. We achieve this by creating a controlled environment named LF-env and store its details within the LoadFlexibility-env.txt file. This file is archived in the GitHub repository and used to set up the target environment on computers used to run the LoadFlexibility tool0-chain.  

# Assumptions
1. A 64-bit version of Windows operating system (Windows 7, or 10)
1. Anaconda development platform, available from (https://www.anaconda.com/distribution/)
1. A current version of LoadFlexibility tool-chain, available from (https://github.com/jbebic/LoadFlexibility)

# Working with the LoadFlexibility environment
## Creating the environment on a target computer
Open Anaconda command prompt and create the environment by following these steps:
1. Start-> All Programs -> Anaconda3 (64-bit) -> Anaconda Prompt
1. Change the directory to the root directory of LoadFlexibility tool-chain
1. Type: "conda create -n LF-env --file LoadFlexibility-env.txt"

## Running Spyder within the new environment
### Method 1
1. Activate the LoadFlexibility environment by executing: "activate LF-env" in the Anaconda prompt.
1. Find out the full path to spyder by executing: "where spyder".
1. Start spyder by typing the full path to it from Anaconda prompt.
1. Exercise the tool-chain as you wish, usually by using a runXXX.py file

### Method 2
1. Start spyder from the Anaconda prompt by executing: "spyder activate LF-env"

## Deactivating the environment
1. Open the anaconda prompt
1. Navigate to the root directory of the LoadFlexibility tool-chain
1. Execute: "deactivate". This will restore the default environment.
