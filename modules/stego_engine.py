
import numpy as np
import cv2
from PIL import Image
import math


class StegoEngine:

    @staticmethod
    def encode_lsb(image_path: str, data_bytes: bytes, output_path: str):
        """
        Oculta datos binarios dentro del bit menos significativo (LSB)
        de una imagen RGB y guarda el resultado en formato PNG.

        Estructura del mensaje:
            - 4 bytes: longitud del mensaje.
            - N bytes: contenido del mensaje.
        """

        # Abrir imagen y convertirla a RGB
        img = Image.open(image_path).convert("RGB")
        img_arr = np.array(img, dtype=np.uint8)

        # Preparar encabezado con la longitud del mensaje
        data_len = len(data_bytes)

        if data_len > 0xFFFFFFFF:
            raise ValueError("El mensaje supera el límite de longitud de 4 bytes.")

        payload = data_len.to_bytes(4, byteorder="big") + data_bytes

        # Convertir los datos a una secuencia de bits
        bits = np.unpackbits(
            np.frombuffer(payload, dtype=np.uint8)
        )

        # Aplanar los canales RGB
        flat_img = img_arr.flatten()

        # Verificar capacidad de la imagen
        if len(bits) > len(flat_img):
            max_bytes = (len(flat_img) // 8) - 4

            raise ValueError(
                f"El tamaño de los datos excede la capacidad de la imagen. "
                f"Capacidad máxima aproximada: {max(0, max_bytes)} bytes. "
                f"Datos recibidos: {data_len} bytes."
            )

        # Insertar los bits mediante operaciones vectorizadas
        bits_array = bits.astype(np.uint8)

        flat_img[:len(bits_array)] = (
            (flat_img[:len(bits_array)] & np.uint8(254))
            | bits_array
        )

        # Reconstruir la imagen
        encoded_img_arr = flat_img.reshape(img_arr.shape)
        encoded_img = Image.fromarray(encoded_img_arr)

        # Guardar siempre en PNG para evitar pérdida de información
        encoded_img.save(output_path, format="PNG")

        return True

    @staticmethod
    def decode_lsb(stego_image_path: str) -> bytes:
        """
        Extrae el mensaje oculto desde el LSB de una imagen PNG.
        """

        # Abrir imagen y convertirla a RGB
        img = Image.open(stego_image_path).convert("RGB")
        img_arr = np.array(img, dtype=np.uint8)

        # Aplanar canales RGB
        flat_img = img_arr.flatten()

        # Verificar que exista espacio para el encabezado
        if len(flat_img) < 32:
            raise ValueError(
                "La imagen es demasiado pequeña para contener el encabezado."
            )

        # Extraer los primeros 32 bits (longitud del mensaje)
        length_bits = flat_img[:32] & np.uint8(1)

        # Reconstruir los 4 bytes del encabezado
        length_bytes = np.packbits(length_bits).tobytes()

        payload_len = int.from_bytes(length_bytes, byteorder="big")

        # Calcular longitud total necesaria
        total_bits = 32 + (payload_len * 8)

        # Validar que el mensaje quepa en la imagen
        if total_bits > len(flat_img):
            raise ValueError(
                "La imagen no contiene un mensaje válido, "
                "está incompleta o ha sido modificada."
            )

        # Extraer los bits del mensaje
        data_bits = flat_img[32:total_bits] & np.uint8(1)

        # Reconstruir los bytes originales
        data_bytes = np.packbits(data_bits).tobytes()

        return data_bytes

    @staticmethod
    def compute_metrics(original_path: str, stego_path: str) -> dict:
        """
        Calcula las métricas de calidad de imagen MSE y PSNR.
        """

        # Leer imágenes
        img1 = cv2.imread(original_path, cv2.IMREAD_COLOR)
        img2 = cv2.imread(stego_path, cv2.IMREAD_COLOR)

        # Verificar que ambas imágenes se hayan cargado
        if img1 is None:
            raise ValueError(
                f"No se pudo cargar la imagen original: {original_path}"
            )

        if img2 is None:
            raise ValueError(
                f"No se pudo cargar la imagen esteganográfica: {stego_path}"
            )

        # Verificar dimensiones
        if img1.shape != img2.shape:
            raise ValueError(
                "Las imágenes deben tener las mismas dimensiones "
                "para calcular las métricas."
            )

        # Calcular MSE
        mse = np.mean(
            (img1.astype(np.float64) - img2.astype(np.float64)) ** 2
        )

        # Calcular PSNR
        if mse == 0:
            psnr = float("inf")
        else:
            psnr = 20 * math.log10(255.0 / math.sqrt(mse))

        return {
            "MSE": round(float(mse), 6),
            "PSNR": round(float(psnr), 2)
        }
