import numpy as np
import cv2
import argparse


lower_bounds = {
    "red": [136, 87, 111],
    "pink": [145, 100, 20],
    "purple": [125, 50, 20],
    "green": [40, 50, 20],
    "blue": [90, 50, 50],
    "yellow": [25, 50, 20]
}
upper_bounds = {
    "red": [180, 255, 255],
    "pink": [160, 255, 255],
    "purple": [150, 255, 255],
    "green": [85, 255, 255],
    "blue": [150, 255, 255],
    "yellow": [35, 255, 255]
}


def print_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        point = frame[y][x]
        print("color at click:", point)


def color_bound(ball_color, loop, video):
    cv2.namedWindow("frame")
    # cv2.setMouseCallback("frame", print_color) # unused

    while loop:
        vcap = cv2.VideoCapture("TestVideos/balls/" + video)

        vcap.set(3, 640)
        vcap.set(4, 480)

        feed = vcap.isOpened()

        frame_counter = 0

        while True:
            feed, frame = vcap.read()
            frame = cv2.rotate(frame, cv2.ROTATE_180)

            if not feed:
                break

            # convert frame from BGR to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # set range for red color and define mask
            color_lower = np.array(lower_bounds[ball_color], np.uint8)
            color_upper = np.array(upper_bounds[ball_color], np.uint8)
            color_mask = cv2.inRange(hsv, color_lower, color_upper)

            # creating contour to track red color
            contours, hierarchy = cv2.findContours(color_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for pic, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area > 300:
                    x, y, w, h = cv2.boundingRect(contour)
                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, "color", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))

            cv2.imshow("frame", frame)

            if cv2.waitKey(1) == ord('p'):
                cv2.waitKey(-1)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                vcap.release()
                cv2.destroyAllWindows()
                loop = False
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--color", help="the color of the ball tested (pick between blue, green, red, yellow, pink, purple).")
    parser.add_argument("-l", "--loop", help="loop the video or not", type=int, default=0)
    parser.add_argument("-v", "--video", help="video path [only file name]", type=str, default="blue_1.h264")
    args = parser.parse_args()
    color_bound(args.color, bool(args.loop), args.video)
