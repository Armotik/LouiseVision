import numpy as np
import cv2
import time
from screeninfo import get_monitors
import mss
import threading
from ultralytics import YOLO
import torch

capture_running = threading.Event()


def get_screen_coords(monitor_index=0):
    """
    Get the screen coordinates of the monitor at the specified index
    :param monitor_index: index of the monitor
    :return: Tuple of screen coordinates (x1, y1, x2, y2)
    """

    monitors = get_monitors()
    if monitor_index > len(monitors):
        raise Exception("Monitor index out of range")
    else:
        monitor = monitors[monitor_index]
        return monitor.x, monitor.y, monitor.width + monitor.x, monitor.height + monitor.y


def capture_screen(coords, output):
    """
    Capture the screen at the specified coordinates
    :param coords: Tuple of screen coordinates (x1, y1, x2, y2)
    :param output: List to store the captured screen, the screen is stored as a numpy array
    """

    with mss.mss() as sct:
        monitor = {"top": coords[1], "left": coords[0], "width": coords[2] - coords[0],
                   "height": (coords[3] - coords[1]) // 1}

        while not capture_running.is_set():
            start_time = time.time()
            screen = np.asarray(sct.grab(monitor))
            end_time = time.time()

            print(f"Capture Time: {end_time - start_time:.4f} sec")  # Debugging performance

            screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
            output[0] = screen


def resize_image(image, width, height):
    """
    Resize the image to the specified width and height
    :param image: Image to resize
    :param width: Width of the resized image
    :param height: Height of the resized image
    :return: Resized image
    """
    dim = (width, height)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized


def run(reisze_image=False, window_name="Screen", window_width=1280, window_height=768):
    """
    Run the screen capture and object detection
    :param reisze_image: Flag to resize the captured screen
    """

    # TODO: utilisation d'une pile pour stocker les images capturées avant le traitement par le modèle (pour éviter de perdre des images mais il va falloir gérer la mémoire et il va y avoir un décalage entre l'image capturée et l'image traitée)

    global capture_running
    capture_running.clear()

    coords = get_screen_coords(0)

    # Load a better model if GPU is available
    if torch.cuda.is_available():
        model = YOLO("yolo11x.pt")
    else:
        model = YOLO("yolov8n.pt")

    screen_output = [None]
    capture_thread = threading.Thread(target=capture_screen, args=(
    coords, screen_output))  # Capture screen in a separate thread to avoid blocking the main thread
    capture_thread.start()

    prev_time = time.time()

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, window_width, window_height)

    while not capture_running.is_set():
        if screen_output[0] is not None:  # Display the screen if it has been captured
            if reisze_image:
                display_screen = resize_image(screen_output[0], 640, 480)
            else:
                display_screen = screen_output[0]

            current_time = time.time()
            fps = 1 / (current_time - prev_time)
            prev_time = current_time

            cv2.putText(display_screen, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                        2)  # Display FPS

            # Detect objects in the screen
            results = model(display_screen)

            annoted_frame = results[0].plot()

            cv2.imshow("Screen", annoted_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()
    capture_thread.join()


def stop():
    """
    Stop the screen capture by setting the capture_running event
    """

    global capture_running
    capture_running.set()


def capture_camera(camera_index=0):
    """
    Capture the camera feed and perform object detection
    :param camera_index: Index of the camera to capture
    """

    try:
        cap = cv2.VideoCapture(camera_index)

        # Load a better model if GPU is available
        if torch.cuda.is_available():
            model = YOLO("yolo11x.pt")
        else:
            model = YOLO("yolov8n.pt")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: failed to capture frame")
                break

            results = model(frame)
            annoted_frame = results[0].plot()
            cv2.imshow("Camera", annoted_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Error: {e}")

    cv2.destroyAllWindows()


def get_monitor(get_primary=False):
    """
    Get the monitor at the specified index
    :param get_primary: Flag to get the primary monitor
    :return: Monitor object
    """

    monitors = get_monitors()

    if len(monitors) == 1:
        return monitors[0]

    if get_primary:
        for monitor in monitors:
            if monitor.is_primary:
                return monitor

    return monitors[0]
