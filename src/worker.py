import time
import redis
import types

import utils

retry_time = 3

r = redis.StrictRedis(host='192.168.100.200', port=6379, db=1,password="6ZSiu3JeTJ")

def decorate_all_in_module(module, decorator):
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, types.FunctionType):
            setattr(module, name, decorator(obj))

def retry(func):
    def wrap(*args, **kwargs):
        for t in range(retry_time):
            try:
                return func(*args, **kwargs)
            except:
                print(f"[-] {func.__name__} failed at {t+1} try, retrying !!!!")
                if t==retry_time-1:
                    print(f"[-] {func.__name__} failed {retry_time} tries,give up!!!!")
                    r.set('active',0)
                time.sleep(3)
                continue
    return wrap

decorate_all_in_module(utils, retry)

while True:
    if r.get('active')!=None and int(r.get('active'))==1:
        reserve_count = int(r.get('reserve_count'))
        if reserve_count >= 6:
            r.set('reserve_count',1)
            access_token,refresh_token=utils.refresh_token(r.get('refresh_token').decode())
            print("token refreshed: "+str(access_token))
            r.set('access_token',access_token)
            r.set('refresh_token',refresh_token)
        else:
            r.set('reserve_count',reserve_count+1)
        reserve_id = r.get('reserve_id').decode()
        utils.cancel_reserve(reserve_id,r.get('access_token').decode())
        print("cancel reserve: "+str(reserve_id))
        time.sleep(0.1)
        reserve_id=utils.reserve(r.get('scooter_id').decode(),r.get('access_token').decode())
        print("reserved: "+str(reserve_id))
        r.set('reserve_id',reserve_id)
    time.sleep(540)
