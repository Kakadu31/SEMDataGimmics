'''
Created on 5 Jun 2022

@author: Sebastien
'''
#File to store helperfunctions
import os
import numpy as np

#Acces the session and then user folder inside the Atlas folder
def extendPath(path):
    with os.scandir(path) as folders:
        for folder in folders:
            #print(folder.name)
            if folder.name.startswith("session"):
                path = path + "\\" + folder.name + "\\User\\"
    return(path)

#Find the folder belonging to the regionNumber
def accesRegion(path, regionNumber):
    with os.scandir(path) as regions:
        for region in regions:
            if ("Region" + str(regionNumber) + "_") in region.name:
                path = path + region.name + "\\"
    return path
                
#Find the image inside the regions folder
def getImage (path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".tif"):
                return str(file)
            
#Function to create directory
def makeNewDir(parentDir, dirName):
    fullpath = os.path.join(parentDir, dirName)
    try:
        os.makedirs(fullpath)
        return fullpath
    except OSError:
        return fullpath
    
def makeImageName(path, prefix, iterator, suffix, image):
    newPath = path + "\\" + prefix + str(iterator) + suffix + os.path.splitext(image)[1]
    
    return newPath
    
def createReagionList(start, end):
    if (start < end):
        regionList = list(np.arange(start, end+1))
    else:
        regionList = list(np.arange(end, start+1))[::-1]
    return regionList