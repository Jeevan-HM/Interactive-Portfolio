from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security.api_key import APIKeyQuery
from area_cal import get_image
from yolo_detection import predict_image
import shutil
import uvicorn
import joblib


app = FastAPI()


# Define your API key
api_keys = [
    "a1n2u3r4a5g61j1e2e3v4a5n3k1u2n3a4l5Yj1u2p3i4t5e6r73V59uY34878X897878978X9S87l1a2w3n4a5i8Xaa11nn22uu33rr44aa55gg"
]

# http://127.0.0.1:8000/protected?api_key=a1n2u3r4a5g61j1e2e3v4a5n3k1u2n3a4l5Yj1u2p3i4t5e6r73V59uY34878X897878978X9S87l1a2w3n4a5i8Xaa11nn22uu33rr44aa55gg&input_string=6005 Aspen Meadow Dr, Indianapolis, IN 46237

# Create an instance of APIKeyQuery with the name "api_key" (matches the query parameter name)
api_key_query = APIKeyQuery(name="api_key")


# Function to validate the API key
def get_api_key(api_key: str = Security(api_key_query)) -> str:
    """
    The function `get_api_key` checks if the provided API key is valid and returns it if it exists in
    the list of valid API keys, otherwise it raises an HTTPException with an unauthorized status code
    and a detail message.

    :param api_key: The `api_key` parameter is a string that represents the API key provided by the user
    :type api_key: str
    :return: the API key if it is found in the `api_keys` list. If the API key is not found or is
    missing, it raises an HTTPException with a status code of 401 (Unauthorized) and a detail message of
    "Invalid or missing API Key".
    """
    if api_key in api_keys:
        print("api key", api_key)
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


def submit(input_address):
    """
    The `submit` function takes an input address, processes an image associated with that address, and
    returns various calculated areas related to the image, such as total lawn area, driveway area, house
    area, and other areas.

    :param input_address: The `input_address` parameter is the address of the property for which you
    want to calculate the lawn and driveway areas
    :return: The function `submit` returns a dictionary with the following keys and values:
    """

    total_area = 0
    driveway_pixel = 0
    driveway_area = 0
    lawn_area = 0
    address = input_address
    (
        file_name,
        timestamp,
        total_area,
        house_area,
        coordinates,
        google_image_url,
    ) = get_image(address)

    print("Before Predict Image")
    (
        house_pixel,
        driveway_pixel,
        extra_driveway,
        extra_lawn,
        extra_sidewalk,
        other_pixels,
        detected_image_url,
    ) = predict_image(file_name, timestamp)
    print("After predicting the predict_image")

    xgb_model = joblib.load("xgb_model.joblib")
    preds_test = xgb_model.predict([[total_area, house_area, house_pixel]])

    # driveway_area_sqft = driveway_pixel * float(preds_test)
    driveway_area_sqft = driveway_pixel * float(preds_test)

    driveway_area_sqft = driveway_pixel * float(
        xgb_model.predict([[total_area, driveway_area_sqft, driveway_pixel]])
    )

    extra_driveway_area_sqft = extra_driveway * float(preds_test)

    extra_driveway_area_sqft = extra_driveway * float(
        xgb_model.predict([[total_area, extra_driveway_area_sqft, extra_driveway]])
    )

    extra_lawn_area_sqft = extra_lawn * float(
        xgb_model.predict([[total_area, house_area, extra_lawn]])
    )
    extra_lawn_area_sqft = extra_lawn * float(
        xgb_model.predict([[total_area, extra_lawn_area_sqft, extra_lawn]])
    )

    extra_sidewalk_area_sqft = extra_sidewalk * float(preds_test)

    other_pixel_area_sqft = other_pixels * float(preds_test)

    other_pixel_area_sqft = other_pixels * float(
        xgb_model.predict([[total_area, other_pixel_area_sqft, other_pixels]])
    )

    driveway_area_sqft = round(driveway_area_sqft)
    extra_driveway_area_sqft = round(extra_driveway_area_sqft)
    extra_lawn_area_sqft = round(extra_lawn_area_sqft)
    total_area = round(total_area)
    house_area = round(house_area)
    other_pixel_area_sqft = round(other_pixel_area_sqft)

    if other_pixel_area_sqft <= 2000:
        lawn_area = round(total_area - house_area - driveway_area_sqft)
    else:
        lawn_area = round(
            total_area
            - house_area
            - driveway_area_sqft
            # - extra_driveway_area_sqft
            - other_pixel_area_sqft
        )
    lawn_area = abs(lawn_area)
    total_lawn_area = round(lawn_area + extra_lawn_area_sqft)
    driveway_area_sqft = round(driveway_area_sqft * 0.35)

    return {
        "total_lawn_area_sqft": total_lawn_area,
        "lawn_area_sqft": lawn_area,
        "driveway_ares_sqft": driveway_area_sqft,
        "house_area_sqft": house_area,
        "total_area_sqft": total_area,
        "other_area_sqft": other_pixel_area_sqft,
        "google_image_url": google_image_url,
        "detected_image_url": detected_image_url,
        "coordinates": coordinates
        # "image_array": predicted_image,
    }


# "image_array": image_array,


# Endpoint that requires an API key and an input string
@app.get("/protected")
def protected_route(input_string: str, api_key: str = Security(get_api_key)):
    """
    This is a protected route in a Python web application that takes an input string and an API key as
    parameters, validates the input string, and then generates an image based on the input string.

    :param input_string: The input_string parameter is a string that represents an address. It is used
    as input for generating an image
    :type input_string: str
    :param api_key: The `api_key` parameter is used to provide authentication and access control to the
    protected route. It is expected to be a string that represents a valid API key
    :type api_key: str
    :return: The code is returning the `area_json_details` if the input string is valid and the image is
    successfully generated. If there is an exception or the input string is invalid, it returns a
    message indicating that the image failed to generate for the given address.
    """
    validated_message = validate_string(input_string)
    try:
        if validated_message == "Input string is valid":
            try:
                shutil.rmtree("runs")
            except:
                pass
            total_area = 0
            lawn_area = 0
            area_json_details = submit(input_string)

            return area_json_details
    except Exception as e:
        print("Exception:", e)
        return {
            "message": f"Image failed to generate for the Addess {input_string}",
            "error": e,
        }


# Function to validate the input string
def validate_string(input_string: str) -> str:
    """
    The function `validate_string` checks if an input string contains illegal characters and raises an
    exception if it does, otherwise it returns a message indicating that the input string is valid.

    :param input_string: The input_string parameter is a string that needs to be validated
    :type input_string: str
    :return: a string that says "Input string is valid".
    """
    if contains_illegal_characters(input_string):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input string",
        )
    return "Input string is valid"


# Function to check for illegal characters (you can define your own logic)
def contains_illegal_characters(input_string: str) -> bool:
    # Define your own logic to check for illegal characters
    # Return True if illegal characters are found, False otherwise
    return False  # Placeholder logic


if __name__ == "__main__":
    uvicorn.run(app="main:app")
