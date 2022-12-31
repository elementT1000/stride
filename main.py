#import deeplabcut
from sys import argv
from pathlib import Path
import angle_finder
from angle_finder import calculate_angles_from_coordinates
import plnconstants
import write_angles
import pandas as pd

import time


#path_config_file = r'C:\Users\trott\Running_Analysis\Sagittal\config.yaml'
script, root_dir = 'test.py', r'C:\Users\trott\stride\root_dir' # change to argv in order to accept command line arguments
file_ext = ".MP4"

def get_full_path_list(root_dir, file_ext):
    """
    Returns a list of full file paths for files with the specified file extension in the given directory.
    """
    full_path_list = []
    root_dir_path = Path(root_dir)
    for vid_file in root_dir_path.glob('*'):
        if vid_file.suffix == file_ext or vid_file.suffix == file_ext.lower():
            full_path_list.append(str(vid_file))
    return full_path_list

def get_file_list(root_dir, full_path_list, extension, alt_ext):
    """
    Returns a list of h5 files by replacing the file extension of each file in full_path_list with _filtered.h5 or _analyzed.h5.
    """
    file_list = []
    root_dir_path = Path(root_dir)
    for joints_dict in full_path_list:
        file = Path(joints_dict)
        file_name = file.name
        new_file_name = file_name.replace(".MP4", extension)
        new_file_path = root_dir_path / new_file_name

        if not new_file_path.exists():
            new_file_name = new_file_name.replace(extension, alt_ext) 
            new_file_path = root_dir_path / new_file_name
        
        ext = "." + extension.split(".")[1]
        if new_file_path.suffix == ext:
            file_list.append(str(new_file_path))

    return file_list

def parse_angles_from_h5_files(h5_list):
    csv_path = []
    for cur_h5 in h5_list:
        df, _ = angle_finder.load_h5(cur_h5)
        #the following code snippet can be used be expanded to filter for af and pf
        name = cur_h5.split('_')
        
        #TODO: Add a conditional in order to push to a specific set of constants and functions
        #if 'sl' or 'sr' in name:
        #add another if block for splitting to sagittal THEN splitting left and right
        state = True if "sl" in name else 0
        raw_dfs = {}
        for joints_dict in plnconstants.POSTERIOR_FRONTAL_JOINTS: # This would probably be more appropriate as a nested function at the top of the angles functions
            for vertex in joints_dict:
                #Uses the Sagittal joints list to filter columns from the DataFrame
                raw_dfs[vertex] = angle_finder.joint_filter(dataframe=df, joints=joints_dict)
        
        #TODO: Probably should move these to angle_finder
        def sagittal_angles(raw_dfs: object):
            angle_dfs = []
            for vertex, df in raw_dfs.items():
                #Maybe I can just eliminate all of the if-elif-else statements and it will still run
                if vertex == "Arm":
                    angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="vertical"))
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
                
                sgtl_result = pd.concat(angle_dfs, axis=1)
            side = "Left" if state else "Right"
            column_header = pd.MultiIndex.from_product([[f'Sagittal Plane {side}'], sgtl_result.columns])
            sgtl_result.columns = column_header

            return sgtl_result
        #sg_result = sagittal_angles(raw_dfs=raw_dfs)

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
        #pf_result = posterior_angles(raw_dfs=raw_dfs)

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
                    l_knee_difference = pd.DataFrame({'Left Knee': l_knee_difference})
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
                    r_knee_difference = pd.DataFrame({'Right Knee': r_knee_difference})
                    angle_dfs.append(r_knee_difference)
                elif vertex == "afRightAnkle":
                    angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge", dev_from_straight=True))
                elif vertex == "afRightFoot":
                    angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="horizontal"))

                ant_result = pd.concat(angle_dfs, axis=1)
            column_header = pd.MultiIndex.from_product([['Anterior Frontal Plane'], ant_result.columns])
            ant_result.columns = column_header
            print(ant_result)

            return ant_result
        af_result = anterior_angles(raw_dfs=raw_dfs)

        #TODO: Maybe here, I can add a title block indicating patient origin, and concatenate all of the angle_dfs.
        #result = pd.concat([sg_result, pstr_result, ant_result], axis=1)
        csv_path.append(angle_finder.df_saver(dataframe=af_result, h5_path=cur_h5))
        #Maybe just return the DataFrame containing ALL angles and send to a .csv in a seperate line. That would prevent this being triggered prematurly
    return csv_path

if __name__ == '__main__':
    #control flow
    flp = get_full_path_list(root_dir, '.MP4')
    #TODO: Bring over the deeplabcut files that I edited on Big Bertha. 
    #TODO: Potentially, load up a new t4-dlc library if it can be private.
    #deeplabcut.analyze_videos(path_config_file, flp, videotype='.MP4')
    #deeplabcut.create_labeled_video(path_config_file, flp, draw_skeleton=True, displaycropped=True, filtered=False)
    h5_list = get_file_list(root_dir, flp, "_filtered.h5", "_analyzed.h5")
    print(h5_list)
    start = time.time()
    csv_path = parse_angles_from_h5_files(h5_list)
    end = time.time()
    total = end - start
    print("The time to complete parse function is: ", str(total))
    #fin_vid_list = get_file_list(root_dir, flp, "_analyzed_labeled.mp4", "_labeled.mp4")

    # Write angles to each labeled video
    '''for fin_vid, csv in zip(fin_vid_list, csv_path):
        write_angles.csv_sagittal_angles_to_video(video=fin_vid, csv=csv)'''
