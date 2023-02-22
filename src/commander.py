from flask import Flask,render_template,request
import redis
import pprint

import utils

r = redis.StrictRedis(host='redis-master.default.svc.cluster.local', port=6379, db=1,password="ER4LZLToVi")
#r.set('foo', 'bar')
#print(r.get('foo'))

app = Flask(__name__)

def get_data():
    try:
        data={
            'tel_num':r.get('tel_num'),
            'code_challenger':r.get('code_challenger'),
            'verify_code':r.get('verify_code'),
            'access_token':"..."+r.get('access_token')[-50:].decode(),
            'refresh_token':"..."+r.get('refresh_token')[-50:].decode(),
            'plate_number':r.get('plate_number'),
            'scooter_id':r.get('scooter_id'),
            'reserve_id':r.get('reserve_id'),
            'reserve_count':r.get('reserve_count'),
            'active':r.get('active')
        }
    except:
        data={}
        pass

    return pprint.pformat(data,sort_dicts=False)

@app.route('/')
def index():
    return render_template('index.html',data=get_data())

@app.route('/tel')
def tel():
    tel_num = request.args.get('tel_num')
    r.set('tel_num',tel_num)
    code_challenger=utils.request_verify_code(tel_num)
    r.set('code_challenger',code_challenger)
    return render_template('index.html',data=get_data())

@app.route('/verify')
def verify():
    verify_code = request.args.get('verify_code')
    r.set('verify_code',verify_code)
    tel_num = r.get('tel_num').decode()
    code_challenger = r.get('code_challenger').decode()
    access_token,refresh_token=utils.submit_verify_code(tel_num,code_challenger,verify_code)
    r.set('access_token',access_token)
    r.set('refresh_token',refresh_token)
    return render_template('index.html',data=get_data())

@app.route('/plate')
def plate():
    plate_number = request.args.get('plate_number')
    access_token = r.get('access_token').decode()
    scooter_id = utils.get_scooter_id(plate_number)
    r.set('plate_number',plate_number)
    r.set('scooter_id',scooter_id)
    reserve_id=utils.reserve(scooter_id,access_token)
    r.set('reserve_id',reserve_id)
    r.set('reserve_count',1)
    r.set('active',1)
    return render_template('index.html',data=get_data())

@app.route('/cancel')
def cancel():
    utils.cancel_reserve(r.get('reserve_id').decode(),r.get('access_token').decode())
    r.set('reserve_id','')
    r.set('reserve_count',0)
    r.set('active',0)
    r.set('plate_number','')
    return render_template('index.html',data=get_data())

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80)
