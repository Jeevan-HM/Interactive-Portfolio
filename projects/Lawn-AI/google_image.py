import datetime
import os
import shutil

import boto3
import numpy as np
import requests

api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY")
map_size = "640x640"
size = "640x640"
zoom = 20
map_type = "satellite"
fov = 110  # Field of view in degrees
pitch = 0
heading = 0  # hybrid"
# satellite


def getimage_google(parcel_coordinates):
    """
    The function `getimage_google` generates a static map image using Google Maps API based on given
    parcel coordinates and saves it as a PNG file.

    :param parcel_coordinates: The parameter `parcel_coordinates` is a list of tuples representing the
    coordinates of the parcels. Each tuple should contain the longitude and latitude values of a parcel.
    For example:
    :return: the content of the response from the Google Maps API.
    """
    try:
        shutil.rmtree("Google_Generated_Image")
    except:
        pass
    if not os.path.exists("Google_Generated_Image"):
        os.makedirs("Google_Generated_Image")
    # Define the filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    filename = f"Google_Generated_Image/measure-{timestamp}.jpg"
    center_lat = (
        max(lat for lon, lat in parcel_coordinates)
        + min(lat for lon, lat in parcel_coordinates)
    ) / 2  # &scale=2.0
    center_lon = (
        max(lon for lon, lat in parcel_coordinates)
        + min(lon for lon, lat in parcel_coordinates)
    ) / 2

    static_map_url_hybrid = f"https://maps.googleapis.com/maps/api/staticmap?center={center_lat},{center_lon}&zoom={zoom}&size={map_size}&maptype={map_type}&key={api_key}&path=color:red|fillcolor:transparent|"

    for lon, lat in parcel_coordinates:
        static_map_url_hybrid += f"{lat},{lon}|"

    static_map_url_hybrid = static_map_url_hybrid[:-1]

    response_hybrid = requests.get(static_map_url_hybrid)

    with open(filename, "wb") as f:
        f.write(response_hybrid.content)

    # The code provided is using the AWS SDK for Python (Boto3) to upload the generated image file
    # to an S3 bucket and make it publicly accessible.

    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "YOUR_AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get(
        "AWS_SECRET_ACCESS_KEY", "YOUR_AWS_SECRET_ACCESS_KEY"
    )
    aws_region = "us-west-2"  # Replace with the correct region
    # The code `s3 = boto3.resource("s3", region_name=aws_region, aws_access_key_id=aws_access_key_id,
    # aws_secret_access_key=aws_secret_access_key)` is creating an instance of the AWS S3 service
    # resource.
    s3 = boto3.resource(
        "s3",
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    bucket_name = "lawnaiabc"
    image_name = f"measure-{timestamp}.jpg"
    object_key = f"Google_Generated_Image/{image_name}"
    # The code block `with open(filename, "rb") as data:
    # s3.Bucket(bucket_name).put_object(Key=object_key, Body=data)
    # s3.put_object_acl(Bucket=bucket_name, Key=object_key, ACL="public-read")` is responsible for
    # uploading the generated image file to an S3 bucket and making it publicly accessible.
    with open(filename, "rb") as data:
        s3.Bucket(bucket_name).put_object(Key=object_key, Body=data)
    client_s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
    )
    client_s3.put_object_acl(Bucket=bucket_name, Key=object_key, ACL="public-read")
    google_image_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
    return filename, timestamp, google_image_url
