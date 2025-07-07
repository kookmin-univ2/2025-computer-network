import socket
from UserDB import UserDB
import datetime
import json

 

# 사용할 IP와 port번호 지정
host = 'localhost' # server 컴퓨터 ip
port = 3333 # server port번호 (다른 프로그램이 사용하지 않는 번호로 지정)


# 서버 소켓 생성
    # AF_INET(IPv4 의미) : 주소 체계 지정
    # SOCK_STREAM : TCP 사용을 지정
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 소켓 옵션 setsockopt() : 
    # socket.SOL_SOCKET: 소켓 레벨의 옵션을 설정
    # SO_REUSEADDR 사용 중인 ip/포트번호를 재사용하겠다 지정
        # 서버 소켓을 닫으면 해당 포트가 TIME_WAIT 상태가 되어 일정 시간 동안 같은 포트 번호로 bind를 못하게 됨. 이 문제를 방지하는 옵션.
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind(): 서버 소켓에 IP주소와 port 할당
server_socket.bind((host,port))

# socket open(열어두고 대기함. 클라이언트의 요청을 기다리는 상태로 만듦)
server_socket.listen()
print(f"서버가 {host}:{port}에서 대기 중!!")


# DB 객체 생성
user_db = UserDB()

while True:
    # accept(): 클라이언트 연결을 대기하고, 요청이 오면 소켓을 만들어 반환함.
    client_socket, client_addr = server_socket.accept()
    print(f"클라이언트가 {client_addr}에 연결됨.")

    try:
        # 클라이언트로부터 받은 요청
        # recv(메시지크기): 소켓에서 크기만큼 읽는 함수. 소켓에 읽을 데이터 없으면 생길 때까지 대기함.
        data = client_socket.recv(1024)
        # 데이터가 없으면 다음 요청으로 넘어감
        if not data:
            continue

        msg = data.decode("utf-8") # 읽은 데이터 디코딩
        print('==========HTTP Request==========')
        print(msg) # 받은 요청 메세지 출력

        # request 파싱
        lines = msg.split("\r\n")
        request_line = lines[0] if lines else "" # lines이 빈 경우 예외처리
        method, path, _ = request_line.split(" ", 2) if request_line else (None, None, None) # 최대 3개로만 나누도록 지정. None으로 예외처리.


        # 본문 추출 / 헤더와 바디를 구분하는 줄 기준으로 바디를 추출
        body = ""
        if "" in lines:
            empty_line_index = lines.index("")
            if empty_line_index + 1 < len(lines):
                body = lines[empty_line_index + 1].strip()

        # Content-Type이 application/json인 경우 JSON 파싱
        is_json = any("application/json" in line for line in lines)
        if is_json and body:
            try:
                json_data = json.loads(body)
            except json.JSONDecodeError:
                json_data = {}
        else:
            json_data = {}


        # GET 요청인 경우 
        if method == "GET":
            # username으로 유저 정보 조회 요청
            if path.startswith("/user?username="): # path가 해당 문자열로 시작하는지 확인 (bool)
                username = path.split("=")[1] # username 파싱
                user = user_db.get_user_by_username(username) # db에서 해당 username으로 db에서 조회

                if user: # 유저가 조회된 경우 (응답코드: 200)
                    response_body = f"username: {user[0]}\nname: {user[1]}\ngender: {user[2]}"
                    response = (
                        f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body.encode())}\r\n"
                        f"Date: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\r\n\r\n{response_body}"
                    )
                else: # 유저가 없는 경우 (응답코드: 404)
                    response_body = "해당 유저가 존재하지 않습니다."
                    response = (
                    f"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body.encode())}\r\n"
                    f"Date: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\r\n\r\n{response_body}"
                    )

                # 클라리언트에게 응답 전송 (HTTP response 메세지 전송)
                client_socket.send(response.encode())


        # POST 요청인 경우
        elif method == "POST":
            # 회원가입 요청
            if path == "/signup":

                # user db에 유저 정보 Insert 후 성공 시 True, 에러 시 False 반환 받음.
                success = user_db.insert_user(
                    json_data["username"], json_data["password"], json_data["name"], json_data["gender"]
                )
                if success: # 유저 insert 성공 (응답코드: 201)
                    response_body = "회원가입 성공"
                    response = (
                        f"HTTP/1.1 201 Created\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body.encode())}\r\n\r\n{response_body}"
                    )
                else: # 예외 발생하여 Insert 실패 (응답코드: 400)
                    response_body = "아이디 중복"
                    response = (
                        f"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body.encode())}\r\n\r\n{response_body}"
                    )

                client_socket.send(response.encode())

            # 로그인 요청
            elif path == "/login":

                # username, password가 일치하면 로그인 성공 (응답코드: 200)
                if user_db.check_login(json_data["username"], json_data["password"]):
                    response_body = "로그인 성공"
                    response = (
                        f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body.encode())}\r\n\r\n{response_body}"
                    )
                else: # 비밀번호 불일치 시 실패 (응답코드: 401)
                    response_body = "비밀번호 오류"
                    response = (
                        f"HTTP/1.1 401 Unauthorized\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body.encode())}\r\n\r\n{response_body}"
                    )

                client_socket.send(response.encode())

        # PUT 요청인 경우
        elif method == "PUT":
            # 유저 정보 업데이트 요청
            if path == "/user/update":
                username = json_data.get("username")
                password = json_data.get("password")
                name = json_data.get("name")
                gender = json_data.get("gender")

                if not username: # username은 null 불가임 예외 처리
                    raise KeyError("username 필수")

                # 유저 정보 update 후 성공 시 True, 에러 시 False 반환 받음.
                success = user_db.update_user(username, password, name, gender)
                if success: # update 성공 (응답코드: 200)
                    response_body = "수정 완료"
                    response = (
                        f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body.encode())}\r\n\r\n{response_body}"
                    )
                else: # update 실패 (응답코드: 400)
                    response_body = "해당 유저 없음 또는 수정 없음"
                    response = (
                        f"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body.encode())}\r\n\r\n{response_body}"
                    )
                client_socket.send(response.encode())

        # HEAD 요청인 경우
        elif method == "HEAD":
            # 서버 상태 응답 요청
            if path == "/status":
                response = (
                    f"HTTP/1.1 204 No Content\r\n"
                    f"Date: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\r\nContent-Length: 0\r\n\r\n"
                )
            client_socket.send(response.encode())

    finally:
        # socket close
        client_socket.close()
