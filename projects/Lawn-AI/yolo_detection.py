import os
import shutil

import boto3
import cv2
import numpy as np
from ultralytics import YOLO

# Load the YOLO model
model = YOLO("best.pt")


# Define a Gradio function to make predictions on an uploaded image


def predict_image(input_image, timestamp):
    """
    The `predict_image` function takes an input image, uses a YOLO model to make predictions on the
    image, and returns the predicted image along with the pixel counts for different classes of objects
    in the image.

    :param input_image: The input image is the image for which you want to make predictions using the
    YOLO model
    :return: The function `predict_image` returns a tuple containing the following values:
    """
    # Make predictions using the YOLO model
    try:
        shutil.rmtree("Detection")
    except:
        pass
    image = cv2.imread(input_image)
    filename = "Image_Detection"
    results_image = model(
        image,
        save=True,
        project="Detection",
        name=filename,
        boxes=False,
        show_labels=False,
    )
    house_pixel = []
    driveway_pixels = []
    extra_lawn = []
    extra_driveway = []
    extra_sidewalk = []
    other_pixels = []
    for r in results_image:
        for i in range(len(results_image[0].masks)):
            classid = int(results_image[0].boxes[i].cls[0].item())
            # Driveways         0
            # Extra Driveway    1
            # Extra Lawn        2
            # Extra Sidewalk    3
            # House             4
            # Other             5
            mask = results_image[0].masks[i].data[0].numpy()
            num_pixels = np.count_nonzero(mask)
            if classid == 0:
                driveway_pixels.append(num_pixels)
            elif classid == 1:
                extra_driveway.append(num_pixels)
            elif classid == 2:
                extra_lawn.append(num_pixels)
            elif classid == 3:
                extra_sidewalk.append(num_pixels)
            elif classid == 4:
                house_pixel.append(num_pixels)
            else:
                other_pixels.append(num_pixels)
            total_removable_pixel = other_pixels + extra_driveway + driveway_pixels

    try:
        house_pixel_pixel = sum(house_pixel) / len(house_pixel)
    except:
        house_pixel_pixel = 0
    try:
        driveway_pixels_pixel = sum(driveway_pixels) / len(driveway_pixels)
    except:
        driveway_pixels_pixel = 0
    try:
        extra_lawn_pixel = sum(extra_lawn) / len(extra_lawn)
    except:
        extra_lawn_pixel = 0
    try:
        extra_driveway_pixel = sum(extra_driveway) / len(extra_driveway)
    except:
        extra_driveway_pixel = 0
    try:
        extra_sidewalk_pixel = sum(extra_sidewalk) / len(extra_sidewalk)
    except:
        extra_sidewalk_pixel = 0
    try:
        other_pixels_pixel = sum(other_pixels) / len(other_pixels)
    except:
        other_pixels_pixel = 0

    os.rename(
        "Detection/Image_Detection/image0.jpg",
        f"Detection/Image_Detection/detection-{timestamp}.jpg",
    )
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "YOUR_AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get(
        "AWS_SECRET_ACCESS_KEY", "YOUR_AWS_SECRET_ACCESS_KEY"
    )
    aws_region = "us-west-2"  # Replace with the correct region
    bucket_name = "lawnaiabc"
    object_key = f"Detection/detection-{timestamp}.jpg"
    s3 = boto3.resource(
        "s3",
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    with open(f"Detection/Image_Detection/detection-{timestamp}.jpg", "rb") as data:
        s3.Bucket(bucket_name).put_object(Key=object_key, Body=data)
    client_s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
    )
    client_s3.put_object_acl(Bucket=bucket_name, Key=object_key, ACL="public-read")
    detected_image_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"

    return (
        house_pixel_pixel,
        driveway_pixels_pixel,
        extra_driveway_pixel,
        extra_lawn_pixel,
        extra_sidewalk_pixel,
        other_pixels_pixel,
        detected_image_url,
    )
