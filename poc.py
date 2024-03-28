import hashlib
import base64

def hash_to_alphanumeric(input_string, length):
    # Hash the input string using SHA-256
    hashed = hashlib.sha256(input_string.encode()).digest()

    # Encode the hashed bytes to Base64
    encoded = base64.b64encode(hashed).decode()
    print(encoded)

    # Filter out non-alphanumeric characters
    alphanumeric = ''.join(char for char in encoded if char.isalnum())

    # Trim or pad the string to the desired length
    truncated = alphanumeric[:length].ljust(length, '0')

    return truncated

input_string = "YourStringHere"
desired_length = 10

hashed_string = hash_to_alphanumeric(input_string, desired_length)
print("Hashed string:", hashed_string)