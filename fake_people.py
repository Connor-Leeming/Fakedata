from datetime import datetime as dt,timedelta
import numpy as np
import pandas as pd
import random
from extract import extract

'''
NEEDS ACCESS TO THE FOLLOWING FILES:
    name_data.xlsx
    age_data.xlsx
    diagnosis_rates.xlsx
    extract.py
        diagnosis_rates.xlsx
'''


def generate(n):

    # Create global vars of clean data for Person class to access
    def global_data_functions():

        '''
        creates dictionaries from spreadsheets
        outputs to global vars, which are used by Person calss
        '''

        def make_first_name_dict():
            '''
            opens 'name_data.xlsx/Boys_f and /Girls_f'
            returns {
                
                'm': {
                    year : [names],
                    year : [names]
                },
                'f' : {
                    year : [names],
                    year : [names],
                }
            }
            '''

            def get_name_data(sex):

                '''
                'm' or 'f'
                opens 'name_data.xlsx'
                transforms into useable df
                '''
                #open file m or f
                if sex == 'm':
                    df = pd.read_excel('name_data.xlsx',sheet_name='Boys_f')
                elif sex == 'f':
                    df = pd.read_excel('name_data.xlsx',sheet_name='Girls_f')
                #set new index by date
                df = df.transpose()
                fn = np.vectorize(lambda x: int(x))
                newindex = list(fn(list(df.head(1).values[0])))
                df.columns = newindex
                df.drop(['Date'],inplace=True)
                return df
            
            def construct(sex):
                df = get_name_data(sex)
                dd = {}
                for y in list(df.columns):
                    sorted = df[y][df[y].notnull()].sort_values()
                    dd[y] = list(sorted.index)
                return dd
            
            m_names_dict = construct('m')
            f_names_dict = construct('f')
            
            return {
                
                'm':m_names_dict,
                'f':f_names_dict
            }
        def make_first_name_weights_list():
            '''
            opens 'name_data.xlsx/weights'
            returns [decending name weights]
            '''
            data = pd.read_excel('name_data.xlsx',sheet_name='weights')
            return data[1:-1]['Unnamed: 4'].values
        def make_age_dict():
            '''
            opens 'age_data.xlsx':
                    /age_female,
                    /age_male,
                    /weights 
            returns {
                'm' : {
                    'bins' : [age bins, ordered by weight]
                    'weights' : [weights]
                },
                'f' : {...}
                }
            }
            '''
            def make_sub_dict(sex):
                if sex == 'm':
                    sheet = 'age_male'
                elif sex == 'f':
                    sheet = 'age_female'
                
                raw = pd.read_excel('age_data.xlsx',sheet_name=sheet)
                srtd = raw.sort_values(by=['p'],ascending=False)
                w = list(srtd['p'].apply(lambda x: round(x*10,3)))
                a = list(srtd['age'])

                return (a,w)
            
            md = make_sub_dict('m')
            fd = make_sub_dict('f')

            return {
                'm': {
                    'bins':md[0],
                    'weights':md[1]
                },
                'f': {
                    'bins':fd[0],
                    'weights':md[1]
                }
            }
        def make_first_name_years_list():
            '''
            opens name_data.xlsx/Boys_f
            returns [name year bins]
            '''
            data = pd.read_excel('name_data.xlsx',sheet_name='Boys_f')
            return list(data['Date'])
        def make_last_name_dict():
            '''
            opens 'name_data.xlsx/surnames
            returns {

                'names': [500 surnames],
                'weights':[corresponding weights]
            }
            '''
            data = pd.read_excel('name_data.xlsx',sheet_name='surnames')
            surnames = list(data['Surname'])
            weights = list(data['weight'].apply(lambda x: round(x,5)))
            
            return {
                'names':surnames,
                'weights':weights
            }
        def make_diagnoses_dict():
            male = extract('male')
            female = extract('female')

            return {
                'm':male,
                'f':female
            }
        def diagnosis_codes():
            codes = pd.read_excel('diagnosis_rates.xlsx',sheet_name='recoding')
            codes.set_index('diagnosis',inplace=True)
            return codes

        global age_dict
        global first_name_dict
        global first_name_weights_list
        global first_name_years_list
        global last_name_dict
        global diagnoses_dict
        global codes

        age_dict = make_age_dict()
        first_name_dict = make_first_name_dict()
        first_name_weights_list = make_first_name_weights_list()
        first_name_years_list = make_first_name_years_list()
        last_name_dict = make_last_name_dict()
        diagnoses_dict = make_diagnoses_dict()
        codes = diagnosis_codes()

    global_data_functions()

    # Define Person class
    class Person():
        def __init__(self):
            self.sex = None

            self.age = None
            self.age_bin = None
            self.dob = None
                    
            self.first_name = None
            self.last_name = None

            self.diagnoses = None

            def give_sex(self):
                ''''
                sets self.sex: 'm' or 'f' with weights (1.05,1)
                '''
                self.sex = random.choices(['m','f'],[0.99,1])[0]

            def give_age(self):
                '''
                sets self.age
                '''
                #get bins and weights from global dict
                bins = age_dict[self.sex]['bins']
                weights = age_dict[self.sex]['weights']

                #get an age
                age_bin = random.choices(bins,weights=weights)[0]
                adjustment = random.randint(0,4)
                age = age_bin + adjustment

                #set self.age
                if age < 20:
                    self.age_bin = 20
                else:
                    self.age_bin = age_bin
                self.age = age

            def give_dob(self):
                '''
                sets self.dob
                random day of birthyear
                '''
                #calc birthyear from age
                birthyear = dt.now().year - self.age

                #get jan1 of birthyear
                jan1_str = '01/01/'+str(birthyear)
                jan1_dt = dt.strptime(jan1_str,"%d/%m/%Y")

                #add random amount of days
                new_dob_dt = jan1_dt + timedelta(days=random.randint(0,364))

                #set self.dob
                self.dob = new_dob_dt

            def give_first_name(self):
                '''
                sets self.first_name
                '''
                #get name_year bucket
                def closest(lst, K):
                    'returns the closest item in the list to k'
                    lst = np.asarray(lst)
                    idx = (np.abs(lst - K)).argmin()
                    return lst[idx]
                
                weights = first_name_weights_list
                names = first_name_dict[self.sex][closest(first_name_years_list,self.dob.year)]
                name = random.choices(names,weights=weights)[0]
                self.first_name = name
        
            def give_last_name(self):
                global last_name_dict
                names = last_name_dict['names']
                weights = last_name_dict['weights']

                name = random.choices(names,weights=weights)[0]
                self.last_name = name
            
            def give_diagnoses(self):
                # Get the probabilites of each diagnosis, given sex and age bin
                    # from global diagnoses dict, save as df
                probs = pd.DataFrame(diagnoses_dict[self.sex][self.age_bin])

                # Add a random roll column, float [0,1)
                probs['roll'] = np.random.random(size=len(probs.index))

                # Add a boolean column on (roll < prob)
                probs['bool'] = (probs['roll'] < probs[self.age_bin])
                
                # self.diagnoses names
                ds = list((probs[probs['bool'] == True]).index)
                
                # Recode diagnosis names
                recoded = [codes.loc[x,'code'] for x in ds]
                
                # Set self.diagnoses to recoded names
                self.diagnoses = recoded
        
            give_sex(self)
            give_age(self)
            give_dob(self)
            give_first_name(self)
            give_last_name(self)
            give_diagnoses(self)

        def as_dict(self):

            return {
                
                'sex':self.sex,
                'age':self.age,
                'dob':self.dob,
                'name':self.first_name,
                'surname':self.last_name,
                'diagnoses':self.diagnoses
            }
        
            
    
    return pd.DataFrame([Person().as_dict() for i in range(n)])