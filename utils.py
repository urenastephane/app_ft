import pandas as pd
import numpy as np

#________________________________________________________________________________________________
## FUNCTION TO SPECIFY WEIGHTS

def define_weights():
    print("Specify the weight of each factor")
    weights = {"is_woman":np.nan,
        "is_intl":np.nan,
        "career_jump":np.nan,
        "satisfaction":np.nan,
        "career_service":np.nan,
        "mobility":np.nan,
        "2022_salary":np.nan,
        "salary_increase":np.nan
    }

    while isinstance(weights["is_woman"],int)==False:
        weights["is_woman"] = input("Weight % of women: ")
        try:
            weights["is_woman"] = int(weights["is_woman"])
        except:
            pass

    while isinstance(weights["is_intl"],int)==False:
        weights["is_intl"] = input("Weight % of internationals: ")
        try:
            weights["is_intl"] = int(weights["is_intl"])
        except:
            pass

    while isinstance(weights["career_jump"],int)==False:
        weights["career_jump"] = input("Weight career jump: ")
        try:
            weights["career_jump"] = int(weights["career_jump"])
        except:
            pass

    while isinstance(weights["satisfaction"],int)==False:
        weights["satisfaction"] = input("Weight satisfaction: ")
        try:
            weights["satisfaction"] = int(weights["satisfaction"])
        except:
            pass

    while isinstance(weights["career_service"],int)==False:
        weights["career_service"] = input("Weight career services: ")
        try:
            weights["career_service"] = int(weights["career_service"])
        except:
            pass

    while isinstance(weights["mobility"],int)==False:
        weights["mobility"] = input("Weight mobility: ")
        try:
            weights["mobility"] = int(weights["mobility"])
        except:
            pass

    while isinstance(weights["2022_salary"],int)==False:
        weights["2022_salary"] = input("Weight salary: ")
        try:
            weights["2022_salary"] = int(weights["2022_salary"])
        except:
            pass

    while isinstance(weights["salary_increase"],int)==False:
        weights["salary_increase"] = input("Weight salary increase: ") 
        try:
            weights["salary_increase"] = int(weights["salary_increase"])
        except:
            pass
    return weights

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
        df[i] = df[i].apply(lambda x: round(x,decimals) if type(x)==float and x==x else x)
    return df
