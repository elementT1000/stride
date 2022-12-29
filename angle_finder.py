import os
import numpy as np
import pandas as pd
import time
import math


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

def row_runner(dataframe: object, vertex: str, orientation: str, anticlockwise=1, dev_from_straight=False):
    angle = dict()
    angle[vertex] = dataframe.apply(lambda row :
        angle_calc(coordinates=row, anticlock=anticlockwise, orient=orientation, dev=dev_from_straight), axis=1
    ).to_numpy()
    angles = pd.DataFrame.from_dict(angle)

    return angles

#I may seperate these out into seperate functions because the parameters used to make the arguements are becoming more
#extensive then necessary 
def angle_calc(coordinates, anticlock, orient="vertical", dev=False):
    pos = coordinates.values
    #print("The numpy array is: " + str(pos))
    series = int(pos.shape[0])
    n = series//2 # n is equal to rows, if the series is x and y coordinates
    pos = pos.reshape((n, 2))

    full_circle_list = []
    if n == 2:
        x1, y1 = pos[0]
        x2, y2 = pos[1]

        single = angle_360(x1-x2, y1-y2)
        
        full_circle_list.append(single)

    elif n == 3:
        x1, y1 = pos[0]
        x2, y2 = pos[1]
        x3, y3 = pos[2]

        #still have to figure out how to do anticlockwise
        pair1 = angle_360(x1-x2, y1-y2)
        pair2 = angle_360(x3-x2, y3-y2)

        full_circle_list = [pair1, pair2]

    else:
        print("There is not a correct amount of joints selected for this system.")

    if orient == "hinge" and n == 3:
        final = abs(full_circle_list[0] - full_circle_list[1])
        #The following measures the deviation of the hinge point from a straight line
        if dev:
            final = abs(180 - final)

    elif orient == "neutral" and n == 2:
        if anticlock:
            first_quadrant = full_circle_list[0] + 180
            if first_quadrant > 360:
                first_quadrant -= 360
        else:
            first_quadrant = full_circle_list[0]
            
        final = first_quadrant

    elif orient == "vertical" and n == 2:
        if full_circle_list[0] > 180:
            final = abs(270-full_circle_list[0])
        else:
            final = abs(90-full_circle_list[0])

    else:
        print("It appears that the orientation string or the joints passed in do not fit a use case.")

    if anticlock==0:
        final = abs(360-final)
        
    return final

def angle_360(x: float, y: float):
    '''
    atan2 returns 0-180 for the top two quadrants and -180-0 for the bottom two, 
     so must correct to 0-360 degrees
     For some reason, the values returned from this appear to be measured clockwise from the left horsizontal line.
    '''
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
    # added 'group_keys=True' on 12/25/22 because of warning
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

