# -*- coding:utf-8 -*-
import numpy as np
import os
import logging
import commands
import shlex
import datetime
import subprocess
import time
import os
from subprocess import Popen, PIPE
from time import sleep
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read
import zipfile
import io
from time import ctime,sleep
import shutil
import docker
import falcon
from falcon_cors import CORS
import sys,stat


public_cors = CORS(allow_all_origins=True)
address=""
stdout=None
filePath="/home/odm/opendrone-qt/openDroneMap/backCode"
dir=""


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
        global dir
        dir =req.get_param('folder')
        #dir="111"
        print(filePath)
        image_path = os.path.join(filePath, "images", dir)
        print(image_path)
        outpath_orthophoto=image_path+"/odm_orthophoto"
        outpath_texturing=image_path+"/odm_texturing"  
        
        cmd_String = "unbuffer docker run -i --rm -v "+ image_path+":/code/images -v "+ outpath_orthophoto+":/code/odm_orthophoto -v "+outpath_texturing+":/code/odm_texturing opendronemap/opendronemap"
        if shell:
            cmdstring_list = cmd_String
        else:
            cmdstring_list = shlex.split(cmd_String)
        if timeout:
            end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        logPath=os.path.join(image_path,"log.txt")
        log_file=open(logPath,"w+")
        #没有指定标准输出和错误输出的管道，因此会打印到屏幕上；
        global stdout
        sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE,shell=shell,stdout=subprocess.PIPE,stderr=log_file,bufsize=4096)
        stdout=sub.stdout
        resp.body = "docker run"
        
       
        

        #subprocess.poll()方法：检查子进程是否结束了，如果结束了，设定并返回码，放在subprocess.returncode变量中 

        '''
        while sub.poll() is None:
            if timeout:
                if end_time <= datetime.datetime.now():
                    raise Exception("Timeout：%s"%cmdstring)
        '''
        
        #print(sub.returncode)

        

class stop_docker(object):
    def on_get(self,req,resp):
        folderName =req.get_param("folder")
        imagesPath=os.path.join("images", folderName)
        print(imagesPath)
        client = docker.from_env()
        print(client.containers.list())
        containers=client.containers.list()
        if len(containers):
            for container in client.containers.list():
                id=container.short_id
                print(id)
                cmd_String = "docker stop "+id
                return_code = subprocess.call(cmd_String, shell=True)  
                print(return_code)                
                resp.body="docker stopped"
        else:
            print("no docker shells")
            resp.body="no docker shells"            
        if os.path.exists(imagesPath): 
            global filePath
            image_path = os.path.join(filePath,imagesPath)
            print(image_path)
            outpath_orthophoto=image_path+"/odm_orthophoto"
            outpath_texturing=image_path+"/odm_texturing" 
            os.chown(outpath_orthophoto, 1000, 1000)
            os.chmod(outpath_orthophoto,stat.S_IRWXO) 
            os.chmod(outpath_texturing,stat.S_IRWXO)         
            shutil.rmtree(filePath) 
            print(123)


class get_orthmap(object):
    def on_get(self,req,resp):
        print(filePath)
        print(dir)
        image_path = os.path.join(filePath, "images", dir)
        outpath_orthophoto=image_path+"/odm_orthophoto"
        output_path=os.path.join(filePath,"zips",dir+".zip")
        resp.stream, resp.stream_len=zipData(outpath_orthophoto,output_path)
        #resp.data=str(sub.returncode)


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
 
class get_progress(object):
    def on_get(self,req,resp):
        #每次取五行传回去   
        global stdout 
        # set the O_NONBLOCK flag of p.stdout file descriptor:
        print(stdout)
       # if stdout is not None:
        flags = fcntl(stdout, F_GETFL) # get current p.stdout flags
        fcntl(stdout, F_SETFL, flags | O_NONBLOCK)
        time.sleep(0.1)
        try:
            result=read(stdout.fileno(),1024)
            if(result.find(u"OpenDroneMap app finished")==-1):
                resp.body=result
            else:
                print(result)
                resp.body="OpenDroneMap app finished"
            print (resp.body)
        except OSError:
            print '[No more data]'
            resp.body=""
        """  
        else:
            resp.body = u'输入的图片量太少'
            resp.status = falcon.HTTP_400
            raise falcon.HTTPBadRequest(title=u"输入错误：", description=u"图片量太少，请重新输入") 
        """



class transfor_map(object):
    def on_post(self, req, resp):
        """Handles GET requests"""
        #页面传过来文件夹名字和文件名字
        folderName =req.get_param('folder')
        fileName=req.get_param('name')
        print(folderName,fileName)
        # 定义要创建的目录
        filePath=os.path.join("images", folderName)
        print(filePath)
       # 调用函数
        mkdir(filePath)
        #mkdir("\\home\\odm\\opendrone-qt\\openDroneMap\\images\\")
        #try:
        data=req.stream.read()
        with open(os.path.join(filePath, fileName),"w",buffering=0) as dst:
            dst.write(data)
            print(dst)
            #将文件名返回给页面
            resp.body=fileName
            #except Exception as e:
                #raise falcon.HTTPError(falcon.HTTP_400, 'Error', e.message)

        
       

class http_test(object):
    def on_get(self,req,resp):
        try:
            resp.body="http connect successfully"
        except Exception as e:
            raise falcon.HTTPError(falcon.HTTP_500, 'Error', e.message)        
       
        
        
def zipData(input_path,output_path):
    zip_path = output_path
    source_path=input_path
    zipf = zipfile.ZipFile(zip_path, 'w')
    pre_len = len(os.path.dirname(source_path))
    for parent, dirnames, filenames in os.walk(source_path):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
            zipf.write(pathfile, arcname)       
    stream = io.open(zip_path, 'rb')
    stream_len = os.path.getsize(zip_path) 
    print(stream_len)
    return stream, stream_len                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
        
""" def server_error(ex, req, resp, params):
    logging.exception(ex)
    raise falcon.HTTPInternalServerError(description=str(ex))
 """

class error400(object):
    def on_get(self,req,resp):
        resp.status=falcon.HTTP_400
        resp.body = 'Bad Request'
        raise falcon.HTTPBadRequest(title=u"Input Error", description=u"图片太少")



api = falcon.API(middleware=[public_cors.middleware])
#api.add_error_handler(Exception, server_error)
api.add_route('/transformap', transfor_map())
api.add_route('/docker', execute_command())
api.add_route('/stopdocker', stop_docker())
api.add_route('/progress',get_progress())
api.add_route('/orthomap',get_orthmap())
api.add_route('/httpTest',http_test())
api.add_route('/error',error400())