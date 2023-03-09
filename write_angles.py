from pathlib import Path
from sys import argv
import typing
import cv2
import pandas as pd
from tqdm import tqdm
import numpy as np


#TODO: Increase abstraction to reduce duplication of code through each of these functions
def write_labels(angle, name, fr, x, y, size, boldness):
    black = (0, 0, 0)
    #opencv uses BGR
    green = (17, 233, 135)
    daffodil = (49, 255, 255)
    cyan = (255, 255, 49)
    #size = 1.2
    #boldness = 3
    if angle == 0:
        cv2.putText(fr, name + ": null", (x, y), cv2.FONT_HERSHEY_SIMPLEX, size, green, boldness)
    else:
        cv2.putText(fr, name + ": " + str(round(angle, 1)), (x, y), cv2.FONT_HERSHEY_SIMPLEX, size, green, boldness)
        
def csv_posterior_angles_to_video(video: str, csv: str, videotype='MP4'):
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
    frame_x = int(cv_video.get(3))
    frame_y = int(cv_video.get(4))
    fps = cv_video.get(5)

    new_fname = str(path_vid).replace("_labeled.mp4", "_angles.mp4")
    print(new_fname)

    #We add a border, so it is necessary to adjust the video writer to handle this
    wider = 380
    vid_writer = cv2.VideoWriter(str(new_fname), cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_x + wider, frame_y))

    path_csv = Path(csv)
    if path_csv.is_file() == False:
        print("This does not seem to be a correct path to a csv file.")
        return
    print(path_csv)
    #May need to filter angles here
    angles_df = pd.read_csv(str(path_csv), index_col=0, header=[0,1])
    angles_df = angles_df.replace(np.nan, 0)
    angles_df.columns = angles_df.columns.get_level_values(1)
    
    pbar = tqdm(total = nframes)
    for f in range(0, nframes, 1):
        pbar.update(1)
        cv_video.set(cv2.CAP_PROP_FRAME_COUNT, f)
        ok, frame = cv_video.read()
        if not ok:
            break
        
        #cv2.imshow("just frame", frame)
        frame = cv2.copyMakeBorder(frame, 0, 0, int(wider/2), int(wider/2), cv2.BORDER_CONSTANT, value=[0, 0, 0])
        #cv2.imshow("bordered frame", frame)

        lt_x = 0
        rt_x = frame_x + int(wider/2)
        y_level = 400

        hip_drop = angles_df.loc[f]['pfWaist']
        write_labels(angle=hip_drop, name="Hip Drop", fr=frame, x=lt_x, y=y_level-100, size=0.6, boldness=2)

        right_hip_angle = angles_df.loc[f]['pfRightFemurHead']
        write_labels(angle=right_hip_angle, name="Right Hip", fr=frame, x=lt_x, y=y_level, size=0.6, boldness=2)

        right_knee_angle = angles_df.loc[f]['pfRightKnee']
        write_labels(angle=right_knee_angle, name="Right Knee", fr=frame, x=lt_x, y=y_level+100, size=0.6, boldness=2)

        right_ankle_angle = angles_df.loc[f]['pfRightAnkle']
        write_labels(angle=right_ankle_angle, name="Right Ankle", fr=frame, x=lt_x, y=y_level+200, size=0.6, boldness=2)

        left_hip_angle = angles_df.loc[f]['pfLeftFemurHead']
        write_labels(angle=left_hip_angle, name="Left Hip", fr=frame, x=rt_x, y=y_level, size=0.6, boldness=2)

        left_knee_angle = angles_df.loc[f]['pfLeftKnee']
        write_labels(angle=left_knee_angle, name="Left Knee", fr=frame, x=rt_x, y=y_level+100, size=0.6, boldness=2)

        left_ankle_angle = angles_df.loc[f]['pfLeftAnkle']
        write_labels(angle=left_ankle_angle, name="Left Ankle", fr=frame, x=rt_x, y=y_level+200, size=0.6, boldness=2)
                
        vid_writer.write(frame)

    pbar.close()

    cv_video.release()

def csv_anterior_angles_to_video(video: str, csv: str, videotype='MP4'):
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
    frame_x = int(cv_video.get(3))
    frame_y = int(cv_video.get(4))
    fps = cv_video.get(5)

    new_fname = str(path_vid).replace("_labeled.mp4", "_angles.mp4")
    print(new_fname)

    wider = 380
    vid_writer = cv2.VideoWriter(str(new_fname), cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_x + wider, frame_y))

    path_csv = Path(csv)
    if path_csv.is_file() == False:
        print("This does not seem to be a correct path to a csv file.")
        return
    print(path_csv)
    #May need to filter angles here
    angles_df = pd.read_csv(str(path_csv), index_col=0, header=[0,1])
    angles_df = angles_df.replace(np.nan, 0)
    angles_df.columns = angles_df.columns.get_level_values(1)
    
    pbar = tqdm(total = nframes)
    for f in range(0, nframes, 1):
        pbar.update(1)
        cv_video.set(cv2.CAP_PROP_FRAME_COUNT, f)
        ok, frame = cv_video.read()
        if not ok:
            break

        frame = cv2.copyMakeBorder(frame, 0, 0, int(wider/2), int(wider/2), cv2.BORDER_CONSTANT, value=[0, 0, 0])
        
        lt_x = 0
        rt_x = frame_x + int(wider/2)
        y_level = 400

        size = 0.6

        right_hip_angle = angles_df.loc[f]['afRightThigh']
        write_labels(angle=right_hip_angle, name="Right Hip", fr=frame, x=lt_x, y=y_level, size=size, boldness=2)

        right_knee_angle = angles_df.loc[f]['afRightKnee']
        write_labels(angle=right_knee_angle, name="Right Knee", fr=frame, x=lt_x, y=y_level+100, size=size, boldness=2)

        right_ankle_angle = angles_df.loc[f]['afRightAnkle']
        write_labels(angle=right_ankle_angle, name="Right Ankle", fr=frame, x=lt_x, y=y_level+200, size=size, boldness=2)

        foot_angle = angles_df.loc[f]['afRightFoot']
        write_labels(angle=foot_angle, name="Right Foot", fr=frame, x=lt_x, y=y_level+300, size=size, boldness=2)

        left_hip_angle = angles_df.loc[f]['afLeftThigh']
        write_labels(angle=left_hip_angle, name="Left Hip", fr=frame, x=rt_x, y=y_level, size=size, boldness=2)

        left_knee_angle = angles_df.loc[f]['afLeftKnee']
        write_labels(angle=left_knee_angle, name="Left Knee", fr=frame, x=rt_x, y=y_level+100, size=size, boldness=2)

        left_ankle_angle = angles_df.loc[f]['afLeftAnkle']
        write_labels(angle=left_ankle_angle, name="Left Ankle", fr=frame, x=rt_x, y=y_level+200, size=size, boldness=2)

        foot_angle = angles_df.loc[f]['afLeftFoot']
        write_labels(angle=foot_angle, name="Left Foot", fr=frame, x=rt_x, y=y_level+300, size=size, boldness=2)

        vid_writer.write(frame)

    pbar.close()

    cv_video.release()

def csv_sagittal_angles_to_video(video: str, csv: str, rt_y=150, lt_x=75, videotype='MP4'):
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
    #May need to filter angles here
    angles_df = pd.read_csv(str(path_csv), index_col=0, header=[0,1])
    angles_df = angles_df.replace(np.nan, 0)
    angles_df.columns = angles_df.columns.get_level_values(1)
    
    pbar = tqdm(total = nframes)
    for f in range(0, nframes, 1):
        pbar.update(1)
        cv_video.set(cv2.CAP_PROP_FRAME_COUNT, f)
        ok, frame = cv_video.read()
        if not ok:
            break
        #The dataframe rows are set down by an extra level because of the headers, so add one
        arm_angle = angles_df.loc[f]['RightArm']
        write_labels(angle=arm_angle, name="Arm Angle", fr=frame, x=lt_x, y=rt_y-200, size=1.2, boldness=3)

        hip_angle = angles_df.loc[f]['RightHip']
        write_labels(angle=hip_angle, name="Hip Angle", fr=frame, x=lt_x, y=rt_y, size=1.2, boldness=3)

        knee_angle = angles_df.loc[f]['RightKnee']
        write_labels(angle=knee_angle, name="Knee Angle", fr=frame, x=lt_x, y=rt_y+200, size=1.2, boldness=3)

        toe_angle = angles_df.loc[f]['RightAnkle']
        write_labels(angle=toe_angle, name="Ankle Angle", fr=frame, x=lt_x, y=rt_y+400, size=1.2, boldness=3)

        toe_angle = angles_df.loc[f]['RightToe']
        write_labels(angle=toe_angle, name="Toe Angle", fr=frame, x=lt_x, y=rt_y+600, size=1.2, boldness=3)

        vid_writer.write(frame)

    pbar.close()

    cv_video.release()

def csv_left_angles_to_video(video: str, csv: str, rt_y=150, lt_x=75, videotype='MP4'):
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
    #May need to filter angles here
    angles_df = pd.read_csv(str(path_csv), index_col=0, header=[0,1])
    angles_df = angles_df.replace(np.nan, 0)
    angles_df.columns = angles_df.columns.get_level_values(1)
    
    pbar = tqdm(total = nframes)
    for f in range(0, nframes, 1):
        pbar.update(1)
        cv_video.set(cv2.CAP_PROP_FRAME_COUNT, f)
        ok, frame = cv_video.read()
        if not ok:
            break
        #The dataframe rows are set down by an extra level because of the headers, so add one
        arm_angle = angles_df.loc[f]['RightArm']
        write_labels(angle=arm_angle, name="Arm Angle", fr=frame, x=lt_x, y=rt_y-200, size=1.2, boldness=3)

        hip_angle = angles_df.loc[f]['RightHip']
        write_labels(angle=hip_angle, name="Hip Angle", fr=frame, x=lt_x, y=rt_y, size=1.2, boldness=3)

        knee_angle = angles_df.loc[f]['RightKnee']
        write_labels(angle=knee_angle, name="Knee Angle", fr=frame, x=lt_x, y=rt_y+200, size=1.2, boldness=3)

        toe_angle = angles_df.loc[f]['RightAnkle']
        write_labels(angle=toe_angle, name="Ankle Angle", fr=frame, x=lt_x, y=rt_y+400, size=1.2, boldness=3)

        toe_angle = angles_df.loc[f]['RightToe']
        write_labels(angle=toe_angle, name="Toe Angle", fr=frame, x=lt_x, y=rt_y+600, size=1.2, boldness=3)

        vid_writer.write(frame)

    pbar.close()

    cv_video.release()

if __name__ == "__main__":
    script, video_path, csv_path = argv
    
    csv_anterior_angles_to_video(video_path, csv_path)
