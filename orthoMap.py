# -*- coding:utf-8 -*-
import falcon
from falcon_cors import CORS
import numpy as np
import os
import logging
import commands
import shlex
import datetime
import subprocess
import time
import os

public_cors = CORS(allow_all_origins=True)
address=""

class execute_command(object):
    def on_get(self, req, resp):
        """执行一个SHELL命令
        封装了subprocess的Popen方法, 支持超时判断，支持读取stdout和stderr
        参数:
        cwd: 运行命令时更改路径，如果被设定，子进程会直接先更改当前路径到cwd
        timeout: 超时时间，秒，支持小数，精度0.1秒
        shell: 是否通过shell运行
        Returns: return_code
        Raises: Exception: 执行超时
        """
        shell=False
        timeout=None
        cwd=None
        dir =req.get_param('addr')
        filePath=os.path.join("/home/odm/opendrone-qt/openDroneMap/backCode/images", dir)
        print(filePath)
        outpath_orthophoto=filePath+"/odm_orthophoto"
        outpath_texturing=filePath+"/odm_texturing"    
        cmd_String = "unbuffer docker run -i --rm -v "+ filePath+":/code/images -v "+ outpath_orthophoto+":/code/odm_orthophoto -v "+outpath_texturing+":/code/odm_texturing opendronemap/opendronemap"
        if shell:
            cmdstring_list = cmd_String
        else:
            cmdstring_list = shlex.split(cmd_String)
        if timeout:
            end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    
        #没有指定标准输出和错误输出的管道，因此会打印到屏幕上；
        sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE,shell=shell,bufsize=4096)
        
        #subprocess.poll()方法：检查子进程是否结束了，如果结束了，设定并返回码，放在subprocess.returncode变量中 
        while sub.poll() is None:
            time.sleep(0.1)
            if timeout:
                if end_time <= datetime.datetime.now():
                    raise Exception("Timeout：%s"%cmdstring)
        print(sub.returncode)
        resp.data=str(sub.returncode)

def mkdir(path):  
 
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
 
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)
 
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        print path+' 创建成功'
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print path+' 目录已存在'
        return False
 


class transfor_map(object):
    def on_post(self, req, resp):
        """Handles GET requests"""
        str_time=time.strftime("%Y-%M-%D")
        #os.mkdir("./123")
        print(str_time)
        #页面传过来站点名称或者经纬度信息
        address =req.get_param('addr')
        fileName=req.get_param('name')
        print(address,fileName)
        # 定义要创建的目录
        filePath=os.path.join("images", address)
        print(filePath)
        # 调用函数
        mkdir(filePath)
        #mkdir("\\home\\odm\\opendrone-qt\\openDroneMap\\images\\")
        data=req.stream.read()
        dst = open(os.path.join(filePath, fileName),"w")
        print(dst)
        dst.write(data)
        dst.close()
        resp.body=fileName
        
        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
        
def server_error(ex, req, resp, params):
    logging.exception(ex)
    raise falcon.HTTPInternalServerError(description=str(ex))

api = falcon.API(middleware=[public_cors.middleware])
api.add_error_handler(Exception, server_error)
api.add_route('/transformap', transfor_map())
api.add_route('/docker', execute_command())