import deeplabcut
from sys import argv
from pathlib import Path
import angle_finder
import plnconstants
import write_angles
import pandas as pd


path_config_file = r'C:\Users\trott\Running_Analysis\Sagittal\config.yaml'
script, root_dir = 'test.py', r'C:\Users\trott\stride\root_dir'# change to argv in order to accept command line arguments
file_ext = ".MP4"

def get_full_path_list(root_dir, file_ext):
    """
    Returns a list of full file paths for files with the specified file extension in the given directory.
    """
    full_path_list = []
    root_dir_path = Path(root_dir)
    for i in root_dir_path.glob('*'):
        if i.suffix == file_ext or i.suffix == file_ext.lower():
            name = i.name.split('_')
            if "sr" in name or "sl" in name:
                full_path_list.append(str(i))
    return full_path_list

def get_file_list(root_dir, full_path_list, extension, alt_ext):
    """
    Returns a list of h5 files by replacing the file extension of each file in full_path_list with _filtered.h5 or _analyzed.h5.
    """
    file_list = []
    root_dir_path = Path(root_dir)
    for i in full_path_list:
        file = Path(i)
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

def calculate_angles(h5_list):
    """
    Calculates angles with row_runner
    and returns a list of csv paths by running angle_finder.df_saver on each h5 file in h5_list.
    """
    csv_path = []
    for cur_h5 in h5_list:
        #keypoints is unnecessary and goes unused
        df, keypoints = angle_finder.load_h5(cur_h5)
        name = cur_h5.split('_')
        default, alt = (1, 0) if "sl" in name else (0, 1)

        dfs = {}
        for i in plnconstants.SAGITTAL_JOINTS:
            #assign each key as vertex to the dataframe containing the bodyparts coordinates 
            for vertex, bpts in i.items():
                #use each of the items to filter the df that was loaded in, and assign the filtered joints to their vertex
                dfs[vertex] = angle_finder.joint_filter(dataframe=df, joints=i)
                #print(f"DataFrame created for {vertex}.")

#TODO: Maybe I can convert the above code into a (nested?) function that returns a list of dfs that can be passed to the following code.
#Not sure if this will make h5 file management easier of more complicated.

        angle_dfs = []
        
        for vertex, df in dfs.items():
            if vertex == "Arm":
                angle_dfs.append(angle_finder.row_runner(df, vertex, orientation="vertical"))
            elif vertex == "Hip":
                angle_dfs.append(angle_finder.row_runner(df, vertex, orientation="hinge", anticlockwise=default))
            elif vertex == "Knee":
                angle_dfs.append(angle_finder.row_runner(df, vertex, orientation="hinge", anticlockwise=alt))
            elif vertex == "Ankle":
                ankle_angles = angle_finder.row_runner(df, vertex, orientation="neutral", anticlockwise=default)
            elif vertex == "Heel":
                heel_angles = angle_finder.row_runner(df, vertex, orientation="neutral", anticlockwise=default)
                ankle_angle = ankle_angles['Ankle']
                heel_angle = heel_angles['Heel']
                angle_difference = abs(heel_angle - ankle_angle)
                angle_difference = pd.DataFrame({'Ankle': angle_difference})
                angle_dfs.append(angle_difference)
            elif vertex == "Toe":
                angle_dfs.append(angle_finder.row_runner(df, vertex, orientation="hinge", anticlockwise=1, dev_from_straight=True))

        # Concatenate the angle dataframes and save the resulting dataframe as a csv file
        result = pd.concat(angle_dfs, axis=1)
        csv_path.append(angle_finder.df_saver(dataframe=result, h5_path=cur_h5))
    return csv_path

if __name__ == '__main__':
    #control flow
    flp = get_full_path_list(root_dir, '.MP4')
    #deeplabcut.analyze_videos(path_config_file, flp, videotype='.MP4')
    #deeplabcut.create_labeled_video(path_config_file, flp, draw_skeleton=True, displaycropped=True, filtered=False)
    h5_list = get_file_list(root_dir, flp, "_filtered.h5", "_analyzed.h5")
    csv_path = calculate_angles(h5_list)
    fin_vid_list = get_file_list(root_dir, flp, "_analyzed_labeled.mp4", "_labeled.mp4")

    # Write angles to each labeled video
    '''for fin_vid, csv in zip(fin_vid_list, csv_path):
        write_angles.csv_sagittal_angles_to_video(video=fin_vid, csv=csv)'''
