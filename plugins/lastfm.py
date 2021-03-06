#!/usr/bin/python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------- #
#                                                                             #
#    Plugin for iSida Jabber Bot                                              #
#    Copyright (C) 2011 diSabler <dsy@dsy.name>                               #
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

global execute, lf_api, lfm_url, timer

lfm_url = 'http://ws.audioscrobbler.com/2.0/'

def last_check_ascii(type, jid, nick, text):
	for tmp in text:
		if tmp > '~' or tmp < ' ':
			send_msg(type, jid, nick, L('Error!'))
			return True
	return None

def last_time_short(tm):
	tm = time.localtime(tm)
	tnow = time.localtime()
	if tm[0] != tnow[0]: form = '%d.%m.%Y %H:%M'
	elif tm[1]!=tnow[1] or tm[2]!=tnow[2]: form = '%d.%m %H:%M'
	else: form = '%H:%M'
	return str(time.strftime(form,tm))

def last_date_now(body):
	if 'nowplaying=\"true\"' in body: return 'now'
	else:
		try: return last_time_short(int(get_subtag(get_tag_full(body,'date'),'uts')))
		except: return 'Unknown'

def lastonetrack(type, jid, nick, text):
	if last_check_ascii(type, jid, nick, text): return
	ms = lf_api('user.getrecenttracks',text, '<track')
	if len(ms): cnt = len(ms)
	else: cnt = 0
	if cnt >=2: msg = L('Last track %s: %s - %s %s') % (text,get_tag(ms[1],'artist'),get_tag(ms[1],'name'),'['+last_date_now(ms[1])+']')
	else: msg = L('Unavailable!')
	send_msg(type, jid, nick, msg)

def lf_api(method, user, splitter):
	user = reduce_spaces_all(user.lower().encode('utf-8').replace('\\x','%')).replace(' ','%20')
	link = '%s?method=%s&user=%s&api_key=%s' % (lfm_url,method,user,GT('lfm_api'))
	return rss_replace(html_encode(load_page(link))).split(splitter)

def lasttracks(type, jid, nick, text):
	if last_check_ascii(type, jid, nick, text): return
	text = reduce_spaces_all(text).split(' ')
	try: cnt = int(text[1])
	except: cnt = GT('lastfm_max_limit')
	cnt += 1
	text = text[0]
	ms = lf_api('user.getrecenttracks',text, '<track')
	if cnt > len(ms): cnt = len(ms)
	msg = L('Last tracks %s:') % text
	for a in ms[1:cnt]: msg += '\n['+last_date_now(a)+'] '+get_tag(a,'artist')+' - '+get_tag(a,'name')
	send_msg(type, jid, nick, msg)

def lastfriends(type, jid, nick, text):
	if last_check_ascii(type, jid, nick, text): return
	ms = lf_api('user.getfriends',text, '<user')
	msg = L('Loved tracks %s:') % text
	for a in ms[1:]:
		msg += ' ' + get_tag(a,'name')+' ('+get_tag(a,'realname')+'),'
	msg = msg[:-1]
	send_msg(type, jid, nick, msg)

def lastloved(type, jid, nick, text):
	if last_check_ascii(type, jid, nick, text): return
	text = reduce_spaces_all(text).split(' ')
	try: cnt = int(text[1])
	except: cnt = GT('lastfm_max_limit')
	cnt += 1
	text = text[0]
	ms = lf_api('user.getlovedtracks',text, '<track')
	if cnt > len(ms): cnt = len(ms)
	msg = L('Loved tracks %s:') % text
	for a in ms[1:cnt]: msg += '\n['+last_date_now(a)+'] '+get_tag(a.split('<artist')[1],'name')+' - '+get_tag(a,'name')
	send_msg(type, jid, nick, msg)

def lastneighbours(type, jid, nick, text):
	if last_check_ascii(type, jid, nick, text): return
	text = reduce_spaces_all(text).split(' ')
	try: cnt = int(text[1])
	except: cnt = GT('lastfm_max_limit')
	cnt += 1
	text = text[0]
	ms = lf_api('user.getneighbours',text, '<user')
	if cnt > len(ms): cnt = len(ms)
	msg = L('Neighbours %s:') % text
	for a in ms[1:cnt]: msg += '\n'+get_tag(a,'match')+' - '+get_tag(a,'name')
	send_msg(type, jid, nick, msg)

def lastplaylist(type, jid, nick, text):
	if last_check_ascii(type, jid, nick, text): return
	text = reduce_spaces_all(text).split(' ')
	try: cnt = int(text[1])
	except: cnt = GT('lastfm_max_limit')
	cnt += 2
	text = text[0]
	ms = lf_api('user.getplaylists',text, '<playlist')
	if cnt > len(ms): cnt = len(ms)
	msg = L('Playlists %s:') % text
	for a in ms[2:cnt]: msg += '\n['+get_tag(a,'id')+'] '+get_tag(a,'title')+' ('+get_tag(a,'description')+') - '+get_tag(a,'size')+' - '+get_tag(a,'duration')
	send_msg(type, jid, nick, msg)

def topalbums(type, jid, nick, text):
	if last_check_ascii(type, jid, nick, text): return
	text = reduce_spaces_all(text).split(' ')
	try: cnt = int(text[1])
	except: cnt = GT('lastfm_max_limit')
	cnt += 1
	text = text[0]
	ms = lf_api('user.gettopalbums',text, '<album')
	if cnt > len(ms): cnt = len(ms)
	msg = L('Top albums %s:') % text
	for a in ms[1:cnt]: msg += '\n['+get_tag(a,'playcount')+'] '+get_tag(a.split('<artist')[1],'name')+' - '+get_tag(a,'name')
	send_msg(type, jid, nick, msg)

def topartists(type, jid, nick, text):
	if last_check_ascii(type, jid, nick, text): return
	text = reduce_spaces_all(text).split(' ')
	try: cnt = int(text[1])
	except: cnt = GT('lastfm_max_limit')
	cnt += 1
	text = text[0]
	ms = lf_api('user.gettopartists',text, '<artist')
	if cnt > len(ms): cnt = len(ms)
	msg = L('Top artists %s:') % text
	for a in ms[1:cnt]: msg += '\n['+get_tag(a,'playcount')+'] '+get_tag(a,'name')
	send_msg(type, jid, nick, msg)

def toptags(type, jid, nick, text):
	if last_check_ascii(type, jid, nick, text): return
	text = reduce_spaces_all(text).split(' ')
	try: cnt = int(text[1])
	except: cnt = GT('lastfm_max_limit')
	cnt += 1
	text = text[0]
	ms = lf_api('user.gettoptags',text, '<tag')
	if cnt > len(ms): cnt = len(ms)
	msg = L('Top tags %s:') % text
	for a in ms[1:cnt]: msg += '\n['+get_tag(a,'count')+'] '+get_tag(a,'name')+' - '+get_tag(a,'url')
	send_msg(type, jid, nick, msg)

def toptracks(type, jid, nick, text):
	if last_check_ascii(type, jid, nick, text): return
	text = reduce_spaces_all(text).split(' ')
	try: cnt = int(text[1])
	except: cnt = GT('lastfm_max_limit')
	cnt += 1
	text = text[0]
	ms = lf_api('user.gettoptracks',text, '<track')
	if cnt > len(ms): cnt = len(ms)
	msg = L('Top tracks %s:') % text
	for a in ms[1:cnt]:
		b = a.split('<artist')
		msg += '\n['+get_tag(a,'playcount')+'] '+get_tag(b[1],'name')+' - '+get_tag(a,'name')
	send_msg(type, jid, nick, msg)

def tasteometer(type, jid, nick, text):
	if last_check_ascii(type, jid, nick, text): return
	text = reduce_spaces_all(text.lower().encode('utf-8').replace('\\x','%')).split(' ',1)
	try: (user1,user2) = text
	except:
		send_msg(type, jid, nick, L('Need two users'))
		return
	link = '%s?method=tasteometer.compare&type1=user&type2=user&value1=%s&value2=%s&api_key=%s' % (lfm_url,user1,user2,GT('lfm_api'))
	lfxml = html_encode(load_page(link))
	scor = get_tag(lfxml,'score')
	try: scor = float(scor)
	except: scor = 0
	if scor <= 0: msg = L('Tastes of %s and %s - soo different!') % (user1,user2)
	else:
		msg,msg2 = L('Match tastes of %s and %s - %s') % (user1,user2,str(int(scor*100))+'%'),''
		lfxml = lfxml.split('<artist')
		cnt = len(lfxml)
		for a in lfxml[2:cnt]: msg2 += get_tag(a,'name')+', '
		if len(msg2): msg += '\n'+L('Artists: %s') % msg2[:-2]
	send_msg(type, jid, nick, msg)

def no_api(type, jid, nick): send_msg(type, jid, nick, L('Not found LastFM api'))

exec_yes = [(3, 'lasttracks', lasttracks, 2, L('Last scrobled tracks')),
		(3, 'last', lastonetrack, 2, L('Last scrobled track')),
		(3, 'lastfriends', lastfriends, 2, L('Last friends')),
		(3, 'lastloved', lastloved, 2, L('Last loved tracks')),
		(3, 'lastneighbours', lastneighbours, 2, L('Last neighbours')),
		(3, 'lastplaylist', lastplaylist, 2, L('Last playlist')),
		(3, 'topalbums', topalbums, 2, L('Top albums')),
		(3, 'topartists', topartists, 2, L('Top artists')),
		(3, 'toptags', toptags, 2, L('Top tags')),
		(3, 'toptracks', toptracks, 2, L('Top tracks')),
		(3, 'tasteometer', tasteometer, 2, L('Music tastes'))]

exec_no = [(3, 'lasttracks', no_api, 1, L('Not found LastFM api')),
	   (3, 'last', no_api, 1, L('Not found LastFM api')),
	   (3, 'lastfriends', no_api, 1, L('Not found LastFM api')),
	   (3, 'lastloved', no_api, 1, L('Not found LastFM api')),
	   (3, 'lastneighbours', no_api, 1, L('Not found LastFM api')),
	   (3, 'lastplaylist', no_api, 1, L('Not found LastFM api')),
	   (3, 'topalbums', no_api, 1, L('Not found LastFM api')),
	   (3, 'topartists', no_api, 1, L('Not found LastFM api')),
	   (3, 'toptags', no_api, 1, L('Not found LastFM api')),
	   (3, 'toptracks', no_api, 1, L('Not found LastFM api')),
	   (3, 'tasteometer', no_api, 1, L('Not found LastFM api'))]

execute = [exec_no,exec_yes][len(GT('lfm_api')) >= 30]

