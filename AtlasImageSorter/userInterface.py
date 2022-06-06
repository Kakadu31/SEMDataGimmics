'''
Created on 5 Jun 2022

@author: Sebastien
'''
import tkinter as tk
import numpy as np
import shutil, os 
from PIL import Image
from functions import extendPath, accesRegion, getImage, makeNewDir, createReagionList, makeImageName
from tkinter import filedialog

path = ""

def changeDirectory():
    # get a directory
    filepath=filedialog.askdirectory(initialdir=r"F:\python\pythonProject",
                                    title="Dialog box")
    entryPath.delete(0, "end")
    entryPath.insert(0, filepath)

def makeCollage():
    rows = int(spinboxY.get())
    columns = int(spinboxX.get())
    targetDir = os.path.join(entryPath.get(), entryNewDir.get())
    lpaths = []
    lImgs = []
    valid_images = [".jpg",".gif",".png",".tif"]
    collageRows = []
    # Get all pictures from the directory and write them in a list
    for f in os.listdir(targetDir):
        ext = os.path.splitext(f)[1]
        if ext.lower() not in valid_images:
            continue
        elif "Collage" in os.path.splitext(f)[0]:
            continue
        lpaths.append(f)
        lpaths.sort()
    for p in lpaths:
        lImgs.append(Image.open(os.path.join(targetDir, p)))
    # Divide the list into rows and columns
    lArrayImgs = [lImgs[i:i+columns] for i in range(0, len(lImgs), columns)]
    # Create horizontal row image(array)-stripes from the rows
    for i in range(rows):
            print(i)
            collageRows.append(np.hstack( (np.asarray( image ) for image in lArrayImgs[i] ) ))
    #Create vertical image collage from the previous generated stripes
    collage = np.vstack( (np.asarray( row ) for row in collageRows ) )
    #Convert array to image and save it
    collageDone = Image.fromarray(collage)
    collageDone.save(os.path.join(targetDir, "Collage"+str(columns)+"x"+str(rows)+".tif"))
    print ("done")

def startExport():
    #Set Variables
    path = entryPath.get()
    newDirName = entryNewDir.get()
    
    startRegion = int(entryRegionStart.get())
    stopRegion = int(entryRegionEnd.get())
    regionList = createReagionList(startRegion, stopRegion)
    
    spinboxX.delete(0, "end")
    spinboxX.insert(0, abs(stopRegion-startRegion))
    
    prefix = entryPrefix.get()
    iteratorStart = entryIterator.get()
    if iteratorStart.isnumeric():
        iteratortype = "number"
        iterator = int(iteratorStart)
    elif iteratorStart.isalpha():
        iteratortype = "alphabet"
        iterator = iteratorStart
    else:
        iteratortype = "unknown"
    suffix = entrySuffix.get()
    
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
    

#main window
root = tk.Tk()
root.columnconfigure(0, minsize=250)
root.rowconfigure([0, 1, 2, 3], minsize=100)

root.title("Atlas Image Sorter")

#create elements
frameTop = tk.Frame(
    master=root,  
    bg="#3e6385",
    width=100,
    )
labelTop = tk.Label(
    master=frameTop,
    text="Sort your Atlas images from many regions into one folder.",
    fg="white",
    bg="#3e6385",
    width=60,
    height=4
)

frameMain = tk.Frame(
    master=root, 
    bg="#3e6385"
    )
#Path elements
labelPath = tk.Label(
    master=frameMain,
    text=" Enter path:",
    fg="white",
    bg="#3e6385",
    #width=25,
    height=1
)
entryPath = tk.Entry(
    master=frameMain,
    fg="black",
    bg="white",
    width=50
)
entryPath.insert(0, "Enter the path to the Atlas folder.")
buttonDirectory = tk.Button(
    master=frameMain,
    command=changeDirectory,
    text="Search",
    fg="white",
    bg="#0056bc",
    width=5,
    #height=1
)

#New folder elements
labelNewDir = tk.Label(
    master=frameMain,
    text=" Enter name of new folder:",
    fg="white",
    bg="#3e6385",
    #width=25,
    height=1
)
entryNewDir = tk.Entry(
    master=frameMain,
    fg="black",
    bg="white",
    width=50
)
entryNewDir.insert(0, "Images")

#Region range
labelRegions = tk.Label(
    master=frameMain,
    text=" Region-range (from _ to _):  ",
    fg="white",
    bg="#3e6385",
    #width=30,
    height=1
)
entryRegionStart = tk.Entry(
    master=frameMain,
    fg="black",
    bg="white",
    width=10
)
entryRegionStart.insert(0, "1")
entryRegionEnd = tk.Entry(
    master=frameMain,
    fg="black",
    bg="white",
    width=10
)

#Empty labels as spacer
frameName = tk.Frame(
    master=root, 
    bg="#3e6385",
    height=20
    )
labelSpacer = tk.Label(
    master=frameMain,
    text="",
    bg="#3e6385",
    height=2
)

labelSpacer2 = tk.Label(
    master=frameName,
    text="",
    bg="#3e6385",
    height=2
)


#Image naming
labelPrefix = tk.Label(
    master=frameName,
    text="Prefix of image names",
    fg="white",
    bg="#3e6385",
    #width=25,
    #height=3
)
labelIterator = tk.Label(
    master=frameName,
    text="Starting Iterator (ex. 1 or a)",
    fg="white",
    bg="#3e6385",
    #width=25,
    #height=3
)
labelSuffix = tk.Label(
    master=frameName,
    text="Suffix of image names",
    fg="white",
    bg="#3e6385",
    #width=25,
    #height=3
)

entryPrefix = tk.Entry(
    master=frameName,
    fg="black",
    bg="white",
    width=30
)
entryIterator = tk.Entry(
    master=frameName,
    fg="black",
    bg="white",
    width=5
)
entryIterator.insert(0, 1)
entrySuffix = tk.Entry(
    master=frameName,
    fg="black",
    bg="white",
    width=30
)

#Button elements
frameStart = tk.Frame(
    master=root,  
    bg="#3e6385"
    )
buttonStart = tk.Button(
    master=frameStart,
    command=startExport,
    text="Export",
    fg="white",
    bg="#0056bc",
    width=50,
    height=2
)
buttonCollage = tk.Button(
    master=frameStart,
    command=makeCollage,
    text="Collage",
    fg="white",
    bg="#0056cd",
    width=10,
    height=2
)
spinboxX = tk.Spinbox(
    master=frameStart,
    from_=0,
    to=10,
    width=2
    )
spinboxY = tk.Spinbox(
    master=frameStart,
    from_=0,
    to=10,
    width=2
    )

# Top elements
frameTop.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
labelTop.grid(row=0, column=0, sticky = "w")

# Main elements
frameMain.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
labelPath.grid(row=0, column=0, sticky = "nw")
entryPath.grid(row=0, column=1, sticky = "nw")
buttonDirectory.grid(row=0, column=2, sticky = "nw")
labelNewDir.grid(row=1, column=0, sticky = "nw")
entryNewDir.grid(row=1, column=1, sticky = "nw")
labelRegions.grid(row=2, column=0, sticky = "nw")
entryRegionStart.grid(row=2, column=1, sticky = "nw")
entryRegionEnd.grid(row=2, column=1, sticky = "n")


labelSpacer.grid(row=2, column=0, sticky = "nw")

# Naming elements
frameName.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
labelPrefix.grid(row=0, column=0, sticky = "s")
labelIterator.grid(row=0, column=1, sticky = "s")
labelSuffix.grid(row=0, column=2, sticky = "s")
entryPrefix.grid(row=1, column=0, sticky = "s")
entryIterator.grid(row=1, column=1, sticky = "s")
entrySuffix.grid(row=1, column=2, sticky = "s")

labelSpacer2.grid(row=2, column=0, sticky = "nw")

# Start button
spinboxY.pack(side = tk.RIGHT)
spinboxX.pack(side = tk.RIGHT)
buttonCollage.pack(side = tk.RIGHT)
buttonStart.pack()
#buttonCollage.pack(side = tk.RIGHT)
frameStart.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
#buttonStart.bind("<Button-1>", startExport)
root.mainloop()

