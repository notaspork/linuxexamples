# This program is designed to provide a simple way to monitor the speed and distance traveled on a treadmill, when the treadmill does not have such capabilities built-in.
# The program uses computer vision (using the cv2 library) to detect an inexpensive red or blue dot sticker on a treadmill and count the number of times the dot passes a certain point.
# This allows the program to calculate the distance traveled over time, and then the speed of the treadmill.
# This information is displayed in the terminal, and is also written to a log file.
# The program can also display the video feed from the camera, and can display the mask used to detect the dots.

import cv2
import numpy as np
import time
import signal
import os
import datetime
import sys
# import simpleaudio as sa

TRACK_LENGTH = 124.1875  # in inches
INCHES_PER_MILE = 63360
TRACK_LENGTH_MILES = TRACK_LENGTH / INCHES_PER_MILE
MILES_PER_KM = 0.621371
FRAME_MEMORY_MAX = 15
WIN_TITLE = "Treadmill Monitor"
TEXT_DISPLAY_INTERVAL = 30  # in frames

SHOW_VIDEO = False
USE_BLUE = True
SHOW_MASK = False
USE_BGR = False

for arg in sys.argv:
    if arg == '-d':
        SHOW_VIDEO = True
    elif arg == '-r':
        USE_BLUE = False
    elif arg == '-m':
        SHOW_MASK = True
        SHOW_VIDEO = True
    elif arg == '-b':
        USE_BGR = True
    elif arg == '-h':
        print("Usage: python treadmillcv.py [-d] [-r] [-m] [-b]")
        print("  -d: Display the video feed from the camera")
        print("  -r: Use a red dot instead of a blue dot (blue dot is the default)")
        print("  -m: Display the mask used to detect the dots on the video feed in real-time")
        print("  -b: Use BGR instead of HSV for dot detection")
        sys.exit(0)

# # Load the sound file
# wave_obj = sa.WaveObject.from_wave_file("treadmill_sound.wav")

# Set up the video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
cap.set(cv2.CAP_PROP_FPS, 30)
# cap.set(cv2.CAP_PROP_CONTRAST, 0.5)
# cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.8)

lower2 = None
upper2 = None
if USE_BGR:
    # Define the lower and upper bounds of the red color in BGR (note: not RGB, since the camera uses BGR)
    if USE_BLUE:
        lower_red = np.array([100, 0, 0])
        upper_red = np.array([255, 100, 100])
    else:
        lower_red = np.array([0, 0, 130])
        upper_red = np.array([100, 100, 255])
else:
    # Define the lower and upper bounds of the red color in HSV
    if USE_BLUE:
        lower_red = np.array([85, 80, 80])
        upper_red = np.array([110, 180, 255])
    else:
        lower_red = np.array([0, 120, 90])
        upper_red = np.array([10, 255, 255])
        lower2 = np.array([170, 120, 90])
        upper2 = np.array([180, 255, 255])

print("Arguments: Show Video: {}, Use Blue: {}, Show Mask: {}, Use BGR: {}".format(SHOW_VIDEO, USE_BLUE, SHOW_MASK, USE_BGR))

# Initialize variables
last_frame_red = 0
loop_count = 0
start_time = time.time()
last_red_dot_time = start_time-5
distance = 0
last_speed = 0
elapsed_time_min = 0

def cleanup():
    # Release the video capture and close the window
    cap.release()
    cv2.destroyAllWindows()

    # Print the number of loops detected
    print("Number of loops detected:", loop_count)

    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # Open the log file in append mode
    with open("activity_log.txt", "a") as f:
        # Write the distance, elapsed time, and timestamp to the log file
        f.write("{},{},miles,{},minutes\n".format(timestamp, distance, elapsed_time_min))

curX = 0
curY = 0
curCount = TEXT_DISPLAY_INTERVAL
phsv = [0,0,0]

def mouse_callback(event, x, y, flags, param):
    global curX,curY

    if event == cv2.EVENT_MOUSEMOVE:
        curX = x
        curY = y

# Define a signal handler function
def signal_handler(sig, frame):
    print("Exiting via signal handler")
    cleanup()
    os.sys.exit(0)

# Register the signal handler function
signal.signal(signal.SIGINT, signal_handler)

try:
    if SHOW_VIDEO:
        cv2.namedWindow(WIN_TITLE)
        cv2.setMouseCallback(WIN_TITLE, mouse_callback)
    while True:
        # Read a frame from the video capture
        ret, frame = cap.read()

        if frame is None or not ret:
            print("Error: No frame captured")
            print("Ret:", ret)
            break

        if not USE_BGR:
            # Convert the frame to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Threshold the frame to only show red pixels
            mask = cv2.inRange(hsv, lower_red, upper_red)
            if lower2 is not None:
                mask2 = cv2.inRange(hsv, lower2, upper2)
                mask = cv2.bitwise_or(mask, mask2)
        else:
            # Threshold the frame to only show red pixels
            mask = cv2.inRange(frame, lower_red, upper_red)

        # Find contours in the thresholded frame
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Check if a red dot is present in the frame
        red_dot_present = False
        area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 200:

                # Find the centroid of the contour
                # M = cv2.moments(contour)
                # cx = int(M['m10'] / M['m00'])
                # cy = int(M['m01'] / M['m00'])

                # Check if the surrounding pixels are black-ish
                # surrounding_pixels = frame[cy-5:cy+5, cx-5:cx+5]
                # if np.all(surrounding_pixels >= [0, 0, 0]) and np.all(surrounding_pixels <= [100, 100, 100]):
                #     # Draw a circle at the centroid of the contour
                #     cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                # else:
                #     continue

                red_dot_present = True

                if SHOW_VIDEO:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
 
                break
        
            # print("Area:", area)
 
        # If a red dot is present and the last frame did not have a red dot, possible hit
        if red_dot_present and not last_frame_red:
            # Calculate the time since the last red dot detection
            current_time = time.time()
            time_since_last_red_dot = current_time - last_red_dot_time
            cur_speed = TRACK_LENGTH_MILES / (time_since_last_red_dot / 3600)

            if cur_speed < 5 or (cur_speed < 7 and last_speed > 2) or (cur_speed < 15 and last_speed > 4):
                # ignore false positives that show ridiculous speeds
                last_speed = cur_speed

                distance += TRACK_LENGTH_MILES
                elapsed_time_min = (current_time - start_time) / 60

                # Update the time of the last red dot detection
                last_red_dot_time = current_time

                # wave_obj.play()
                print("Speed = {:.2f}mph, Distance = {:.2f}mi, Time = {:.2f}m, Avg Speed = {:.2f}, LoopTime = {:.2f}s".format(cur_speed, distance, elapsed_time_min, distance/(elapsed_time_min/60), time_since_last_red_dot))
                
                loop_count += 1

        # Update the last frame red dot status
        if red_dot_present:
            last_frame_red = FRAME_MEMORY_MAX
        elif last_frame_red > 0:
            last_frame_red -= 1

        # Display the frame
        if SHOW_VIDEO:
            if SHOW_MASK:
                frame = cv2.bitwise_and(frame, frame, mask=mask)

            if curCount == TEXT_DISPLAY_INTERVAL:
                curCount = 0
                # Get the RGB value of the selected pixel
                pbgr = frame[curY, curX]

                # Convert the RGB value to HSV
                phsv = cv2.cvtColor(np.uint8([[pbgr]]), cv2.COLOR_BGR2HSV)
                phsv = phsv[0][0]
            curCount += 1

            cv2.putText(frame, f"X: {curX}, Y: {curY}, HSV: {phsv}, AREA: {area}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow(WIN_TITLE, frame)

            # Exit the program if the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

except Exception as e:
    print("Exiting")
    print(e)

cleanup()