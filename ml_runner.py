import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib


def ml_runner(csv_path):
    df = pd.read_csv(csv_path, index_col=0, header=[0,1]) #add ehader arguments
    pd.set_option('display.max_columns', None)

    #adjust scaler to make inquiries into divergent results
    s_scaler = MinMaxScaler()
    df = pd.DataFrame(s_scaler.fit_transform(df), columns=df.columns) #Need to strip off both headwers
    df_array = np.nan_to_num(df, 0)

    #load the model and predict
    rightleg_model = joblib.load(r'root_dir\config_files\ml-models\rightleg_runlab_model_021323.sav')
    rl_predict = rightleg_model.predict(df_array)
    df_rl = pd.DataFrame(rl_predict, columns=['RL - RunLab'])

    leftleg_model = joblib.load(r'root_dir\config_files\ml-models\leftleg_runlab_model_021323.sav')
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

    df_angles = pd.DataFrame(s_scaler.inverse_transform(df), columns=df.columns)

    final = pd.concat([df_angles, predictions], axis='columns')

    #filename = 'predicted ' + file
    final.to_csv(csv_path, index=True)
    
    return print(csv_path + " has been used to generate prediction.")

if __name__ == "__main__":
    csv_path = r"root_dir\Dataset_1_Ethan_01062023.csv"
    ml_runner(csv_path=csv_path)

