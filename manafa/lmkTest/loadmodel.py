import os
import profile
import numpy as np
import tensorflow as tf
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2
from tensorflow.python.profiler import model_analyzer
from tensorflow.python.profiler.option_builder import ProfileOptionBuilder
from tensorflow.keras.models import load_model
# path to your saved .h5 model
model_path = "/home/ubuntu/E-MANAFA/manafa/lmkTest/MobileNetV2.h5"

# load the model
model = load_model(model_path)

# confirm load
print("Model loaded successfully!")
model.summary()

size_bytes = os.path.getsize(model_path)
size_mb = size_bytes / (1024 * 1024)
print(f"Model size: {size_bytes} bytes ({size_mb:.2f} MB)")
total_params = model.count_params()
print(f"Total parameters: {total_params}")

func = tf.function(lambda x: model(x))
input_shape = model.input_shape  # e.g., (None, 224, 224, 3)
concrete_func = func.get_concrete_function(
    tf.TensorSpec([1, *input_shape[1:]], model.inputs[0].dtype)
)

# Convert to frozen graph
frozen_func = convert_variables_to_constants_v2(concrete_func)

# Profile FLOPs
opts = ProfileOptionBuilder.float_operation()
flops_stats = model_analyzer.profile(graph=frozen_func.graph, options=opts)
print(f"FLOPs: {flops_stats.total_float_ops:,}")

# ============================
# Convert to TensorFlow Lite
# ============================
tflite_model_path = "/home/ubuntu/E-MANAFA/manafa/lmkTest/MobileNetV2.tflite"

converter = tf.lite.TFLiteConverter.from_keras_model(model)

# (Optional) Optimization for smaller size
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Convert
tflite_model = converter.convert()

# Save to file
with open(tflite_model_path, "wb") as f:
    f.write(tflite_model)

print(f"✅ TFLite model saved at: {tflite_model_path}")
print(f"📦 TFLite model size: {os.path.getsize(tflite_model_path) / 1024:.2f} KB")