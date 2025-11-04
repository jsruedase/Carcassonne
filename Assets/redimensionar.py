from PIL import Image
import os

# Carpeta donde están tus imágenes
carpeta = "C:/Users/pctor/Desktop/Nacional/Semestre6/IntroIA/Proyecto2/Carcassonne/Assets/ImagenesLosas"

# Tamaño deseado
nuevo_tamano = (333, 333)

# Crear carpeta de salida 
salida = os.path.join(carpeta, "redimensionadas")
os.makedirs(salida, exist_ok=True)

# Procesar cada imagen PNG
for archivo in os.listdir(carpeta):
    if archivo.lower().endswith(".png"):
        ruta = os.path.join(carpeta, archivo)
        imagen = Image.open(ruta)
        imagen_redimensionada = imagen.resize(nuevo_tamano)
        imagen_redimensionada.save(os.path.join(salida, archivo))

print(" Todas las imágenes fueron redimensionadas a 333x333 píxeles.")
print(f"Se guardaron en: {salida}")
