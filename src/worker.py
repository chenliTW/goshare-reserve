import time
import redis

import utils

r = redis.StrictRedis(host='192.168.100.200', port=6379, db=1,password="6ZSiu3JeTJ")

while True:
    if r.get('active')!=None and int(r.get('active'))==1:
        reserve_count = int(r.get('reserve_count'))
        if reserve_count >= 6:
            r.set('reserve_count',1)
            access_token,refresh_token=utils.refresh_token(r.get('refresh_token').decode())
            print("token refreshed: "+access_token)
            r.set('access_token',access_token)
            r.set('refresh_token',refresh_token)
        else:
            r.set('reserve_count',reserve_count+1)
        reserve_id = r.get('reserve_id').decode()
        utils.cancel_reserve(reserve_id,r.get('access_token').decode())
        print("cancel reserve: "+reserve_id)
        time.sleep(0.1)
        reserve_id=utils.reserve(r.get('scooter_id').decode(),r.get('access_token').decode())
        print("reserved: "+reserve_id)
        r.set('reserve_id',reserve_id)
    time.sleep(540)
