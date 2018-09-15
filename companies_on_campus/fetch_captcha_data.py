import requests
import json
import time
import sys
# import socks
import socket
from cairosvg import svg2png
from matplotlib import pyplot as plt
import numpy as np
from bs4 import BeautifulSoup



def dump_to_file(arr,  fout):
    np.savetxt(fout,arr)
    
def save_to_png(data, name):
    svg2png(bytestring=data,write_to=name)

def read_img(name):
    return plt.imread(name)

def save_as_grayscale(image, name):
    image[...,3]=1
    image[np.where(image[...,0]>0)]=1
    plt.imsave(name,image[...,0],cmap=plt.cm.gray)

def split_chars(data):
    soup = BeautifulSoup(data, 'html.parser')
    paths=[]
    svgs=[]
    for i in range(6):
        a=soup.find('path').extract()
        if(not a.get('fill')=='none'):
            paths.append(a)
    for path in paths:
        outer_tag = BeautifulSoup(str(soup), 'html.parser').find('svg').extract()
        outer_tag.insert(1,path)
        svgs.append(str(outer_tag))
    
    return svgs

def fetch_captcha(captcha_url, headers):
    global global_counter
    
    response = requests.get(captcha_url, headers=headers, verify=False)
    data = response.json()["captcha"]
    
    svgs=split_chars(data)
    captcha_data = []
    for i in range(len(svgs)):
        data=svgs[i]
        save_to_png(data, temp_image_name)
        
        image = read_img(temp_image_name)
        save_as_grayscale(image, str(global_counter)+".png")
        global_counter+=1
        image = read_img(temp_image_name)
        image[np.where(image[...,0]>0)]=1
        
        captcha_data.append(image[...,0].flatten())
        
    return captcha_data

    

if __name__=='__main__':

    global_counter = 0
    temp_image_name = "temp.png"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    train_data = "train_data.csv"
    
    captcha_data = []
    
    for i in range(100):
        captcha_data += fetch_captcha("https://tnp.iitd.ac.in/api/captcha", headers)
        time.sleep(1)
    np.savetxt("captcha_data.csv",captcha_data,delimiter=",",fmt="%i")
    
    
    