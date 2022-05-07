import numpy
import math
import cv2


def get_FOV2s(frame_dim: (float, float), dFov: float = 55) -> (float, float):
    """ Calculates the horizontal and vertical FOVs from the frame (w/h) and diagonal FOV. """
    frame_width, frame_height = frame_dim
    dFov2 = dFov / 2

    dy = math.sqrt((frame_width / 2) ** 2 + (frame_height / 2) ** 2)

    dh = dy / math.sin(math.radians(dFov2))

    dx = dy / math.tan(math.radians(dFov2))
    print(f'dy: {dy}, dh: {dh}, dx: {dx}')

    hFov2 = math.degrees(math.atan((frame_width / 2) / dx))
    vFov2 = math.degrees(math.atan((frame_height / 2) / dx))

    return hFov2, vFov2


def get_distance(vFov2: float, alpha: float, y: float) -> float:
    """ Use basic trigonometry to estimate an object's distance. """
    gamma = alpha - vFov2
    return y * math.tan(math.radians(gamma))


if __name__ == "__main__":
    # diagonal fov
    dFov = 55
    # vertical fov
    vFov = 41

    cap = cv2.VideoCapture(0)
    dim = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    cap.release()

    # hFOV, vFOV = get_FOV2s(dim, dFov)
    print('vFOV:', vFov)

    camera_height = 24.5
    pan_angle = 70
    distance = get_distance(vFov2=vFov, alpha=pan_angle, y=camera_height)
    print('distance:', distance)

