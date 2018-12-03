#!/usr/bin/env python
# coding:utf-8
# Author:Yang

'''rpc client'''

import pika
import random
import re
import json

class RPC_Client(object):
    def __init__(self):
        self.credentials = pika.PlainCredentials('yang123', '960314') # 输入rabbitmq 用户名密码（guest用户只能在本地访问）
        self.connection=pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1',5672,'/',self.credentials)) # 创建连接实例（mq的ip，端口号，虚拟主机，plain）
        self.channel=self.connection.channel()
        cmd_result=self.channel.queue_declare(exclusive=True)  #  server端执行完的结果 用一个随机生成的queue接收（就是callback_queue）
        self.callback_queue=cmd_result.method.queue
        self.channel.basic_consume(self.on_response,
                                   queue=self.callback_queue)

    def on_response(self,ch,method,props,body):# 回调函数
        if self.corr_id==props.correlation_id:   # 如果client端生成的随机id与server端返回的随机id一致 则将返回的消息赋给body
            self.response=body

    def call(self,cmd):
        self.response=None
        self.corr_id=self.create_corr_id()
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',  # 发送数据的时候使用rpc_queue
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,  # props里制定了server端执行完要返回结果通过的queue为上面随机生成的queue
                                       correlation_id=self.corr_id, # 带上生成的随机id为参数
                                   ),
                                   body=cmd
        )
        while self.response is None:
            self.connection.process_data_events()  # 这句是死循环接受server返回的信息，没有结果不用一直等待，是表示使用非阻塞式的connection.start_consuming
        return self.response.decode(),self.corr_id



    def create_corr_id(self): # 生成随机task id
        j=6
        id=[]
        id=''.join(str(i) for i in random.sample(range(0,9),j))
        return id


if __name__=='__main__':
    host=[]
    host_already=['192.168.1.1','192.168.1.2','192.168.1.3','192.168.1.29']
    id_response={}
    while True:
        rpc_client=RPC_Client()
        cmd_string=input(">>:")
        if cmd_string in id_response.keys(): # 判断输入的是任务id还是命令字符串
            print(id_response[cmd_string])
        else:

            cmd=re.compile(r'\"(.*?)\"').findall(cmd_string)[0] # 正则过滤出远程主机ip
            host_string=cmd_string.split("\"")[2].split()
            for i in range(len(host_string)):
                if i>0:
                    if host_string[i] in host_already:
                       host.append(host_string[i])
                    else:
                        print("remote host:%s is not exist.."%host_string[i])
            cmd_dict={'cmd':cmd,'host':host}
            response=rpc_client.call(str(cmd_dict))[0]
            corr_id=rpc_client.call(str(cmd_dict))[1]
            print("task id :",corr_id)
            id_response[corr_id]=response
