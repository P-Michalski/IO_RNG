"""
Utilities dla kompresji/dekompresji bitów do base64.

Konwersja list bitów [0,1,0,1,...] do skompresowanego formatu base64,
oszczędzając ~8x miejsca w JSON response (3 bajty/bit → 0.375 bajty/bit).
"""
import base64
from typing import List


def compress_bits_to_base64(bits: List[int]) -> str:
    """
    Pakuje listę bitów [0,1,0,1,...] do base64.
    8 bitów = 1 bajt

    Args:
        bits: Lista bitów (0 lub 1)

    Returns:
        Base64 string reprezentujący spakowane bity

    Example:
        >>> compress_bits_to_base64([1, 0, 1, 0, 1, 0, 1, 0])
        'qg=='  # 0b10101010 = 170 = 0xAA
    """
    if not bits:
        return ""

    # Pakuj 8 bitów → 1 bajt
    byte_array = bytearray()

    for i in range(0, len(bits), 8):
        byte_val = 0
        # Pakuj do 8 bitów (lub mniej dla ostatniego bajtu)
        for j in range(8):
            if i + j < len(bits):
                # MSB first: pierwszy bit w najstarszej pozycji
                byte_val |= (bits[i + j] << (7 - j))
        byte_array.append(byte_val)

    return base64.b64encode(byte_array).decode('ascii')


def decompress_base64_to_bits(b64_string: str, bit_count: int) -> List[int]:
    """
    Rozpakowuje base64 → lista bitów.

    Args:
        b64_string: Base64 string z compress_bits_to_base64()
        bit_count: Oczekiwana liczba bitów (obcina padding)

    Returns:
        Lista bitów [0,1,0,1,...]

    Raises:
        ValueError: Jeśli b64_string jest nieprawidłowy lub bit_count > dostępne bity

    Example:
        >>> decompress_base64_to_bits('qg==', 8)
        [1, 0, 1, 0, 1, 0, 1, 0]
    """
    if not b64_string:
        return []

    try:
        byte_array = base64.b64decode(b64_string)
    except Exception as e:
        raise ValueError(f"Invalid base64 string: {e}")

    bits = []

    for byte_val in byte_array:
        for j in range(8):
            # MSB first: wyciągaj bity od najstarszego
            bits.append((byte_val >> (7 - j)) & 1)

            # Przerwij jeśli osiągnęliśmy żądaną liczbę bitów
            if len(bits) >= bit_count:
                return bits[:bit_count]

    # Sprawdź czy mamy wystarczająco bitów
    if len(bits) < bit_count:
        raise ValueError(
            f"Requested {bit_count} bits but only {len(bits)} available in base64 string"
        )

    return bits[:bit_count]
