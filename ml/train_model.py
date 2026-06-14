import os
import json
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam

# ===== Config =====
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 20
TRAIN_DIR = "data/train_resized"
VAL_DIR   = "data/val_resized"
SAVE_DIR  = "model/models"
MODEL_PATH = os.path.join(SAVE_DIR, "skin_model.h5")
CLASS_INDICES_PATH = os.path.join(SAVE_DIR, "class_indices.json")
HISTORY_PATH = os.path.join(SAVE_DIR, "training_history.json")

os.makedirs(SAVE_DIR, exist_ok=True)

# ===== Data Generators with aggressive augmentation =====
train_gen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

val_gen = ImageDataGenerator(rescale=1./255)

train_data = train_gen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

val_data = val_gen.flow_from_directory(
    VAL_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False
)

# Save class mapping
with open(CLASS_INDICES_PATH, "w") as f:
    json.dump(train_data.class_indices, f)

# ===== Transfer Learning with MobileNetV2 =====
base_model = MobileNetV2(
    weights='imagenet', 
    include_top=False, 
    input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3)
)

# Freeze base model layers initially
base_model.trainable = False

# Build custom top layers
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.5)(x)
predictions = Dense(train_data.num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

# Compile model
model.compile(
    optimizer=Adam(learning_rate=1e-3),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# ===== Callbacks =====
callbacks = [
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6, verbose=1),
    ModelCheckpoint(MODEL_PATH, monitor='val_loss', save_best_only=True, verbose=1)
]

print("Starting Phase 1: Training top layers (frozen base)...")
history1 = model.fit(
    train_data,
    validation_data=val_data,
    epochs=10,
    callbacks=callbacks
)

# (Optional) Fine-tuning: Unfreeze top layers of base model for better accuracy
print("Starting Phase 2: Fine-tuning top layers of base model...")
base_model.trainable = True

# Freeze bottom 100 layers, unfreeze the rest
for layer in base_model.layers[:100]:
    layer.trainable = False

# Recompile with a lower learning rate
model.compile(
    optimizer=Adam(learning_rate=1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history2 = model.fit(
    train_data,
    validation_data=val_data,
    epochs=10,
    callbacks=callbacks
)

# Combine history
hist1_dict = history1.history
hist2_dict = history2.history
combined_hist = {}
for key in hist1_dict.keys():
    combined_hist[key] = [float(x) for x in hist1_dict[key]] + [float(x) for x in hist2_dict[key]]

# Save training history to JSON
with open(HISTORY_PATH, "w") as f:
    json.dump(combined_hist, f)

print(f"✅ Training complete.\n- Model: {MODEL_PATH}\n- Class indices: {CLASS_INDICES_PATH}\n- History: {HISTORY_PATH}")
