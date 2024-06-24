import colorama
import os
import json
import shutil

def print_banner():
    print(colorama.Fore.RED + """
  _   _      _    __ _ _         _____            _    _           
 | \\ | |    | |  / _| (_)       / ____|          | |  (_)          
 |  \\| | ___| |_| |_| |___  __ | |     ___   ___ | | ___  ___  ___ 
 | . ` |/ _ \\ __|  _| | \\ \\/ / | |    / _ \\ / _ \\| |/ / |/ _ \\/ __|
 | |\\  |  __/ |_| | | | |>  <  | |___| (_) | (_) |   <| |  __/\\__ |
 |_| \\_|\\___|\\__|_|_|_|_/_/\\_\\  \\_____\\___/ \\___/|_|\\_\\_|\\___||___/
                / ____| |             | |                          
               | |    | |__   ___  ___| | _____ _ __               
               | |    | '_ \\ / _ \\/ __| |/ / _ \\ '__|              
               | |____| | | |  __/ (__|   <  __/ |                 
                \\_____|_| |_|\\___|\\___|_|\\_\\___|_|                                                        
    """)
    print("-------------------------------------------------------------------" + colorama.Fore.RESET)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def convert_to_netscape_format(cookie):
    """ Convert the cookie dictionary to the Netscape cookie format string """
    flag = cookie.get('flag', '').upper()
    return "{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
        cookie['domain'], 'TRUE' if flag == 'TRUE' else 'FALSE', cookie['path'],
        'TRUE' if cookie.get('secure', False) else 'FALSE', cookie.get('expiration', ''), cookie['name'], cookie['value']
    )

def process_json_files(directory):
    """ Process JSON files, convert them to Netscape format, and move the originals to a different folder """
    json_after_conversion_folder = "json_cookies_after_conversion"  # Directory to move JSON cookies after conversion

    os.makedirs(json_after_conversion_folder, exist_ok=True)
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                try:
                    cookies = json.load(file)
                    if isinstance(cookies, list) and all('domain' in cookie for cookie in cookies):
                        netscape_cookie_file = os.path.join(directory, filename.replace('.json', '.txt'))
                        with open(netscape_cookie_file, 'w') as outfile:
                            outfile.writelines([convert_to_netscape_format(cookie) + '\n' for cookie in cookies])
                        shutil.move(file_path, os.path.join(json_after_conversion_folder, filename))
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file {filename}")