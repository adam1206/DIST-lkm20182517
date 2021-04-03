
p = 11
q = 13
n = p * q
phi_n = (p-1) * (q-1)

e = 7

d = 0
mod = 0
while True:
    d += 1
    mod = (e * d) % phi_n
    if mod == 1:
        break

# Encryption
# C = P^e mod abs(

plain = "DIST-lkm20182517"
plain_list = [ord(x) for x in plain]

# 위의 [ord(x) for x in plain]은
# for x in plain:
# plain_list.append(ord(x))
# 와 동일함! by 박성환 조교님

cipher = []
for i in plain_list:
    x = (i ** e) % n
    cipher.append(int(x))
    
# Decryption
# P = C^d mod n

decrypted = []
for i in cipher:
    x = (i ** d) % n
    decrypted.append(int(x))
    
print('plain text', plain_list)
print('cipher text', cipher)
print('decrypted text', decrypted)

print([chr(x) for x in decrypted])
decrypted_text = ''.join([chr(x) for x in decrypted])
print(decrypted_text)
