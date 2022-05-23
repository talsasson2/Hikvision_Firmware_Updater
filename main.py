import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib import request
from zipfile import ZipFile


xml_remove_character = '{http://www.hikvision.com/ver20/XMLSchema}'


class Device:
    def __init__(self):
        print('Enter Hikvision Device IP:')
        self.hik_ip = input()

        print('Enter Admin Password:')
        self.hik_password = input()

    def get_info(self, info):
        r = requests.get('http://' + self.hik_ip + '/ISAPI/System/deviceInfo', auth=('admin', self.hik_password))
        tree = ET.ElementTree(ET.fromstring(r.content))
        root = tree.getroot()
        for child in root:
            tag_new = child.tag.replace(xml_remove_character, '')
            if tag_new == info:
                return child.text


def get_link(camera_model):
    vgm_url = 'https://www.hikvision.com/en/support/download/firmware/'
    html_text = requests.get(vgm_url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    found_file = False

    for link in soup.find_all('a'):
        if "DS-" in link.text:
            if ".pdf" not in link.text:
                if camera_model in link.text:
                    found_file = True
        if link.get('data-link') is None:
            continue
        if ".pdf" in link.get('data-link'):
            continue
        if found_file:
            return link.get('data-link')
            found_file = False


def upgrade():
    print('\n')
    print('Start Upgrading...')
    with open('digicap.dav', 'rb') as finput:
        response = requests.put('http://' + p.hik_ip + '/ISAPI/System/updateFirmware', data=finput.read(), auth=('admin',p.hik_password))
        if response.status_code == 200:
            print('Upgrade Complete!')
            print('\n')
            print("Sending Reboot Command...")
            reboot = requests.put('http://' + p.hik_ip + '/ISAPI/System/reboot', auth=('admin', p.hik_password))
            if reboot.status_code == 200:
                print('Reboot Complete!')
                print('\n')
                print('Good Bye!')
            else:
                print('Reboot Failed!')
                print('\n')
                print('Try Again, Good Bye!')

        else:
            print('Upgrade Failed!')
            print('Try Again, Good Bye!')

p = Device()
try:
    print('is your model is ' + p.get_info('model') + '? (type: [1]yes / [2]no)')
    yes_no = input()
    if yes_no == 'yes' or yes_no == '1':
        print('\n')

        print("Searching Firmwares...")
        if get_link(p.get_info('model')) is None:
            print("Search Complete!")
            print('\n')
            print("No Upgrade Found")

        else:
            print("Search Complete!")
            if ".zip" in get_link(p.get_info('model')):
                local_file = 'firmware.zip'
                print('\n')
                print("Start Downloading...")
                request.urlretrieve(get_link(p.get_info('model')), local_file)
                print("Download Complete!")
                print('\n')

                with ZipFile('firmware.zip', 'r') as zip:
                    print("Start Extracting...")
                    zip.extractall()
                    print('Extracting Complete!')
                    print('\n')

                    print('Are You Ready For Upgrade? (type: [1]yes /[2] no)')
                    yes_no = input()
                    if yes_no == 'yes' or yes_no == '1':
                        upgrade()

            if ".dav" in get_link(p.get_info('model')):
                local_file = 'firmware.dav'
                request.urlretrieve(get_link(p.get_info('model')), local_file)
                print('Are You Ready For Upgrade? (type: [1]yes /[2] no)')
                yes_no = input()
                if yes_no == 'yes' or yes_no == '1':
                    upgrade()

    else:
        print('\n')
        print('An exception occurred')

except:
    print('\n')
    print("An exception occurred... please try again")

