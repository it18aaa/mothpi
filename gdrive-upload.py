from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import requests

###  function to test internet connection
#
def connected() -> bool:
    url = "http://www.google.com"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False
    
if not connected():
    print("No internet")
    quit()
else:
    print("Internet okay")

print("proceeding with upload list")

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

#load list of pending uploads
files_list = set(line.strip() for line in open('pending.txt'))

new_files_list = files_list.copy()
files_uploaded = 0


#  for every file in the list, test connection, check file exists, upload!
# then remove that filename from the set of pending uploads

for filename in files_list:
    print(filename)
    if connected():
        if os.path.isfile(filename):
            try:
                drive_file = drive.CreateFile({'title': filename})
                drive_file.SetContentFile(filename)
                drive_file.Upload()
                new_files_list.remove(filename)
                files_uploaded += 1
            except Exception as ex:
                print(f"couldn't upload {filename}")
                print(str(ex))
            finally:
                drive_file.content.close()
                
        else:
            print(f"{filename} not found")
    else:
        print("not connected")
        
print(f"{files_uploaded} files uploaded")

# write the set of pending uploads
#
pending = open("pending.txt", "w")
for line in new_files_list:
    f.write(f"{line}\n")

    
