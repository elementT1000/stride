from pathlib import Path
import typing
import cv2
import pandas as pd
from tqdm import tqdm
import numpy as np
        

def csv_frame_to_video(video: str, csv: str, rt_y=500, lt_x=75, videotype='MP4'):
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
    x = int(cv_video.get(3))
    y = int(cv_video.get(4))
    fps = cv_video.get(5)

    new_fname = str(path_vid).replace("_labeled.mp4", "_numbered.mp4")
    print(new_fname)

    vid_writer = cv2.VideoWriter(str(new_fname), cv2.VideoWriter_fourcc(*'mp4v'), fps, (x, y))

    path_csv = Path(csv)
    if path_csv.is_file() == False:
        print("This does not seem to be a correct path to a csv file.")
        return
    print(path_csv)
    angles_df = pd.read_csv(str(path_csv))
    angles_df = angles_df.replace(np.nan, 0)
    
    pbar = tqdm(total = nframes)
    for f in range(0, nframes, 1):
        pbar.update(1)
        cv_video.set(cv2.CAP_PROP_FRAME_COUNT, f)
        ok, frame = cv_video.read()
        if not ok:
            break
        
        #The dataframe rows are set down by an extra level because of the headers, so add one
        df_row = f+1
        array_number = angles_df.loc[df_row][0]
        write_labels(angle=array_number, name="Frame", fr=frame, x=lt_x, y=rt_y)
  
        vid_writer.write(frame)

    pbar.close()

    cv_video.release()

def write_labels(angle, name, fr, x, y):
    black = (0, 0, 0)
    #opencv uses BGR
    daffodil = (49, 255, 255)
    cyan = (255, 255, 49)
    
    cv2.putText(fr, name + ": " + str(round(angle, 1)), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, cyan, 3)

if __name__ == "__main__":
    video_path = r"C:\Users\14124\stride\root_dir\Subject_1\processed_files\tk_091322_sr_ns_analyzed_labeled.mp4"
    csv_path = r"C:\Users\14124\stride\root_dir\Subject_1\processed_files\angles_tk_091322_sr_ns_analyzed.csv"
    #Note: Origin is in the upper left hand corner
    csv_frame_to_video(video_path, csv_path, lt_x=75, rt_y=700)

