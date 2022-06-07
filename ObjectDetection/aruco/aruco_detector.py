import numpy as np
import cv2
import os


class ArucoDetector():
    def __init__(self):
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.aruco_parameters = cv2.aruco.DetectorParameters_create()

        self.aruco_size = 10 # cm

        # camera characteristics
        script_dir = os.path.dirname(os.path.realpath(__file__))
        npzfile = np.load(os.path.join(script_dir, 'calibration_data.npz'))
        self.camera_matrix = npzfile['mtx']
        self.dist_coeffs = npzfile['dist']

    def aruco_angle(self, corners):
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners,
                                                              self.aruco_size,
                                                              self.camera_matrix,
                                                              self.dist_coeffs)

        # get single marker
        x, z = tvecs[0][0][0], tvecs[0][0][2]
        angle = np.rad2deg(np.arctan(x/z))

        return angle

    def detect_markers(self, frame, return_image=False):
        # detect markers in frame
        (corners, ids, rejectedImgPoints) = cv2.aruco.detectMarkers(frame,
                                                                  self.aruco_dict,
                                                                  parameters=self.aruco_parameters)


        angle = None

        # verify *at least* one ArUco marker was detected
        if len(corners) > 0:
            # flatten the ArUco IDs list
            ids = ids.flatten()

            angle = self.aruco_angle(corners)

            # loop over the detected ArUCo corners
            for (markerCorner, markerID) in zip(corners, ids):
                # extract the marker corners (which are always returned
                # in top-left, top-right, bottom-right, and bottom-left
                # order)
                corners = markerCorner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = corners

                # convert each of the (x, y)-coordinate pairs to integers
                topRight = (int(topRight[0]), int(topRight[1]))
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))

                # draw the bounding box of the ArUCo detection
                cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

                # compute and draw the center (x, y)-coordinates of the
                # ArUco marker
                cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)

                # draw the ArUco marker ID on the frame
                cv2.putText(frame, str(markerID),
                            (topLeft[0], topLeft[1] - 15),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 2)
        return angle, frame
