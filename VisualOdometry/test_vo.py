import os
import sys
from pathlib import Path

import cv2
from visual_odometry_picar import VisualOdometryPicar

# modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = str(Path(script_dir).parents[0])
sys.path.append(project_root_dir)

from RobotControl.video_playback import read_video


def main():
    print("make sure pySLAM is installed in the git directory")
    path = "../TestVideos/SLAM/20220502-133022.h264"
    video = read_video(path)

    vop = VisualOdometryPicar()

    fps = 24
    mspf = int(1e3 / fps)

    for i_frame in range(video.shape[0]):
        frame = video[i_frame, ...]

        try:
            vop.process_frame(frame)
        except Exception as e:
            print(e)

        cv2.imshow("frame", frame)
        cv2.waitKey(mspf)


if __name__ == '__main__':
    main()
