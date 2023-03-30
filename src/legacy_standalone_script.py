import requests
import json
import time
from string import ascii_letters,digits
import random
from base64 import b64encode
from hashlib import sha256
from os import urandom

retry_time=100

access_token=""
refresh_token=""

def retry(func):
    def wrap(*args, **kwargs):
        for t in range(retry_time):
            try:
                return func(*args, **kwargs)
            except:
                print(f"[-] {func.__name__} failed at {t+1} try, retrying !!!!")
                if t==retry_time-1:
                    print(f"[-] {func.__name__} failed {retry_time} tries,give up!!!!")
                    exit(0)
                time.sleep(3)
                continue
    return wrap

def login():
    global access_token,refresh_token

    random.seed(urandom(8))

    h=sha256()
    code_verifier=''.join([ random.choice(ascii_letters+digits) for _ in range(43)])
    h.update(code_verifier.encode())
    code_challenge=b64encode(h.digest()).decode().replace("=","").replace("+","-").replace("/","_")

    phone_number=input("enter phone number: ")

    header={
        "Content-Type":"application/json",
        "User-Agent": "okhttp/3.12.1",
    }

    data={
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "username": "+886"+phone_number[1:]
    }

    res=requests.post("https://auth.ridegoshareapi.com/v1/sms_code",data=json.dumps(data),headers=header)

    print(res.text)

    sms_code=input("verify code: ")

    header={
        "User-Agent": "okhttp/3.12.1",
        "Authorization":"Basic NTFlZmVkNjktYjQ0MC00N2Q3LThhNTMtMmEzY2ViZTY1YzkyOg=="
    }

    data={
        "grant_type":"sms",
        "username":"+886"+phone_number[1:],
        "uuid":"54ed48f9-9f9e-4162-8542-2ed8f35ebb50",
        "sms_code":sms_code,
        "code_verifier":code_verifier
    }

    res=requests.post("https://auth.ridegoshareapi.com/oauth/token",data=data,headers=header)

    data=res.json()

    access_token=data["access_token"]
    refresh_token=data['refresh_token']

    print("[*] login success")

@retry
def do_refresh_token():
    global access_token,refresh_token

    header={
        "User-Agent": "okhttp/3.12.1",
        "Authorization":"Basic NTFlZmVkNjktYjQ0MC00N2Q3LThhNTMtMmEzY2ViZTY1YzkyOg=="
    }

    data={
        "grant_type":"refresh_token",
        "uuid":"54ed48f9-9f9e-4162-8542-2ed8f35ebb50",
        "refresh_token":refresh_token
    }

    res=requests.post("https://auth.ridegoshareapi.com/oauth/token",data=data,headers=header)

    data=res.json()

    print(data)

    access_token=data["access_token"]
    refresh_token=data['refresh_token']

    print("\n[!] token refresh")


def get_scooter_id(plate):
    res=requests.get("https://rental.ridegoshareapi.com/v2/cities/514f2d1d-9faf-490b-b9b2-fe8ce4dce584/scooters")
    for scooter in res.json()['upsert_lst']:
        if scooter['plate']==plate:
            return scooter["id"]
    print("[-] plate not found, Exiting")
    exit(0)

@retry
def reserve(scooter_id):

    data={
        "corporate_type": 0,
        "scooter_id": scooter_id,
        "source": 0
    }

    header={
        "User-Agent": "okhttp/3.12.1",
        "Authorization":f"Bearer {access_token}",
        "Content-Type":"application/json"
    }

    res=requests.post("https://rental.ridegoshareapi.com/v2.1/rentals",data=json.dumps(data),headers=header)

    data=res.json()
    print("\n[+] reserved")
    print(data)

    return data["id"]

@retry
def cancel_reserve(reserve_id):

    data={
        "action": 0,
        "payment_method": 0
    }

    header={
        "User-Agent": "okhttp/3.12.1",
        "Authorization":f"Bearer {access_token}",
        "Content-Type":"application/json"
    }

    res=requests.patch(f"https://rental.ridegoshareapi.com/v2.1/rentals/{reserve_id}",data=json.dumps(data),headers=header)
    print("\n[-] reserve canceled")
    print(res.json())

    assert res.json()['id']==reserve_id
    assert res.json()['state']==4


login()
scooter_plate=input("enter scooter_plate: ")
scooter_id=get_scooter_id(scooter_plate)

cnt=0

while True:
    reserve_id=reserve(scooter_id)
    cnt+=1
    if cnt>=6:
        cnt=1
        do_refresh_token()
    time.sleep(540)
    cancel_reserve(reserve_id)
    time.sleep(0.1)
