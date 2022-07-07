import pandas as pd
import numpy as np

#________________________________________________________________________________________________________
## FUNCTION TO IMPORT DATAFRAMES

def import_BDD(path):
    df = pd.read_csv(path)
    #remove useless columns from the dataframe
    #From BDD we remove: name, surname, promo
    drop_idx = [1,2,20]
    df.drop(df.columns[drop_idx], axis = 1, inplace=True)
    #rename columns
    df.columns = ["bid",
            "sex",
            "french",
            "nationality",
            "job_y1",
            "job_location_y1",
            "job_sector_y1",
            'satisfaction_y1',
            'career_center_y1',
            "job_y2",
            "job_location_y2",
            "job_sector_y2",
            'satisfaction_y2',
            'career_center_y2',
            'entrepreneur_y1',
            'entrepreneur_y2',
            'job_post_y1',
            'job_post_y2',
            'salary_y1',
            'salary_y2']
    #eliminate rows with just null values
    df.dropna(how = 'all',inplace = True)
        
    return df

def import_qualtrics(path):
    col_names = ['bid',
                'sex',
                'nationality1',
                'nationality2',
                'admission1',
                'admission2',
                'satisfaction_y3_1',
                'satisfaction_y3_2',
                'job_company_now',
                'job_post_now',
                'job_location_now',
                'job_y3',
                'job_company_y3',
                'job_post_y3',
                'job_category_y3',
                'job_function_y3',
                "job_sector_y3",
                'job_location_y3',
                'job_city_y3',
                'salary_y3',
                'salary_increase',
                'first_salary']
    try:
        df = pd.read_csv(path)
        #From Qualtrics we remove: all multiple emails, etc
        drop_idx = np.r_[1:3,24:27]
        df.drop(df.columns[drop_idx], axis = 1, inplace=True)
        df.columns = col_names
        #eliminate rows with just null values
        df.dropna(how="all", inplace = True)
    except:
        print("No qualtrics data available for the 3rd year")
        df = pd.DataFrame(columns = col_names)
    return df

def round_all(df, decimals):
    for i in df.columns:
        df[i] = df[i].apply(lambda x: round(x,decimals) if isinstance(x,(int, float)) and x==x else x)
    return df
