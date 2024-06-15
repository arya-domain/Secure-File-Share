import os
from cryptography.fernet import Fernet
from .models import UploadedFile


def decrypt_file(file_path):
    
    file_instance = UploadedFile.objects.get(file_path="files\\"+file_path)
    print(file_instance)
    with open(file_instance.file_path, "rb") as encrypted_file:
        encrypted_file_content = encrypted_file.read()
        
    key = file_instance.encryption_key.encode()
    cipher_suite = Fernet(key)
    decrypted_file_content = cipher_suite.decrypt(encrypted_file_content)
    decrypted_folder = os.path.join(
        os.path.dirname(file_instance.file_path), "decrypted"
    )
    if not os.path.exists(decrypted_folder):
        os.makedirs(decrypted_folder)
    decrypted_file_path = os.path.join(
        decrypted_folder,
        os.path.basename(file_instance.file_path),
    )
    with open(decrypted_file_path, "wb") as decrypted_file:
        decrypted_file.write(decrypted_file_content)

    return decrypted_file_path
