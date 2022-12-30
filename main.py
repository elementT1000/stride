import deeplabcut
from sys import argv
from pathlib import Path
import angle_finder
from angle_finder import calculate_angles_from_coordinates
import plnconstants
import write_angles
import pandas as pd


#path_config_file = r'C:\Users\trott\Running_Analysis\Sagittal\config.yaml'
script, root_dir = 'test.py', r'C:\Users\trott\stride\root_dir' # change to argv in order to accept command line arguments
file_ext = ".MP4"

#TODO: adjust this to find af and pf as well, maybe just drop 'if "sr" in name or "sl" in name:'
#and search for .mp4's. Or add pf and af filters.
def get_full_path_list(root_dir, file_ext):
    """
    Returns a list of full file paths for files with the specified file extension in the given directory.
    """
    full_path_list = []
    root_dir_path = Path(root_dir)
    for joints_dict in root_dir_path.glob('*'):
        if joints_dict.suffix == file_ext or joints_dict.suffix == file_ext.lower():
            name = joints_dict.name.split('_')
            if "sr" in name or "sl" in name:
                full_path_list.append(str(joints_dict))
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
        #add another if block for splitting to sagittal THEN splitting left and right
        default, alt = (1, 0) if "sl" in name else (0, 1)
        raw_dfs = {}

        for joints_dict in plnconstants.SAGITTAL_JOINTS:
            for vertex in joints_dict:
                #Uses the Sagittal joints list to filter columns from the DataFrame
                raw_dfs[vertex] = angle_finder.joint_filter(dataframe=df, joints=joints_dict)
        
        #if 'sl' or 'sr' in name:
        def sagittal_angles(raw_dfs: object):
            angle_dfs = []
            for vertex, df in raw_dfs.items():
                if vertex == "Arm":
                    angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="vertical"))
                elif vertex == "Hip":
                    angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge", anticlockwise=default))
                elif vertex == "Knee":
                    angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge", anticlockwise=alt))
                elif vertex == "Ankle":
                    ankle_angles = calculate_angles_from_coordinates(df, vertex, orientation="neutral", anticlockwise=default)
                elif vertex == "Heel":
                    heel_angles = calculate_angles_from_coordinates(df, vertex, orientation="neutral", anticlockwise=default)
                    ankle_angle = ankle_angles['Ankle']
                    heel_angle = heel_angles['Heel']
                    angle_difference = abs(heel_angle - ankle_angle)
                    angle_difference = pd.DataFrame({'Ankle': angle_difference})
                    angle_dfs.append(angle_difference)
                elif vertex == "Toe":
                    angle_dfs.append(calculate_angles_from_coordinates(df, vertex, orientation="hinge", anticlockwise=1, dev_from_straight=True))
                
                sgtl_result = pd.concat(angle_dfs, axis=1)
                column_header = pd.MultiIndex.from_product([['Sagittal Plane'], sgtl_result.columns])
                sgtl_result.columns = column_header
                print(sgtl_result)

            return sgtl_result
        result = sagittal_angles(raw_dfs=raw_dfs)

        #if 'pf' in name:
        def posterior_angles():
            pass

        def anterior_angles():
            pass
        
        #TODO: Maybe here, I can add a title block indicating patient origin, and concatenate all of the angle_dfs.
        #TODO: In order to accomplish, I need a function for every plane.
        #result = pd.concat(angle_dfs, axis=1)
        #Saves the DataFrame as a .csv for storage
        csv_path.append(angle_finder.df_saver(dataframe=result, h5_path=cur_h5))
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
    csv_path = parse_angles_from_h5_files(h5_list)
    #fin_vid_list = get_file_list(root_dir, flp, "_analyzed_labeled.mp4", "_labeled.mp4")

    # Write angles to each labeled video
    '''for fin_vid, csv in zip(fin_vid_list, csv_path):
        write_angles.csv_sagittal_angles_to_video(video=fin_vid, csv=csv)'''
