# Netflix Cookies Checker
This tools helps you automate the process of checking if a Netflix cookie is valid or not saving you time and effort. Simply put all of your cookies in Netscape in a new directory called `cookies` and run the script. It will check all of the cookies and output the valid ones in a new folder called `hits`, and the invalid ones in a new folder called `failures`.

## How to run the script?
1. Install the required packages by running `pip install -r requirements.txt`.
2. Create a new directory called `cookies` and put all of your cookies in it.
3. Run the script by running `python main.py`.

> [!NOTE]
> No proxy is needed. Also, this script only supports Netscape format for now.

Keep in mind that the cookies will be renamed then moved to their respective folders. If the cookie is valid, the script will try to extract 4 things:
- The country of sign up. (e.g. US, BR, MX, etc.).
- Does the account have extra members feature. (e.g. True, None).
- Account GUID.
- Member since date.

> [!TIP]
> By default, the script automatically handles duplicates since it names working cookies in this format `cookie_` + `_country_` + `_extra(True/None)_` + `_guid_`. So basically, any duplicates will be overitten.
> Also, this script supports multi-threading.

## Disclaimer
This tool was created for educational purposes. Use it at your own risk.
