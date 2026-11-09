# Sistema Integrado de Seguridad: Criptografía, Esteganografía y Blockchain

Plataforma de ingeniería de software desarrollada en **Python** y **Streamlit** para la protección integral, ocultamiento, trazabilidad y verificación de evidencias digitales, integrando de forma cohesiva tres disciplinas criptográficas y de seguridad informática.

---

## 📂 Estructura del Proyecto

El proyecto está organizado de manera modular para garantizar la mantenibilidad, escalabilidad y separación de responsabilidades:

```text
cripto_stego_blockchain/
├── app.py                     # Interfaz gráfica de usuario y orquestador (Streamlit)
├── modules/
│   ├── __init__.py
│   ├── crypto_engine.py       # Motor criptográfico (AES-GCM, RSA-OAEP, RSA-PSS, SHA-256)
│   ├── stego_engine.py        # Motor esteganográfico (LSB con NumPy/OpenCV y métricas PSNR/MSE)
│   └── blockchain_engine.py   # Motor de trazabilidad local y validación de integridad
├── requirements.txt           # Dependencias y librerías externas del proyecto
└── README.md                  # Documentación oficial e instrucciones de instalación
```

🏛️ Arquitectura del Sistema y Flujo de Operación
El sistema se divide en tres capas principales:

Capa de Interfaz de Usuario (Streamlit):

Pestaña 1 (Emisor): Permite cargar el archivo a proteger y la imagen PNG contenedora para ejecutar el cifrado y ocultamiento.

Pestaña 2 (Receptor): Permite cargar la imagen modificada para extraer los bits, descifrar la información y validar firmas y hashes.

Pestaña 3 (Auditoría): Muestra la cadena de bloques local en tiempo real e incluye un módulo de simulación de ataques para probar la detección de alteraciones.

Capa de Módulos Backend (Python):

CryptoEngine: Gestiona el cifrado simétrico autenticado (AES-256-GCM), el intercambio seguro de claves mediante RSA-OAEP (2048-bit), las firmas digitales de autenticidad con RSA-PSS y las huellas digitales con SHA-256.

StegoEngine: Oculta el paquete cifrado en los bits menos significativos (LSB) de imágenes PNG utilizando aritmética segura y calcula las métricas de calidad de imagen MSE y PSNR.

BlockchainEngine: Mantiene una cadena de bloques local basada en hashes SHA-256 para registrar metadatos y evidencias de forma inmutable.

Capa de Almacenamiento Local:

Archivos de texto/PDF/JSON de prueba.

Imágenes PNG originales y modificadas (esteganográficas).

Estado de la cadena de bloques en memoria de sesión.

⚙️ Requerimientos Técnicos y Dependencias
El prototipo requiere Python 3.8 o superior. Las librerías necesarias están especificadas en el archivo requirements.txt:

cryptography>=41.0.0 (Criptografía avanzada AES y RSA)

Pillow>=10.0.0 / numpy>=1.24.0 (Manipulación de imágenes y arreglos de bits LSB)

opencv-python>=4.8.0 (Cálculo de métricas PSNR y MSE)

streamlit>=1.28.0 (Interfaz gráfica web interactiva)

🚀 Guía de Instalación y Ejecución
Sigue estos pasos para instalar y ejecutar el prototipo en cualquier equipo:

1. Clonar o descomprimir el proyecto
Abre tu terminal (PowerShell en Windows o Bash en Linux/macOS) y sitúate en la carpeta raíz del proyecto:

Bash
cd ruta/a/cripto_stego_blockchain
2. Crear y activar un entorno virtual
En Windows (PowerShell):

PowerShell
python -m venv venv
venv\Scripts\Activate
En Linux / macOS (Bash):

Bash
python3 -m venv venv
source venv/bin/activate
3. Instalar las dependencias
Bash
pip install -r requirements.txt
4. Ejecutar la aplicación
Inicia el servidor local de Streamlit ejecutando:

Bash
streamlit run app.py
La aplicación se abrirá automáticamente en tu navegador web predeterminado (por lo general en la dirección http://localhost:8501).

📋 Verificación de Funcionalidades (Requerimientos Mínimos)
RF01 a RF04 (Criptografía): Sube un archivo de texto/JSON en la Pestaña 1 y ejecuta el flujo para ver el hash SHA-256, el cifrado AES-GCM protegido por RSA y la firma digital.

RF05 a RF07 (Esteganografía): Carga una imagen PNG junto con el archivo; el sistema ocultará la información calculando métricas con un PSNR > 75 dB. En la Pestaña 2 podrás extraerla y descifrarla.

RF08 a RF10 (Blockchain): En la Pestaña 3 podrás auditar la cadena de bloques y hacer clic en el botón de simulación de ataque para comprobar cómo el sistema detecta de forma inmediata modificaciones no autorizadas ("ALTERADA 🔴").
