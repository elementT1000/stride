import numpy as np
from sys import argv
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib
from plnconstants import home


def ml_runner(csv_path, planes):
    df = pd.read_csv(csv_path, index_col=0, header=[0,1]) #add ehader arguments
    pd.set_option('display.max_columns', None)

    df_planes = df.loc[:, df.columns.get_level_values(0).isin(planes)]

    #adjust scaler to make inquiries into divergent results
    s_scaler = MinMaxScaler()
    df_scaled = pd.DataFrame(s_scaler.fit_transform(df_planes), columns=df_planes.columns) #Need to strip off both headwers
    #may be able to keep df data structure and convert to 0 here
    df_array = np.nan_to_num(df_scaled, 0)

    #load the model and predict
    rightleg_model = joblib.load(home + r'\product\stride\root_dir\config_files\ml-models\rightleg_Double60_031423.sav')
    rl_predict = rightleg_model.predict(df_array)
    df_rl = pd.DataFrame(rl_predict, columns=['RL - RunLab'])

    leftleg_model = joblib.load(home + r'\product\stride\root_dir\config_files\ml-models\leftleg_Double60_031423.sav')
    ll_predict = leftleg_model.predict(df_array)
    df_ll = pd.DataFrame(ll_predict, columns=['LL - RunLab'])
    
    #The labelencoding tool labels the classes in alphabetical order, so need to decode as such
    mapping = {
        0: 'Initial Strike', 
        1: 'Initial Swing', 
        2: 'Loading Response',
        3: 'Midstance', 
        4: 'Midswing', 
        5: 'Terminal Stance', 
        6: 'Terminal Swing', 
        7: 'Toe Off'
    }
    # Replace the values in the dataframe column using the mapping dictionary
    df_rl.iloc[:, 0] = df_rl.iloc[:, 0].map(mapping)
    
    df_ll.iloc[:, 0] = df_ll.iloc[:, 0].map(mapping)
    
    #Insert a new level 1 header: df_results = pd.concat([df_results], axis=1, keys=['RL - RunLab']).swaplevel(0, 1, 1)
    predictions = pd.concat([df_rl, df_ll], axis='columns') #Columns have different names, so "keys" argument is failing here
    predictions = pd.concat([predictions], axis='columns', keys=['Phase']) #Add level 0 header in seperate step.

    #df_angles = pd.DataFrame(s_scaler.inverse_transform(df_scaled), columns=df.columns)

    final = pd.concat([df, predictions], axis='columns')

    #filename = 'predicted ' + file
    final.to_csv(csv_path, index=True)
    
    return print(csv_path + " has been used to generate prediction.")

if __name__ == "__main__":
    #script, csv_path = argv
    csv_path = r"C:\Users\14124\Downloads\Pontikos_Eli\angles_ep_031323_sr_s_analyzed - Copy.csv"
    plns = ['Sagittal Plane Left', 'Sagittal Plane Right']
    ml_runner(csv_path=csv_path, planes=plns)

