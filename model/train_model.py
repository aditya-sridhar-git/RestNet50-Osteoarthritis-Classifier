import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model

train_dir = "../data/train"
test_dir = "../data/test"

datagen = ImageDataGenerator(rescale=1./255)

train = datagen.flow_from_directory(train_dir, target_size=(224,224))
test = datagen.flow_from_directory(test_dir, target_size=(224,224))

base = ResNet50(weights="imagenet", include_top=False)
base.trainable = False

x = GlobalAveragePooling2D()(base.output)
x = Dense(256, activation="relu")(x)
output = Dense(5, activation="softmax")(x)

model = Model(base.input, output)
model.compile("adam", "categorical_crossentropy", ["accuracy"])
model.fit(train, epochs=10, validation_data=test)

model.save("arthritis_severity_model.h5")
