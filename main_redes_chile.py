# -*- coding: utf-8 -*-
"""MAIN_REDES_CHILE.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NHFyth7gPRbRAVpV7U0vdQjyCcAn4S6Y
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import tensorflow as tf
import csv
from tensorflow.keras.layers import Input, Conv2D, BatchNormalization, ReLU, MaxPooling2D, GlobalAveragePooling2D, Dense, Add, Dropout, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import seaborn as sns
from sklearn.utils import class_weight

def cargar_datos(ruta):
    datos = []
    etiquetas = []
    for clase in os.listdir(ruta):
        if clase == 'Nsr':
            etiqueta = 0
        elif clase == 'Chf':
            etiqueta = 1
        else:
            continue
        clase_ruta = os.path.join(ruta, clase)
        for archivo in os.listdir(clase_ruta):
            archivo_ruta = os.path.join(clase_ruta, archivo)
            # Cargar datos de CSV
            dato = pd.read_csv(archivo_ruta, header=None).values
            datos.append(dato)
            etiquetas.append(etiqueta)
    return np.array(datos), np.array(etiquetas)

def plot_metric(history, version, save_path, metric, metric_label, title, ylabel):
    """

    Args:
      history:
      version:
      save_path:
      metric:
      metric_label:
      title:
      ylabel:
    """
    plt.figure()
    plt.ylim(bottom=0)
    plt.plot(history.history[metric], label=f'{metric_label} de Entrenamiento', linewidth=2)
    plt.plot(history.history[f'val_{metric}'], label=f'{metric_label} de Validación', linewidth=2)
    plt.grid()
    plt.title(f'{title} - {version}')
    plt.ylabel(ylabel)
    plt.xlabel('Epoch')
    plt.legend(loc='upper right')
    plt.savefig(f'{save_path}/{version}_{metric}.png')
    plt.show()

def plot_accuracy(history, version, save_path):
    plot_metric(history, version, save_path, 'accuracy', 'Exactitud', 'Exactitud', 'Exactitud')

def plot_loss(history, version, save_path):
    plot_metric(history, version, save_path, 'loss', 'Pérdida', 'Pérdida', 'Pérdida')

def plot_precision(history, version, save_path):
    precision_key = [key for key in history.history.keys() if 'precision' in key.lower()][0]
    plot_metric(history, version, save_path, precision_key, 'Precisión', 'Precisión', 'Precisión')

def plot_recall(history, version, save_path):
    recall_key = [key for key in history.history.keys() if 'recall' in key.lower()][0]
    plot_metric(history, version, save_path, recall_key, 'Recall', 'Recall', 'Recall')

def choose_model():
    print("Choose a model to use:")
    print("1. Sequential Model 1")
    print("2. VGG19 Model")
    print("3. MNIST Test Model")
    print("4. ResNet Model")

    opcion = int(input("Enter the number of the model you want to use: "))

    if opcion == 1:
        return sequential_model_1()
    elif opcion == 2:
        return vgg19_model()
    elif opcion == 3:
        return mnist_test_model()
    elif opcion == 4:
        return resnet_model((64, 64, 1), 1)
    else:
        print("Invalid opcion")
    return None

def sequential_model_1():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(filters=512, kernel_size=3, activation='relu', padding='same', input_shape=(256, 256, 1)),
        tf.keras.layers.Conv2D(filters=128, kernel_size=3, activation='relu', padding='same'),
        tf.keras.layers.MaxPool2D(),
        tf.keras.layers.Dropout(0.2),

        tf.keras.layers.Conv2D(filters=128, kernel_size=3, activation='relu', padding='same'),
        tf.keras.layers.MaxPool2D(),
        tf.keras.layers.Dropout(0.2),

        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(1024, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1024, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

def vgg19_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same', input_shape=(256, 256, 1)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.MaxPooling2D((2, 2), strides=(2, 2)),

        tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.MaxPooling2D((2, 2), strides=(2, 2)),

        tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.MaxPooling2D((2, 2), strides=(2, 2)),

        tf.keras.layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.MaxPooling2D((2, 2), strides=(2, 2)),

        tf.keras.layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
        tf.keras.layers.MaxPooling2D((2, 2), strides=(2, 2)),

        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(4096, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(4096, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

def mnist_test_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(32, (5,5), padding='same', activation='relu', input_shape=(256, 256, 1)),
        tf.keras.layers.Conv2D(32, (5,5), padding='same', activation='relu'),
        tf.keras.layers.MaxPool2D(),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Conv2D(64, (3,3), padding='same', activation='relu'),
        tf.keras.layers.Conv2D(64, (3,3), padding='same', activation='relu'),
        tf.keras.layers.MaxPool2D(strides=(2,2)),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

def rexsidual_block(x, filters, kernel_size=3, stride=1):
    shortcut = x

    x = Conv2D(filters, kernel_size=kernel_size, strides=stride, padding='same')(x)
    x = BatchNormalization()(x)
    x = ReLU()(x)

    x = Conv2D(filters, kernel_size=kernel_size, padding='same')(x)
    x = BatchNormalization()(x)

    if stride != 1 or shortcut.shape[-1] != filters:
        shortcut = Conv2D(filters, kernel_size=1, strides=stride)(shortcut)
    x = Add()([x, shortcut])
    x = ReLU()(x)

    return x

def resnet_model(input_shape, num_classes):
    inputs = Input(shape=input_shape)
    x = Conv2D(64, 7, strides=2, padding='same')(inputs)
    x = BatchNormalization()(x)
    x = ReLU()(x)
    x = MaxPooling2D(pool_size=3, strides=2, padding='same')(x)

    x = residual_block(x, 64, stride=1)
    x = residual_block(x, 64, stride=1)
    x = residual_block(x, 128, stride=2)
    x = residual_block(x, 128, stride=1)
    x = residual_block(x, 256, stride=2)
    x = residual_block(x, 256, stride=1)
    x = residual_block(x, 512, stride=2)
    x = residual_block(x, 512, stride=1)

    x = GlobalAveragePooling2D()(x)
    outputs = Dense(num_classes, activation='sigmoid')(x)

    model = Model(inputs, outputs)
    return model


def save_training_history(history, version, save_path):
    file_path = f'{save_path}/{version}_historial_entrenamiento.csv'

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Escribir la cabecera
        writer.writerow(['epoch'] + list(history.history.keys()))
        # Escribir los datos
        for i in range(len(history.history['loss'])):
            row = [i + 1] + [history.history[key][i] for key in history.history.keys()]
            writer.writerow(row)

def test_model(version, results_dir, x_test, y_test):
    """
    Realiza el test del modelo guardado, muestra las métricas de evaluación y guarda los resultados en un archivo CSV y la matriz de confusión como imagen.

    Parámetros:
    version: Versión del modelo.
    results_dir: Directorio donde se encuentra el modelo guardado.
    x_test: Datos de prueba.
    y_test: Etiquetas de prueba.
    """
    # Cargar el modelo guardado
    model_path = os.path.join(results_dir, f'model_{version}.h5')
    model = tf.keras.models.load_model(model_path)

    # Evaluar el modelo en los datos de prueba
    test_loss, test_accuracy, test_precision, test_recall = model.evaluate(x_test, y_test)

    # Predecir y calcular la puntuación F1
    y_pred = model.predict(x_test)
    y_pred_classes = (y_pred > 0.5).astype("int32")  # Para clasificaciones binarias
    f1 = f1_score(y_test, y_pred_classes, average='weighted')

    # Reporte de clasificación
    report = classification_report(y_test, y_pred_classes, output_dict=True)

    # Guardar los resultados en un archivo CSV
    csv_path = os.path.join(results_dir, f'{version}_evaluacion_modelo.csv')
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Escribir la cabecera
        writer.writerow(['Métrica', 'Valor'])
        writer.writerow(['Loss', test_loss])
        writer.writerow(['Accuracy', test_accuracy])
        writer.writerow(['Precision', test_precision])
        writer.writerow(['Recall', test_recall])
        writer.writerow(['F1 Score', f1])

        # Escribir las métricas detalladas del reporte de clasificación
        writer.writerow([])
        writer.writerow(['Clase', 'Precision', 'Recall', 'F1-Score', 'Support'])
        for class_label, metrics in report.items():
            if isinstance(metrics, dict):
                writer.writerow([class_label, metrics['precision'], metrics['recall'], metrics['f1-score'], metrics['support']])

    print(f'Resultados de evaluación guardados en {csv_path}')

    # Mostrar y guardar la matriz de confusión como imagen
    conf_matrix = confusion_matrix(y_test, y_pred_classes)
    plt.figure(figsize=(10, 8))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
    plt.title('Matriz de Confusión')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.savefig(os.path.join(results_dir, f'{version}_confusion_matrix.png'))
    plt.show()


#####  MAAAAINNNNNNNN
train_dir = 'C:/Users/Gtaco/Documents/PROYECTO/Train'
validation_dir = 'C:/Users/Gtaco/Documents/PROYECTO/Validation'
test_dir = 'C:/Users/Gtaco/Documents/PROYECTO/Test'
results_dir = 'C:/Users/Gtaco/Documents/PROYECTO/Results'

version = 'Vgg19'

# Cargar datos
x_train, y_train = cargar_datos(train_dir)
x_val, y_val = cargar_datos(validation_dir)
x_test, y_test = cargar_datos(test_dir)

# Convertir los datos a tensores
x_train = x_train.astype('float32') / 255
x_val = x_val.astype('float32') / 255
x_test = x_test.astype('float32') / 255

# Imprimir tamaños de los conjuntos de datos
print('x_train shape:', x_train.shape)
print('y_train shape:', y_train.shape)
print('x_val shape:', x_val.shape)
print('y_val shape:', y_val.shape)
print('x_test shape:', x_test.shape)
print('y_test shape:', y_test.shape)

# Definir y compilar modelo
model = choose_model()
if model:
    print(model.summary())
    # Optional: save the model summary to a CSV file
    model_summary = []
    model.summary(print_fn=lambda x: model_summary.append(x))
    with open("model_summary.csv", 'w') as f:
        for line in model_summary:
            f.write(line + '\n')
    print("Saved to model_summary.csv")



# Compilar modelo
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])

# Definir el callback EarlyStopping
#early_stopping = EarlyStopping(monitor='val_loss', patience=3)


# Calcular los pesos de las clases
class_weights = class_weight.compute_class_weight(class_weight='balanced',
                                                  classes=np.unique(y_train),
                                                  y=y_train)

# Convertir a un diccionario para usar en el modelo
class_weights_dict = dict(enumerate(class_weights))

# Imprimir los pesos calculados
print("Class Weights: ", class_weights_dict)

# Entrenar el modelo con EarlyStopping
history = model.fit(x_train,
                    y_train,
                    epochs=100,  # Asegúrate de establecer un número suficientemente alto de épocas
                    verbose=1,
                    validation_data=(x_val, y_val),
                    class_weight=class_weights_dict)
                    #callbacks=[early_stopping])

# Guardar el modelo
model.save(f'{results_dir}/model_{version}.h5')

# Imprimir las claves del historial de entrenamiento para identificar las métricas
print(history.history.keys())

# Imprimir el historial de entrenamiento
print(history.history)
plot_accuracy(history, version, results_dir)
plot_loss(history, version, results_dir)

# Ajusta las llamadas a las funciones de trazado de precisión y recall con las claves correctas
plot_precision(history, version, results_dir)
plot_recall(history, version, results_dir)

# Guardar el historial de entrenamiento
save_training_history(history, version, results_dir)

# Evaluar modelo
test_model(version, results_dir, x_test, y_test)