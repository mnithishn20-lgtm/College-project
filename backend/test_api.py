import urllib.request, json, sys

def call_get(path):
    url = f'http://127.0.0.1:5000{path}'
    try:
        with urllib.request.urlopen(url, timeout=5) as res:
            print(path, res.getcode())
            print(res.read().decode())
    except Exception as e:
        print(path, 'ERROR', e)


def call_post(path, payload):
    url = f'http://127.0.0.1:5000{path}'
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req, timeout=5) as res:
            print(path, res.getcode())
            print(res.read().decode())
    except Exception as e:
        print(path, 'ERROR', e)

if __name__ == '__main__':
    call_get('/health')
    call_post('/predict', {'mathematics':90,'physics':95,'chemistry':95,'community':'OC','stream':'ENGINEERING'})
    call_post('/chat', {'message':'Tell me about cutoff calculations'})
    call_get('/colleges')
    call_get('/colleges/districts')
