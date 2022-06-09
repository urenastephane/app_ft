import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from copy import deepcopy

def weight_years(y1,y2,y3):
    '''
    Weights for the different years are taken from 
    https://www.ft.com/mim-method
    '''
    #if you have all years available
    if ((y1==y1) and (y2==y2) and (y3==y3)):
        score = 0.5*y3+0.25*y2+0.25*y3
    
    elif ((y2==y2) and (y3 ==y3)):
        score = 0.6*y3+0.4*y2
    
    elif ((y1==y1) and (y3==y3)):
        score = 0.7*y3+0.3*y1
    
    #when none of the above combinations is available, just take the latest avaialble possible
    elif y3==y3:
        score = y3
    
    elif y2==y2:
        score = y2
    
    elif y1 == y1:
        score = y1
    
    else:
        score = np.nan
    
    return score


#from original dataframe get just one column
def gender(row):
    '''
    Check sex columns from both tables (they are in two different languages)
    Return 1 if female, 0 if male
    '''
    gender = row["sex_x"] if row["sex_x"]==row["sex_x"] else row["sex_y"]
    if gender=="Female" or gender=="Femme":
        gender = 1

    elif gender == "Male" or gender=="Homme":
        gender = 0
    
    else:
        gender = np.nan
    return gender

    


def international(row):
    '''
    Xheck all columns regarding nationality
    return 1 if international, 0 if French
    '''
    int = 1
    if row["french"]=="Yes":
        int = 0
    if row["nationality"]=="France":
        int = 0
    if row["nationality1"] =="Française" or row["nationality1"] == "France":
        int = 0
    if row["nationality2"] =="Française" or row["nationality2"] =="France":
        int = 0 

    #if all are missing return missing value
    if (row["french"]!=row["french"]) & (row["nationality"]!=row["nationality"]) & (row["nationality1"]!=row["nationality1"]):
        int = np.nan
        
    return int


def salary(row, years_before = 0):
    '''
    Salary at year3
    It is possible to go back up to n years_before in case the latest salary is missing
    years_before can be max 2 (salary_y1)
    '''
    salary = np.nan
    years = 0
    while salary==np.nan or years<=years_before:
        #goes one back of one year till it finds a valid salary or the max year we can look back is reached
        column = f"salary_y{3-years}"
        if row[column] == row[column]:
            salary = row[column]
        years +=1
    
    return salary


def salary_increase(row, qualtrics = True):
    if qualtrics:
        #First choice: salary increase in percentage multiplied by the first salary
        # It does not use ranges, so it is more precise
        if ((row["salary_y1"] == row["salary_y1"]) and (row["salary_increase"] == row["salary_increase"])):
            increase = row["salary_increase"]*row["salary_y1"]
            perc = row["salary_increase"]
        
        #Second choice: if the first salary is available but the salary increase is not,
        #take the difference between the first salary (BDD) and the last salary (qualtrics)
        elif ((row["salary_y1"]==row["salary_y1"]) and (row["salary_y1"]!=0) and (row["salary_y3"]==row["salary_y3"])):
            increase = row["salary_y3"]-row["salary_y1"]
            perc = increase/row["salary_y1"]

        #Third choice: if we have last salary (qualtrics) and the percentage salary increase (qualtrics)
        #Compute the first salary from the two and then take the difference
        elif ((row["salary_y3"] == row["salary_y3"]) and (row["salary_y3"]!=0)and (row["salary_increase"] == row["salary_increase"])):
            salary_y1 = row["salary_y3"]/(1+row["salary_increase"])
            increase = row["salary_y3"]-salary_y1
            perc = increase/salary_y1

        #Foruth choice: If we just have the last salary and the first salary just from qualtrics, take the difference between the two
        #Compute the difference between the two
        elif ((row["salary_y3"] == row["salary_y3"]) and (row["first_salary"]==row["first_salary"]) and (row["first_salary"]!=0)):
            increase = row["salary_y3"]-row["first_salary"]
            perc = increase/row["first_salary"]

        else:
            increase = np.nan
            perc = np.nan
    
    else:
        #if we do not have qualtrics data then take the difference between y1 and y2 (BDD) if both are available
        if row["salary_y2"]==row["salary_y2"] and row["salary_y1"] == row["salary_y1"] and row["salary_y1"]!=0:
            increase = row["salary_y2"]-row["salary_y1"] 
            perc = increase/row["salary_y1"]
        else:
            increase = np.nan
            perc = np.nan
    
    return [increase, perc]


def satisfaction(row, keep_reccomandations = False):

    y1 = row["satisfaction_y1"]
    y2 = row["satisfaction_y2"]
    if keep_reccomandations == False:
        y3 = row["satisfaction_y3_1"]
    else:
        y3 = (row["satisfaction_y3_1"]+row["satisfaction_y3_1"])/2

    return weight_years(y1,y2,y3)


def career_services(row):
    '''
    Note: career center satisfaction not in qualtrics dataframe --> no data for y3
    latest available info is taken into consideration
    '''

    y1 = row["career_center_y1"]
    y2 = row["career_center_y2"]
    y3 = np.nan

    return weight_years(y1,y2,y3)


def mobility(row, qualtrics = True):
    nationality = row["nationality"] if row["nationality"]==row["nationality"] else row["nationality1"]
    nationality2 = row["nationality2"] if row["nationality2"] == row["nationality2"]  else ""

    if qualtrics:
        work_place = row["job_location_now"] if row["job_location_now"]==row["job_location_now"] else row["job_location_y3"]
    else:
        work_place = row["job_location_y2"] if row["job_location_y2"]==row["job_location_y2"] else row["job_location_y1"]

    if nationality == nationality and work_place==work_place:
        if work_place.lower()!="france" and work_place.lower()!=nationality.lower() and work_place.lower()!=nationality2.lower():
            return 1
        else:
            return 0
    else:
        return np.nan


def career_jump(row):
    junior_words = ['consultant','analyst','consultante','analyste','junior','graduate']
    senior_words = ['manager','senior','associate','chef','responsable','chargée','head','lead','chargé','specialist','ceo']

    #create two lists also for job categories in qualtrics survey
    junior_categories = ["Junior Manager",'Student','Professional','Analyst','Self-employed']
    senior_categories = ['Senior Manager / Executive','President / CEO / MD','Department Head','Other directors / VP','Partner']

    junior = np.array([0,0,0])
    senior = np.array([0,0,0])
    
    category3 = row["job_category_y3"] if type(row["job_category_y3"])==str else "None"

    job1 = row["job_post_y1"] if type(row["job_post_y1"])==str else "None"
    job2 = row["job_post_y2"] if type(row["job_post_y2"])==str else "None"
    job3 = row["job_post_y3"] if type(row["job_post_y3"])==str else "None"

    job = row["job_post_now"] if type(row["job_post_now"])==str else "None"

    if any(word in job1 for word in junior_words):
        junior[0]=1

    if any(word in job1 for word in senior_words):
        senior[0]=1
    
    if any(word in job2 for word in junior_words):
        junior[1]=1

    if any(word in job2 for word in senior_words):
        senior[1]=1
    
    if any(word in job3 for word in junior_words)\
        or (category3 in junior_categories)\
        or any(word in job for word in junior_words):
        junior[2]=1

    if any(word in job3 for word in senior_words)\
        or (category3 in senior_categories)\
        or any(word in job for word in senior_words):
        senior[2]=1

    jump = 0

    #if we have no data return null value
    if np.sum(junior)==0 and np.sum(senior)==0:
        jump =  np.nan
    
    else:
        #if there is a change from junior to senior from any two years there is a career jump
        if senior[1]==1 and junior[0]==1:
            jump = 1
        
        if (senior[2]==1 and (junior[0]==1 or junior[0]==0)) \
            or (senior[2]==1 and (junior[1]==1 or junior[1]==0)) \
            or (senior[2]==1 and junior[0]==0 and junior[1]==0):
            jump = 1
    
    return jump


def factors_df(df, grouping_criteria=[], years_before = 0, qualtrics = True, recommendations = True, q = 0.95, q_increase = 0.95, outliers = "eliminate"):
    
    grouping_criteria = grouping_criteria if type(grouping_criteria)==list else [grouping_criteria]
    
    #create new dataframe
    new_df = pd.DataFrame()

    #add a column for each factor
    new_df["BID"] = df["bid"]
    new_df["is_woman"]= df.apply(gender, axis = 1)
    new_df["is_int"]= df.apply(international, axis = 1)
    new_df["salary_increase_abs"] = df.apply(lambda x: salary_increase(x,qualtrics), axis = 1).apply(lambda x: x[0])
    new_df["salary_increase_perc"] = df.apply(lambda x: salary_increase(x,qualtrics), axis = 1).apply(lambda x: x[1])
    new_df["salary"] = df.apply(lambda x: salary(x, years_before),axis = 1)
    new_df["satisfaction"] = df.apply(lambda x: satisfaction(x,recommendations), axis = 1)
    new_df["career_service"] = df.apply(career_services, axis = 1)
    new_df["mobility"] = df.apply(lambda x: mobility(x, qualtrics), axis = 1)
    new_df["career_jump"] = df.apply(career_jump, axis = 1)

    #add columns for grouping criteria
    for i in grouping_criteria:
        new_df[i] = df[i]

    #compute quantiles salary
    q_low = new_df["salary"].quantile(1-q)
    q_hi  = new_df["salary"].quantile(q)

    #compute quantiles salary increase
    q_high = new_df["salary_increase_abs"].quantile(q_increase)

    if outliers=="eliminate":
        #eliminate salary outliers
        new_df = new_df[(new_df["salary"] < q_hi) & (new_df["salary"] > q_low)]
        #eliminate salary increase outliers
        new_df=new_df[new_df["salary_increase_abs"]<q_high]
    else:
        new_df.loc[(new_df["salary"] < q_hi) & (new_df["salary"] > q_low), "salary"] = np.nan
        new_df.loc[new_df["salary_increase_abs"]<q_high, "salary_increase_abs"] = np.nan

    scaler = MinMaxScaler()
    #numericals=['salary_increase_abs','salary_increase_perc','salary','satisfaction','career_service']
    numericals=['salary_increase_abs','salary_increase_perc','salary','satisfaction','career_service']
    new_df[numericals] = scaler.fit_transform(new_df[numericals])
    
    return new_df

#_______________________________________________________________________________________________________________________

#weigthed sum
def weighted_sum(row,weights):
    tot = 0
    for key, value in weights.items():
        tot+=row[key]*value
    return tot

#function that computes the final score for each possible subgroup
def score(df, group, weights, na_method = 'ignore', weighted = True):
    '''
    na_method = ["ignore", "general", "group"]
    '''
    col = f"Group: {group}"
    col_names = [col,"is_woman", "is_int", "career_jump","satisfaction","career_service","mobility","salary","salary_increase_perc", "salary_increase_abs","total_score","count", "missing_salary_count"]
    
    #this is needed to check if we need to add the extra row for everyone but ASC
    admissions = group == "Admission" 
    admissions_ast = group=="Admission AST"

    result =pd.DataFrame(columns = col_names)
    groups = [i for i in df[group].unique() if i==i]

    if admissions or admissions_ast:
        groups.append("AST (ASTI+ASTF) + DD")

    df_new = deepcopy(df)

    if na_method == "general":
        missing_values = {group : df_new[group].mode()[0],
                        "is_woman": df_new["is_woman"].mode()[0],
                        "is_int": df_new["is_int"].mode()[0],
                        "career_jump": df_new["career_jump"].mode()[0],
                        "satisfaction":df_new["satisfaction"].mean(),
                        "career_service": df_new["career_service"].mean(),
                        "mobility": df_new["mobility"].mode()[0],
                        "salary": df_new["salary"].mean(),
                        "salary_increase_perc": df_new["salary_increase_perc"].mean(),
                        "salary_increase_abs":df_new["salary_increase_abs"].mean()}
        
        df_new.fillna(value = missing_values, inplace = True)

    else:
        groups.extend(["Other","General"])

    result[col] = groups

    for i in groups:
        if i == "General":
            temp= df_new
        
        elif i == "Other":
            temp = df_new.loc[df_new[group].isna(),:]

        elif i == "AST (ASTI+ASTF) + DD":
            if admissions:
                temp = df_new.loc[df_new[group].isin(['ASTF','ASTI','DD']),:]
            else:
                temp = df_new.loc[df_new[group].isin(['AST','DD']),:]
        else:
        #filter the dataframe for one group
            temp = df_new.loc[df_new[group]==i, :]
            
        if na_method == "group":
            try:    
                missing_values = {"is_woman": temp["is_woman"].mode()[0],
                        "is_int": temp["is_int"].mode()[0],
                        "career_jump": temp["career_jump"].mode()[0],
                        "satisfaction":temp["satisfaction"].mean(),
                        "career_service": temp["career_service"].mean(),
                        "mobility": temp["mobility"].mode()[0],
                        "salary": temp["salary"].mean(),
                        "salary_increase_perc": temp["salary_increase_perc"].mean(),
                        "salary_increase_abs":temp["salary_increase_abs"].mean()}

                temp.fillna(value = missing_values, inplace = True)

            except:
                print(f"Value not replaced for group {i} because not enough values")

        if weighted:      
            result.loc[result[col] == i,"is_woman"] = (1-abs(0.5 - temp["is_woman"].mean()))*weights["is_woman"]
            result.loc[result[col] == i, "is_int"] =  temp["is_int"].mean()*weights["is_int"] 
            result.loc[result[col] == i, "career_jump"] = temp["career_jump"].mean()*weights["career_jump"]
            result.loc[result[col] == i, "satisfaction"] = temp["satisfaction"].mean()*weights["satisfaction"]
            result.loc[result[col] == i, "career_service"] = temp["career_service"].mean()*weights["career_service"]
            result.loc[result[col] == i, "mobility"] = temp["mobility"].mean()*weights["mobility"]
            result.loc[result[col] == i, "salary"] = temp["salary"].mean()*weights["salary"]
            result.loc[result[col] == i, "salary_increase_perc"] =  temp["salary_increase_perc"].mean()*weights["salary_increase_perc"]
            result.loc[result[col] == i, "salary_increase_abs"] =  temp["salary_increase_abs"].mean()*weights["salary_increase_abs"]
            result.loc[result[col] == i, "count"] = len(temp)
            result.loc[result[col] == i, "missing_salary_count"] = len(temp[temp.salary.isna()])
        else:
            result.loc[result[col] == i,"is_woman"] = (1-abs(0.5 - temp["is_woman"].mean()))
            result.loc[result[col] == i, "is_int"] =  temp["is_int"].mean()
            result.loc[result[col] == i, "career_jump"] = temp["career_jump"].mean()
            result.loc[result[col] == i, "satisfaction"] = temp["satisfaction"].mean()
            result.loc[result[col] == i, "career_service"] = temp["career_service"].mean()
            result.loc[result[col] == i, "mobility"] = temp["mobility"].mean()
            result.loc[result[col] == i, "salary"] = temp["salary"].mean()
            result.loc[result[col] == i, "salary_increase_perc"] =  temp["salary_increase_perc"].mean()
            result.loc[result[col] == i, "salary_increase_abs"] =  temp["salary_increase_abs"].mean()
            result.loc[result[col] == i, "count"] = len(temp)
            result.loc[result[col] == i, "missing_salary_count"] = len(temp[temp.salary.isna()])

    if weighted:   
        result["total_score"] = result.iloc[:,1:-2].sum(axis=1)

    else:
        result["total_score"] = result.apply(lambda row: weighted_sum(row, weights), axis = 1)
    
    if not weighted:
        names = {}
        for i in result.columns:
            if i in weights.keys():
                names[i] = f"{i} ({weights[i]})"
        result.rename(columns= names,inplace = True)

    return result