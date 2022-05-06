import cv2
from datetime import datetime

import os
import sys
from pathlib import Path
import time

from picamera.array import PiRGBArray
from picamera import PiCamera

# add pyslam to path to import modules
script_dir = os.path.dirname(os.path.abspath(__file__))
git_dir = str(Path(script_dir).parents[1])
pyslam_dir = os.path.join(git_dir, "pyslam")
sys.path.append(pyslam_dir)

from timer import Timer


def main():
    # CHESSBOARD SIZE
    chessboard_size = (11, 7)

    # grab an image every
    kSaveImageDeltaTime = 1  # second

    timer = Timer()
    lastSaveTime = timer.elapsed()

    # initialize camera
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.5)

        # main control loop
        try:
            for frame in camera.capture_continuous(rawCapture, format="bgr",
                                                   use_video_port=True):  # use_video_port=True
                image = frame.array

                # check if pattern found
                ret, corners = cv2.findChessboardCorners(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), chessboard_size, None)

                if ret == True:
                    print('found chessboard')
                    # save image
                    filename = datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss%f') + '.bmp'
                    image_path = "./calib_images/" + filename

                    elapsedTimeSinceLastSave = timer.elapsed() - lastSaveTime
                    do_save = elapsedTimeSinceLastSave > kSaveImageDeltaTime

                    if do_save:
                        lastSaveTime = timer.elapsed()
                        print('saving file ', image_path)
                        cv2.imwrite(image_path, image)

                    # draw the corners
                    image = cv2.drawChessboardCorners(image, chessboard_size, corners, ret)

                cv2.imshow('camera', image)
                rawCapture.truncate(0)  # Release cache

                # quit on keypress
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            camera.close()
            rawCapture.close()


if __name__ == "__main__":
    main()
