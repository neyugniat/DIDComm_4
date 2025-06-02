import base58

# Giả sử bạn có raw Ed25519 public key bytes (32 bytes)
raw_public_key_bytes = base58.b58decode("Py5KDeqSL7mqAZeRwmchCK5kbyuenxczoNZpJTzTpGW")
# Multicodec prefix Ed25519 public key theo chuẩn là 0xed01
multicodec_prefix = bytes([0xed, 0x01])

# Đóng gói public key với prefix multicodec
prefixed_key = multicodec_prefix + raw_public_key_bytes

print("prefixed_key", prefixed_key)
print("base58.b58encode(prefixed_key): ", base58.b58encode(prefixed_key))
# Encode lại theo base58btc, thêm 'z' làm prefix multibase
did_key = 'z' + base58.b58encode(prefixed_key).decode()

print(did_key)
