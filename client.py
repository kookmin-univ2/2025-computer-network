import socket
import json
import time


# reqeust 요청 메소드 생성
def sendRequest(method, path, body_dict=None): # method와 path, 그리고 본문 내용을 dict으로 받음
    host = 'localhost' # server ip
    port = 3333 # server port번호

    # request body 구성 초기화
    body = ""
    headers = { "Host": host, }

    if body_dict: # 본문을 포함한 요청인 경우
        body = json.dumps(body_dict) # body에 내용 포함 시킴
        headers["Content-Type"] = "application/json" # json을 헤더에 명시?
        headers["Content-Length"] = str(len(body.encode())) # 본문 길이 헤더에 반영?
    else:
        headers["Content-Length"] = 0

    # header를 json 형태로 assemble ?
    headers_raw = "".join([f"{k}: {v}\r\n" for k, v in headers.items()])

    # 최종 reqeust할 메세지
    request = f"{method} {path} HTTP/1.1\r\n{headers_raw}\r\n{body}"


    # request를 서버로 send
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect( (host,port) ) # 소켓 connect 시도
            client_socket.sendall(request.encode("utf-8")) # request 메세지 send (utf-8로 인코딩하여 보냄)
            print(f"[Request]\n{request}")
            print("\n")

            response = client_socket.recv(1024).decode("utf-8")
            print(f"[Rsponse]\n{response}") # 응답 받아 출력
            print("------------------------------------------------------------")

    except Exception as e:
        print(f"요청 중 예외 발생함: {e}")


def testCases():
    time.sleep(0.5) # 와이어샤크 캡처용 딜레이

    # 존재하지 않는 사용자 조회 요청
    sendRequest("GET", "/user?username=unknown")  
    time.sleep(0.5)

    # 회원가입 요청
    sendRequest("POST", "/signup", {
        "username": "iyeon",
        "password": "pass",
        "name": "한이연",
        "gender": "female"
    })  
    time.sleep(0.5)

    # username이 중복된 회원가입 요청
    sendRequest("POST", "/signup", {
        "username": "iyeon",
        "password": "pass",
        "name": "한이연",
        "gender": "female"
    })
    time.sleep(0.5)

    # 로그인 요청 성공
    sendRequest("POST", "/login", {
        "username": "iyeon",
        "password": "pass"
    })
    time.sleep(0.5)

    # 로그인 요청 실패
    sendRequest("POST", "/login", {
        "username": "iyeon",
        "password": "wrongpass"
    })
    time.sleep(0.5)

    # 유저 정보 수정 요청
    sendRequest("PUT", "/user/update", {
        "username": "iyeon",
        "name": "한이연22",
        "gender": "female"
    })
    time.sleep(0.5)

    # 유저 정보 수정 요청 실패 (username 없음)
    sendRequest("PUT", "/user/update", {
        "username": "notexist",
        "name": "아무나"
    })
    time.sleep(0.5)

    # 서버 상태 확인 요청
    sendRequest("HEAD", "/status")


if __name__ == "__main__":
    testCases()
    print("클라이언트 요청 종료")