# 📸 Image Segmentation with YoLo Model 🚀

Welcome to our repository! Here, we're all about image segmentation. Our star player is the `image_segmentation.ipynb` file, a Jupyter notebook that uses the YoLo model to perform image segmentation on a set of input images. 🖼️

## 📁 Files in this Repository

### 📄 requirements.txt

This is the magic scroll 📜 that lists all the Python dependencies you need to run our software. It's like a shopping list for your Python environment! 🛒 Some of the major dependencies include numpy, pandas, matplotlib, opencv-python, torch, torchvision, and many others which are used by YOLO.

To install all the dependencies listed in this file, just run the following command in your terminal:

```bash
pip install -r requirements.txt
```

🔔 **Note:** The versions of the dependencies are explicitly mentioned to ensure that the software runs as expected. If a different version of a dependency is used, it may cause unexpected behavior or errors.

### 📓 image_segmentation.ipynb

This is where the magic happens! 🎩✨ This Jupyter notebook uses the YoLo model to detect objects such as houses, lawns, driveways, etc., in images. It reads images from an input folder, performs object detection on each image, and saves the results in an output folder.

Here are some of the key functions/methods used in this notebook:

1. `YOLO()`: This function from the ultralytics library is used to load the trained YoLo model weights.
2. `os.listdir()`: This function from the os library is used to get the list of all files in the input folder.
3. `cv2.imread()`: This function from the cv2 library is used to read an image file.
4. `model()`: This method is used to perform object detection on an image.

Here's a quick example of how to use it:

```python
model = YOLO("model/best.pt")
input_folder = "input_images"
output_folder = "Results"
for filename in os.listdir(input_folder):
    input_image_path = os.path.join(input_folder, filename)
    image = cv2.imread(input_image_path)
    results_image = model(
        image,
        save=True,
        project=output_folder,
        name=os.path.splitext(filename)[0],
        boxes=False,
        show_labels=False,
    )
```

🔔 **Notes:**
1. The 'boxes' parameter in the model method is deprecated and will be removed in future versions of ultralytics. The 'show_boxes' parameter should be used instead.
2. The results of the object detection are saved in the output folder with the same name as the input image file.
3. Ensure that you are using python version 3.11.
4. You can check your python version using the command

    ```bash
    python3 --version
    ```

That's all folks! We hope you find this repository useful and exciting. Happy coding! 🎉👩‍💻👨‍💻🎉
