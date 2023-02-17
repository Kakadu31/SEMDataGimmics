'''
Created on 17 Feb 2023

@author: Kakadu31
Extracts MetaData of all Zeiss SEM images in a certain folder and writes it in a textfile. Currcently programmed to get the orientation angle of the image. 
You can uncomment line 27 and 28 to get a list of all other tags and change the output accordingly in line 30-34.
You can enter the folder path if starting a console, or change the path manually in line 17.
'''
import exifread
import os
from tkinter import Tk
scanRotation = "0"

tm = Tk()
path = input("Type in folderpath: ")
if (path == ""):
    path = "E:\\myPath1\\myPath2\\"
tm.destroy()

text_file = open(path + "\\" + "scanRotations.txt", "w")
for filename in os.listdir(path):
    if ".tif" in filename:
        try:
            image = open(path + "\\" + filename, 'rb')
            tags = exifread.process_file(image)
            # Uncomment to get a list of all tags!
            for val in tags:
                print (val)
            semValueList = str((tags["Image Tag 0x8546"]).values).split("\\r\\")
            #Info: The Scan Rotation is nested in the Tag 0x8546!
            for semValue in semValueList:
                if ("Scan Rotation = ") in semValue:
                    print (semValue);
                    scanRotation = semValue.split("=")[1][1:-5]
                    #print (scanRotation)
            #Adjusts the formation to a useful output.
            text_file.write (filename[:-4] + "\t" + scanRotation + "\n")
            image.close()
        except:
            print("No metadata found.")
text_file.close()
