from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import shutil

key = 'super_cool_dump_key'  # Encryption key
source_file = 'encryption_test/test_output.db'  # Path to the original SQLite database file
encrypted_file = 'out.db'  # Path to the encrypted SQLite database file (destination file)


def encrypt_file():
    # Generate the SHA-256 hash of the encryption key
    hashed_key = SHA256.new(key.encode()).digest()

    # Create AES cipher in CBC mode with the hashed key
    cipher = AES.new(hashed_key, AES.MODE_CBC)

    # Open the source database file for reading
    with open(source_file, 'rb') as src_file:
        # Read the contents of the source file
        src_data = src_file.read()

    # Pad the data to match the AES block size
    padded_data = pad(src_data, AES.block_size)

    # Encrypt the padded data
    encrypted_data = cipher.encrypt(padded_data)

    # Write the encrypted data and the initialization vector (IV) to the destination file
    with open(encrypted_file, 'wb') as dest_file:
        dest_file.write(cipher.iv + encrypted_data)

    print("Encryption completed successfully.")

def decrypt_file():
    # Generate the SHA-256 hash of the encryption key
    hashed_key = SHA256.new(key.encode()).digest()

    # Open the encrypted database file for reading
    with open(encrypted_file, 'rb') as src_file:
        # Read the IV and encrypted data from the source file
        iv = src_file.read(16)
        encrypted_data = src_file.read()

    # Create AES cipher in CBC mode with the hashed key and IV
    cipher = AES.new(hashed_key, AES.MODE_CBC, iv=iv)

    # Decrypt the encrypted data
    decrypted_data = cipher.decrypt(encrypted_data)

    # Unpad the decrypted data
    unpadded_data = unpad(decrypted_data, AES.block_size)

    # Write the decrypted data to a temporary file
    temp_file = encrypted_file + '.tmp'
    with open(temp_file, 'wb') as dest_file:
        dest_file.write(unpadded_data)

    # Replace the original database file with the decrypted data
    shutil.move(temp_file, source_file)

    print("Decryption completed successfully.")


decrypt_file()