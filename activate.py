from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

filename = 'activate.txt'
gauth = GoogleAuth()
drive = GoogleDrive(gauth)
drive_file = drive.CreateFile({'title': filename})
drive_file.SetContentFile(filename)
drive_file.Upload()

                              
