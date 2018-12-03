#!/usr/bin/env python
# coding:utf-8
# Author:Yang


'''rpc server'''
import pika
import socket
import os

class RPC_Server(object):
    def __init__(self):
        self.credentials = pika.PlainCredentials('yang123', '960314')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.29', 5672, '/', self.credentials))
        self.channel=self.connection.channel()
        self.channel.queue_declare(queue='rpc_queue')


    def excute_cmd(self,cmd):

        try:
            result=os.popen(cmd).read()
            return result
        except Exception as e:
            return"cmd is not exist"

    def on_request(self,ch,method,props,body):
        cmd_receive=body.decode()
        cmd_dict=eval(cmd_receive)
        cmd=cmd_dict['cmd']
        host=cmd_dict['host']
        myhost=self.get_host_ip()
        if myhost in host:
            response=self.excute_cmd(cmd)

            ch.basic_publish(
                exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(
                    correlation_id=props.correlation_id,
                ),
                body=response
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)



    def get_host_ip(self): # 获取本机ip
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip


rpc_server=RPC_Server()
rpc_server.channel.basic_consume(rpc_server.on_request,queue='rpc_queue')
rpc_server.channel.start_consuming()

