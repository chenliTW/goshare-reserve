import time

f=open('/src/check','r')
t=int(f.read())
f.close()

if int(time.time())-t>15:
    exit(1)
