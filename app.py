import streamlit as st
import os
import json
import time
from modules.crypto_engine import CryptoEngine
from modules.stego_engine import StegoEngine
from modules.blockchain_engine import Blockchain

st.set_page_config(page_title="Sistema de Protección, Esteganografía y Blockchain", layout="wide")

# Inicialización del estado de sesión
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain()

if 'keys' not in st.session_state:
    priv, pub = CryptoEngine.generate_rsa_keypair()
    st.session_state.keys = {'private': priv, 'public': pub}

st.title("🛡️ Sistema Integrado: Criptografía, Esteganografía y Blockchain")
st.markdown("Plataforma de protección integral de evidencias digitales y transmisión confidencial.")

tabs = st.tabs(["1. Cifrar y Ocultar (Emisor)", "2. Extraer y Descifrar (Receptor)", "3. Trazabilidad Blockchain"])

# TAB 1: EMBEDDING & ENCRYPTION
with tabs[0]:
    st.header("Protección y Ocultamiento de Información")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Seleccione archivo a proteger", type=["txt", "pdf", "png", "json"])
        stego_cover = st.file_uploader("Seleccione imagen contenedora (PNG)", type=["png"])

    with col2:
        if uploaded_file and stego_cover:
            if st.button("Ejecutar Flujo de Protección"):
                start_time = time.time()
                file_bytes = uploaded_file.read()
                
                # 1. Hashes originales y firmas
                file_hash = CryptoEngine.generate_sha256(file_bytes)
                signature = CryptoEngine.sign_rsa_pss(file_bytes, st.session_state.keys['private'])
                
                # 2. Cifrado AES-GCM
                aes_res = CryptoEngine.encrypt_aes_gcm(file_bytes)
                enc_aes_key = CryptoEngine.encrypt_rsa_oaep(aes_res['key'], st.session_state.keys['public'])
                
                # Empaquetado de la carga útil
                payload_dict = {
                    "nonce": aes_res['nonce'].hex(),
                    "enc_key": enc_aes_key.hex(),
                    "ciphertext": aes_res['ciphertext'].hex(),
                    "signature": signature.hex()
                }
                payload_bytes = json.dumps(payload_dict).encode()
                
                # Guardar imagen temporal
                os.makedirs("temp", exist_ok=True)
                cover_path = os.path.join("temp", stego_cover.name)
                stego_path = os.path.join("temp", "stego_" + stego_cover.name)
                with open(cover_path, "wb") as f:
                    f.write(stego_cover.read())
                
                # 3. Esteganografía LSB
                StegoEngine.encode_lsb(cover_path, payload_bytes, stego_path)
                metrics = StegoEngine.compute_metrics(cover_path, stego_path)
                
                # 4. Registro en Blockchain (Solo hashes y metadatos)
                block_data = {
                    "filename": uploaded_file.name,
                    "file_hash_sha256": file_hash,
                    "metrics": metrics
                }
                new_block = st.session_state.blockchain.add_block(block_data)
                
                exec_time = round(time.time() - start_time, 4)

                st.success(f"¡Proceso completado en {exec_time} segundos!")
                st.json({
                    "SHA-256 Original": file_hash,
                    "Bloque Registrado": new_block.index,
                    "Métricas Esteganográficas": metrics
                })
                
                with open(stego_path, "rb") as f:
                    st.download_button("Descargar Imagen Esteganográfica", f, file_name="stego_result.png")

# TAB 2: EXTRACTION & DECRYPTION
with tabs[1]:
    st.header("Extracción, Descifrado y Verificación")
    stego_input = st.file_uploader("Cargue la imagen esteganográfica recibida (PNG)", type=["png"], key="stego_in")
    
    if stego_input:
        if st.button("Procesar Imagen"):
            os.makedirs("temp", exist_ok=True)
            input_path = os.path.join("temp", "received_stego.png")
            with open(input_path, "wb") as f:
                f.write(stego_input.read())
            
            try:
                # 1. Extraer LSB
                raw_payload = StegoEngine.decode_lsb(input_path)
                payload = json.loads(raw_payload.decode())
                
                # 2. Descifrar Clave AES mediante RSA-OAEP
                aes_key = CryptoEngine.decrypt_rsa_oaep(bytes.fromhex(payload['enc_key']), st.session_state.keys['private'])
                
                # 3. Descifrar Archivo con AES-GCM
                original_bytes = CryptoEngine.decrypt_aes_gcm(
                    bytes.fromhex(payload['ciphertext']),
                    aes_key,
                    bytes.fromhex(payload['nonce'])
                )
                
                # 4. Verificar Firma Digital RSA-PSS
                is_sig_valid = CryptoEngine.verify_rsa_pss(
                    original_bytes,
                    bytes.fromhex(payload['signature']),
                    st.session_state.keys['public']
                )
                
                extracted_hash = CryptoEngine.generate_sha256(original_bytes)
                
                st.subheader("Resultados de la Extracción:")
                col_a, col_b = st.columns(2)
                col_a.metric("Firma RSA-PSS Validada", "Sí" if is_sig_valid else "No")
                col_b.metric("Hash SHA-256 Extraído", extracted_hash[:16] + "...")
                
                st.download_button("Descargar Archivo Restaurado", original_bytes, file_name="restored_file.bin")
            except Exception as e:
                st.error(f"Error procesando la imagen: {str(e)}")

# TAB 3: BLOCKCHAIN AUDIT
with tabs[2]:
    st.header("Auditoría de Integridad y Trazabilidad (Blockchain)")
    
    chain_valid = st.session_state.blockchain.is_chain_valid()
    st.metric("Estado de Integridad de la Red", "VÁLIDA 🟢" if chain_valid else "ALTERADA 🔴")
    
    st.subheader("Cadena de Bloques Actual")
    for block in st.session_state.blockchain.chain:
        with st.expander(f"Bloque #{block.index} - Hash: {block.hash[:20]}..."):
            st.json({
                "Index": block.index,
                "Timestamp": block.timestamp,
                "Data": block.data,
                "Previous Hash": block.previous_hash,
                "Hash": block.hash
            })
            
    st.subheader("Demostración de Detección de Alteraciones (Simulación de Ataque)")
    if st.button("Corromper Bloque #1 (Simular Alteración)"):
        if len(st.session_state.blockchain.chain) > 1:
            st.session_state.blockchain.chain[1].data["file_hash_sha256"] = "0000000000000000000000"
            st.warning("El contenido del Bloque #1 ha sido modificado maliciosamente.")
            st.rerun()