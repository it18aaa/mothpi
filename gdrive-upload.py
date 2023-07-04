from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import requests


pending_file = "pending.txt"

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
files_list = set(line.strip() for line in open(pending_file))

uploaded_list = set()
files_uploaded = 0


#  for every file in the list,
#  test connection, check file exists, and then upload
#  if successful upload, add to list
#
for filename in files_list:
    print(filename)
    if connected():
        # TODO: refactor this into its own func?
        # uploads may be very slow, so perhaps update the pending.txt after every upload?
        #
        if os.path.isfile(filename):
            try:
                head_tail = os.path.split(filename)
                drive_file = drive.CreateFile({'title': head_tail[1]})
                drive_file.SetContentFile(filename)
                drive_file.Upload()
                #  this isn't ideal, need a better way to test
                uploaded_list.add(filename)
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




# Absorb any changes to the original file list
# create a left over list that wasn't uploaded!
#
# TODO: file locking to make this operation atomic
#
updated_files_list = set(line.strip() for line in open(pending_file))
all_files = files_list.union(updated_files_list)
left_over_files  = all_files.difference(uploaded_list)

pending = open(pending_file, "w")
for line in left_over_files:
    pending.write(f"{line}\n")

pending.close()

    
