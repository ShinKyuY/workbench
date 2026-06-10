"""사용자 서비스 모듈.

UserService 하나가 DB 접근, 이메일 전송, 로깅, 인증/세션까지 전부 담당한다.
"""

import hashlib
import secrets
import sqlite3
import time


class UserService:
    def __init__(self, smtp_client=None, log_path=None):
        self.db = sqlite3.connect(":memory:")
        self.db.execute(
            "CREATE TABLE users ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " email TEXT UNIQUE NOT NULL,"
            " password_hash TEXT NOT NULL,"
            " salt TEXT NOT NULL,"
            " name TEXT,"
            " active INTEGER DEFAULT 1,"
            " created_at REAL)"
        )
        self.smtp_client = smtp_client
        self.log_path = log_path
        self.logs = []
        self.sessions = {}
        self.sent_emails = []

    # -------------------------------------------------- 로깅
    def _log(self, level, message):
        line = "[%s] %s %s" % (level, time.strftime("%Y-%m-%d %H:%M:%S"), message)
        self.logs.append(line)
        if self.log_path:
            with open(self.log_path, "a") as f:
                f.write(line + "\n")

    # -------------------------------------------------- 이메일
    def _send_email(self, to, subject, body):
        if self.smtp_client is not None:
            self.smtp_client.send("noreply@example.com", to, subject, body)
        else:
            self.sent_emails.append((to, subject, body))
        self._log("INFO", "email sent to=%s subject=%s" % (to, subject))

    # -------------------------------------------------- 인증 유틸
    def _hash_password(self, password, salt):
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    def _generate_token(self):
        return secrets.token_hex(16)

    # -------------------------------------------------- 회원 가입
    def register(self, email, password, name=None):
        if "@" not in email:
            self._log("WARN", "register rejected: bad email %s" % email)
            return {"ok": False, "error": "이메일 형식 오류"}
        if len(password) < 8:
            self._log("WARN", "register rejected: weak password for %s" % email)
            return {"ok": False, "error": "비밀번호는 8자 이상"}
        row = self.db.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if row is not None:
            self._log("WARN", "register rejected: duplicate %s" % email)
            return {"ok": False, "error": "이미 가입된 이메일"}
        salt = secrets.token_hex(8)
        password_hash = self._hash_password(password, salt)
        cur = self.db.execute(
            "INSERT INTO users (email, password_hash, salt, name, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (email, password_hash, salt, name, time.time()),
        )
        self.db.commit()
        self._send_email(email, "가입을 환영합니다", "%s님, 가입이 완료되었습니다." % (name or email))
        self._log("INFO", "user registered id=%d email=%s" % (cur.lastrowid, email))
        return {"ok": True, "user_id": cur.lastrowid}

    # -------------------------------------------------- 로그인 / 세션
    def login(self, email, password):
        row = self.db.execute(
            "SELECT id, password_hash, salt, active FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if row is None:
            self._log("WARN", "login failed: no such user %s" % email)
            return {"ok": False, "error": "존재하지 않는 사용자"}
        user_id, password_hash, salt, active = row
        if not active:
            self._log("WARN", "login failed: deactivated %s" % email)
            return {"ok": False, "error": "비활성화된 계정"}
        if self._hash_password(password, salt) != password_hash:
            self._log("WARN", "login failed: wrong password %s" % email)
            return {"ok": False, "error": "비밀번호 불일치"}
        token = self._generate_token()
        self.sessions[token] = {"user_id": user_id, "issued_at": time.time()}
        self._log("INFO", "login ok user_id=%d" % user_id)
        return {"ok": True, "token": token, "user_id": user_id}

    def verify_session(self, token):
        session = self.sessions.get(token)
        if session is None:
            return {"ok": False, "error": "유효하지 않은 세션"}
        if time.time() - session["issued_at"] > 3600:
            del self.sessions[token]
            self._log("INFO", "session expired user_id=%d" % session["user_id"])
            return {"ok": False, "error": "세션 만료"}
        return {"ok": True, "user_id": session["user_id"]}

    def logout(self, token):
        if token in self.sessions:
            user_id = self.sessions[token]["user_id"]
            del self.sessions[token]
            self._log("INFO", "logout user_id=%d" % user_id)
            return {"ok": True}
        return {"ok": False, "error": "유효하지 않은 세션"}

    # -------------------------------------------------- 비밀번호 재설정
    def reset_password(self, email):
        row = self.db.execute(
            "SELECT id, name FROM users WHERE email = ?", (email,)
        ).fetchone()
        if row is None:
            self._log("WARN", "reset rejected: no such user %s" % email)
            return {"ok": False, "error": "존재하지 않는 사용자"}
        user_id, name = row
        temp_password = secrets.token_hex(6)
        salt = secrets.token_hex(8)
        self.db.execute(
            "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
            (self._hash_password(temp_password, salt), salt, user_id),
        )
        self.db.commit()
        self._send_email(
            email, "임시 비밀번호 안내", "%s님의 임시 비밀번호: %s" % (name or email, temp_password)
        )
        self._log("INFO", "password reset user_id=%d" % user_id)
        return {"ok": True}

    # -------------------------------------------------- 프로필 / 상태
    def update_email(self, token, new_email):
        session = self.verify_session(token)
        if not session["ok"]:
            return session
        if "@" not in new_email:
            return {"ok": False, "error": "이메일 형식 오류"}
        dup = self.db.execute(
            "SELECT id FROM users WHERE email = ?", (new_email,)
        ).fetchone()
        if dup is not None:
            return {"ok": False, "error": "이미 사용 중인 이메일"}
        self.db.execute(
            "UPDATE users SET email = ? WHERE id = ?",
            (new_email, session["user_id"]),
        )
        self.db.commit()
        self._send_email(new_email, "이메일 변경 안내", "이메일이 변경되었습니다.")
        self._log("INFO", "email updated user_id=%d" % session["user_id"])
        return {"ok": True}

    def deactivate_user(self, token):
        session = self.verify_session(token)
        if not session["ok"]:
            return session
        self.db.execute(
            "UPDATE users SET active = 0 WHERE id = ?", (session["user_id"],)
        )
        self.db.commit()
        self.logout(token)
        self._log("INFO", "user deactivated user_id=%d" % session["user_id"])
        return {"ok": True}

    def get_user(self, user_id):
        row = self.db.execute(
            "SELECT id, email, name, active FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if row is None:
            return None
        return {"id": row[0], "email": row[1], "name": row[2], "active": bool(row[3])}
