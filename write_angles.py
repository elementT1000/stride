from pathlib import Path
import typing
import cv2
import pandas as pd
from tqdm import tqdm
import numpy as np


def list_videos(
    videos: typing.Union[typing.List[str], str],
    videotype: typing.Union[typing.List[str], str] = ""
) -> typing.List[str]:

    if isinstance(videos, str):
        videos = [videos]

    if [Path.is_dir(i) for i in videos] == [True]:
        videofolder = videos[0]
        #Open the directory and join all of the files into a list of paths
        videos = [(Path(videofolder).parent).joinpath(file) for file in Path.iterdir(videofolder)]

    if isinstance(videotype, str):
        videotype = [videotype]

    videos = [
        v
        for v in videos
        if Path.is_file(v)
        and any(v.endswith(ext) for ext in videotype)
    ]
    return videos

def write_labels(angle, name, fr, x, y):
    black = (0, 0, 0)
    #opencv uses BGR
    daffodil = (49, 255, 255)
    cyan = (255, 255, 49)
    if angle == 0:
        cv2.putText(fr, name + ": not identified", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, black, 2)
    else:
        cv2.putText(fr, name + ": " + str(round(angle, 1)), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, daffodil, 2)
        

def csv_frontal_angles_to_video(video: str, csv: str, rt_x=700, rt_y=700, lt_x=150, videotype='MP4'):
    '''
    Set path to csv file, then open the file as a dataframe
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

    #collect video info for subsequent writing
    x = int(cv_video.get(3))
    y = int(cv_video.get(4))
    fps = cv_video.get(5)

    new_fname = str(path_vid).replace("_labeled.mp4", "_angles.mp4")
    print(new_fname)


    vid_writer = cv2.VideoWriter(str(new_fname), cv2.VideoWriter_fourcc(*'mp4v'), fps, (x, y))

    path_csv = Path(csv)
    if path_csv.is_file() == False:
        print("This does not seem to be a correct path to a csv file.")
        return
    print(path_csv)
    angles_df = pd.read_csv(str(path_csv))
    angles_df = angles_df.replace(np.nan, 0)

    #test alignment variables
    #rt_x = 400
    #rt_y = 400
    #lt_x = 150
    
    pbar = tqdm(total = nframes)
    for f in range(0, nframes, 1):
        pbar.update(1)
        cv_video.set(cv2.CAP_PROP_FRAME_COUNT, f)
        ok, frame = cv_video.read()
        if not ok:
            break
        
        hip_drop = angles_df.loc[f]['Waist']
        write_labels(angle=hip_drop, name="Hip Drop", fr=frame, x=lt_x+400, y=rt_y-100)

        right_hip_angle = angles_df.loc[f]['RightFemurHead']
        write_labels(angle=right_hip_angle, name="Right Hip Angle", fr=frame, x=rt_x, y=rt_y)

        right_knee_angle = angles_df.loc[f]['RightKnee']
        write_labels(angle=right_knee_angle, name="Right Knee Angle", fr=frame, x=rt_x, y=rt_y+200)

        right_ankle_angle = angles_df.loc[f]['RightAnkle']
        write_labels(angle=right_ankle_angle, name="Right Ankle Angle", fr=frame, x=rt_x, y=rt_y+400)

        left_hip_angle = angles_df.loc[f]['LeftFemurHead']
        write_labels(angle=left_hip_angle, name="Left Hip Angle", fr=frame, x=lt_x, y=rt_y)

        left_knee_angle = angles_df.loc[f]['LeftKnee']
        write_labels(angle=left_knee_angle, name="Left Knee Angle", fr=frame, x=lt_x, y=rt_y+200)

        left_ankle_angle = angles_df.loc[f]['LeftAnkle']
        write_labels(angle=left_ankle_angle, name="Left Ankle Angle", fr=frame, x=lt_x, y=rt_y+400)
                
        vid_writer.write(frame)

    pbar.close()

    cv_video.release()

def csv_sagittal_angles_to_video(video: str, csv: str, videotype='MP4'):
    '''
    Set path to csv file, then open the file as a dataframe
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

    #collect video info for subsequent writing
    x = int(cv_video.get(3))
    y = int(cv_video.get(4))
    fps = cv_video.get(5)

    new_fname = str(path_vid).replace("_labeled.mp4", "_angles.mp4")
    print(new_fname)

    vid_writer = cv2.VideoWriter(str(new_fname), cv2.VideoWriter_fourcc(*'mp4v'), fps, (x, y))

    path_csv = Path(csv)
    if path_csv.is_file() == False:
        print("This does not seem to be a correct path to a csv file.")
        return
    print(path_csv)
    angles_df = pd.read_csv(str(path_csv))
    angles_df = angles_df.replace(np.nan, 0)

    #test alignment variables
    rt_x = 100
    rt_y = 700
    lt_x = 700
    
    pbar = tqdm(total = nframes)
    for f in range(0, nframes, 1):
        pbar.update(1)
        cv_video.set(cv2.CAP_PROP_FRAME_COUNT, f)
        ok, frame = cv_video.read()
        if not ok:
            break
        
        arm_angle = angles_df.loc[f]['Arm']
        write_labels(angle=arm_angle, name="Arm Angle", fr=frame, x=rt_x, y=rt_y-200)

        hip_angle = angles_df.loc[f]['Hip']
        write_labels(angle=hip_angle, name="Hip Angle", fr=frame, x=rt_x, y=rt_y)

        knee_angle = angles_df.loc[f]['Knee']
        write_labels(angle=knee_angle, name="Knee Angle", fr=frame, x=rt_x, y=rt_y+200)

        toe_angle = angles_df.loc[f]['Toe']
        write_labels(angle=toe_angle, name="Toe Angle", fr=frame, x=rt_x, y=rt_y+400)

        vid_writer.write(frame)

    pbar.close()

    cv_video.release()
