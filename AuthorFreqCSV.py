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
import itertools
import re

##----------------Funtions to be excuted in the application----------------##
#Convert dataframe to csv for export
def convert_df(df):
    return df.to_csv().encode('utf-8')

#One Global Password for all users function
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


if check_password():

##----------------Application Title----------------##
# Add Title for Streamlit App
    st.title('Author Count Tool')


##----------------Work Instructions Tool Overview and Process Steps----------------##
    st.markdown("The author count tool provides an author list with frequency of that author for a particular topic. The topic is selected in collecting the data (eg, pubmed search). The tool will replace special characters automatically. Follow these instructions to create your author list.")
    st.markdown("""
    1. Download data from a PubMed search in **CSV** format (Ensure your search is specific enough to achieve the desired list – ie consider using only clinical trial publications to identify clinician scientists)
    2. Ensure that your spreadsheet has **PMID** at the top of the column for this variable (**ensure all caps – this should be standard in pubmed files**)
    3. Save your file as a CSV
    4. Drag and drop your CSV file into the designated space
    5. Download your Author List!
    """)

##----------------Input File Uploader Widget----------------##
# File Uploader Widget with specified .csv file type or returns error statement
    st.subheader("Select a CSV file")
    uploaded_file = st.file_uploader("Choose a .csv file", type = [".csv"])

##----------------Input File Uploader Widget and Input Data Preview----------------##
# Checks to ensure a file is uploaded, then run app
    if uploaded_file is not None:
        # Creates dataframe with "file-like" object as input
        df = pd.read_csv(uploaded_file)

        # # Checkbox to allow user to show/hide preview of input dataframe
        # st.subheader("Review Input data (Optional)")
        # preview = st.checkbox('Show input data')
        # preview_placeholder = st.empty()

        # if preview:
        #     with preview_placeholder.container():
        #         st.subheader('Input data')
        #         st.write(df) #main df full input data
        #         st.stop() #Box checked: stops run
        # else:
        #     preview_placeholder.empty() #Box unchecked: continues to run and no dataframe shown
        
        #UI message to show tool is runninga
        placeholder=st.empty()
        placeholder.text("Generating Author Count and DOI List. Please wait...")


##----------------Webscrape Using PMID Input and Output to Parameter Lists----------------##
    # Get PMID list for webscrape
        pmidlist=df['PMID'].to_list()

        # Webscrape with Pubmed Parser for Names, Affiliations and DOI
        #completed_date_list = []
        lastname_list=[]
        forename_list = []
        affiliations_list =[]
        doi_url=[]


        for item in pmidlist:
            #PubmedParserforAuthorInfo
            efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s" % (item)
            handle = urlopen(efetch)
            data = handle.read()
            root = ET.fromstring(data)
            for article in root.findall("PubmedArticle"):
                author_list = article.findall("MedlineCitation/Article/AuthorList/Author") #embedded fn,ln affiliation innfo-affiliation
                doi_authorlastname_set =[]
                doi_authorfirstname_set =[]
                for auth in author_list:
                    # Author Lastname
                    auth_lastname = auth.findall('LastName')
                    for lastname in auth_lastname:
                        lastname_list.append(lastname.text) 
                        doi_authorlastname_set.append(lastname.text)
                    # Author Forename
                    auth_forename = auth.findall('ForeName')
                    for forename in auth_forename:
                        forename_list.append(forename.text)
                        doi_authorfirstname_set.append(forename.text)
                    ##Author affiliations
                    affiliations_info = auth.findall('AffiliationInfo')
                    affils_return = len(affiliations_info) #if >1 affiliation listed
                    af_set=[] #list for all affiliations if >1
                    for i in affiliations_info:
                        if affils_return == 1:
                            affil = i.findall('Affiliation')
                            for x in affil:
                                af_set.append(x.text)
                                #print(x.text) #append if one affiliation only to list
                        elif affils_return >1:
                            affil_set = i.findall('Affiliation')
                            for y in affil_set:
                                af_set.append(y.text)
                        elif affils_return == 0:
                            pass
                    affiliations_list.append(af_set)

        # print(affiliations_list)

        # Author list, full names
        full_auth_name =list(map(' '.join, itertools.zip_longest(forename_list, lastname_list,fillvalue = "empty")))

        # Affilations list with null items removed
        full_affiliations_list = [xrs for xrs in affiliations_list if xrs != []]

        # Affiliations filter to pull email information
        email_regex = r"[a-zA-Z0-9\.\-+_]+@[a-zA-Z0-9\.\-+_]+\.[a-zA-Z]+"
        emails=[]    
        for affiliation in full_affiliations_list:
            email_set=[]
            for affil_email in affiliation:
                if re.search(email_regex,affil_email):
                    email_affil = re.findall(email_regex,affil_email)
                    email_affil_str = str(email_affil) #str value
                    email_affil_str = email_affil_str.replace('[','') #remove brackets and '
                    email_affil_str = email_affil_str.replace(']','')
                    email_affil_str =email_affil_str.replace ("'",'')
                    email_set.append(email_affil_str)
                elif 'Email address:' in affil_email:
                    emailaddress_split = affil_email.split(':')[1]
                    #print(emailaddress_split)
                    email_set.append(emailaddress_split)
                elif 'Electronic address:' in affil_email:
                    email_split = affil_email.split(':')[1]
                    #print(email_split)
                    email_set.append(email_split)
                else:
                    email_set.append('')
            emails.append(email_set)

        
        
        # list of emails (nested)
        # print(emails)
        # # list of authorfullnames (not nested)        
        # print(full_auth_name)

        #Drop the @onwards from emails
        sublist_emails=[]
        for sublist in emails:
            for item in sublist:
                subitem_email = item.split('@')[0].lower() #alone = returns less#removes the @ and after email info for just first part to match wih anything in ln
                subitem_nodot = subitem_email.replace('.','')
                subitem_uscore = subitem_nodot.replace('_','')
                subitem = subitem_uscore.replace('-','')
                sublist_emails.append(subitem)
        #print(sublist_emails)
        #set fullname list to all lower case, no spaces
        fn_lower_nospace = [item.replace(' ','').lower() for item in full_auth_name]
        fn_lower=[item.replace('-','') for item in fn_lower_nospace]
        # print(fn_lower)

        tester1 = [l1 for l1 in sublist_emails if any([l2 in l1 for l2 in fn_lower])]
        # # print(tester1)

        shortened_lnlist=[x.lower() for x in lastname_list]
        tester3 = [l1 for l1 in sublist_emails if any([l2 in l1 for l2 in shortened_lnlist])]
        # print(tester3) #prints best match emails vs surname of author

        filtered_list=[]
        for sublist in emails:
            subfiltered_list=[]
            for item in sublist:
                #print(item) #email
                subitem_email = item.split('@')[0].lower() #alone = returns less#removes the @ and after email info for just first part to match wih anything in ln
                subitem_nodot = subitem_email.replace('.','')
                subitem_uscore = subitem_nodot.replace('_','')
                subitem = subitem_uscore.replace('-','')
                if subitem in tester3 or subitem in tester1:
                    subfiltered_list.extend([item])
                else:
                    subfiltered_list.extend([''])
            filtered_list.append(subfiltered_list)

        # print(filtered_list)



#----------------Author Count and Affiliations DataFrame for CSV output----------------##
        #Main df contains all info from webscraoe lists for Author, Affil and Email
        df_main = pd.DataFrame(list(zip(full_auth_name,full_affiliations_list,filtered_list,emails)), columns=['Author (Forename, Lastname)','Affiliation','FilteredEmails',"Email"])

        # Create map to add Publication Count column to main df
        df_main['Publication Count'] = df_main["Author (Forename, Lastname)"].map(df_main["Author (Forename, Lastname)"].value_counts())
        #Filter main df for unique auth so auth name only appears once
        df_main_unique = df_main.drop_duplicates(subset=['Author (Forename, Lastname)'])
        #Sort main unique df by Count from highest to lowest count
        # Output df for csv file
        final_sorted_df = df_main_unique.sort_values(by=['Publication Count'],ascending=False)
        final_sorted_df['Author (Forename, Lastname)'] = final_sorted_df['Author (Forename, Lastname)'].apply(unidecode)
        
#         #st.write(final_sorted_df)

# ##----------------Preview Output Publication Count Table, Downloadable Files for Publication Count and DOI tables------------------------##  
    # # Checkbox to allow user to show/hide preview of Author Count
        placeholder.empty()
    #     st.subheader("Preview Author Count and Affiliations (Optional)") 
    #     if st.checkbox('Preview Author Count and Affiliations data'):
    #         st.subheader('Author Count and Affiliations data')
    #         st.write(final_sorted_df)
        # Convert Author Count df to csv file
        csv = convert_df(final_sorted_df)
        # File Download Widget for AuthorCount.csv to Downloads folder
        st.subheader("Download Author Count and Affiliations File") 
        ste.download_button(
        label="Download AuthorCountandAffiliations.csv",
        data=csv,
        file_name='AuthorCountandAffiliations.csv',
        mime='text/csv')
