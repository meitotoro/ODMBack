import docker
import subprocess

def stop():
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
    else:
        print("no docker shells")

    


if __name__=="__main__":
    stop()
