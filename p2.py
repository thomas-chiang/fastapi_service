import asyncio
from bitarray import bitarray
from app.services import get_random_bytes_of_length_128
ran = get_random_bytes_of_length_128()

ran2 = ran+ran

def bytes_to_bitarray(byte_string: bytes) -> bitarray:
    bits = bitarray()
    bits.frombytes(byte_string)
    return bits

bitarray128 = bytes_to_bitarray(ran)



c = bitarray('1111000')
p = bitarray('1111111')


def bit_equal_by_idx(found_diff: bitarray, current: bitarray, previous: bitarray, idx: int) -> None:
        if found_diff:
            return
        if current[idx] != previous[idx]:
            found_diff.append(1)

async def check_first_n_bits_equal(current: bitarray, previous: bitarray, first_n: str) -> bool:
    found_diff = bitarray()
    await asyncio.gather(   
        *(asyncio.to_thread(bit_equal_by_idx, found_diff, current, previous, idx) for idx in range(first_n))
    )
    return False if found_diff else True

def compute_score_by_idx(sum_ref: list, current: bitarray, previous: bitarray, numerator: int, denominator: int, idx: int):
    if current[idx] == previous[idx]:
        sum_ref[0] += numerator / denominator

async def compute_score_for_remaining_bit(current: bitarray, previous: bitarray, first_n: int) -> float:
    sum_ref = [0]
    await asyncio.gather(   
        *(asyncio.to_thread(compute_score_by_idx, sum_ref, current, previous, len(current)-idx+first_n, len(current), idx) for idx in range(first_n, len(current)))
    )
    # await asyncio.gather(   
    #     *(asyncio.to_thread(compute_score_by_idx, sum_ref, current, previous, 1, 1, idx) for idx in range(first_n, len(current)))
    # )

    return sum_ref[0]

async def compute_score(current: bitarray, previous: bitarray, first_n: int) -> float:
    is_equal, score = await asyncio.gather( 
        check_first_n_bits_equal(current, previous, first_n),
        compute_score_for_remaining_bit(current, previous, first_n)
    )

    return score if is_equal else 0

res = asyncio.run(compute_score_for_remaining_bit(bitarray128, bitarray128, 256))
print(res)
s = sum(((1024-i)/1024 for i in range(768)))
print(s)
res = asyncio.run(compute_score(bitarray128, bitarray128, 256))
print(s)

res = asyncio.run(check_first_n_bits_equal(c, p, 7))
print(res)

def compute_s(current: bitarray, previous: bitarray, first_n: int, total_n: int) -> float:
    for i in range(first_n):
        if current[i] != previous[i]:
            return 0
    
    score = 0.0
    for i in range(total_n-first_n):
        score += (1024 - i) / 1024 * (current[i + first_n] == previous[i + first_n])
    return score

print(compute_s(bitarray128, bitarray128, 256, 1024))