# Introduction
This package analyses the coverage of a given raw text file in your different base word lists.
The results will be summarised in an excel file. This contains:

+ Overview of your raw text file and base word lists. Counts tokens and distinct types of the raw text and tokens plus families in base word lists.
+ Coverage of your raw text in a specific base word list or cumulated over all base word lists in percent. Analysis for all tokens of a raw text or just the distinct types. The output contains lists of raw text tokens in/not in a specific base word list.
+ Coverage of your base word lists in a given raw text in percent. The excel file contains lists of base word list families in/not in the raw text. 

# Installation
There are a few dependencies that must be resolved before you can use
this program.  

+ To run this program python 3 is required. As of now the latest version
is 3.5.2 and can be downloaded [here](https://www.python.org/downloads/release/python-352/).
Make sure to check the boxes that add python to your environment variables
and install the installation tool pip.
+ There is one additional dependency, a package from John McNamara called 
XlsxWriter. It provides excellent capabilities to create Excel documents in
python. For further information regarding this project click [here](http://xlsxwriter.readthedocs.io/).
To install it please open the command line and execute the following command:
    `pip install xlsxwriter`    
+ Download the Vocabulary Coverage Analyzer from this repository and extract the files.
 
# Basic Usage
Analyzing your text files needs just two simple steps:  

+ Adjusting the config.ini

   The config.ini file is in the extracted `src` folder. Adjust the original file or create different copies for every text you want to analyze. This file contains different sections that influence the execution of the program. The first two sections direct the program to the raw text files and base word lists that should be analysed. Please fill in the file paths to your raw text and the base word lists for the comparison.  If you are not in possesion of base word lists you can use those in the `example` folder. The third section contains the output file path for the Excel worksheet. 

+ Executing the program

   Open the command line at the location of the extracted files. To analyze a text with VCA please execute the following command and inform the program which config.ini to use as follows:  
   `python LanguageStats.py "C:\the\path\to\your\config.ini"`

The coverage will be analysed and the results will be stored in a convenient Excel worksheet.