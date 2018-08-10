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
containers={}
filePath="/home/odm/opendrone-qt/openDroneMap/backCode"
dir={}
logPath={}
client = docker.from_env()
before_time=datetime.datetime.now()


class execute_command(object):
    def on_get(self, req, resp):        
        folder=req.get_param('folder')
        runDocker(folder)
        global filePath
        image_path = os.path.join(filePath, "images", folder)
        logPath[folder]=os.path.join(image_path,"log.txt")
        
        resp.body = "docker run"

def runDocker(folder):
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
    dir[folder] =folder
    print(dir[folder])
    #dir="111"
    image_path = os.path.join(filePath, "images", dir[folder])
    print(image_path)
    outpath_orthophoto=image_path+"/odm_orthophoto"
    print(outpath_orthophoto)
    outpath_texturing=image_path+"/odm_texturing" 
    if os.path.exists(outpath_orthophoto): 
        cmd_String ="docker run --rm -v "+outpath_orthophoto+"/:/target/ removefile"
        print(cmd_String)
        return_code = subprocess.call(cmd_String, shell=True)  
        cmd_String ="docker run --rm -v "+outpath_texturing+"/:/target/ removefile"
        return_code = subprocess.call(cmd_String, shell=True)
        print(return_code)         
    
    print(image_path) 
   # cmd_string ="unbuffer docker run -i --rm --name "+folder+" -v "+ image_path+":/code/images -v "+ outpath_orthophoto+":/code/odm_orthophoto -v "+outpath_texturing+":/code/odm_texturing opendronemap/opendronemap"
    volumes_string={image_path:{"bind":"/code/images","mode":"rw"},outpath_orthophoto:{"bind":"/code/odm_orthophoto","mode":"rw"}, outpath_texturing:{"bind":"/code/odm_texturing","mode":"rw"}}
  #  print(cmd_string)
    global stdout
    
    containers[folder]=client.containers.run(image="opendronemap/opendronemap",name=folder,auto_remove=True,detach=True,volumes=volumes_string)
    
    #since_time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))
    #stdout[folder]=containers[folder].logs(since=2)

        
    #print(container.logs())
    """  
    if shell:
        cmdstring_list = cmd_String
    else:
        cmdstring_list = lshlex.split(cmd_String.encode('utf-8'))
    if timeout:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout) """
    
    #没有指定标准输出和错误输出的管道，因此会打印到屏幕上；
    
    #sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE,shell=shell,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=4096)
    #stdout[folder]=sub.stdout


        

class docker_command(object):
    def on_get(self,req,resp):
        folderName =req.get_param("folder")
        command=req.get_param("command")
        imagesPath=os.path.join("images", folderName)
        print(imagesPath)
        global client
        try:
            container=client.containers.get(folderName)
            print(container)
            if command=="stop":
                print("stop docker")
                try:
                    container.stop()
                    resp.body="docker stopped"
                except docker.errors.APIError:
                    print("docker"+folderName+"stop failed")
                    resp.body=""
            elif command=="pause":
                print("pause docker")
                try:
                    container.pause()
                    resp.body="docker paused"
                except:
                    print("docker"+folderName+"pause failed")
                    resp.body=""
            elif command=="restart":
                print("docker restart")
                try:
                    container.restart()
                    stdout[folder]=container.logs()
                    resp.body="docker restart"
                except:
                    print("docker"+folderName+"restart failed")
                    resp.body=""
        except:
            runDocker(folderName)


class get_orthmap(object):
    def on_get(self,req,resp):
        folder=req.get_param('folder')
        print(filePath)
        print(dir[folder])
        image_path = os.path.join(filePath, "images", dir[folder])
        outpath_orthophoto=image_path+"/odm_orthophoto"
        output_path=os.path.join(filePath,"zips",dir[folder]+".zip")
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
        print path+u' 创建成功'
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print path+u' 目录已存在'
        return False
 
class get_progress(object):
    def on_get(self,req,resp):
        folderName =req.get_param("folder")
        global before_time
        now_time=datetime.datetime.now()
        print(now_time)
        seconds=(now_time-before_time).seconds
        print(seconds)
        stdout=containers[folderName].logs(since=seconds)
        before_time=now_time
        print(stdout)
        global logPath
        log_file=open(logPath[folderName],"a")
        log_file.write(stdout)    
        if(stdout.find(u"OpenDroneMap app finished")==-1):
            resp.body=stdout
        else:
            log_file.close()
            resp.body="OpenDroneMap app finished"




class transfor_map(object):
    def on_post(self, req, resp):
        """Handles GET requests"""
        #页面传过来文件夹名字和文件名字
        folderName =unicode(req.get_param('folder'))
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

class delete_image(object):
    def on_get(self,req,resp):
        folderName =req.get_param('folder')
        path=os.path.join("images", folderName)
        for root,dirs,files in os.walk(path):#（使用 os.walk ,这个方法返回的是一个三元tupple(dirpath(string), dirnames(list), filenames(list)), 其中第一个为起始路径， 第二个为起始路径下的文件夹, 第三个是起始路径下的文件.）
            for name in files:
                if '.JPG' in name:#判断某一字符串是否具有某一字串，可以使用in语句
                    os.remove(os.path.join(root,name))##os.move语句为删除文件语句
                    print('Delete files:',os.path.join(root,name))           
        resp.body="all images deleted"

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
api.add_route('/delteImage',delete_image())
api.add_route('/transformap', transfor_map())
api.add_route('/docker', execute_command())
api.add_route('/dockerCommand', docker_command())
api.add_route('/progress',get_progress())
api.add_route('/orthomap',get_orthmap())
api.add_route('/httpTest',http_test())
api.add_route('/error',error400())
