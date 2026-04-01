/*
 * Minimal wyhash implementation matching Bun.hash() (wyhash final version 4).
 * Compiled to a shared library and called via ctypes from Python.
 */
#include <stdint.h>
#include <string.h>

static inline uint64_t _wyrot(uint64_t x) { return (x >> 32) | (x << 32); }

static inline void _wymum(uint64_t *A, uint64_t *B) {
    __uint128_t r = (__uint128_t)*A * *B;
    *A = (uint64_t)r;
    *B = (uint64_t)(r >> 64);
}

static inline uint64_t _wymix(uint64_t A, uint64_t B) {
    _wymum(&A, &B);
    return A ^ B;
}

static inline uint64_t _wyr8(const uint8_t *p) {
    uint64_t v;
    memcpy(&v, p, 8);
    return v;
}

static inline uint64_t _wyr4(const uint8_t *p) {
    uint32_t v;
    memcpy(&v, p, 4);
    return v;
}

static inline uint64_t _wyr3(const uint8_t *p, size_t k) {
    return ((uint64_t)p[0]) << 16 | ((uint64_t)p[k >> 1]) << 8 | p[k - 1];
}

static const uint64_t _wyp[4] = {
    0xa0761d6478bd642full, 0xe7037ed1a0b428dbull,
    0x8ebc6af09c88c6e3ull, 0x589965cc75374cc3ull
};

uint64_t wyhash(const void *key, size_t len, uint64_t seed, const uint64_t *secret) {
    const uint8_t *p = (const uint8_t *)key;
    seed ^= _wymix(seed ^ secret[0], secret[1]);
    uint64_t a, b;
    if (len <= 16) {
        if (len >= 4) {
            a = (_wyr4(p) << 32) | _wyr4(p + ((len >> 3) << 2));
            b = (_wyr4(p + len - 4) << 32) | _wyr4(p + len - 4 - ((len >> 3) << 2));
        } else if (len > 0) {
            a = _wyr3(p, len);
            b = 0;
        } else {
            a = b = 0;
        }
    } else {
        size_t i = len;
        if (i > 48) {
            uint64_t see1 = seed, see2 = seed;
            do {
                seed = _wymix(_wyr8(p) ^ secret[1], _wyr8(p + 8) ^ seed);
                see1 = _wymix(_wyr8(p + 16) ^ secret[2], _wyr8(p + 24) ^ see1);
                see2 = _wymix(_wyr8(p + 32) ^ secret[3], _wyr8(p + 40) ^ see2);
                p += 48;
                i -= 48;
            } while (i > 48);
            seed ^= see1 ^ see2;
        }
        while (i > 16) {
            seed = _wymix(_wyr8(p) ^ secret[1], _wyr8(p + 8) ^ seed);
            i -= 16;
            p += 16;
        }
        a = _wyr8(p + i - 16);
        b = _wyr8(p + i - 8);
    }
    a ^= secret[1];
    b ^= seed;
    _wymum(&a, &b);
    return _wymix(a ^ secret[0] ^ len, b ^ secret[1]);
}

/* Batch hash: takes an array of string offsets/lengths, writes uint32 results */
void wyhash_batch(
    const char *data,           /* concatenated strings */
    const uint32_t *offsets,    /* start offset of each string */
    const uint32_t *lengths,    /* length of each string */
    uint32_t *results,          /* output: uint32 hashes */
    uint32_t count              /* number of strings */
) {
    for (uint32_t i = 0; i < count; i++) {
        uint64_t h = wyhash(data + offsets[i], lengths[i], 0, _wyp);
        results[i] = (uint32_t)(h & 0xFFFFFFFF);
    }
}

/* Single hash for convenience */
uint32_t wyhash_single(const char *data, uint32_t len) {
    return (uint32_t)(wyhash(data, len, 0, _wyp) & 0xFFFFFFFF);
}
