from bitarray import bitarray

def compute_s(current: bitarray, previous: bitarray, first_n: int, total_n: int) -> float:
    for i in range(first_n):
        if current[i] != previous[i]:
            return 0
    
    score = 0.0
    for i in range(total_n-first_n):
        score += (1024 - i) / 1024 * (current[i + first_n] != previous[i + first_n])
    return score