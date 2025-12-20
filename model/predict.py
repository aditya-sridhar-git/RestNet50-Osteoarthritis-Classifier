import cv2, numpy as np, tensorflow as tf
from config import LABELS, IMG_SIZE

model = tf.keras.models.load_model("model/arthritis_severity_model.h5")

def predict_severity(path):
    img = cv2.imread(path)
    img = cv2.resize(img, IMG_SIZE) / 255.0
    img = np.expand_dims(img, 0)
    pred = model.predict(img)
    return LABELS[np.argmax(pred)]
