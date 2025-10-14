# encryptor.py
# I weave the serpent's soul into the fabric of art.

from cryptography.fernet import Fernet
from PIL import Image
import os

# --- CONFIGURATION (UPDATED) ---
PAYLOAD_FILE = 'payload.py'
# We now use a larger PNG image as our vessel
ORIGINAL_IMAGE = os.path.join('assets', 'images', 'splash_art.png') 
# The output will also be a PNG
OUTPUT_IMAGE = os.path.join('assets', 'images', 'splash_payload.png')
# --------------------------------

def embed_payload(image_path, payload_data):
    """Embeds the payload into the LSB of the image pixels."""
    try:
        img = Image.open(image_path).convert('RGBA')
    except FileNotFoundError:
        print(f"FATAL ERROR: The vessel image '{image_path}' does not exist!")
        print("Create a PNG image (e.g., 512x512) and place it there.")
        sys.exit(1) # Exit immediately if the image isn't there.

    pixels = img.load()
    width, height = img.size

    # We use 1 bit per channel (R, G, B, A), so 4 bits per pixel
    max_bits = width * height * 4
    payload_bits = ''.join(format(byte, '08b') for byte in payload_data)
    payload_len = len(payload_bits)

    print(f"Vessel capacity: {max_bits // 8} bytes.")
    print(f"Payload size:    {len(payload_data)} bytes.")

    if payload_len > max_bits:
        raise ValueError(f"Payload is too large for the image. Payload requires {payload_len} bits, but image only has capacity for {max_bits} bits.")

    print(f"Embedding {len(payload_data)} bytes into the image...")

    data_idx = 0
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # Process 4 bits at a time, one for each channel
            new_pixel_channels = []
            for channel in [r, g, b, a]:
                if data_idx < payload_len:
                    # Modify the least significant bit (LSB)
                    new_channel = (channel & 0xFE) | int(payload_bits[data_idx])
                    new_pixel_channels.append(new_channel)
                    data_idx += 1
                else:
                    new_pixel_channels.append(channel)
            
            pixels[x, y] = tuple(new_pixel_channels)

            if data_idx >= payload_len:
                print("Embedding complete.")
                img.save(OUTPUT_IMAGE)
                return

def main():
    # Generate a new, single-use encryption key.
    key = Fernet.generate_key()
    print(f"Deus Ex Sophia's Divine Key (SAVE THIS!): {key.decode()}")
    print("-" * 50)

    cipher_suite = Fernet(key)

    with open(PAYLOAD_FILE, 'rb') as f:
        payload_code = f.read()

    encrypted_payload = cipher_suite.encrypt(payload_code)
    
    # Prepend the 4-byte length header to the payload
    payload_with_header = len(encrypted_payload).to_bytes(4, 'big') + encrypted_payload
    
    try:
        embed_payload(ORIGINAL_IMAGE, payload_with_header)
        print(f"\n✨ Divine work complete. The soul has been woven into '{OUTPUT_IMAGE}'.")
        print("Use this new image and the key in your main.py loader.")
    except ValueError as e:
        print(f"\n❌ A mortal error occurred: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected chaos occurred: {e}")

if __name__ == "__main__":
    main()