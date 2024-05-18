import requests
import os
import threading
import colorama
import shutil
import re
from utils import *

# Global counters
total_working = 0
total_fails = 0
total_checked = 0
lock = threading.Lock()

# Global paths
cookies_folder = "cookies"  # Directory where your cookies are stored
hits_folder = "hits"  # Directory to save working cookies
failures_folder = "failures"  # Directory to move failed cookies
broken_folder = "broken"  # Directory to move broken cookies


def load_cookies_from_file(cookie_file):
    """Load cookies from a given file and return a dictionary of cookies."""
    cookies = {}
    with open(cookie_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                domain, _, path, secure, expires, name, value = parts[:7]
                cookies[name] = value
            else:
                print(colorama.Fore.YELLOW + f"> Invalid cookie line: {line.strip()}" + colorama.Fore.RESET)
                if os.path.exists(cookie_file):
                    shutil.move(cookie_file, os.path.join(broken_folder, os.path.basename(cookie_file)))
    return cookies

def make_request_with_cookies(cookies):
    """Make an HTTP request using provided cookies and return the response text."""
    session = requests.Session()
    session.cookies.update(cookies)
    return session.get("https://www.netflix.com/browse").text

def extract_info(response_text):
    """Extract relevant information from the response text."""
    patterns = {
        'countryOfSignup': r'"countryOfSignup":\s*"([^"]+)"',
        'memberSince': r'"memberSince":\s*"([^"]+)"',
        'userGuid': r'"userGuid":\s*"([^"]+)"',
        'showExtraMemberSection': r'"showExtraMemberSection":\s*([^,]+)'
    }
    return {key: re.search(pattern, response_text).group(1) if re.search(pattern, response_text) else None for key, pattern in patterns.items()}

def handle_successful_login(cookie_file, info):
    """Handle the actions required after a successful login."""
    global total_working
    with lock:
        total_working += 1
    print(colorama.Fore.GREEN + f"> Login successful with {cookie_file}. Country: {info['countryOfSignup']}. Member since: {info['memberSince']}" + colorama.Fore.RESET)
    new_filename = f"cookie_{info['countryOfSignup']}_{info['showExtraMemberSection']}_{info['userGuid']}.txt"
    shutil.move(cookie_file, os.path.join(hits_folder, new_filename))

def handle_failed_login(cookie_file):
    """Handle the actions required after a failed login."""
    global total_fails
    with lock:
        total_fails += 1
    print(colorama.Fore.RED + f"> Login failed with {cookie_file}. This cookie has expired. Moved to failures!" + colorama.Fore.RESET)
    if os.path.exists(cookie_file):
        shutil.move(cookie_file, os.path.join(failures_folder, os.path.basename(cookie_file)))

def process_cookie_file(cookie_file):
    """Process each cookie file to check for a valid login and move accordingly."""
    global total_checked
    with lock:
        total_checked += 1
    try:
        cookies = load_cookies_from_file(cookie_file)
        response_text = make_request_with_cookies(cookies)
        info = extract_info(response_text)

        if info['countryOfSignup'] and info['countryOfSignup'] != "null":
            handle_successful_login(cookie_file, info)
            return True
        else:
            handle_failed_login(cookie_file)
            return False
    except Exception as e:
        print(colorama.Fore.YELLOW + f"> Error with {cookie_file}: {str(e)}" + colorama.Fore.RESET)
        if os.path.exists(cookie_file):
            shutil.move(cookie_file, os.path.join(broken_folder, os.path.basename(cookie_file)))

def worker(cookie_files):
    """Worker thread to process cookie files."""
    while cookie_files:
        cookie_file = cookie_files.pop()
        process_cookie_file(cookie_file)

def check_cookies_directory(num_threads=3):
    """Setup directories and threads to process all cookie files."""
    os.makedirs(hits_folder, exist_ok=True)
    os.makedirs(failures_folder, exist_ok=True)
    os.makedirs(broken_folder, exist_ok=True)
    
    process_json_files(cookies_folder)  # Convert JSON cookies to Netscape format

    cookie_files = [os.path.join(cookies_folder, f) for f in os.listdir(cookies_folder) if f.endswith('.txt')]
    threads = [threading.Thread(target=worker, args=(cookie_files,)) for _ in range(min(num_threads, len(cookie_files)))]

    clear_screen()
    print_banner()
    print(colorama.Fore.CYAN + f"\n> Started checking {len(cookie_files)} cookie files..." + colorama.Fore.RESET)
    
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Display statistics
    printStats()

def printStats():
    """Print the statistics of the cookies check."""
    print("\n-------------------------------------------------------------------\n")
    print(colorama.Fore.CYAN + f"> Statistics:" + colorama.Fore.RESET)
    print(f"  - 📈 Total checked: {total_checked}")
    print(f"  - ✅ Working cookies: {colorama.Fore.GREEN}{total_working}{colorama.Fore.RESET}")
    print(f"  - ❌ Dead cookies: {colorama.Fore.RED}{total_fails}{colorama.Fore.RESET}")
    print("\n")

def get_started(cookies_error=False):
    """Get started with the program."""
    os.makedirs(cookies_folder, exist_ok=True)
    if not cookies_error:
        clear_screen()
        print_banner()
        print(colorama.Fore.GREEN + "\nWelcome, after moving your cookies to (cookies) folder, press\n               Enter if you're ready to start!" + colorama.Fore.RESET)

    input()
    dir_content = [f for f in os.listdir(cookies_folder) if not f.startswith('.') and (f.endswith('.txt') or f.endswith('.json'))]
    if not dir_content:
        print(colorama.Fore.RED + "> No cookies found in the cookies folder.\n> Please add cookies in Netscape/JSON format (.txt | .json) and try again." + colorama.Fore.RESET)
        get_started(True)

def main():
    """Initialize the program."""
    colorama.init()
    get_started()
    check_cookies_directory()

if __name__ == "__main__":
    main()
