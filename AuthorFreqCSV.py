#AuthorsFrequency, inputs csv of single column titled AUTHORS, output count of author names
#Import streamlit, io and pandas
import streamlit as st
from io import StringIO
from pandas import DataFrame
import pandas as pd

#NEED TO REPLACE ; or . with , in excel using find replace

#Function to convert dataframe to csv

def convert_df(df):
    return df.to_csv().encode('utf-8')

# Add Title for Streamlit App
st.title('AuthorsFrequencyTool')

# File Uploader Widget with specified .csv file type or returns error statement
st.subheader("Select a CSV file")
uploaded_file = st.file_uploader("Choose a .csv file", type = [".csv"])

# Checks to ensure a file is uploaded, then runs AuthorFreq application
if uploaded_file is not None:
     # Creates dataframe with "file-like" object as input
     df = pd.read_csv(uploaded_file)
     # Checkbox to allow user to show/hide preview of input dataframe
     st.subheader("Review Input data (Optional)") 
     if st.checkbox('Show input data'):
        st.subheader('Input data')
        st.write(df)
     #st.write(df) # Creates preview by default
     content = list(df["AUTHORS"])
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



