import requests
import os
import threading
import colorama
import shutil
import re
from utils import *

def load_cookies_from_file(cookie_file):
    """Load cookies from a given file and return a dictionary of cookies."""
    cookies = {}
    with open(cookie_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                domain, _, path, secure, expires, name, value = parts[:7]
                cookies[name] = value
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

def handle_successful_login(cookie_file, info, hits_folder):
    """Handle the actions required after a successful login."""
    print(colorama.Fore.GREEN + f"> Login successful with {cookie_file}. Country: {info['countryOfSignup']}. Member since: {info['memberSince']}" + colorama.Fore.RESET)
    new_filename = f"cookie_{info['countryOfSignup']}_{info['showExtraMemberSection']}_{info['userGuid']}.txt"
    shutil.move(cookie_file, os.path.join(hits_folder, new_filename))

def handle_failed_login(cookie_file, failures_folder):
    """Handle the actions required after a failed login."""
    print(colorama.Fore.RED + f"> Login failed with {cookie_file}. This cookie has expired. Moved to failures!" + colorama.Fore.RESET)
    shutil.move(cookie_file, os.path.join(failures_folder, os.path.basename(cookie_file)))

def process_cookie_file(cookie_file, hits_folder, failures_folder):
    """Process each cookie file to check for a valid login and move accordingly."""
    try:
        cookies = load_cookies_from_file(cookie_file)
        response_text = make_request_with_cookies(cookies)
        info = extract_info(response_text)

        if info['countryOfSignup'] and info['countryOfSignup'] != "null":
            handle_successful_login(cookie_file, info, hits_folder)
            return True
        else:
            handle_failed_login(cookie_file, failures_folder)
            return False
    except Exception as e:
        print(colorama.Fore.YELLOW + f"> Error with {cookie_file}: {str(e)}" + colorama.Fore.RESET)
        handle_failed_login(cookie_file, failures_folder)

def worker(cookie_files, hits_folder, failures_folder):
    """Worker thread to process cookie files."""
    while cookie_files:
        cookie_file = cookie_files.pop()
        process_cookie_file(cookie_file, hits_folder, failures_folder)

def check_cookies_directory(directory_path, hits_folder, failures_folder, num_threads=3):
    """Setup directories and threads to process all cookie files."""
    os.makedirs(hits_folder, exist_ok=True)
    os.makedirs(failures_folder, exist_ok=True)
    cookie_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.txt')]
    threads = [threading.Thread(target=worker, args=(cookie_files, hits_folder, failures_folder)) for _ in range(min(num_threads, len(cookie_files)))]

    clear_screen()
    print_banner()
    print(colorama.Fore.CYAN + f"\n> Started checking {len(cookie_files)} cookie files..." + colorama.Fore.RESET)
    
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

def get_started(cookies_folder, cookies_error=False):
    """Get started with the program."""
    os.makedirs(cookies_folder, exist_ok=True)
    if not cookies_error:
        clear_screen()
        print_banner()
        print(colorama.Fore.GREEN + "\nWelcome, after moving your cookies to (cookies) folder, press\n               Enter if you're ready to start!" + colorama.Fore.RESET)

    input()
    dir_content = [f for f in os.listdir(cookies_folder) if not f.startswith('.') and f.endswith('.txt')]
    if not dir_content:
        print(colorama.Fore.RED + "> No cookies found in the cookies folder.\n> Please add cookies in Netscape format (.txt) and try again." + colorama.Fore.RESET)
        get_started(cookies_folder, True)

def main():
    """Initialize the program."""
    colorama.init()
    cookies_folder = "cookies"  # Directory where your cookies are stored
    hits_folder = "hits"  # Directory to save working cookies
    failures_folder = "failures"  # Directory to move failed cookies
    get_started(cookies_folder)
    check_cookies_directory(cookies_folder, hits_folder, failures_folder)

if __name__ == "__main__":
    main()
