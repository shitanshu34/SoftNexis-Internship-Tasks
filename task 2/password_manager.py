# -*- coding: utf-8 -*-
"""
Created on Tue May  5 20:50:39 2026

@author: SHITANSHU KUMAR
"""

import os
import json
import base64
import getpass
import argparse
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

VAULT_FILE = "vault.json"

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 32-byte key from the master password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return kdf.derive(password.encode())

def save_vault(vault_data):
    """Save the encrypted vault data to a JSON file safely."""
    with open(VAULT_FILE, "w") as f:
        json.dump(vault_data, f, indent=4)

def load_vault():
    """Load the vault data from the JSON file."""
    if os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, "r") as f:
            return json.load(f)
    return None

def add_entry(master_pwd):
    """Encrypt and add a new credential to the vault."""
    vault = load_vault()
    if not vault:
        salt = os.urandom(16)
        vault = {"salt": base64.b64encode(salt).decode(), "entries": {}}
    else:
        salt = base64.b64decode(vault["salt"])

    key = derive_key(master_pwd, salt)
    aesgcm = AESGCM(key)
    
    website = input("Website Name: ")
    username = input("Username: ")
    password = getpass.getpass("Password to store: ")

    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, password.encode(), None)
    
    vault["entries"][website] = {
        "username": username,
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }
    
    save_vault(vault)
    print(f"\n[+] Success: Credentials for {website} saved securely!")

def get_entry(master_pwd):
    """Retrieve and decrypt a credential from the vault."""
    vault = load_vault()
    if not vault:
        print("[-] Error: Vault file not found.")
        return

    salt = base64.b64decode(vault["salt"])
    key = derive_key(master_pwd, salt)
    aesgcm = AESGCM(key)
    
    website = input("Enter Website Name to retrieve: ")
    if website in vault["entries"]:
        entry = vault["entries"][website]
        try:
            nonce = base64.b64decode(entry["nonce"])
            ciphertext = base64.b64decode(entry["ciphertext"])
            decrypted_password = aesgcm.decrypt(nonce, ciphertext, None).decode()
            print(f"\n[!] Credentials for {website}:")
            print(f"    Username: {entry['username']}")
            print(f"    Password: {decrypted_password}")
        except Exception:
            print("[-] Error: Incorrect Master Password or data corruption.")
    else:
        print("[-] Error: Website not found in vault.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Secure CLI Password Manager")
    parser.add_argument("command", choices=["add", "get"], help="Command to run")
    args = parser.parse_args()

    m_password = getpass.getpass("Enter Master Password: ")
    
    if args.command == "add":
        add_entry(m_password)
    elif args.command == "get":
        get_entry(m_password)