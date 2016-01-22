import random
import urllib.request

def download_web_image(url):
    image_name = random.randrange(1, 100)
    full_name = str(image_name) + ".pdf"
    urllib.request.urlretrieve(url, full_name)

download_web_image("https://cumoodle.coventry.ac.uk/pluginfile.php/1159097/mod_resource/content/10/M19COM/Lectures/Overview_M19COM_2014_15_Sem4.pdf")