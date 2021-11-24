#!/usr/bin/python3

########################################################################
# Adapted from the Open CV & Numpy Integration example from RealSense. #
########################################################################


import pyrealsense2 as rs
import numpy as np
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def configure_realsense():
    """
    Function to configure and start the realsense camera.

    @return: The pipeline object for accessing color & depth frames.
    """

    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)

    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))

    # Ensure that the RGB Sensor is running
    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)

    # Set configuration items
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)
    return pipeline


pipeline = configure_realsense()

try:
    with mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7) as hands:

        while True:

            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                print("Skipping Empty Frame!")
                continue

            # Convert image to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())

            # TODO: WHY DOES THIS LINE TURN ME BLUE?
            color_image = cv2.cvtColor(
                cv2.flip(color_image, 1), cv2.COLOR_BGR2RGB)

            # Run MEDIAPIPE here.
            color_image.flags.writeable = True
            results = hands.process(color_image)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:

                    # ----------------------------------------
                    # ESTIMATED HAND LANDMARKS ACCESSIBLE HERE
                    # ----------------------------------------

                    print(hand_landmarks)

                    mp_drawing.draw_landmarks(
                        color_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Show images
            cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('RealSense', color_image)
            cv2.waitKey(1)

finally:

    # Stop streaming
    pipeline.stop()