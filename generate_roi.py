import cv2
import os
import json
import numpy as np

        
def loadImages(folder_path):
    images = []
    img_c = 0
    for filename in os.listdir(folder_path):
        # Construct the full path to the file
        file_path = os.path.join(folder_path, filename)
        # Check if the file is an image based on its extension
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            # Load the image using OpenCV
            image = cv2.imread(file_path)
            image_meta = {
                "image_id": f'image_{img_c}',
                "url": file_path,
                "condition": None,
                "roi_array": []
            }
            if image is not None:
                images.append(image_meta)
            else:
                print(f"Warning: {filename} could not be loaded as an image.")
        img_c+=1
    return images


def generateROI(image):
    #display image
    condition = input("Which condition was applied to this sample?: ")
    #check if valid condition
    image['condition'] = condition
    image_ptr = cv2.imread(image['url'])
    try:
        roi_c = input("How many regions of interest are in this image?: ")
        roi_c = int(roi_c)
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
    for i in range(0,roi_c):
        # List to store points
        points = []
        # Mouse callback function to capture points
        def select_points(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((x, y))
                cv2.circle(image_ptr, (x, y), 5, (0, 0, 255), -1)
                cv2.imshow("Image", image_ptr)

        # Load the image
        cv2.imshow("Image", image_ptr)

        # Set mouse callback
        cv2.setMouseCallback("Image", select_points)

        # Wait for user to press 'q' after selecting points
        print("Click to select points for the irregular ROI. Press 'q' when done.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Convert points to a NumPy array for fillPoly
        if points:
            roi_points = np.array([points], dtype=np.int32)
            mask = np.zeros(image_ptr.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [roi_points], color=(255))
            # Apply mask to the image
            masked_image = cv2.bitwise_and(image_ptr, image_ptr, mask=mask)
            # Display masked ROI
            cv2.imshow("Irregular ROI", masked_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            mean_color = cv2.mean(image_ptr, mask=mask)[:3]
            print(mean_color)
            roi = {
                "roi_id": f'roi_{i}',
                "coordinates": roi_points.tolist(),
                "average_color": mean_color
            }
            image['roi_array'].append(roi)
            #Save masked image
            image_id = image['image_id']
            roi_id = roi['roi_id']
            masked_image_id = image_id + '-' + roi_id + '.png'
            cv2.imwrite(f'./images/rois/{masked_image_id}', masked_image)
        else:
            print("Unable to select ROI")
    
def createFile(data):
    with open('images.json', "w") as json_file:
        json.dump(data, json_file, indent=4)
    
def main():
    images = loadImages('./images')
    for image in images: 
        generateROI(image)
    createFile(images)

main()