import cv2
import numpy as np


def read_video(path):
    cap = cv2.VideoCapture(path)
    ret = True
    frames = []
    while ret:
        ret, img = cap.read()  # read one frame from the 'capture' object; img is (H, W, C)
        if ret:
            frames.append(img)
    video = np.stack(frames, axis=0)  # dimensions (T, H, W, C)
    return video


def main():
    path = "../TestVideos/20220427-170057.h264"
    video = read_video(path)

    fps = 24
    mspf = int(1e3 / fps)

    for i_frame in range(video.shape[0]):
        frame = video[i_frame, ...]
        cv2.imshow("frame", frame)
        cv2.waitKey(mspf)


if __name__ == '__main__':
    main()
