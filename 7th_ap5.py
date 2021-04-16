import random
from math import gcd


class RSA:    # class는 여러 함수를 가질 수 있음
    def __init__(self):    # init은 초기화 과정 / __ 붙은 변수는 private한 변수. 즉, 외부에서 접근 불가
        __prime_list = self.primes_in_range(10, 99)
        __p = random.choice(__prime_list)
        __prime_list.remove(__p)
        __q = random.choice(__prime_list)
        
        n, e, d = self.init_setting(__p, __q)
        self.pub_key = [n, e]    # n, e, d 중 public key는 n, e
        self.pri_key = [n, d]    # n, e, d 중 private key는 n, d
        
    def init_setting(self, p: int, q: int):
        n = p * q
        phi_n = (p-1) * (q-1)
        e = self.find_e(phi_n)
        d = self.find_d(phi_n, e)
        
        return n, e, d
    
    @staticmethod    # self 값이 없는 method에는 이렇게 @staticmethod를 적어줌!
    def find_e(phi_n: int):    # 주어진 조건을 만족하는 소수 e를 찾는 함수
        temp_e = 0
        for i in range(2, phi_n):
            if gcd(phi_n, i) == 1:
                temp_e = i
                break
        return temp_e
    
    @staticmethod
    def find_d(phi_n: int, e: int):    # # 주어진 조건을 만족하는 소수 d를 찾는 함수
        temp_d = 1
        for i in range(phi_n):
            if (e * i) % phi_n == 1:
                temp_d = i
                break
        return temp_d
    
    @staticmethod
    def primes_in_range(x: int, y: int):
        prime_list = []
        for n in range(x, y):
            isPrime = True
            
            for num in range(2, n):
                if n % num == 0:
                    isPrime = False
                    break
            
            if isPrime:
                prime_list.append(n)
        
        return prime_list
    
    @staticmethod
    def encrypt(plain_text: str, key: list):    # 암호화 함수에 대한 정의
        plain_bytes = [ord(x) for x in plain_text]
        cipher_bytes = []
        for i in plain_bytes:
            cipher_bytes.append((i ** key[1]) % key[0])
        
        cipher_hex = []
        for i in cipher_bytes:
            tmp_hex = "{:08x}".format(i)
            cipher_hex.append(tmp_hex)
        cipher_text = "0x" + "".join(cipher_hex)
        
        return cipher_text
    
    @staticmethod
    def decrypt(cipher_text: str, key: list):    # 복호화 함수에 대한 정의
        cipher_tmp = cipher_text.split("x")[-1]
        length = 8
        cipher_bytes = [int(cipher_tmp[x:x+length], 16) for x in range(0, len(cipher_tmp), length)]
        
        plain_bytes = []
        for i in cipher_bytes:
            plain_bytes.append((int(i) ** key[1]) % key[0])
        
        dec_text = "".join([chr(x) for x in plain_bytes])
        return dec_text


class Person:    # class는 여러 함수를 가질 수 있음
    def __init__(self, name: str):     # init은 초기화 과정
        self.name = name    # 이 객체가 사용하는 변수 이름이 self.
        self.rsa = RSA()    # class RSA
        self.communication = Communication()    # class Communication
        
        self.nonce = str(random.randint(0, 10000))    # 0~10000 사이의 임의의 정수(nonce)를 생성해 self.nonce에 저장
        self.target_key = []    # public key를 담을 수 있는 빈 list이므로 []
        self.__msg_history = []    # __가 붙은 변수는 private 변수라는 뜻, 외부에서 접근 불가!
    
    def recv_msg(self, msg: str): 
        self.__msg_history.append(msg)    # msg를 받아 self.__msg_history에 추가(append)하는 함수
    
    def recv_key(self, key: list):
        self.target_key = key    # key를 받아 self.target_key에 저장하는 함수
    
    def get_latest_msg(self):
        return self.__msg_history[-1]    #msg_history 중 가장 끝에 있는 메시지를 출력하는 함수


class Communication:
    @staticmethod    # self가 필요 없는, self 값이 없는 method에는 @staticmethod를 붙임!
    def send_msg(target: Person, msg: str):    #target 타입이 Person, msg 타입이 str(문자열)
        target.recv_msg(msg)    # target에 recv_msg 함수를 사용해 msg를 보내줌
    
    @staticmethod
    def send_key(target: Person, key: list):    # target 타입이 Person, key 타입이 list(리스트)
        target.recv_key(key)    #target에 recv_key 함수를 사용해 key를 보내줌


if __name__ == '__main__':    # 가장 핵심이 되는 main(메인) 함수의 시작 지점
    alice = Person("alice")    # Person은 class이다!
    bob = Person("bob")
    
    say_hi = "Hi! I'm Alice"
    alice.communication.send_msg(bob, say_hi)    # target bob에게 say_hi라는 str(문자열)을 보내라!
    print(bob.get_latest_msg())    # bob이 메시지를 잘 받았는지 확인, 실행 시 출력되는 첫번째 줄
    
    bob.communication.send_msg(alice, bob.nonce) # target alice에게 bob.nonce라는 nonce값을 보내라!
    print("bob nonce: ", bob.nonce)    # 아래의 alice nonce와 bob nonce가 같은지 확인하기 위한 줄, 실행 시 출력되는 두번째 줄
    print("alice nonce: ", alice.get_latest_msg())    # alice가 메시지를 잘 받았는지 확인, 실행 시 출력되는 세번째 줄
    
    alice.communication.send_msg(bob, alice.rsa.encrypt(alice.get_latest_msg(), alice.rsa.pri_key))
    # 129번째 줄: alice가 bob한테 받은 nonce를 자기의 private key로 암호화한 뒤 bob한테 보내는 과정
    print(bob.get_latest_msg())    # bob이 가장 최근에 받은 메시지를 확인(암호화된 텍스트가 출력됨), 실행 시 출력되는 네번째 줄
    alice.communication.send_key(bob, alice.rsa.pub_key)    # alice가 bob한테 자기의 public key를 보내는 과정
    print("alice pub key: ", alice.rsa.pub_key)    # 아래의 bob pub key와 alice pub key가 같은지 확인하기 위한 줄, 실행 시 출력되는 다섯번째 줄
    print("bob pub key: ", bob.target_key)    # bob이 alice가 준 public key, 즉 자신의 target key를 확인, 실행 시 출력되는 여섯번째 줄
    
    if bob.nonce == bob.rsa.decrypt(bob.get_latest_msg(), bob.target_key):
        # 136번째 줄: 'bob의 nonce'와 'bob이 받은 암호문을 bob의 target key = alice의 public key로 복호화한 결과'가 같으면
        say_hello = "Hello! I'm Bob"
        bob.communication.send_msg(alice, bob.rsa.encrypt(say_hello, bob.target_key))
        print(say_hello)    # "Hello! I'm Bob" 전송, 실행 시 출력되는 일곱번째 줄
    else:    # 이 과정에서 뭔가가 틀어졌으면
        print("is hacked...TT")    # "해킹당한듯...ㅠㅠ" 전송, 이게 출력되면 코드 중 어딘가를 잘못 작성했다는 뜻!!
    
    print("check: ", alice.rsa.decrypt(alice.get_latest_msg(), alice.rsa.pri_key))    # 최종 점검을 위한 줄, 실행 시 출력되는 마지막 줄