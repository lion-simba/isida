#!/usr/bin/python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------- #
#                                                                             #
#    Plugin for iSida Jabber Bot                                              #
#    Copyright (C) 2011 Vit@liy <vitaliy@root.ua>                             #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                             #
# --------------------------------------------------------------------------- #

def gcalc(type, jid, nick, text):
	if not text.strip(): msg = L('What?')
	else:
		try:
			data = load_page('http://www.google.ru/search?', {'q':text.encode('utf-8'),'hl':GT('youtube_default_lang')})
			result = re.search('<h2 class=r style="font-size:138%"><b>(.+?)</b>', data).group(1)
			msg = result.replace("<font size=-2> </font>",",").replace(" &#215; 10<sup>","E").replace("</sup>","").replace('<sup>','^').decode('utf-8', 'ignore')
		except: msg = L('Google Calculator results not found')
	send_msg(type, jid, nick, msg)


def define(type, jid, nick, text):
	text = text.strip()
	target, define_silent = '', False
	if not text: msg = L('What?')
	else:
		if re.search('\A\d+?(-\d+?)? ', text): target, text = text.split(' ', 1)
		data = load_page('http://www.google.com.ua/search?', {'hl': 'ru', 'q': text.encode('utf-8'), 'tbs': 'dfn:1'}).decode('utf-8')
		result = re.findall('<li style="list-style:none">(.+?)</li></ul><div style="color:#551a8b"><cite><span class=bc><a href="/url\?url=(.+?)&amp', data)
		if target:
			try: n1 = n2 = int(target)
			except: n1, n2 = map(int, target.split('-'))
			if n1+n2 == 0: define_silent,n1,n2 = True,1,1
		if not result: msg = [L('I don\'t know!'),''][define_silent]
		else:
			if target:
				msg = ''
				if 0 < n1 <= n2 <= len(result):
					for k in xrange(n1-1,n2): msg += '%s\n%s\n\n' % (result[k][0], urllib.unquote(result[k][1].replace('%25', '%').encode('utf8')).decode('utf8'))
				else: msg = [L('I don\'t know!'),''][define_silent]
			else:
				result = random.choice(result)
				msg = result[0] + '\n' + urllib.unquote(result[1].replace('%25', '%').encode('utf8')).decode('utf8')
			if '<' in msg and '>' in msg: msg = unhtml_hard(msg)
	if msg: send_msg(type, jid, nick, msg)

def define_message(room,jid,nick,type,text):
	s = get_config(room,'parse_define')
	if s != 'off':
		cof = getFile(conoff,[])
		if (room,'define') in cof: return
		tmppos = arr_semi_find(confbase, room)
		nowname = getResourse(confbase[tmppos])
		text = re.sub('^%s[,:]\ ' % re.escape(nowname), '', text.strip())
		what = re.search([u'^(?:(?:что такое)|(?:кто такой)) ([^?]+?)\?$',u'(?:(?:что такое)|(?:кто такой)) ([^?]+?)\?'][s=='partial'], text, re.I+re.U+re.S)
		if what:
			access_mode = get_level(room,nick)[0]
			text = 'define 0 ' + what.group(1)
			com_parser(access_mode, nowname, type, room, nick, text, jid)
			return True

def goo_gl_raw(text, is_qr):
	url = text.strip().encode('utf-8')
	if '://' not in url[:10] and not is_qr: url = 'http://'+url
	if is_qr: regex = 'http://goo\.gl/[a-zA-Z0-9]+?\.qr\Z'
	else: regex = 'http://goo\.gl/[a-zA-Z0-9]+?\Z'
	if not url: msg = L('What?')
	elif re.match(regex, url):
		if is_qr: url = url[:-3]
		f = get_opener(url)[0]
		if L('Error! %s') % '' in f: msg = f
		else: msg = urllib.unquote(f.geturl().encode('utf8')).decode('utf8')
	else:
		data = load_page(urllib2.Request('http://goo.gl/api/url','url=%s' % urllib.quote(url)))
		if L('Error! %s') % '' in data: msg = data
		else:
			msg = simplejson.loads(data)['short_url']
			if is_qr: msg += '.qr'
	return msg

def goo_gl_qr(type, jid, nick, text): send_msg(type, jid, nick, goo_gl_raw(text, True))

def goo_gl(type, jid, nick, text): send_msg(type, jid, nick, goo_gl_raw(text, False))

global execute, message_control

message_act_control = [define_message]

execute = [(3, 'gcalc', gcalc, 2, L('Google Calculator')),
	(3, 'define', define, 2, L('Definition for a word or phrase.\ndefine word - random define of word or phrase\ndefine N word - N-th define of word or phrase\ndefine a-b word - from a to b defines of word or phrase')),
	(3, 'ggl', goo_gl, 2, L('Google URL Shortener/Unshortener')),
	(3, 'qr', goo_gl_qr, 2, L('Google QR-code generator'))]
