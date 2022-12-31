import os
import numpy as np
import pandas as pd
import time
import math

import warnings


def load_h5(filepath: str):
    '''
    Read the H5 file created by the DeepLabCut video analysis.
    Input:
        The complete path to the H5 file.
    Output:
        A pandas dataframe containing keypoints and their x and y values.
    '''
    df = pd.read_hdf(filepath)
    keypoints = df.columns.get_level_values("bodyparts").unique().to_list()

    return df, keypoints

def filter_low_prob(cols, threshold: float):
    mask = cols.iloc[:, 2] < threshold
    cols.iloc[mask, :2] = np.nan
    return cols

def calculate_angles_from_coordinates(dataframe: object, vertex: str, orientation: str, anticlockwise=1, dev_from_straight=False):
    coords = dataframe.values # Return a numpy array
    n = int(coords.shape[1])//2 # n is equal to # of x,y groups
    
    if n == 2:
        x1, y1, x2, y2 = coords[:, 0], coords[:, 1], coords[:, 2], coords[:, 3]
        full_circle_array = np.vectorize(angle_360)(x1-x2, y1-y2)
        
    elif n == 3:
        x1, y1, x2, y2, x3, y3 = coords[:, 0], coords[:, 1], coords[:, 2], coords[:, 3], coords[:, 4], coords[:, 5]
        full_circle_array_1 = np.vectorize(angle_360)(x1-x2, y1-y2) 
        full_circle_array_2 = np.vectorize(angle_360)(x3-x2, y3-y2)
        final = abs(np.subtract(full_circle_array_1, full_circle_array_2))
        if dev_from_straight:
            final = abs(np.subtract(final, 180))

    else:
        print(f"There is not a correct amount of joints selected for this system. The n that was passed is {n}")
        return

    #Neutral measures with a standard unit circle operation, useful for disconnected lines
    if orientation == "neutral" and n == 2:
        def neutral_if_else(val, anticlock):
            if anticlock:
                first_quadrant = np.add(180, val)
                first_quadrant = np.where(first_quadrant > 360, first_quadrant - 360, first_quadrant)
            else:
                first_quadrant = val
            return first_quadrant
        final = np.vectorize(neutral_if_else)(full_circle_array, anticlockwise)

    elif orientation == "horizontal" and n == 2:
        final = abs(np.subtract(full_circle_array, 180))
    
    elif orientation == "vertical" and n == 2:
        def vertical_if_else(val):
            if val > 180:
                return abs(270-val)
            else:
                return abs(90-val)
        final = np.vectorize(vertical_if_else)(full_circle_array)

    elif orientation == "hinge" and n == 3:
        pass

    else:
        print("It appears that the orientation string or the joints passed in do not fit a use case.")

    if anticlockwise==0:
        final = abs(np.subtract(final, 360))
    
    return pd.DataFrame.from_dict({vertex: final})

def angle_360(x: float, y: float):
    '''
    atan2 returns 0-180 for the top two quadrants and -180-0 for the bottom two, 
     so must correct to 0-360 degrees
     *For some reason, the values returned from this appear to be measured clockwise from the left horsizontal line.
    '''
    # Catch the NaN warning from the vectorization method
    if np.isnan(x) or np.isnan(y):
        full_circle = np.nan
        return
    else:
        ang = math.atan2(y, x)
        if ang < 0:
            ang += 2 * math.pi
        full_circle = (180 / math.pi) * ang
    return full_circle

def joint_filter(dataframe: object, joints: dict, pcutoff=0.6):
    '''
    Convert a dataframe containing all joint locations into a numpy array that contains just 
    the x and y locations of the joints selected in the joints argument.
    Input: 
        A pandas dataframe created from a DLC .h5 file. 
        A dictionary of joints of the form {vertex: [joint1, vertex, joint2]} or {vertex: [joint, vertex]}
    Ouput: 
        A pandas dataframe containing the x and y coordinates for the selected joints.
    '''
    # added 'group_keys=False' on 12/25/22 because of warning
    '''FutureWarning: Not prepending group keys to the result index of transform-like apply. 
    In the future, the group keys will be included in the index, regardless of whether the applied function returns a like-indexed object.'''
    df_likely = dataframe.groupby("bodyparts", axis=1, group_keys=False).apply(filter_low_prob, threshold=pcutoff)
    
    for vertex, bpts in joints.items():
        #print(f"Collecting joint info for {vertex}...")
        mask_bp = df_likely.columns.get_level_values("bodyparts").isin(bpts)
        temp_df = df_likely.iloc[:, mask_bp]
        values = ['x', 'y']
        mask_coords = temp_df.columns.get_level_values("coords").isin(values)
        temp_df = temp_df.iloc[:, mask_coords]
        
        fin_df = temp_df.reindex(columns=bpts, level='bodyparts')       
        
    return fin_df

def df_saver(dataframe: object, h5_path: str):
    col_name = dataframe.columns.values
    str_col_name = str(col_name).lstrip('[').rstrip(']')

    head_tail = os.path.split(h5_path)

    output_filename = "angles_" + head_tail[1]
    output_filename = output_filename.replace(".h5", ".csv")

    complete_path = os.path.join(head_tail[0], output_filename)
    
    csv_path = dataframe.to_csv(complete_path)

    return complete_path

