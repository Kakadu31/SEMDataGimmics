'''
Created on 2 Jun 2022

@author: Kakadu31
'''
from functions import extendPath, accesRegion, getImage, makeNewDir, createReagionList, makeImageName
#from PIL import Image
import shutil, os

#Variables
path = "E:\CodingStuff\ZnO_Test_data" #Path to atlas folder
newDirName = "Images"

prefix = "l40f_f"
iteratortype = "alphabet"
suffix = "_muh"
if iteratortype == "number":
    iterator = 1
elif iteratortype == "alphabet":
    iterator = "a"
else:
    iterator = 0

startRegion = 4
stopRegion = 17
regionList = createReagionList(startRegion, stopRegion)
print(regionList)

#Create directory for images
newDir = makeNewDir(path, newDirName )

#Acces path to the images
extPath = extendPath(path)                  #Acces the session folder inside the Atlas folder
for region in regionList:
    try:
        regionPath = accesRegion(extPath, region)   #Acces the region folder inside the session folder
        imagePath = getImage(regionPath)            #Acces image inside the region folder
        shutil.copy2(os.path.join(regionPath, imagePath),makeImageName(newDir, prefix, iterator, suffix, imagePath))
        if iteratortype == "number":
            iterator += 1
        elif iteratortype == "alphabet":
            iterator = chr(ord(iterator) + 1)
        else:
            iterator += 1
        #im = Image.open(imagePath)
        #im.show()
    except:
        pass    # let exception propagate if we just can't