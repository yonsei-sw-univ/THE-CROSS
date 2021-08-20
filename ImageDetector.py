import os
import cv2
import numpy as np
import tensorflow as tf
from object_detection.builders import model_builder
from object_detection.utils import config_util
import pandas as pd
import tensorflow_hub as hub

detector = hub.load("https://tfhub.dev/tensorflow/efficientdet/lite2/detection/1")

customDetector = tf.saved_model.load('customDetector/saved_model')

labels = pd.read_csv('labels.csv', sep=';', index_col='ID')
labels = labels['OBJECT (2017 REL.)']

ambulance_rectCol = (255, 51, 000)
cane_rectCol = (204, 51, 000)
wheelchair_rectCol = (204, 51, 000)
baby_carriage_rectCol = (204, 51, 000)


def Detector(image):
    # Convert img to RGB
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Is optional but i recommend (float conversion and convert img to tensor image)
    rgb_tensor = tf.convert_to_tensor(rgb, dtype=tf.uint8)

    # Add dims to rgb_tensor
    rgb_tensor = tf.expand_dims(rgb_tensor, 0)

    boxes, scores, classes, num_detections = detector(rgb_tensor)

    pred_labels = classes.numpy().astype('int')[0]

    pred_labels = [labels[i] for i in pred_labels]
    pred_boxes = boxes.numpy()[0].astype('int')
    pred_scores = scores.numpy()[0]

    img_result = image
    pos_result = []

    # loop throughout the detections and place a box around it
    for score, (ymin, xmin, ymax, xmax), label in zip(pred_scores, pred_boxes, pred_labels):
        if score < 0.5 or label != 'person':
            continue

        score_txt = f'{100 * round(score, 0)}'
        img_result = cv2.rectangle(img_result, (xmin, ymax), (xmax, ymin), (0, 255, 0), 1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img_result, label, (xmin, ymax - 10), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(img_result, score_txt, (xmax, ymax - 10), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

        pos_result.append([xmin, ymax, xmax, ymin])

    return img_result, pos_result


# image = Pure Image that not drew anything
# drawOnImg = image that you gonna draw something on
def CustomDetector(image, drawOnImg=None):
    # Convert img to RGB
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Is optional but i recommend (float conversion and convert img to tensor image)
    rgb_tensor = tf.convert_to_tensor(rgb, dtype=tf.uint8)

    # Add dims to rgb_tensor
    rgb_tensor = tf.expand_dims(rgb_tensor, 0)
    output_dict = customDetector(rgb_tensor)

    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    pred_labels = output_dict['detection_classes']
    pred_boxes = output_dict['detection_boxes']
    pred_scores = output_dict['detection_scores']

    h, w, c = image.shape
    img_result = image

    ambulance_pos = []
    cane_pos = []
    wheelchair_pos = []
    baby_carriage_pos = []

    if drawOnImg is not None:
        img_result = drawOnImg

    # loop throughout the detections and place a box around it
    for score, (ymin, xmin, ymax, xmax), label in zip(pred_scores, pred_boxes, pred_labels):
        if score < 0.5:
            continue

        y_min = int(ymin * h)
        x_min = int(xmin * w)
        y_max = int(ymax * h)
        x_max = int(xmax * w)
        
        #Try-catch will be removed
        try:
            score_txt = f'{100 * round(score, 0)}'
            if label == 4:
                label_txt = 'ambulance'
                img_result = cv2.rectangle(img_result, (x_min, y_max), (x_max, y_min), ambulance_rectCol, 1)
                ambulance_pos.append([x_min, y_max, x_max, y_min])
            elif label == 3:
                label_txt = 'cane'
                img_result = cv2.rectangle(img_result, (x_min, y_max), (x_max, y_min), cane_rectCol, 1)
                cane_pos.append([x_min, y_max, x_max, y_min])
            elif label == 1:
                label_txt = 'wheelchair'
                img_result = cv2.rectangle(img_result, (x_min, y_max), (x_max, y_min), wheelchair_rectCol, 1)
                wheelchair_pos.append([x_min, y_max, x_max, y_min])
            elif label == 2:
                label_txt = 'baby_carriage'
                img_result = cv2.rectangle(img_result, (x_min, y_max), (x_max, y_min), baby_carriage_rectCol, 1)
                baby_carriage_pos.append([x_min, y_max, x_max, y_min])

            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img_result, label_txt, (x_min, y_max - 10), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(img_result, score_txt, (x_max, y_max - 10), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
        except Exception as e:
            print(e)

    return img_result, ambulance_pos, cane_pos, wheelchair_pos, baby_carriage_pos
