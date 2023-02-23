from pathlib import Path
import typing
import cv2
import pandas as pd
from tqdm import tqdm
import numpy as np
from sys import argv
        

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

def frame_to_video(video: str, rt_y=500, lt_x=75, videotype='MP4'):
    '''
    Find path for the video and import it with cv2 reader
    Open each frame of the video
        for the corresponding index
            take the angles and print them to the screen in the appropriate place
            write the output video
    '''

    path_vid = Path(video)
    print(path_vid)
    if path_vid.is_file() == False:
        print("This does not appear to be a correct path for a video file.")
        return
    
    cv_video = cv2.VideoCapture(str(path_vid))
    nframes = int(cv_video.get(cv2.CAP_PROP_FRAME_COUNT))
    x = int(cv_video.get(3))
    y = int(cv_video.get(4))
    fps = cv_video.get(5)

    #original_dir_path = path_vid.parent / 'Numbered'
    #original_dir_path.mkdir()

    new_fname = path_vid.stem.replace("_labeled", "_numbered")
    output_path = path_vid.parent / (new_fname + path_vid.suffix)
    print(output_path)

    vid_writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*'mp4v'), fps, (x, y))
    
    pbar = tqdm(total = nframes)
    for f in range(0, nframes, 1):
        pbar.update(1)
        cv_video.set(cv2.CAP_PROP_FRAME_COUNT, f)
        ok, frame = cv_video.read()
        if not ok:
            break

        #print("This is the f var: " + str(f))
        write_labels(number=f, name="Frame", fr=frame, x=lt_x, y=rt_y)

        vid_writer.write(frame)

    pbar.close()

    cv_video.release()

def write_labels(number, name, fr, x, y):
    black = (0, 0, 0)
    #opencv uses BGR
    daffodil = (49, 255, 255)
    cyan = (255, 255, 49)
    
    cv2.putText(fr, name + ": " + str(round(number, 1)), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, cyan, 3)

if __name__ == "__main__":
    #sagittal_dir = r"C:\Users\14124\OneDrive - University of Texas at San Antonio\Desktop\PGR_Pilot_Set_1\_Labeled_Sagittal_Videos"
    script, sag_dir = argv
    video_path_list = get_full_path_list(sag_dir, ".MP4")
    
    #Note: Origin is in the upper left hand corner
    for video_path in video_path_list:
        frame_to_video(video_path, lt_x=75, rt_y=700)

    path_vid = Path(video_path_list[0])
    original_dir_path = path_vid.parent / 'Labeled_Videos'
    if not original_dir_path.exists():
        original_dir_path.mkdir()

    for video_path in video_path_list:
        path_var = Path(video_path)
        file = path_var.name
        str_path = original_dir_path / file
        print(str_path)
        path_var.rename(str_path)


