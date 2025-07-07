import sqlite3


class UserDB:
    def __init__(self, db_name = "user.db"):
        self.db_name = db_name # db 명 지정
        self.init_db() # 초기화 시 db 테이블 생성함

    # db 연결 객체 생성 메서드
    def get_connection(self):
        return sqlite3.connect(self.db_name)

    # user 테이블 생성 메서드
    def init_db(self):
        conn = self.get_connection() # 연결 객채 선언
        cur = conn.cursor() # cursor() sql 실행을 위한 커서를 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                gender TEXT NOT NULL
            )
        """)
        conn.commit() # db 변경사항을 반영
        conn.close() # db 연결 종료


    # 회원가입 시 유저 insert 메서드
    def insert_user(self, username, password, name, gender):
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO users (username, password, name, gender) VALUES (?, ?, ?, ?)
            """, (username, password, name, gender))
            conn.commit()
            return True # 성공 시 True 반환암
        
        except sqlite3.IntegrityError: 
            return False # 데이터베이스 제약 조건 위반 시 예외 발생. username PK가 중복되면 에러 발생함. False 반환

        finally: conn.close() 


    # username으로 유저 정보 조회 메서드
    def get_user_by_username(self, username):
        conn = self.get_connection()
        cur = conn.cursor()
        # username, name, gender 조회
        cur.execute("""
        SELECT username, name, gender FROM users WHERE username = ?
        """, (username,))
        result = cur.fetchone() # fetchone(): 결과의 한 row을 가져오는 함수
        conn.close()

        return result # 결과값(유저 정보)을 반환함. 또는 없으면 None

    # 로그인 메서드
    def check_login(self, username, password):
        conn = self.get_connection()
        cur = conn.cursor()
        # username, password 일치하는 유저 조회
        cur.execute("""
        SELECT * FROM users WHERE username = ? AND password = ?
        """, (username, password))
        result = cur.fetchone()
        conn.close()

        return result is not None # 조회된 row가 있으면 결과 반환, 없으면 None 반환


    # 유저 정보 수정 함수 (입력된 필드만 업데이트)
    def update_user(self, username, password=None, name=None, gender=None):
        conn = self.get_connection()
        cur = conn.cursor()
        updates = [] # sql SET절에 포함시킬 문자열 리스트
        values = [] # ?에 바인딩될 값 리스트

        # 변경할 항목이 있는 경우에만 반영
        if password:
            updates.append("password = ?")
            values.append(password)

        if name:
            updates.append("name = ?")
            values.append(name)

        if gender:
            updates.append("gender = ?")
            values.append(gender)

        # 항목이 존재하지 않는 경우 False 반환
        if not updates: return False
        
        values.append(username) # WHERE절의 조건에 사용하기 위한 username 추가

        sql = f"UPDATE users SET {', '.join(updates)} WHERE username = ?" # updates 내용 반영한 문자열
        cur.execute(sql, values) 
        conn.commit()
        affected = cur.rowcount # return True를 위한 row 수 카운트
        conn.close()
        return affected > 0 # rowcount가 1 이상이면 True 반환.

