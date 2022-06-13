from optparse import Values
import pandas as pd
import utils
import preprocessing
import factors
from copy import deepcopy
from io import BytesIO
#from pyxlsb import open_workbook as open_xlsb

import streamlit as st


def load_data(year):
    #import BDD file
    df_y1_y2 = utils.import_BDD(f"data/BDD{year}.csv")
    #import qualtrics file (substituted by an empty file if not avaialable)
    df_y3 = utils.import_qualtrics(f"data/qualtrics{year}.csv")
    #merge the two data sources (BDD and qualtrics)
    df_all = pd.merge(df_y1_y2,df_y3, how="outer", on="bid")
    #import file containing admission codes
    admissions = pd.read_csv("data/admission.csv")
    admissions.dropna(inplace = True)
    admissions.drop("STVATTS_DESC", axis = 1, inplace = True)
    #modify something in admission valid just for year 2020
    if year == 2020:
        df = deepcopy(df_all)
        df["Admission"] = df["admission1"]
        df["Admission AST"] = df["admission1"].replace(["ASTF", "ASTI"], "AST")
    else:
        #join the admissions codes with the general df
        df = df_all.merge(admissions, how = "left", left_on = "admission1", right_on = "STVATTS_CODE")
        df.drop("STVATTS_CODE", axis = 1, inplace = True)
    return df


def to_excel(df_factors):
    output = BytesIO()
    with pd.ExcelWriter(output) as writer:
        df_factors.to_excel(writer, sheet_name = "factors", index = False)
        for group in groups:
            temp = factors.score(df_factors, group, weights, na_method, weighted=False)
            temp = utils.round_all(temp,decimals)
            temp.to_excel(writer, sheet_name=group, index=False)
    processed_data = output.getvalue()
    return processed_data



st.title('FT Simulations')
year = st.number_input("Year of analysis", min_value=2018, max_value=2020, step=1)
data_load_state = st.text('Loading data...')
try:
    data = load_data(year)
    data_load_state.text("Done!")
except:
    data = None
    data_load_state.text("No data available for this year")

qualtrics_data = st.checkbox(f"Check if Qualtrics questionnaire available for the promo {year}")


st.header('Parameters for Preprocessing')

c1, c2 = st.columns(2)
method_range = c1.selectbox("How do you wish to substitute ranges of salaries?", ["mean", "min", "max"], index=0)
use_recommendations= c2.checkbox("Do you wish to use also recommendations to compute satisfaction")

if use_recommendations:
    value_binary = c2.number_input("Which value do you want to assign to a positive recommendation?", min_value=1, max_value=2, step=1)
else:
    value_binary=2 #not used in reality, but we need an input for the preprocessing function

years = c1.number_input("How many years back do you want to go to find a valid salary?", min_value=0, max_value=2, step=1)

if qualtrics_data == False and years == 0:
    years = 1

st.header('Weights for Computing the Score')
weights = {}

col1, col2, col3 = st.columns(3)
#specify weight for each factor
weights["is_woman"] = col1.number_input("% of women", min_value=None, max_value=None, value=5, step=1)
weights["is_int"] = col2.number_input("% of international ", min_value=None, max_value=None, value=5, step=1)
weights["career_jump"] = col3.number_input("career jump", min_value=None, max_value=None, value=5, step=1)
weights["satisfaction"] = col1.number_input("satisfaction", min_value=None, max_value=None, value=5, step=1)
weights["career_service"] = col2.number_input("career service satisfaction", min_value=None, max_value=None, value=5, step=1)
weights["mobility"] = col3.number_input("mobility", min_value=None, max_value=None, value=8, step=1)
weights["salary"] = col1.number_input("salary", min_value=None, max_value=None, value=20, step=1)
weights["salary_increase_perc"] = col2.number_input("salary increase in percentage", min_value=None, max_value=None, value=5, step=1)
weights["salary_increase_abs"] = col3.number_input("salary increase in absolute value", min_value=None, max_value=None, value=5, step=1)


st.header('Handling of missing values')

c3,c4 = st.columns((1,4))
#specificy method to handle missing values
na_method = c3.selectbox("Method", ["ignore", "general", "group"], index=0)
c4.markdown("**Explanation**")
c4.markdown("ignore = do not consider the null values in the averages")
c4.markdown("general = substitute every missing value with the general average of that variable")
c4.markdown("group = sustitute missing values with the average of the subgroup")

#___________________________________________________________________________________________________________________
st.header('Handling of outliers')

#select quantiles for salary and for salary increase
st.markdown("Specify the percentage of data to exclude(0 means keeping all observations)")
st.markdown("If 5% is specified is going to eliminate anything lower than 0.025 quantile and higher than the 0.975 percentile")
quantile =1-st.number_input(label = "Salary", min_value = 0.9, max_value = 1.0, value = 0.95, step = 0.01)/2
quantile_increase = 1-st.number_input(label = "Salary Increase", min_value = 0.9, max_value = 1.0, value = 0.95, step = 0.01)/2

#method to deal with outliers
st.markdown("**What do you want to do with outliers?**")
st.markdown("eliminate = eliminate the row")
st.markdown("substitute = substitute the value in that column with null value (keep the values for other columns)")
outliers = st.selectbox("Method", ["eliminate", "substitute"], index=1)

#_______________________________________________________________________________________________________________________
st.header("Analysis")

#start the preprocessing of the data
status = st.text('Preprocesing the data...')

#preprocess the file
df_prep = preprocessing.preprocessing_df(data, method_range,value_binary)
status.text("Computing all the factors... ")

#compute all the single variables
df_factors = factors.factors_df(df_prep, 
                                grouping_criteria=["Admission", "Admission AST"],
                                years_before = years, qualtrics = qualtrics_data,
                                recommendations = use_recommendations,
                                q = quantile,
                                q_increase = quantile_increase,
                                outliers = outliers)

#add info about the chaires if available
try:
    chaires = pd.read_csv(f"data/chaires{year}.csv")
    chaires["Chaires"] = chaires.Chaires.apply(lambda x: x.split(",")[0] if type(x)==str else x)
    df_factors = pd.merge(df_factors, chaires, how = "left", left_on= "BID", right_on="Ecole_BID")
    df_factors.drop("Ecole_BID", axis = 1)
    groups = ["is_woman", "is_int", "Admission", "Admission AST", "Chaires"]
except:
    groups = ["is_woman", "is_int", "Admission", "Admission AST"]
status.text("Done")

#select groups to visualize and formatting options
formatting_group = {"is_woman":"by gender",
                    "is_int": "by origin",
                    "Admission": "by admission",
                    "Admission AST": "by admission (AST tracks all combined)"}

group = st.selectbox("Grouping to visualize", groups, index=0,format_func=lambda x: formatting_group[x])
decimals = st.number_input("Decimal positions to visualize?", min_value=0, max_value=None, value=2, step=1)
weighted = st.checkbox("Visualize weighted partial scores")
scores = factors.score(df_factors, group, weights, na_method,weighted)
scores = utils.round_all(scores,decimals)

#visualize the table for one specific group, highlighting the first column
st.table(scores.astype(str).style.set_properties(**{'background-color': 'yellow'}, subset=[f"total_score"]))

#dowload of the complete excel table
df_xlsx = to_excel(df_factors)
st.download_button(label=f'📥 Download Analysis Year {year}',
                                data=df_xlsx ,
                                file_name= f'analysis{year}.xlsx')



