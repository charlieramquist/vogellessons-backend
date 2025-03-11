from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64
import json
import requests

# ✅ Fetch Microsoft's Public Keys (JWKS)
JWKS_URL = "https://login.microsoftonline.com/common/discovery/keys"
response = requests.get(JWKS_URL)
jwks_keys = response.json()["keys"]

# ✅ Find the Key with Your `kid`
KID_TO_FIND = "imi0Y2z0dYKxBttAqK_Tt5hYBTk"  # Replace with your token's kid
matching_key = None

for key in jwks_keys:
    if key["kid"] == KID_TO_FIND:
        matching_key = key
        break

if not matching_key:
    print("🚨 ERROR: No matching key found for kid:", KID_TO_FIND)
    exit()

# ✅ Extract Modulus (`n`) and Exponent (`e`) from JWK
n = int.from_bytes(base64.urlsafe_b64decode(matching_key["n"] + "=="), "big")
e = int.from_bytes(base64.urlsafe_b64decode(matching_key["e"] + "=="), "big")

# ✅ Convert JWK to PEM
public_key = rsa.RSAPublicNumbers(e, n).public_key()
pem_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# ✅ Print the PEM Key
pem_key_str = pem_key.decode("utf-8")
print("✅ Converted Public Key (PEM Format):\n")
print(pem_key_str)

# ✅ Save the PEM Key to a file
with open("microsoft_public_key.pem", "w") as pem_file:
    pem_file.write(pem_key_str)
    print("\n✅ PEM key saved to `microsoft_public_key.pem`")
