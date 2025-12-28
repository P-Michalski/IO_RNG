/**
 * Utilities for compressing/decompressing bits to/from base64.
 * Compatible with backend Python implementation.
 */

/**
 * Decompresses base64 → list of bits.
 *
 * @param b64String - Base64 string from backend
 * @param bitCount - Expected number of bits (trims padding)
 * @returns List of bits [0,1,0,1,...]
 * @throws Error if b64String is invalid or bitCount > available bits
 *
 * @example
 * decompressBase64ToBits('qg==', 8) // [1, 0, 1, 0, 1, 0, 1, 0]
 */
export function decompressBase64ToBits(
  b64String: string,
  bitCount: number
): number[] {
  if (!b64String) {
    return [];
  }

  let byteArray: Uint8Array;

  try {
    // Decode base64 to byte array
    const binaryString = atob(b64String);
    byteArray = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      byteArray[i] = binaryString.charCodeAt(i);
    }
  } catch (e) {
    throw new Error(`Invalid base64 string: ${e}`);
  }

  const bits: number[] = [];

  // Extract bits from each byte
  for (const byteVal of byteArray) {
    for (let j = 0; j < 8; j++) {
      // MSB first: extract bits from most significant
      bits.push((byteVal >> (7 - j)) & 1);

      // Break if we've reached the requested number of bits
      if (bits.length >= bitCount) {
        return bits.slice(0, bitCount);
      }
    }
  }

  // Check if we have enough bits
  if (bits.length < bitCount) {
    throw new Error(
      `Requested ${bitCount} bits but only ${bits.length} available in base64 string`
    );
  }

  return bits.slice(0, bitCount);
}

/**
 * Compresses list of bits to base64.
 * (Optional - if you want to send bits to backend)
 *
 * @param bits - List of bits [0,1,0,1,...]
 * @returns Base64 string representing packed bits
 *
 * @example
 * compressBitsToBase64([1, 0, 1, 0, 1, 0, 1, 0]) // 'qg=='
 */
export function compressBitsToBase64(bits: number[]): string {
  if (!bits.length) {
    return "";
  }

  const byteArray: number[] = [];

  // Pack 8 bits → 1 byte
  for (let i = 0; i < bits.length; i += 8) {
    let byteVal = 0;

    // Pack up to 8 bits (or less for last byte)
    for (let j = 0; j < 8; j++) {
      if (i + j < bits.length) {
        // MSB first: first bit in most significant position
        byteVal |= bits[i + j] << (7 - j);
      }
    }

    byteArray.push(byteVal);
  }

  // Convert byte array to base64
  const binaryString = String.fromCharCode(...byteArray);
  return btoa(binaryString);
}

/**
 * Helper to check if response contains compressed bits
 */
export function hasCompressedBits(data: any): boolean {
  return data.bits_format === "base64-bitpack" && !!data.bits_compressed;
}

/**
 * Universal function to extract bits from response
 * (automatically detects format)
 */
export function extractBitsFromResponse(data: any): number[] {
  if (hasCompressedBits(data)) {
    return decompressBase64ToBits(
      data.bits_compressed,
      data.bits_count || data.count
    );
  }

  // Fallback to regular array
  return data.bits || data.generated_bits || [];
}
