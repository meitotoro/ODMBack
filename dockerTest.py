import docker
import subprocess
from threading import Timer
import time

def Rundocker():
    
    image_path = "/home/odm/opendrone-qt/openDroneMap/backCode/test2/"
    print(image_path)
    outpath_orthophoto=image_path+"/odm_orthophoto"
    print(outpath_orthophoto)
    outpath_texturing=image_path+"/odm_texturing" 
   # cmd_string ="unbuffer docker run -i --rm --name "+folder+" -v "+ image_path+":/code/images -v "+ outpath_orthophoto+":/code/odm_orthophoto -v "+outpath_texturing+":/code/odm_texturing opendronemap/opendronemap"
    volumes_string={image_path:{"bind":"/code/images","mode":"rw"},outpath_orthophoto:{"bind":"/code/odm_orthophoto","mode":"rw"}, outpath_texturing:{"bind":"/code/odm_texturing","mode":"rw"}}
    print(volumes_string)
  #  print(cmd_string)
    global stdout
    client=docker.from_env()
    container=client.containers.run(image="opendronemap/opendronemap",name="2018-8-10",auto_remove=True,detach=True,volumes=volumes_string)
    stdout=container.logs(since=)


    


if __name__=="__main__":
    Rundocker()