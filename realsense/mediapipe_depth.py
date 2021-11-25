#!/usr/bin/python3
"""
########################################################################
# Adapted from the Open CV & Numpy Integration example from RealSense. #
########################################################################
"""

import pyrealsense2 as rs
import numpy as np
import cv2
import mediapipe as mp

import mapper as mpr

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def landmark_to_pixels(landmark, width=640, height=480):
    """
    Width: 640
    Height: 480

    @return: the landmark estimation converted to a pixel tuple.
    """
    return int(landmark.x * width), int(landmark.y * height)


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


def configure_libmapper():
    """
    This function is used to configure a libmapper device with one signal.

    @return: both the mapper device as well as the associated mapper signal.
    """
    mpr_dev = mpr.device("realsense")
    mpr_sig = mpr_dev.add_signal(mpr.DIR_OUT, "wrist", 3, mpr.FLT,
                                 "position", 0, 1000, None, lambda s, e, i, v, t: print(v))

    while not mpr_dev.get_is_ready():
        mpr_dev.poll()

    print("MPR_DEV IS READY!!")

    return mpr_dev, mpr_sig


pipeline = configure_realsense()
mpr_dev, mpr_sig = configure_libmapper()


try:
    with mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7) as hands:

        while True:

            """
            Poll the libmapper device here with non-blocking strategy
            """
            mpr_dev.poll(0)

            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                print("Skipping Empty Frame!")
                continue

            # Convert image to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # TODO: WHY DOES THIS LINE TURN ME BLUE?
            color_image = cv2.cvtColor(
                cv2.flip(color_image, 1), cv2.COLOR_BGR2RGB)

            depth_image = cv2.flip(depth_image, 1)

            # Run MEDIAPIPE here.
            color_image.flags.writeable = True
            results = hands.process(color_image)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:

                    # ----------------------------------------
                    # HANDLE THE ESTIMATED HAND LANDMARKS HERE
                    #
                    # FYI: landmark[0] is the wrist joint.
                    # ----------------------------------------

                    if(hand_landmarks.landmark[0]):
                        # Convert landmark estimation to pixels within the wxh range
                        px = landmark_to_pixels(hand_landmarks.landmark[0])
                        # Print the depth of the wrist, as measured by the realsense
                        try:
                            print(depth_frame.get_distance(px[0], px[1]))
                        except:
                            print("skip")
                    else:
                        print("skip")

                    mp_drawing.draw_landmarks(
                        color_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # -------- Handle the Depth Map Image Stuff below --------

            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(
                depth_image, alpha=0.03), cv2.COLORMAP_JET)

            depth_colormap_dim = depth_colormap.shape
            color_colormap_dim = color_image.shape

            # If depth and color resolutions are different, resize color image to match depth image for display
            if depth_colormap_dim != color_colormap_dim:
                resized_color_image = cv2.resize(color_image, dsize=(
                    depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
                images = np.hstack((resized_color_image, depth_colormap))
            else:
                images = np.hstack((color_image, depth_colormap))
            # -------------------------------------------------------------------

            # TODO: I'd like to draw a circle or similar on the depth image that corresponds to the estimated wrist joint.
            # Show images
            cv2.namedWindow('RealSense w/ libmapper', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('RealSense w/ libmapper', images)
            cv2.waitKey(1)

finally:

    # Stop streaming
    pipeline.stop()
