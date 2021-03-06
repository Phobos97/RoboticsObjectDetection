from operator import itemgetter

import cv2
from RobotControl.video_playback import read_video
import os



class ObjectDetector:
    def __init__(self, object_names=["CUP", "BOOK", "BOTTLE", "BED"], threshold=.45):
        self.class_names = []

        file_path = os.path.realpath(__file__)
        class_file = os.path.join(os.path.dirname(file_path), 'coco.names')
        with open(class_file, 'rt') as f:
            self.class_names = f.read().rstrip('\n').split('\n')

        config_path = os.path.join(os.path.dirname(file_path), 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt')
        weights_path = os.path.join(os.path.dirname(file_path), 'frozen_inference_graph.pb')
        self.net = cv2.dnn_DetectionModel(weights_path, config_path)
        self.net.setInputSize(320, 320)
        self.net.setInputScale(1.0 / 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)

        self.object_names = object_names
        self.threshold = threshold

    def check_for_object(self, frame, distance_to_dodge=320, all_objects=False, show_video=False):
        classIds, confs, bbox = self.net.detect(frame, confThreshold=self.threshold)

        found_objects = []
        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                if self.class_names[classId - 1].upper() in self.object_names:
                    color = (0, 255, 0)
                    if not all_objects:
                        found_objects.append((classId, confidence, box))
                else:
                    color = (255, 0, 0)
                if all_objects:
                    found_objects.append((classId, confidence, box))
                cv2.rectangle(frame, box, color=color, thickness=2)
                cv2.putText(frame, self.class_names[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)


        close_objects = []
        dodge_directions = []

        print('-----\n')
        for object in found_objects:
            lower_bounding_line = object[2][1] + object[2][3]
            upper_bounding_line = object[2][1]

            width = object[2][2]
            height = object[2][3]

            print(f'{lower_bounding_line = }')
            print(f'{upper_bounding_line = }')
            print(f'{width = }')
            print(f'{height = }')

            if lower_bounding_line > distance_to_dodge \
                    and 550 > width > 150 \
                    and 550 > height > 150:

                close_objects.append(object)
                cv2.imshow("Output", frame)
                cv2.waitKey(1)

                left_edge = object[2][0]
                right_edge = 640 - (object[2][0] + object[2][2])

                if left_edge > right_edge:
                    dodge_directions.append("left")
                else:
                    dodge_directions.append("right")

        if show_video:
            cv2.imshow("Output", frame)
            cv2.waitKey(1)

        if len(close_objects) > 0:
            if len(close_objects) > 1:
                print("multiple close objects detected, returning the one with highest confidence")

            object_to_dodge = max(close_objects, key=itemgetter(1))
            index = close_objects.index(object_to_dodge)
            dodge_direction = dodge_directions[index]

            return object_to_dodge, dodge_direction

        return None, None


if __name__ == '__main__':
    detector = ObjectDetector(object_names=["CUP", "BOOK", "BOTTLE"], threshold=0.45)
    # video = read_video(path="../TestVideos/task1/20220502-131951.h264")
    video = read_video(path="../TestVideos/task1/20220502-131951.h264")

    for frame in video:
        object, direction = detector.check_for_object(frame, show_video=True)
        if object:
            print("object: ", object, " dodge direction: ", direction)


