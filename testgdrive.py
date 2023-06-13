from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime
import socket

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

folder = '1oQYJ_aOY3MCzdMNNrJnt43SLuASKF19S'

now = datetime.now()
filename = socket.gethostname() + " - " + now.strftime("%Y%m%d - T%H:%M:%S") + ".txt"

file1 = drive.CreateFile({'parents': [{'id':folder}], 'title' : filename})
file1.SetContentString(now.strftime("%H:%M:%S") + ' This is another test file!')

file1.Upload()
