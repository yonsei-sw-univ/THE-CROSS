import tensorflow_hub as hub
import cv2
import numpy
import tensorflow as tf
import pandas as pd

detector = hub.load("https://tfhub.dev/tensorflow/efficientdet/lite2/detection/1")
customDetector = tf.saved_model.load('customDetector')

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

    boxes, scores, classes, num_detections = customDetector(rgb_tensor)

    pred_labels = classes.numpy().astype('int')[0]

    pred_labels = [labels[i] for i in pred_labels]
    pred_boxes = boxes.numpy()[0].astype('int')
    pred_scores = scores.numpy()[0]

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

        score_txt = f'{100 * round(score, 0)}'

        if label == 'ambulance':
            img_result = cv2.rectangle(img_result, (xmin, ymax), (xmax, ymin), ambulance_rectCol, 1)
            ambulance_pos.append([xmin, ymax, xmax, ymin])
        elif label == 'cane':
            img_result = cv2.rectangle(img_result, (xmin, ymax), (xmax, ymin), cane_rectCol, 1)
            cane_pos.append([xmin, ymax, xmax, ymin])
        elif label == 'wheelchair':
            img_result = cv2.rectangle(img_result, (xmin, ymax), (xmax, ymin), wheelchair_rectCol, 1)
            wheelchair_pos.append([xmin, ymax, xmax, ymin])
        elif label == 'baby_carriage':
            img_result = cv2.rectangle(img_result, (xmin, ymax), (xmax, ymin), baby_carriage_rectCol, 1)
            baby_carriage_pos.append([xmin, ymax, xmax, ymin])

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img_result, label, (xmin, ymax - 10), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(img_result, score_txt, (xmax, ymax - 10), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

    return img_result, ambulance_pos, cane_pos, wheelchair_pos, baby_carriage_pos
