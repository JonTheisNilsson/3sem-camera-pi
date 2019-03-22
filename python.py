# script for raspberry pi with camera to take picture every 15 minute, upload it to dropbox
# and send shared link to rest webservice. Zibat 3. semester Computer Science
#
# build upon example from dropbox
# Jon Theis Nilsson

import sys
import time
import requests
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from picamera import PiCamera

# Add OAuth2 access token here.
# You can generate one for yourself in the App Console.
# See <https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/>
TOKEN = 'zcZd9um6pSAAAAAAAAAABjaZN3e3590O3JlftulYkAXPo3tOJgfcxz3reU9lR_ek'

url = 'http://camerarestservice.azurewebsites.net/Service1.svc/images/'
LOCALFILE = 'picture.png'
backuppath = ''
folder = '3SemExam3dPrintercamRest'
name = 'picture'
extension = '.png'
counter = 0 #should be saved somewhere or it resets everytime the program is restarted.

camera = PiCamera()
camera.resolution = (1280,720)

# Uploads contents of LOCALFILE to Dropbox
def backup():

    update_filename()
    with open(LOCALFILE, 'rb') as f:
        # We use WriteMode=overwrite to make sure that the settings in the file
        # are changed on upload
        print("Uploading " + LOCALFILE + " to Dropbox as " + backuppath + "...")
        try:
            dbx.files_upload(f.read(), backuppath, mode=WriteMode('overwrite'))
        except ApiError as err:
            # This checks for the specific error where a user doesn't have
            # enough Dropbox space quota to upload this file
            if (err.error.is_path() and
                    err.error.get_path().error.is_insufficient_space()):
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                print(err.user_message_text)
                sys.exit()
            else:
                print(err)
                sys.exit()

def update_filename():
    global backuppath
    global counter

    counter = counter + 1
    # todo change hardcoding to variable
    backuppath = '/3SemExam3dPrintercamRest/' + name + str(counter) + extension

def take_picture():
    # maybe disable preview since headless. Affect picture?
    try:
        camera.start_preview()
        time.sleep(5)
        camera.capture('picture.png')
    finally:
        camera.stop_preview()
    
def get_images(): #for testing
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ApiError('GET /tasks/ {}'.format(resp.status_code))
    for item in resp.json():
        print('{} {}'.format(item['Datetime'], item['Link']))

def post_image_link(link):
    resp = requests.post(url, json=link)
    print("Status code: " + str(resp.status_code))

if __name__ == '__main__':
    while(True):
        print("Creating a Dropbox object...")
        dbx = dropbox.Dropbox(TOKEN)

        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
        except AuthError as err:
            sys.exit("ERROR: Invalid access token; try re-generating an "
            "access token from the app console on the web.")
        
        take_picture()
        
        # Create a backup of the current settings file
        backup()

        print("Done!")
        result = dbx.files_get_temporary_link(backuppath)
        print(result.link)
        post_image_link(str(result.link))

        time.sleep(900) #seconds. 900 is 15 min
