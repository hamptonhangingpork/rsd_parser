import requests, random, warnings, time, json, re, os, csv
from bs4 import BeautifulSoup as soup

warnings.filterwarnings("ignore")

row_header = ['State', 'Store Name', 'Address', 'Phone', 'Email']

with open('record_store_list.csv', 'w', encoding='UTF8') as f:
	writer = csv.writer(f)

	# write the header
	writer.writerow(row_header)

	user_agents_list = [
	"Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
	"Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
	"Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
	]

	s = requests.Session()
	state_list = ['OR', 'NV', 'AZ' , 'OK', 'WI', 'IL', 'VA', 'NC', 'IN', 'GA', 'PA', 'CT', 'MA', 'AR']
	base_url = 'https://recordstoreday.com/'
	for state in state_list:
		try:
			print(f"[-] Parsing {state}")
			url = f'https://recordstoreday.com/Venues?state={state}'
			user_agent = random.choice(user_agents_list)

			headers = {
			  'User-Agent': user_agent
			}

			store_list = list()

			#Get url directory
			response = s.get(url, verify=False, headers=headers, allow_redirects=True, timeout=None)
			time.sleep(2)
			directory_handle = soup(response.text, "html.parser")
			raw_html = directory_handle.find_all('div', attrs={"id": "mainContent_1column"})
			raw_script = raw_html[0].find('script').text
			raw_script_list = raw_script.splitlines()
			for line in raw_script_list:
				store_url = re.match('"view_url":"(.+)"', line.strip())
				if store_url:
					if store_url[1] not in store_list:
						store_list.append(store_url[1])
			
			#Get store details
			for store in store_list:
				response = s.get(f"{base_url}{store}", verify=False, headers=headers, allow_redirects=True, timeout=None)
				store_handle = soup(response.text, "html.parser")
				raw_sub_html = store_handle.find('div', attrs={'class': 'col-xs-12'}).text.strip()
				raw_html_list = raw_sub_html.splitlines()
				store_name = raw_html_list[0]
				phone = ''
				email = ''
				address = ''
				for line in raw_html_list:
					phone_re = re.match(r'Phone: (.+)', line.strip())
					email_re = re.match('Email: (.+)', line.strip())
					address_re = re.match('(.+)MAP IT', line.strip())
					if phone_re:
						phone = phone_re[1]
					if email_re:
						email = email_re[1]
					if address_re:
						address = address_re[1]	
				writer.writerow([state, store_name, phone, address, email])
				time.sleep(3)
		except Exception as e:
			print(f"--> [ERROR] {e}")
