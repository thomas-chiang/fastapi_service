byte1 = bytes([0b10101100])  # Example byte 1 (binary representation)
byte2 = bytes([0b11001010])  # Example byte 2 (binary representation)
print(byte1)
# Mask to extract the first bit
mask = bytes([0b10000000])  # Mask with only the first bit set to 1

# Extracting the first bit from each byte using AND (&) operation with the mask
bit1 = bytes([byte1[0] & mask[0]])
bit2 = bytes([byte2[0] & mask[0]])

# XORing the first bits
result = bytes([bit1[0] ^ bit2[0]])

print("Byte 1:", bin(byte1[0]))
print("Byte 2:", bin(byte2[0]))
print("First bit of Byte 1:", bin(bit1[0]))
print("First bit of Byte 2:", bin(bit2[0]))
print("XOR of first bits:", bin(result[0]))



# import random
# from typing import List

# def get_random_1024_bytes() -> bytes:
#     bits = [random.randint(0, 1) for _ in range(1024)]
#     byte_array = bytearray()
#     for i in range(0, 1024, 8):
#         byte = 0
#         for j in range(8):
#             byte |= bits[i + j] << (7 - j)
#         byte_array.append(byte)
#     return bytes(byte_array)

# def compute_score(Ct: bytes, Cd: bytes) -> float:
#     print(len(Ct))
#     score = 1
#     for i in range(32):
#         score *= not (Ct[i] ^ Cd[i])  # Product of the first 256 bits
#     print(score)
#     score *= sum(((1024 - i) / 1024) * (not (Ct[i + 256] ^ Cd[i + 256])) for i in range(768))  # Score for the remaining 768 bits
#     return score

# # Generate Ct and Cd
# Ct = get_random_1024_bytes()
# Cd = get_random_1024_bytes()

# # Copy first 256 bits of Ct to Cd
# Cd = Ct[:256] + Cd[256:]

# # Compute the score
# score = compute_score(Ct, Cd)
# print("Score:", score)
