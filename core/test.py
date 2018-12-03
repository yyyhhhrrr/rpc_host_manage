#!/usr/bin/env python
# coding:utf-8
# Author:Yang

import re

a='run "df -h" --hosts 192.168.3.55 10.4.3.4 '

str_pat=re.compile(r'\"(.*?)\"')
print(str_pat.findall(a)[0])
b=a.split("\"")[2].split()
print(b)
for i in range(len(b)):
    if i >0:
        print(b[i])

j=2
if j in [1,2]:
    print(1)

e=[1,2]
d={'a':a,'list':e}
c=str(d)
print(type(str(d)))
print(type(eval(c)))


f={"a":1,"b":2}
if "a" in f.keys():
   print(1)