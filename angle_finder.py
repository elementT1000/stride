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

def calculate_angles_from_coordinates(dataframe: object, vertex: str, orientation: str, anticlockwise=1, dev_from_straight=False):
    coords = dataframe.values # Return a numpy array
    n = int(coords.shape[1])//2 # n is equal to # of x,y groups
    
    if n == 2:
        x1, y1, x2, y2 = coords[:, 0], coords[:, 1], coords[:, 2], coords[:, 3]
        full_circle_array = np.vectorize(angle_360)(x1-x2, y1-y2)
        full_circle_array = np.where(full_circle_array == None, np.nan, full_circle_array)
        
    elif n == 3:
        x1, y1, x2, y2, x3, y3 = coords[:, 0], coords[:, 1], coords[:, 2], coords[:, 3], coords[:, 4], coords[:, 5]
        full_circle_array_1 = np.vectorize(angle_360)(x1-x2, y1-y2) 
        full_circle_array_2 = np.vectorize(angle_360)(x3-x2, y3-y2)
        full_circle_array_1 = np.where(full_circle_array_1 == None, np.nan, full_circle_array_1)
        full_circle_array_2 = np.where(full_circle_array_2 == None, np.nan, full_circle_array_2)
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
        if anticlockwise:
            final = abs(np.subtract(full_circle_array, 180))
        else: 
            #Catches the case of the right foot for anterior frontal.
            final = abs(np.subtract(full_circle_array, 360))
    
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

def coords_to_csv(dataframe: object, vertex: str):
    coords = dataframe.values # Return a numpy array
    n = int(coords.shape[1])//2 # n is equal to # of x,y groups
    
    if n == 1:
        x, y = coords[:, 0], coords[:, 1]
        x_label = vertex + "X"
        y_label = vertex + "Y"
        return pd. DataFrame.from_dict({x_label: x}), pd. DataFrame.from_dict({y_label: y})
    
    else:
        print("Not the right amount of coords for the get_coords function.")
        pass

def sagittal_angles(raw_dfs: object, state: bool):
    angle_dfs = []
    for vertex, df in raw_dfs.items():
        #Maybe I can just eliminate all of the if-elif-else statements and it will still run
        if vertex == "Arm":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="vertical"))
        elif vertex == "Elbow":
            elbow_x, elbow_y = coords_to_csv(df, vertex)
            angle_dfs.append(elbow_x)
            angle_dfs.append(elbow_y)
        elif vertex == "Hip":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge", anticlockwise=state))
        elif vertex == "Knee":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge", anticlockwise=(not state)))
        elif vertex == "Ankle":
            ankle_angles = calculate_angles_from_coordinates(df, vertex, orientation="neutral", anticlockwise=state)
        elif vertex == "Heel":
            heel_angles = calculate_angles_from_coordinates(df, vertex, orientation="neutral", anticlockwise=state)
            ankle_angle = ankle_angles['Ankle']
            heel_angle = heel_angles['Heel']
            angle_difference = abs(heel_angle - ankle_angle)
            angle_difference = pd.DataFrame({'Ankle': angle_difference})
            angle_dfs.append(angle_difference)
        elif vertex == "Toe":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge", dev_from_straight=True))
        elif vertex == "Ank":
            ankle_x, ankle_y = coords_to_csv(df, vertex)
            angle_dfs.append(ankle_x)
            angle_dfs.append(ankle_y)
        
        sgtl_result = pd.concat(angle_dfs, axis=1)
    side = "Left" if state else "Right"
    sgtl_result = sgtl_result.add_prefix(side)
    column_header = pd.MultiIndex.from_product([[f'Sagittal Plane {side}'], sgtl_result.columns])
    sgtl_result.columns = column_header

    return sgtl_result

def posterior_angles(raw_dfs: object):
    angle_dfs = []
    for vertex, df in raw_dfs.items():
        if vertex == "pfWaist":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="horizontal"))
        elif vertex == "pfLeftFemurHead":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="vertical"))
        elif vertex == "pfLeftKnee":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge", dev_from_straight=True))
        elif vertex == "pfLeftAnkle":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge", dev_from_straight=True))
        elif vertex == "pfRightFemurHead":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="vertical"))
        elif vertex == "pfRightKnee":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge",  dev_from_straight=True))
        elif vertex == "pfRightAnkle":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge",  dev_from_straight=True))

        pstr_result = pd.concat(angle_dfs, axis=1)
    #Executing on every loop, try moving it out
    column_header = pd.MultiIndex.from_product([['Posterior Frontal Plane'], pstr_result.columns])
    pstr_result.columns = column_header

    return pstr_result

def anterior_angles(raw_dfs: object):
    angle_dfs = []
    for vertex, df in raw_dfs.items():
        if vertex == "afLeftThigh":
            #Get the ab/adduction value, then use this angle to estimate knee var/val
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="vertical"))
            L_thigh_angles = calculate_angles_from_coordinates(df, vertex, orientation="neutral")
        elif vertex == "afLeftShin":
            #repeating code block, time for a nested function
            L_shin_angles = calculate_angles_from_coordinates(df, vertex, orientation="neutral")
            L_thigh_angle = L_thigh_angles['afLeftThigh']
            L_shin_angle = L_shin_angles['afLeftShin']
            l_knee_difference = abs(L_thigh_angle - L_shin_angle)
            l_knee_difference = pd.DataFrame({'afLeftKnee': l_knee_difference})
            angle_dfs.append(l_knee_difference)
        elif vertex == "afLeftAnkle":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge", dev_from_straight=True))
        elif vertex == "afLeftFoot":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="horizontal"))
        elif vertex == "afRightThigh":
            #Get the ab/adduction value, then use this angle to estimate knee var/val
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="vertical"))
            R_thigh_angles = calculate_angles_from_coordinates(df, vertex, orientation="neutral")
        elif vertex == "afRightShin":
            R_shin_angles = calculate_angles_from_coordinates(df, vertex, orientation="neutral")
            R_thigh_angle = R_thigh_angles['afRightThigh']
            R_shin_angle = R_shin_angles['afRightShin']
            r_knee_difference = abs(R_thigh_angle - R_shin_angle)
            r_knee_difference = pd.DataFrame({'afRightKnee': r_knee_difference})
            angle_dfs.append(r_knee_difference)
        elif vertex == "afRightAnkle":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge", dev_from_straight=True))
        elif vertex == "afRightFoot":
            angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="horizontal", anticlockwise=0))

        ant_result = pd.concat(angle_dfs, axis=1)
    column_header = pd.MultiIndex.from_product([['Anterior Frontal Plane'], ant_result.columns])
    ant_result.columns = column_header

    return ant_result

def df_saver(dataframe: object, h5_path: str):
    col_name = dataframe.columns.values
    str_col_name = str(col_name).lstrip('[').rstrip(']')

    #TODO: Chnage these to pathlib operations
    head_tail = os.path.split(h5_path)

    output_filename = "angles_" + head_tail[1]
    output_filename = output_filename.replace(".h5", ".csv")

    complete_path = os.path.join(head_tail[0], output_filename)
    
    csv_path = dataframe.to_csv(complete_path)

    return complete_path

