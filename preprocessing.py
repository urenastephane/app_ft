import numpy as np

#NLP packages used to preprocess job posts
import re
import string
from copy import deepcopy

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')

# SALARY PREPROCESSING 
def salary_prep(column):
    '''
    convert salaries in float in case they aren't already
    '''
    return column.replace({"#VALUE!":np.nan,",":'.'}).astype(float)

def salary_prep_range(column, how = "mean"):
    '''
    Preprocess salaries expressed in ranges
    It is possible to specify:
    - mean: uses the mean of the min and the max of the range
    - min: uses the min of the range
    - max: uses the max of the range
    '''
    if how not in ["mean", "min", "max"]:
        raise ValueError("The methods you can use are: mean, min, max")

    if how =="mean":
        conversion = {"51K€<60K€":(51000+60000)/2,
                    '<50K€':50000,
                    '<30K€':30000,
                    '61K€<70K€': (61000+70000)/2,
                    '71K€<80K€': (71000+80000)/2,
                    '91K€<100K€': (91000+100000)/2,
                    '101K€<150K€': (101000+150000)/2, 
                    '>150K€': 150000, 
                    '81K€<90K€': (81000+90000)/2
                    }
    if how =="min":
        conversion = {"51K€<60K€":51000,
                    '<50K€':50000,
                    '<30K€':30000,
                    '61K€<70K€': 61000,
                    '71K€<80K€': 71000,
                    '91K€<100 K€': 91000,
                    '101K€<150K€': 101000, 
                    '>150K€': 150000, 
                    '81K€<90K€': 81000
                    }

    if how =="max":
        conversion = {"51K€<60K€":60000,
                    '<50K€':50000,
                    '<30K€':30000,
                    '61K€<70K€': 70000,
                    '71K€<80K€': 80000,
                    '91K€<100K€': 100000,
                    '101K€<150K€': 150000, 
                    '>150K€': 151000, 
                    '81K€<90K€': 90000
                    }
    column = column.apply(lambda x: "".join(x.replace('>', "<").split(" ")) if x==x else x)

    return column.map(conversion, na_action = 'ignore')

#___________________________________________________________________________________________
#SALARY INCREASE PREPROCESSING

def increase_prep(column):
    '''
    Trasform the percentage increse written as a string in a number and then divide it by 100
    If there is nan values it returns a nan value
    '''
    return column.apply(lambda x: int(''.join(filter(str.isdigit, x)))/100 if x==x else x)


#_____________________________________________________________________________________________
#SATISFACTION PREPROCESSING

def satisfaction_prep(column, language = "en", value_binary = 2):
    '''
    Convert the satisfaction grading to numbers
    It supports french and english
    '''
    if "Oui" in column.unique().tolist():
        conversion = {"Oui": value_binary,
        "Non":-value_binary}

    else:
        if language =="en":
            conversion = {'Very satisfied':2,
            'Satisfied':1,
            'Neither satisfied nor dissatisfied':0,
            'Unsatisfied':-1,
            'Very unsatisfied':-2
            }
        else:
            conversion = {'Très satisfait(e)':2,
            'Satisfait(e)':1,
            'Ni satisfait(e) ni insatisfait(e)':0,
            'Insatisfait(e)':-1,
            'Très insatisfait(e)':-2}

    return column.map(conversion, na_action = 'ignore')


#__________________________________________________________________________________________
# CAREER SERVICE SATISFACTION

def career_prep(column):
    '''
    This function transforms the career services evaluation into numbers
    '''
    conversion= {'Very useful':3,
    'Rather useful':2,
    'Not really useful':1,
    'Useless':0}

    return column.map(conversion, na_action = 'ignore')


#_________________________________________________________________________________________
#PREPROCESS JOB POSTS

def preprocess_job_post(text):
    """
    Convert to lowercase.
    Rremove URL links, special characters and punctuation.
    Tokenize and remove stop words.
    """
    if text==text:
        stopwords_list = stopwords.words('english') + stopwords.words('french')
        text = text.lower()
        text = re.sub('https?://\S+|www\.\S+', '', text)
        text = re.sub('<.*?>+', '', text)
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub('\n', '', text)
        text = re.sub('[’“”…]', '', text)

        # removing the stop-words
        text_tokens = word_tokenize(text)
        tokens_without_sw = [
            word for word in text_tokens if not word in stopwords_list]
        filtered_sentence = (" ").join(tokens_without_sw)
        text = filtered_sentence
    else:
        text = text
    return text

#____________________________________________________________________________________

def preprocessing_df(df, method_range = "mean",value_binary = 2):
    df_prep = deepcopy(df)
    df_prep["salary_y3"] = salary_prep_range(df_prep.salary_y3, how = method_range)
    df_prep["first_salary"] = salary_prep_range(df_prep.first_salary, how= method_range)

    df_prep["salary_increase"] = increase_prep(df_prep.salary_increase)

    df_prep["career_center_y1"] = career_prep(df_prep.career_center_y1)
    df_prep["career_center_y2"] = career_prep(df_prep.career_center_y2)

    df_prep["satisfaction_y1"] = satisfaction_prep(df_prep["satisfaction_y1"])
    df_prep["satisfaction_y2"] = satisfaction_prep(df_prep["satisfaction_y2"])
    df_prep["satisfaction_y3_1"] = satisfaction_prep(df_prep["satisfaction_y3_1"], language = "fr")
    df_prep["satisfaction_y3_2"] = satisfaction_prep(df_prep["satisfaction_y3_2"],value_binary)

    df_prep["job_post_y1"] = df_prep.job_post_y1.apply(preprocess_job_post)
    df_prep["job_post_y2"] = df_prep.job_post_y2.apply(preprocess_job_post)
    df_prep["job_post_y3"] = df_prep.job_post_y3.apply(preprocess_job_post)
    
    return df_prep