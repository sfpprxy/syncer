import requests
import urllib.request
from bs4 import BeautifulSoup


login_url = 'https://cumoodle.coventry.ac.uk/login/index.php'
user = {'username': 'cuiq4', 'password': 'Cucu.109'}

file_url = 'https://cumoodle.coventry.ac.uk/pluginfile.php/1159097/mod_resource/content/12/M19COM/Lectures/Overview_M19COM_2015_16.pdf'


s = requests.session()
s.post(login_url, data=user)


def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = s.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                # f.flush() commented by recommendation from J.F.Sebastian
    return local_filename


download_file(file_url)
