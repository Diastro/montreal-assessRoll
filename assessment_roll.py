import json
import cookielib
import requests
import sys
import Queue
import re
import os
from operator import itemgetter
from bs4 import BeautifulSoup

class req():
	def __init__(self):
		self.session = requests.Session()

		# inital request - sets session cookie
		r = self.session.get('http://evalweb.ville.montreal.qc.ca/default.asp')

	def streetLookup(self, streetName):
		self.session.cookies.set_cookie(cookielib.Cookie(
			version=0,
			name='nom_rue',
			value=streetName,
			port=None,
			port_specified=False,
			domain="evalweb.ville.montreal.qc.ca",
			domain_specified=True,
			domain_initial_dot=False,
			path="/",
			path_specified=True,
			secure=False,
			expires=None,
			discard=False,
			comment=None,
			comment_url=None,
			rest=None
		))

		payload = {'text1': streetName}
		URL = "http://evalweb.ville.montreal.qc.ca/Role2014actu/recherche.asp"
		r = self.session.get(URL, data=payload)
		content =  r.text.encode('utf-8').strip()

		return content

	def queryStreet(self, streetId):
		URL = "http://evalweb.ville.montreal.qc.ca/Role2014actu/RechAdresse.ASP?IdAdrr=%20" + streetId
		r = self.session.get(URL)
		content =  r.text.encode('utf-8').strip()

		return content

	def queryAdress(self, adressId):
		URL = "http://evalweb.ville.montreal.qc.ca/Role2014actu/roleact_arron_min.asp?ue_id=" + adressId
		temp = self.session.get(URL)

		# bypass - for some reason this page has mutiple html tags preventing beautifulSoup from parsing it properly
		r = ""
		secondTag = False
		for line in temp.iter_lines():
			if secondTag == True:
				r = r + line
			if "</html>" in line:
				secondTag = True
		content =  r # TODO : utf-8

		return content


def main():
	foundStreets = []
	selectedStreets = []
	selectedAdresses = []
	roll = []

	request = req()

	streets = raw_input('\nEnter street names or parts of street names separated by spaces (ex: Fonteneau Bourassa Papineau): ').split(" ")

	# get the street list (id, name)
	for street in streets:
		r = request.streetLookup(street)
		soup = BeautifulSoup(r)
		results = soup.findAll('option')

		for result in results:
			if "/" in result.text:
				foundStreets.append({'id': result['value'], 'name': result.text})

	# print the result for user selection
	if len(foundStreets) == 0:
		print 'No street found with this name. Please try again.\n'
		sys.exit(0)

	for i, res in enumerate(foundStreets):
		print str(i) + " - " + "[" + res['id'] + "]" + " - " + re.sub(' +', ' ', res['name'])
	print str(len(foundStreets)) + " - Select all results"

	# which streets to query
	streetI = raw_input('\nWhich streets do you want to query? Entrer each street id seperated by spaces (ex: 0 2 3): ').split(" ")

	if int(streetI[0]) == len(foundStreets):
		selectedStreets = foundStreets
	else:
		for i in streetI:
			selectedStreets.append(foundStreets[int(i)])

	# query selectedStreets
	for street in selectedStreets:
		r = request.queryStreet(street['id'])
		soup = BeautifulSoup(r)
		results = soup.findAll('option')

		for result in results:
			if "%" in result['value']:
				selectedAdresses.append({'id': result['value'], 'adress': result.text})

	# query selectedAdresses
	for count, adress in enumerate(selectedAdresses):
		r = request.queryAdress(adress['id'])
		soup = BeautifulSoup(r)
		soup.prettify()
		results = soup.findAll('font')

		postal_addr = ''
		value_int = 0
		value_str = ''
		ownerA = ''
		for i, result in enumerate(results):
			if "Adresse :" in result.text:
				postal_addr = results[i+1].text.encode('utf-8')

			if "Valeur imposable de l'immeuble :" in result.text:
				try:
					value_int = int(results[i+1].text.replace(" ", "").replace("$",""))
					value_str = results[i+1].text.encode('utf-8')
				except:
					continue

			if "Nom :" in result.text and ownerA == "":
				ownerA = results[i+1].text.replace(",", " ").replace("  ", " ").encode('utf-8') # TODO : remove utf-8

		# does the job, but needs review
		sys.stdout.write('  \b')
		a =  ' ' * 200 + '\r'
		sys.stdout.write(a)
		sys.stdout.write('  \b')

		b =  ' Collecting data, please wait : ' + str(count) + '/' + str(len(selectedAdresses)) + '\r'
		sys.stdout.write(b)
		sys.stdout.flush()

		if value_int != 0:
			roll.append({'postal_adress': postal_addr,
						 'ownerA': ownerA,
						 'value_int': value_int,
						 'value_str': value_str})

	sortedRoll = sorted(roll,key=itemgetter('value_int'), reverse=True)

	# fianl data printing
	f = open('assessment_roll_data.csv', 'w')
	print '\n\n' + "Sorted assessment roll : \n"
	for r in sortedRoll:
		output = r['postal_adress'] + "," + r['ownerA'] + "," + r['value_str']
		f.write(output + '\n')
		print output
	print '\n'

	print 'Data successfuly written to assessement_roll_data.csv\n'


if __name__ == "__main__":
	main()
