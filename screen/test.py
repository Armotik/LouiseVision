import cv2
import mss
import numpy as np
from screeninfo import get_monitors
from screen import get_screen_coords


def capture_screen(coords, output):
    with mss.mss() as sct:
        monitor = {"top": coords[1], "left": coords[0], "width": 380, "height": 210}

        while True:
            screen = np.asarray(sct.grab(monitor))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
            output[0] = screen


def get_monitor(get_primary=False):
    monitors = get_monitors()

    if len(monitors) == 1:
        return monitors[0]

    if get_primary:
        for monitor in monitors:
            if monitor.is_primary:
                return monitor

    return monitors[0]


if __name__ == '__main__':
    print("Testing screen capture")
    print("----------------------")
    print("monitors: ", get_monitors())
    print("----------------------")
    print("default monitor: ", get_monitor(True))
    print("----------------------")

    coords = get_screen_coords(0)
    screen_output = [None]
    capture_screen(coords, screen_output)
    if screen_output[0] is not None:
        cv2.imshow("Screen", screen_output[0])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
