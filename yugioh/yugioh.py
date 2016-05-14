import urllib2
from urllib2 import Request, urlopen
from pprint import pprint
import json
from itertools import groupby

# path = 'http://yugiohprices.com/api/card_data/Trap Hole'
# opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
# opener.open(path)

def get_card_data(name):
	print 'Getting %s' % str(name)
	request = Request('http://yugiohprices.com/api/card_data/' + urllib2.quote(name))
	response_body = urlopen(request).read()
	return response_body

def finish_card(card):
	data = get_card_data(card['name'])
	card['data'] = data
	return card

def main_data_retrieval():
	filename = 'cardlist.txt'
	cards = []
	lines = []
	with open(filename, 'r') as fin:
		lines = fin.readlines()
	splits = [l.strip().split('\t') for l in lines]
	cards = [{'code': s[0], 'name': s[1]} for s in splits]
	cards = [finish_card(card) for card in cards]

	with open('cardlist_final.txt', 'w') as fout:
		for card in cards:
			fout.write('%s\t%s\t%s\n' % (card['code'], card['name'], card['data']))

def process_intermediate(card):
	response = json.loads(card[2])
	newcard = {'status': False}
	if response['status'] == 'success':
		newcard = response['data']
		newcard['status'] = True
	newcard['code'] = card[0]
	if not 'name' in newcard:
		newcard['name'] = card[1]
	return newcard

def retry(card):
	name = card['name'].title()
	response = json.loads(get_card_data(name))
	if response['status'] == 'success':
		newcard = response['data']
		newcard['code'] = card['code']
		newcard['status'] = True
		return newcard
	else:
		return card

def rewrite_data():
	filename = 'cardlist_final.txt'
	cards = []
	lines = []
	with open(filename, 'r') as fin:
		lines = fin.readlines()
	cards = [line.strip().split('\t') for line in lines]
	cards = [process_intermediate(card) for card in cards]

	with open('cardlist_objects.txt', 'w') as fout:
		for card in cards:
			fout.write(json.dumps(card) + '\n')

def read_card_objects(filename):
	with open(filename, 'r') as fin:
		lines = fin.readlines()
		cards = [json.loads(l.strip()) for l in lines]
		return cards

def write_card_objects(filename, cards):
	with open(filename, 'w') as fout:
		for card in cards:
			fout.write(json.dumps(card) + '\n')

def main_data_analysis():
	filename = 'cardlist_objects.txt'
	cards = read_card_objects(filename)

	errors = filter(lambda x: x['status'] == False, cards)
	retries = [retry(c)  for c in errors]
	write_card_objects('retried_cards.txt', retries)

	errors2 = filter(lambda x: x['status'], retries)

	print len(errors2)
	print len(retries)

	# numwords = map(lambda x: len(x['name'].split(' ')), errors)
	# numwords = sorted(numwords)
	# print [len(list(group)) for key, group in groupby(numwords)]

	# print numwords
	# print len(numwords) 

	# print len(filter(lambda x: x['status'], cards))
	# print len(cards)

def merge_retries():
	retries = read_card_objects('retried_cards.txt')
	main_cards = read_card_objects('cardlist_objects.txt')

	numerrors = len(filter(lambda x: x['status'] == False, main_cards))
	print '%d out of %d' % (numerrors, len(main_cards))

	def replace_if_possible(card):
		matches = filter(lambda x: x['name'].lower() == card['name'].lower(), retries)
		if len(matches) > 0:
			return matches[0]
		else:
			return card
	main_cards = map(replace_if_possible, main_cards)

	numerrors = len(filter(lambda x: x['status'] == False, main_cards))
	print '%d out of %d' % (numerrors, len(main_cards))

	write_card_objects('cardlist_objects.txt', main_cards)

# rewrite_data()
merge_retries()

# print json.loads(get_card_data('Trap Hole'))