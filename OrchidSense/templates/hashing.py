# hashing.py
import hashlib
import base64
import os

def gerar_hash_scrypt(senha, N=32768, r=8, p=1):
    salt = os.urandom(16)  # Gera um salt aleatório
    hash_scrypt = hashlib.scrypt(
        senha.encode(),
        salt=salt,
        n=N,
        r=r,
        p=p,
        maxmem=0,
        dklen=64  # Tamanho do hash resultante
    )
    salt_base64 = base64.b64encode(salt).decode('utf-8')
    hash_base64 = base64.b64encode(hash_scrypt).decode('utf-8')
    return f"scrypt:{N}:{r}:{p}${salt_base64}${hash_base64}"
