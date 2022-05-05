import os
import sys
from pathlib import Path
import yaml
import numpy as np
import cv2

# add pyslam to path to import modules
script_dir = os.path.dirname(os.path.abspath(__file__))
git_dir = str(Path(script_dir).parents[1])
pyslam_dir = os.path.join(git_dir, "pyslam")
sys.path.append(pyslam_dir)

from camera import PinholeCamera
from feature_tracker_configs import FeatureTrackerConfigs
from feature_tracker import feature_tracker_factory
from visual_odometry import VisualOdometry
from mplot_thread import Mplot2d, Mplot3d


def read_cam_settings(cam_settings_file):
    cam_settings = None

    with open(cam_settings_file, 'r') as stream:
        try:
            cam_settings = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)

    def DistCoef():
        k1 = cam_settings['Camera.k1']
        k2 = cam_settings['Camera.k2']
        p1 = cam_settings['Camera.p1']
        p2 = cam_settings['Camera.p2']
        k3 = 0
        if 'Camera.k3' in cam_settings:
            k3 = cam_settings['Camera.k3']
        _DistCoef = np.array([k1, k2, p1, p2, k3])
        return _DistCoef

    cam = PinholeCamera(cam_settings['Camera.width'], cam_settings['Camera.height'],
                        cam_settings['Camera.fx'], cam_settings['Camera.fy'],
                        cam_settings['Camera.cx'], cam_settings['Camera.cy'],
                        DistCoef(), cam_settings['Camera.fps'])

    return cam


# To import all packages correctly, make sure RoboticsObjectDetection and pyslam are both in the folder 'git/'.
class VisualOdometryPicar:
    def __init__(self, plot=True):
        # read camera settings
        cam = read_cam_settings("PiCamera.yaml")

        # initialize tracker
        num_features = 2000  # how many features do you want to detect and track?

        # TODO: change tracker to tracker that can use color?
        # select your tracker configuration (see the file feature_tracker_configs.py)
        # LK_SHI_TOMASI, LK_FAST
        # SHI_TOMASI_ORB, FAST_ORB, ORB, BRISK, AKAZE, FAST_FREAK, SIFT, ROOT_SIFT, SURF, SUPERPOINT, FAST_TFEAT
        tracker_config = FeatureTrackerConfigs.LK_SHI_TOMASI
        tracker_config['num_features'] = num_features

        feature_tracker = feature_tracker_factory(**tracker_config)

        # create visual odometry object
        self.vo = VisualOdometry(cam, groundtruth=None, feature_tracker=feature_tracker)

        self.frame_id = 0
        self.x = 0
        self.y = 0
        self.z = 0

        self.plot = plot
        if self.plot:
            # 2D trajectory plot
            traj_img_size = 800
            self.traj_img = np.zeros((traj_img_size, traj_img_size, 3), dtype=np.uint8)
            self.half_traj_img_size = int(0.5 * traj_img_size)
            self.draw_scale = 1

            # 3D trajectory plot
            self.plt3d = Mplot3d(title='3D trajectory')

    def draw_2d_trajectory(self):
        draw_x, draw_y = int(self.draw_scale * self.x) + self.half_traj_img_size, self.half_traj_img_size - int(self.draw_scale * self.z)
        cv2.circle(self.traj_img, (draw_x, draw_y), 1, (self.frame_id * 255 / 4540, 255 - self.frame_id * 255 / 4540, 0), 1)
        # write text on traj_img
        cv2.rectangle(self.traj_img, (10, 20), (600, 60), (0, 0, 0), -1)
        text = "Coordinates: x=%2fm y=%2fm z=%2fm" % (self.x, self.y, self.z)
        cv2.putText(self.traj_img, text, (20, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, 8)
        # show
        cv2.imshow('Trajectory', self.traj_img)

    def draw_3d_trajectory(self):
        self.plt3d.drawTraj(self.vo.traj3d_est, 'estimated', color='g', marker='.')
        self.plt3d.refresh()

    def process_frame(self, frame):
        self.vo.track(frame, self.frame_id)  # main VO function

        if self.frame_id > 2:  # start drawing from the third image (when everything is initialized and flows in a normal way)
            self.x, self.y, self.z = self.vo.traj3d_est[-1]

            if self.plot:
                self.draw_2d_trajectory()
                self.draw_3d_trajectory()

                # draw camera image
                cv2.imshow('Camera', self.vo.draw_img)

        self.frame_id += 1


if __name__ == "__main__":
    vop = VisualOdometryPicar()
