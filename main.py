import deeplabcut
from sys import argv
import subprocess
from pathlib import Path
import angle_finder
from angle_finder import *
from plnconstants import *
from write_angles import *
from ml_runner import ml_runner
import pandas as pd
import time


script, root_dir = argv  # change to argv in order to accept command line arguments. 'main.py', r'C:\Users\14124\stride\root_dir\Subject_7'
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

def filter_joints_df(df: object, constants: list):
    raw_dfs = {}
    for joints_dict in constants: 
        for vertex in joints_dict:
            raw_dfs[vertex] = angle_finder.joint_filter(dataframe=df, joints=joints_dict)
    return raw_dfs

def parse_angles_from_h5_files(h5_list):
    csv_path = []
    concat_list = []
    for cur_h5 in h5_list:
        df, _ = angle_finder.load_h5(cur_h5)
        
        strings = cur_h5.split('_')
        if any(substring in strings for substring in ['sl', 'sr']):
            sag_coord_dfs = filter_joints_df(df, SAGITTAL_JOINTS)
            state = True if "sl" in strings else 0
            concat_list.append(sagittal_angles(raw_dfs=sag_coord_dfs, state=state))

        elif 'pf' in strings:
            pf_coord_dfs = filter_joints_df(df, POSTERIOR_FRONTAL_JOINTS)
            concat_list.append(posterior_angles(raw_dfs=pf_coord_dfs))

        elif 'af' in strings:
            af_coord_dfs = filter_joints_df(df, ANTERIOR_FRONTAL_JOINTS)
            concat_list.append(anterior_angles(raw_dfs=af_coord_dfs))
        
        else:
            print("There doesn't seem to be an indication of what plane of view this is. CHeck the file names.")

    #TODO: Maybe here, I can add a title block indicating patient origin, and concatenate all of the angle_dfs.
    result = pd.concat(concat_list, axis=1).applymap(lambda x: round(x, 2))
    #print(result)
    csv_path.append(angle_finder.df_saver(dataframe=result, h5_path=cur_h5))

    return csv_path

def run_stride(fpl: list):
    #Each inference is informed by a different config file, so we have to control the flow to those files
    for file in fpl:
        path = Path(file)
        file_name = path.name
        name = file_name.split('_')
        if any(substring in name for substring in ['sl', 'sr']):
            deeplabcut.analyze_videos(sagittal_config_file, file, videotype='.MP4')
            deeplabcut.create_labeled_video(sagittal_config_file, file, draw_skeleton=True, displaycropped=True, filtered=False)
        
        elif 'pf' in name:
            deeplabcut.analyze_videos(posterior_config_file, file, videotype='.MP4')
            deeplabcut.create_labeled_video(posterior_config_file, file, draw_skeleton=True, displaycropped=True, filtered=False)

        elif 'af' in name:
            deeplabcut.analyze_videos(anterior_config_file, file, videotype='.MP4')
            deeplabcut.create_labeled_video(anterior_config_file, file, draw_skeleton=True, displaycropped=True, filtered=False)
    
    h5_list = get_file_list(root_dir, fpl, "_filtered.h5", "_analyzed.h5")
    #print(h5_list)

    #start = time.time()
    csv_path = parse_angles_from_h5_files(h5_list) # Returns a list so take the first index in order to access later
    csv_path = str(csv_path[0])
    #end = time.time()
    #total = end - start
    #print("The time to complete parse function is: ", str(total))
    
    fin_vid_list = get_file_list(root_dir, fpl, "_analyzed_labeled.mp4", "_labeled.mp4")
    for vid in fin_vid_list:
        path = Path(vid)
        file_name = path.name
        name = file_name.split('_')

        if 'sl' in name:
            csv_left_angles_to_video(vid, csv_path, lt_x=100, rt_y=500)

        elif 'sr' in name:
            csv_sagittal_angles_to_video(vid, csv_path, lt_x=600, rt_y=400)
        
        elif 'pf' in name:
            csv_posterior_angles_to_video(vid, csv_path)

        elif 'af' in name:
            csv_anterior_angles_to_video(vid, csv_path)

    plns = ['Sagittal Plane Left', 'Sagittal Plane Right']

    ml_runner(csv_path, plns)

if __name__ == '__main__':
    video_list = get_full_path_list(root_dir, '.MP4')
    
    run_stride(video_list)

    #Create a list of all files
    root_dir = Path(root_dir)
    # Convert both lists to sets of strings representing the file paths
    video_set = {str(p) for p in video_list}
    all_files = {str(p) for p in root_dir.glob('*')}    

    #Create a folder to store processed files
    path_0 = Path(video_list[0])
    processed_dir_path = path_0.parent / 'Processed_Files'
    if not processed_dir_path.exists():
        processed_dir_path.mkdir()

    for file in all_files:
        if file not in video_set:
            path_obj = Path(file)
            f = path_obj.name
            new_path = processed_dir_path / f
            path_obj.rename(new_path)

