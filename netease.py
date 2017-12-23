#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from Crypto.Cipher import AES
import binascii
import json
from hashlib import md5
import re
import requests
import sys
import urllib

def netease_encrypt(body):
    BLOCK_SIZE = 16
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    body = json.dumps(body)
    raw = pad(body)
    cipher = AES.new('\x72\x46\x67\x42\x26\x68\x23\x25\x32\x3F\x5E\x65\x44\x67\x3A\x51', AES.MODE_ECB)
    return {'eparams' : binascii.hexlify(cipher.encrypt(raw)).upper()}
    

def download_playlist(playlist):
    print("retriving playlist...")
    r = requests.get(playlist)
    arr = r.json()['result']['tracks']
    ids = []
    names = {}
    print("enumerating tracks...")
    for i in range(len(arr)):
        name = str(i + 1) + ' ' + arr[i]['name'] + '.mp3'
        songid = arr[i]['id']
        names[str(songid)] = arr[i]['name']
        ids.append(songid)
    print("%d tracks found..." % (len(ids)))
    print("encrypting messages...")
    post = netease_encrypt({'method' : 'POST', 'params' : {'ids' : ids, 'br' : 320000}, 'url' : 'http://music.163.com/api/song/enhance/player/url'})
    print("forwarding messages to netease...")
    songs = requests.post('http://music.163.com/api/linux/forward', post)
    songs = songs.json()['data']
    print("obtaining download URLs...")
    for song in songs:
        url = song['url']
        name = names[str(song['id'])] + '.mp3'
        urllib.request.urlretrieve(url, name)
        print("- completed: %s" % (name))


if __name__ == "__main__":
    playlist_regex = re.compile('^(?:\d+)$')
    playlist = None
    if len(sys.argv) == 2:
        playlist = sys.argv[1].strip()
    else:
        playlist = input("Please type the id of the netease playlist:\n").strip()
    while not playlist_regex.match(playlist):
        playlist = input("Wrong URL, please type the id of the netease playlist:\n").strip()
    
    download_playlist("http://music.163.com/api/playlist/detail?id=%s" % (playlist))
    