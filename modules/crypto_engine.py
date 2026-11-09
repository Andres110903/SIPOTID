import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.hashes import Hash, SHA256

class CryptoEngine:
    @staticmethod
    def generate_sha256(data: bytes) -> str:
        """Calcula el hash SHA-256 de un bloque de datos."""
        digest = Hash(SHA256())
        digest.update(data)
        return digest.finalize().hex()

    @staticmethod
    def generate_rsa_keypair():
        """Genera par de llaves RSA de 2048 bits."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def encrypt_aes_gcm(plaintext: bytes) -> dict:
        """Cifra datos usando AES-256-GCM."""
        key = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # Nonce recomendado de 96 bits
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
        return {
            "key": key,
            "nonce": nonce,
            "ciphertext": ciphertext
        }

    @staticmethod
    def decrypt_aes_gcm(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
        """Descifra datos cifrados con AES-256-GCM."""
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, associated_data=None)

    @staticmethod
    def encrypt_rsa_oaep(data: bytes, public_key) -> bytes:
        """Cifra la clave simétrica usando RSA-OAEP."""
        return public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    @staticmethod
    def decrypt_rsa_oaep(encrypted_data: bytes, private_key) -> bytes:
        """Descifra la clave simétrica usando RSA-OAEP."""
        return private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    @staticmethod
    def sign_rsa_pss(data: bytes, private_key) -> bytes:
        """Genera una firma digital utilizando RSA-PSS."""
        return private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    @staticmethod
    def verify_rsa_pss(data: bytes, signature: bytes, public_key) -> bool:
        """Verifica una firma digital RSA-PSS."""
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False