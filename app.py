from optparse import Values
import pandas as pd
import utils
import preprocessing
import factors
from copy import deepcopy

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
method_range = st.selectbox("How do you wish to substitute ranges of salaries?", ["mean", "min", "max"], index=0)
use_recommendations= st.checkbox("Do you wish to use also recommendations to compute satisfaction")

if use_recommendations:
    value_binary = st.number_input("Which value do you want to assign to a positive recommendation?", min_value=0, max_value=2, step=1)
else:
    value_binary=2 #not used in reality, but we need an input for the preprocessing function

years = st.number_input("How many years back do you want to go to find a valid salary?", min_value=0, max_value=2, step=1)

if qualtrics_data == False and years == 0:
    years = 1

st.header('Parameters for Computing the Score')
weights = {}
weights["is_woman"] = st.number_input("Weigth for % of women", min_value=None, max_value=None, value=5, step=1)
weights["is_int"] = st.number_input("Weigth for % of international ", min_value=None, max_value=None, value=5, step=1)
weights["career_jump"] = st.number_input("Weigth for career jump", min_value=None, max_value=None, value=5, step=1)
weights["satisfaction"] = st.number_input("Weigth for satisfaction", min_value=None, max_value=None, value=5, step=1)
weights["career_service"] = st.number_input("Weigth for career service satisfaction", min_value=None, max_value=None, value=5, step=1)
weights["mobility"] = st.number_input("Weigth for mobility", min_value=None, max_value=None, value=8, step=1)
weights["salary"] = st.number_input("Weigth for salary", min_value=None, max_value=None, value=20, step=1)
weights["salary_increase_perc"] = st.number_input("Weigth for salary increase in percentage", min_value=None, max_value=None, value=5, step=1)
weights["salary_increase_abs"] = st.number_input("Weigth for salary increase in absolute value", min_value=None, max_value=None, value=5, step=1)

na_method = st.selectbox("How would you like to substitute null values", ["ignore", "general", "group"], index=0)
st.text("Explanation: \n ignore = do not consider the null values in the averages \n general = substitute every missing value with the general average of that variable \n group = sustitute missing values with the average of the subgroup")

status = st.text('Preprocesing the data...')


#preprocess the file
df_prep = preprocessing.preprocessing_df(data, method_range,value_binary)

status.text("Computing all the factors... ")
#compute all the single variables
df_factors = factors.factors_df(df_prep, grouping_criteria=["Admission", "Admission AST"], years_before = years, qualtrics = qualtrics_data, recommendations = use_recommendations)

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

st.header("Analysis")
group = st.selectbox("Grouping to visualize", groups, index=0)
decimals = st.number_input("Decimal positions to visualize?", min_value=0, max_value=None, value=2, step=1)
weighted = st.checkbox("Visualize weighted partial scores")
scores = factors.score(df_factors, group, weights, na_method,weighted)
scores = utils.round_all(scores,decimals)
st.dataframe(scores.astype(str))


