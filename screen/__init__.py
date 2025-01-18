import numpy as np
import cv2
import time
from screeninfo import get_monitors
import mss
import threading
from ultralytics import YOLO

capture_running = threading.Event()

def get_screen_coords(monitor_index=0):

    monitors = get_monitors()
    if monitor_index > len(monitors):
        raise Exception("Monitor index out of range")
    else:
        monitor = monitors[monitor_index]
        return monitor.x, monitor.y, monitor.width + monitor.x, monitor.height + monitor.y


def capture_screen(coords, output):
    with mss.mss() as sct:
        monitor = {"top": coords[1], "left": coords[0], "width": coords[2] - coords[0], "height": coords[3] - coords[1]}
        while not capture_running.is_set():
            screen = np.asarray(sct.grab(monitor))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
            output[0] = screen

def resize_image(image, width, height):
    dim = (width, height)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized

def run(reisze_image=False):
    global capture_running
    capture_running.clear()

    coords = get_screen_coords()

    model = YOLO("yolo11x.pt")

    screen_output = [None]
    capture_thread = threading.Thread(target=capture_screen, args=(coords, screen_output))
    capture_thread.start()

    prev_time = time.time()

    cv2.namedWindow("Screen", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Screen", 640*2, 384*2)

    while not capture_running.is_set():
        if screen_output[0] is not None:
            if reisze_image:
                display_screen = resize_image(screen_output[0], 1920, 1080)
            else:
                display_screen = screen_output[0]

            current_time = time.time()
            fps = 1 / (current_time - prev_time)
            prev_time = current_time

            cv2.putText(display_screen, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Detect objects in the screen
            results = model(display_screen)

            annoted_frame = results[0].plot()

            cv2.imshow("Screen", annoted_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()
    capture_thread.join()

def stop():
    global capture_running
    capture_running.set()