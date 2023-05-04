#AuthorsFrequency, inputs csv of single column titled AUTHORS, output count of author names
#Import streamlit, io and pandas
import streamlit as st
from io import StringIO
from pandas import DataFrame
import pandas as pd
from unidecode import unidecode
#Added for webscraping
import xml.etree.ElementTree as ET
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import streamlit_ext as ste

##-------Funtions to be excuted in the application-------
#Convert dataframe to csv for export
def convert_df(df):
    return df.to_csv().encode('utf-8')

##-------App Title-------
# Add Title for Streamlit App
st.title('Author Count Tool')

##-------Work Instructions Tool Overview and Process Steps-------
st.markdown("The author count tool provides an author list with frequency of that author for a particular topic. The topic is selected in collecting the data (eg, pubmed search). The tool will replace special characters automatically. Follow these instructions to create your author list.")
st.markdown("""
1. Download data from a PubMed search in **CSV** format (Ensure your search is specific enough to achieve the desired list – ie consider using only clinical trial publications to identify clinician scientists)
2. Prepare your excel spreadsheet by labeling the first cell of the columns which includes your author data as AUTHOR (**ensure all caps**)
    - If using PubMed2XL data for the author list, be sure to Find/Replace “||” with “, “ before saving (**ensure space is included in replace**)
3. Save your file as a CSV
4. Pubmed CSV files will have author last name and first initial – if you would like to get the full author names, use PubMed2xl to collect detailed information and use that as your source data
5. Examine results before downloading to confirm
6. Download your Author List!
""")

##-------Upload Files-------
# File Uploader Widget with specified .csv file type or returns error statement
st.subheader("Select a CSV file")
uploaded_file = st.file_uploader("Choose a .csv file", type = [".csv"])

# Checks to ensure a file is uploaded, then runs AuthorFreq application
if uploaded_file is not None:
     # Creates dataframe with "file-like" object as input
     df = pd.read_csv(uploaded_file)
     #add list readout for PMID
     pmidlist=df['PMID'].to_list()
     df["AUTHOR"].replace(regex=True, inplace=True, to_replace=r'\|\|', value=r', ') #find and replace '||' with ',[space]' 
     df = df["AUTHOR"].apply(unidecode)#removes accents from input
     # Checkbox to allow user to show/hide preview of input dataframe
     st.subheader("Review Input data (Optional)")
     preview = st.checkbox('Show input data')
     preview_placeholder = st.empty()

     if preview:
        with preview_placeholder.container():
            st.subheader('Input data')
            st.write(df) #main df full input data
            st.stop() #Box checked: stops run
     else:
        preview_placeholder.empty() #Box unchecked: continues to run and no dataframe shown

     placeholder=st.empty()
     placeholder.text("Generating Author Count and DOI List. Please wait...")

     content = list(df)
     separator = " "
     content = separator.join(content)
     L = content.split("," or ".")
     #st.write(L) # Creates preview by default
     authorfreq = pd.Series(L).value_counts()
     autdict = dict(authorfreq)
     #st.write(autdict) # Creates preview by default
     df = pd.DataFrame.from_dict(autdict, orient="index")
    ##----------------Start of Webcrawl for DOI table------------------------##
    #Lists with all authors in entire input document
     auth_name_set=[]
     doi_url=[]
     pmid_df_list=[]
     for item in pmidlist:
        #PubmedParserforAuthorInfo
        efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s" % (item)
        handle = urlopen(efetch)
        data = handle.read()
        root = ET.fromstring(data)
        #bs4Parser for doi
        doi_article  = requests.get(efetch)
        soup = BeautifulSoup(doi_article.content,'xml')
        doi = soup.find("ELocationID") 
        if doi is not None:   
            doi_text = doi.text
        ##Scrape DOI to list format for each PMID
            doi_url.append("https://doi.org/"+doi_text)
        else:
            doi_url.append('')
        #PMID float to string for list
        pmid_df_list.append(str(item))
        #Lists with each PMID author set, to be appended to main list as sublist
        forename_set_PMID = []
        lastset_PMID = []
        auth_name_set_PMID=[]
        for article in root.findall("PubmedArticle"):
            forename = article.findall("MedlineCitation/Article/AuthorList/Author/ForeName")
            lastname = article.findall("MedlineCitation/Article/AuthorList/Author/LastName")
            for i in forename:
                forename_set_PMID.append(i.text)
            for l in lastname:
                lastset_PMID.append(l.text)
            for ln,init in zip(lastset_PMID,forename_set_PMID):
                auth_name_set_PMID.append(ln+' '+init)
        auth_name_set.append(auth_name_set_PMID)
     #List of all PMID Authors in auth_name_set=[]
     #Get 1st and last author names in separate lists
     first_auth =[]
     last_auth =[]
     for auth_items in auth_name_set:
         first_auth.append(auth_items[0])
         last_auth.append(auth_items[-1])
    ##List for PMID, FirstAuth, LastAuth, Authors, DOI
    ##Convert to df w/list and zip
     pubinfo_doi_df = pd.DataFrame(list(zip(pmid_df_list,first_auth,last_auth,auth_name_set,doi_url)),columns=['PMID','FirstAuthor (Lastname,Forename)','LastAuthor (Lastname,Forename)','Authors (Lastname,Forename)','DOI_link'])
    ##-----------------------------------------------------------------------##
    # Checkbox to allow user to show/hide preview of Author Count
     placeholder.empty()
     st.subheader("Preview Author Count (Optional)") 
     if st.checkbox('Preview Author Count data'):
        st.subheader('Author Count data')
        st.write(df)
     # Convert Author Count df to csv file
     csv = convert_df(df)
     # File Download Widget for AuthorCount.csv to Downloads folder
     st.subheader("Download Author Count File") 
     ste.download_button(
     label="Download AuthorCount.csv",
     data=csv,
     file_name='AuthorCount.csv',
     mime='text/csv')
    # File Download Widget for PMID_DOI.csv to Downloads folder
     st.subheader("Download Author Information and Link File") 
     csv_doi = convert_df(pubinfo_doi_df)
     ste.download_button(
     label="Download AuthorInfoandLink.csv",
     data=csv_doi,
     file_name='AuthorInfoandLink.csv',
     mime='text/csv')
