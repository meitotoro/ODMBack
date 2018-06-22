import io
import os
import zipfile

def zipData():
    filePath="/home/odm/opendrone-qt/openDroneMap/backCode/images"
    name="1-2018.06.12"
    zip_path = os.path.join("/home/odm/opendrone-qt/openDroneMap/backCode", name+".zip")
    source_path="/home/odm/opendrone-qt/openDroneMap/backCode/images/1-2018.06.12/odm_orthophoto/"
    zipf = zipfile.ZipFile(zip_path, 'w')
    pre_len = len(os.path.dirname(source_path))
    for parent, dirnames, filenames in os.walk(source_path):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
            zipf.write(pathfile, arcname)       
    stream = io.open(zip_path, 'rb')
    stream_len = os.path.getsize(zip_path) 

    return stream, stream_len

if __name__=="__main__":
    zipData()