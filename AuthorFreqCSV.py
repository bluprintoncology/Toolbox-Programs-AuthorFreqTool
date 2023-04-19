#AuthorsFrequency, inputs csv of single column titled AUTHORS, output count of author names
#Import streamlit, io and pandas
import streamlit as st
from io import StringIO
from pandas import DataFrame
import pandas as pd
from unidecode import unidecode

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


# File Uploader Widget with specified .csv file type or returns error statement
st.subheader("Select a CSV file")
uploaded_file = st.file_uploader("Choose a .csv file", type = [".csv"])

# Checks to ensure a file is uploaded, then runs AuthorFreq application
if uploaded_file is not None:
     # Creates dataframe with "file-like" object as input
     df = pd.read_csv(uploaded_file)
     df = df["AUTHOR"].apply(unidecode) #removes accents from input
     # Checkbox to allow user to show/hide preview of input dataframe
     st.subheader("Review Input data (Optional)") 
     if st.checkbox('Show input data'):
        st.subheader('Input data')
        st.write(df)
     #st.write(df) # Creates preview by default
     content = list(df)
     separator = " "
     content = separator.join(content)
     L = content.split("," or ".")
     #st.write(L) # Creates preview by default
     authorfreq = pd.Series(L).value_counts()
     autdict = dict(authorfreq)
     #st.write(autdict) # Creates preview by default
     df = pd.DataFrame.from_dict(autdict, orient="index")
    # Checkbox to allow user to show/hide preview of Author Count
     st.subheader("Preview Author Count (Optional)") 
     if st.checkbox('Preview Author Count data'):
        st.subheader('Author Count data')
        st.write(df)
     # Convert Author Count df to csv file
     csv = convert_df(df)
     # File Download Widget for AuthorCount.csv to Downloads folder
     st.subheader("Download Author Count File") 
     st.download_button(
     label="Download AuthorCount.csv",
     data=csv,
     file_name='AuthorCount.csv',
     mime='text/csv',
 )



