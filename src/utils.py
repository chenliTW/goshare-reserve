import requests
import json
import time
from string import ascii_letters,digits
import random
from base64 import b64encode
from hashlib import sha256
from os import urandom

def request_verify_code(phone_number):
    
    random.seed(urandom(8))

    h=sha256()
    code_verifier=''.join([ random.choice(ascii_letters+digits) for _ in range(43)])
    h.update(code_verifier.encode())
    code_challenge=b64encode(h.digest()).decode().replace("=","").replace("+","-").replace("/","_")

    header={
        "Content-Type":"application/json",
        "User-Agent": "okhttp/3.12.1",
    }

    data={
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "username": "+886"+phone_number[1:]
    }

    requests.post("https://auth.ridegoshareapi.com/v1/sms_code",data=json.dumps(data),headers=header)

    return code_verifier

def submit_verify_code(phone_number,code_verifier,sms_code):

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

    print(data)

    access_token=data["access_token"]
    refresh_token=data['refresh_token']

    return access_token,refresh_token

def get_scooter_id(plate):
    res=requests.get("https://rental.ridegoshareapi.com/v2/cities/514f2d1d-9faf-490b-b9b2-fe8ce4dce584/scooters")
    for scooter in res.json()['upsert_lst']:
        if scooter['plate']==plate:
            return scooter["id"]
    return None

def reserve(scooter_id,access_token):

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

    return data["id"]

def cancel_reserve(reserve_id,access_token):

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

    #assert res.json()['id']==reserve_id
    #assert res.json()['state']==4

def refresh_token(refresh_token):

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

    access_token=data["access_token"]
    refresh_token=data['refresh_token']

    return access_token,refresh_token