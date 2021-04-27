import hmac # hmac이라는 모듈 import
import hashlib # hashlib이라는 모듈 import


class Person8th:
    def __init__(self, key): # init 초기화 함수 사용
        self.key = bytearray([ord(x) for x in key]) # 문자열(str)을 바이트(byte) 형태로 만들어 주는 것, 즉 byte로 타입을 변경해주는 것
        self.msg_to_send = "" # 보낼 메시지 초기화(문자열 형태로)
        self.recv_msg = "" # 받은 메시지 초기화(문자열 형태로)
    
    def encode_msg(self, msg: str): # '메시지 인코딩' 정의
        self.msg_to_send = msg.encode('utf-8') # utf-8로 메시지를 인코딩해준 뒤 보낼 메시지에 저장
        
    def create_hmac(self):
        hmac_msg = hmac.new(self.key, self.msg_to_send, hashlib.sha256) # (bytearray로 변경한 키, utf-8로 인코딩된 메시지, sha256 해시함수)를 가지고 hmac_msg 생성
        return hmac_msg.hexdigest() # hexdigest 함수를 사용하여 눈으로 볼 수 있는 헥사코드 형태로 변경해주고 return
    
    def read_file(self, file_name: str):
        with open(file_name, 'r') as f: # 파일을 읽기 방식'r'으로 열어줌
            lines = f.readlines() # 위에서 읽은 값들을 lines라는 변수 안에 담아줌, lines는 리스트 형태
        
        check_hmac = hmac.new(self.key, lines[1].encode('utf-8'), hashlib.sha256) # alice가 보낸 hmac값과 둘이 공유하고 있는 키로 만든 hmac값을 비교
        
        if lines[0].rstrip('\n') != check_hmac.hexdigest(): # \n을 지워주는 역할: rstrip 이걸 안지워주면 오류 메시지가 출력됨! / lines[0]과 check_hmac이 다르면
            print("This file is fake!!") # 오류 메시지 출력
        else:
            self.recv_msg = lines[1] # lines[0]과 check_hmac이 같으면 recv_msg에 lines[1]을 받아옴
            print(f"I got a msg: {self.recv_msg}") # 정상 메시지 출력 / 여기서 f를 빠뜨리면 {self.recv_msg}가 출력됨!


if __name__=='__main__': # main 함수 시작
    KEY = 'DIST'
    alice = Person8th(KEY) # Person8th class에 KEY값 받음
    bob = Person8th(KEY) # alice와 bob은 같은 KEY 공유 중
    
    text = 'hello DIST'
    alice.encode_msg(text) # alice가 텍스트를 인코딩
    
    alice_hmac = alice.create_hmac() # alice가 메시지 인증 코드를 생성
    
    with open('./hello.txt', 'w') as f: # with 구문을 사용하면 f.open, f.close를 따로 쓰지 않아도 됨
        wrter = [alice_hmac+'\n', text] # alice_hmac과 전송할 텍스트를 wrter 리스트에 저장, \n: 개행 문자(alice_hmac과 텍스트를 한 칸 나눠줌)
        
        for w in wrter: 
            f.write(w) # wrter의 element를 하나씩 가져와서 한 줄씩 적어나감
    
    bob.read_file('./hello.txt') # bob이 파일을 읽음

