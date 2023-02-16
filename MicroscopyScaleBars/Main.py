'''
Created on 2 Mar 2020

@author: Sebastien
'''
#Suitable for lightt microscopes by changing the values in line 577
#Suitable for tescan, Jeol and Zeiss electorn microscope from the philipss university of marburg
#!/usr/bin/python
# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import Tk
from tkinter import filedialog
import cv2 as cv
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from statistics import stdev, mean
import os, glob, math, traceback, exifread

#opens the input machine
tm = Tk()

#Initialize GUI variables
tkinterOs = tk.StringVar()
tkinterDevice = tk.StringVar()
tkinterFFTToggle = tk.BooleanVar()
tkinterFolder_path = tk.StringVar()
tkinterHeight = tk.DoubleVar(tm, value='0.15')
tkinterWidth = tk.DoubleVar(tm, value='0.3')
tkinterScale = tk.DoubleVar(tm, value='0.02')
tkinterSERange = tk.DoubleVar(tm, value='2')
tkinterBSERange = tk.DoubleVar(tm, value='1.8')

tkinterOs.set("windows")
tkinterDevice.set("Tescan")
tkinterFFTToggle.set("True")

def ShowOsChoice():
    print (tkinterOs.get())

def ShowDeviceChoice():
    print (tkinterDevice.get())

def ShowFFTToggleChoice():
    print (tkinterFFTToggle.get())
    
def browse_button():
    global tkinterFolder_path
    filename = filedialog.askdirectory()
    tkinterFolder_path.set(filename)
    print(filename)
    
def startCode():
    print("Os:  " + tkinterOs.get())
    print("Device:  " + tkinterDevice.get())
    print("ScaleBox:  "  + "Height:  " + str(tkinterHeight.get()) + "   Width:   " + str(tkinterWidth.get()) + "   ScaleBar:   " + str(tkinterScale.get()))
    print("FFT:  " + str(tkinterFFTToggle.get()) + "   SERange:   " + str(tkinterSERange.get()) + "   BSERange:   " + str(tkinterBSERange.get()))
    print("Path:  " + str(tkinterFolder_path.get()))
    buttonStart.configure(bg = "gold")
    #--------------------------------
    #--------Things GUI changes------
    #--------------------------------
    osUsing = tkinterOs.get()     #Choose OS: mac, windows
    device = tkinterDevice.get()        #Chose device. Options: Zeiss, Jeol, Tescan, Light
    fileEnding = ".tif"     #Chose Default fileEnding
    fftWanted = tkinterFFTToggle.get()        #Choose if FFT Wanted.

    if (device == "Light"):
        fileEnding = ".jpg"
    fileEndingSave = ".png"

    #Dimensions of scale Box:
    scalaSizeH = tkinterHeight.get()       #Height in Percent of image
    scalaSizeW = tkinterWidth.get()        #Width in Percent of image
    scalaSizeHeight = tkinterScale.get()  #Scale Size in Percent of image
    acceptableScales = [100e-09,200e-09,500e-09,1e-06,2e-06,4e-06,5e-06,10e-06,20e-06,25e-06,50e-06,100e-06,200e-06] #List of all acceptable Scales to Choose from

    #Fine Tune FFT auto Detection Sensitivity for SEM or BSE image
    #SEFFTRange = tkinterSERange.get()
    #BSEFFTRange = tkinterBSERange.get()


    #chooses the Font: Arial
    if (osUsing == "mac"):
        FolderEnding =  "//"
        fontpath = "/Library/Fonts/Microsoft/arial.ttf" 
    elif (osUsing == "windows"):
        FolderEnding =  "\\"
        fontpath = "./arial.ttf" 
    else:
        print("Wrong OS")
        
    #Defines save Path
    saveFolderName = "Split" + FolderEnding
    saveFolderNameFFT = "FFT" + FolderEnding

    #--------------------------------

    #Demands Path input
    path = tkinterFolder_path.get() + FolderEnding
    if (path == FolderEnding):
        path = tm.clipboard_get() + FolderEnding

    #Creates array with all image names in the designated folder
    imageNames = [os.path.splitext(os.path.basename(image))[0] for image in glob.glob(path + "*" + fileEnding)]
    print (path)
    #Defines Offsets
    ySE = 0
    yBSE = 0
    xSE = 0

    #Crop values for scale bars etc (might change in next steps)
    if (device != "Zeiss"):
        hCrop = 0.86 #Percent
    else:
        hCrop = 1.0
    #fftBorderCrop = 0.0 #Percent
    #w = 1000
    flagSEAndBSE = True

    #Create new folders for FFT and Split images (split and/or with scale bars)
    #Creates log file
    if not os.path.exists(path + saveFolderName):
        os.mkdir(path + saveFolderName)
    if (not os.path.exists(path + saveFolderNameFFT)) and (fftWanted == True):
        os.mkdir(path + saveFolderNameFFT)
    log = open(path + saveFolderName +'log.txt', 'w+')
    if (fftWanted == True):
        freqLog = open(path + saveFolderNameFFT +'Freq.txt', 'w+')
        freqLog.write("Sample\t" + "Detector\t" + "Angle [deg]\t" + "Periodicity [units]\t" + "Deviation [units]\t" + "Units\t" + '\n')

    #Method to extract an FFT spectrum from an image
    def FFTImage(Oimage, log = True, modus = "SE"):
        planes = [np.float32(Oimage), np.zeros(Oimage.shape, np.float32)]
        complexI = cv.merge(planes)                         # Add to the expanded another plane with zeros
        cv.dft(complexI, complexI)                          # this way the result may fit in the source matrix
        cv.split(complexI, planes)                          # planes[0] = Re(DFT(I), planes[1] = Im(DFT(I))
        cv.magnitude(planes[0], planes[1], planes[0])       # planes[0] = magnitude
        magI = planes[0]

        matOfOnes = np.ones(magI.shape, dtype=magI.dtype)
        cv.add(matOfOnes, magI, magI)                  #  switch to logarithmic scale
        #cv.log(magI, magI)

        magI_rows, magI_cols = magI.shape[:2]
        # crop the spectrum, if it has an odd number of rows or columns
        magI = magI[0:(magI_rows & -2), 0:(magI_cols & -2)]
        cx = int(magI_rows/2)
        cy = int(magI_cols/2)
        
        q0 = magI[0:cx, 0:cy]                                   # Top-Left - Create a ROI per quadrant
        q1 = magI[cx:cx+cx, 0:cy]                               # Top-Right
        q2 = magI[0:cx, cy:cy+cy]                               # Bottom-Left
        q3 = magI[cx:cx+cx, cy:cy+cy]                           # Bottom-Right
        
        tmp = np.copy(q0)                                       # swap quadrants (Top-Left with Bottom-Right)
        magI[0:cx, 0:cy] = q3
        magI[cx:cx + cx, cy:cy + cy] = tmp
        tmp = np.copy(q1)                                       # swap quadrant (Top-Right with Bottom-Left)
        magI[cx:cx + cx, 0:cy] = q2
        magI[0:cx, cy:cy + cy] = tmp
        
        if (modus == "SE"):
            cv.normalize(magI, magI, 0, 300, cv.NORM_MINMAX)        # Transform the matrix with float values into a
        elif (modus == "BSE"):
            cv.normalize(magI, magI, 0, 100, cv.NORM_MINMAX)
        return (magI)

    #Method to check if 3 points are aligned
    def colinear(p1, p2, p3):       
        """ Calculation the area of   
            triangle. W e have skipped  
            multiplication with 0.5 to 
            avoid floating point computations """
        a = p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1]) 
      
        if (abs(a) < 1000): 
            #print ("Yes: " + str(a))
            return True
        else: 
            #print ("No: " + str(a))
            return False
        
    #Alternative Method to check if 3 points are aligned   
    def colinear2(p1, p2, p3):       
        a = ((p3[1] - p1[1])*(p2[0] - p1[0])) - ((p2[1] - p1[1])*(p3[0] - p1[0]))
      
        if ((abs(a) < 100) and ((p1[0]-p3[0])*(p1[0]-p3[0])) > 0): 
            #print ("Yes: " + str(a))
            return True
        else: 
            #print ("No: " + str(a))
            return False
        
    #Method to calculate the distance of 2 points in the spectrum
    def distance(p1, p2):
        return math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))

    #Method to calculate the angle of 2 points in the spectrum
    def angle (p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        dX = x2 - x1
        dY = y2 - y1
        rads = math.atan2 (-dY, dX) #wrong for finding angle/declination?
        deg = math.degrees (rads)
        #if (deg < 0):
        #    deg = deg + 180
        return deg

    #Method to extract and group frequencies in the FFT spectrum
    def frequencyDetection(image, modus = "SE", pixelSize = 1):
        #----------------------SE-Frequency Detection-------------------
        #SE_thresh = cv.adaptiveThreshold(SE_magI_UINT8,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY_INV,3,10)
        image_UINT8 = np.array(image * 255, dtype = np.uint8)
        image_UINT8 = cv.GaussianBlur(image_UINT8,(3,3),0)
        dist = cv.distanceTransform(image_UINT8, cv.DIST_L2, 3)
        cv.normalize(dist, dist, 0, 1.0, cv.NORM_MINMAX)
        if (modus == "SE"):
            _, dist = cv.threshold(dist, 0.4, 1.0, cv.THRESH_BINARY)
        elif (modus == "BSE"):
            _, dist = cv.threshold(dist, 0.4, 1.0, cv.THRESH_BINARY)
        # Dilate a bit the dist image
        kernel1 = np.ones((3,3), dtype=np.uint8)
        dist = cv.dilate(dist, kernel1)
        dist_8u = dist.astype('uint8')
        # Find total markers
        contours = cv.findContours(dist_8u, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        # Create the marker image for the watershed algorithm
        #markers = np.zeros(dist.shape, dtype=np.int32)
        dist = cv.cvtColor(dist, cv.COLOR_GRAY2BGR)
        #create a set of different contour items -> extract points of interest of the image
        cv.drawContours(dist, contours, -1, (255, 0, 0), 1)
        contours_poly = [None]*len(contours)
        boundRect = [None]*len(contours)
        boundRectW = [None]*len(contours)
        boundRectH = [None]*len(contours)
        centers = [None]*len(contours)
        for i, c in enumerate(contours):
            contours_poly[i] = cv.approxPolyDP(c, 3, True)
            boundRect[i] = cv.boundingRect(contours_poly[i])
            boundRectW [i] = boundRect [i][2]
            boundRectH [i] = boundRect [i][3]

        #Created to store standarderivations and means
        stdevWidth = stdev(boundRectW)
        stdevHeight = stdev(boundRectH)
        meanWidth = mean(boundRectW)
        meanHeight = mean(boundRectH)
        i = 0
        #Go trough each rectangle and store data
        for rectangle in boundRect:
            cv.rectangle(dist, (rectangle[0], rectangle[1]), (rectangle[0]+rectangle[2], rectangle[1]+rectangle[3]), (0, 0, 255), 1)
            centers[i] = (int(boundRect[i][0]+boundRect[i][2]/2), int(boundRect[i][1]+boundRect[i][3]/2))
            i = i + 1
        middle = ((dist.shape[1]/2), (dist.shape[0]/2))
        freqs = []

        i = 0
        #Make from the contour items boy items to better define aspect ratios, middle, etc..
        while i < (len(boundRect)):
            #print (boundRect[i][2])
            if (boundRect[i][2] > (meanWidth + 2*stdevWidth)) or (boundRect[i][3] > (meanHeight + 2*stdevHeight)):
                #print (boundRect[i][2])
                cv.rectangle(dist, (boundRect[i][0], boundRect[i][1]), (boundRect[i][0]+boundRect[i][2], boundRect[i][1]+boundRect[i][3]), (0, 255, 255), 1)
                boundRect.remove(boundRect[i])
                centers.remove(centers[i])
            elif abs(distance(centers[i], middle) < 1):
                boundRect.remove(boundRect[i])
                centers.remove(centers[i])
            else:
                i = i+1
        #For each rectangle combination, look if they are mathcing (colinear with middle)
        #for center1 in centers:
        #    for center2 in centers:
        #        if (center1 is not center2):
        #            if (colinear2(center1, center2, middle)):
        #                line = cv.line(dist, center1, center2, (255, 255, 255), 1)
        #                freqs.append([0, distance(center1, middle),angle(center1, center2)])
        stdevFreqs = [10000]
        stdevFreqsHighest = max(stdevFreqs)
        delta = 0.07
        marginFreq = 0.15     #Percent / 100
        deg = -180
        degPlus = 20
        while(stdevFreqsHighest > delta):
            if (degPlus <= 2):
                break
            #print (centers)
            #print("-------------")
            while deg < 180:
                k = 0
                while k < (len(centers)):
                    center = centers[k]
                    angleToMid = angle(center, middle)
                    if (angleToMid < 0):
                        angleToMid = angleToMid + 180
                    if (angleToMid < (deg + 3)):
                        freqs.append([deg, distance(center, middle),angleToMid])
                        #line = cv.line(dist, center, (int (middle[0]), int (middle[1])), (255, 255, 255), 1)
                        centers.remove(center)
                        k = k
                    else:
                        k = k + 1
                deg = deg + degPlus
                
            #Help function
            def getAngle(arg):
                return arg[2]
            
            #Sort the frequencies and group them to +- degRange
            freqs2 =  sorted(freqs.copy(), key=getAngle)
            
            freqGroups = []
            freqGroupsDeg = []
            group = []
            groupDeg = []
            groupCurrentDeg = freqs2[0][2]
            i = 0
            while i < (len(freqs2)):
                if (abs(freqs2[i][2]-groupCurrentDeg)<degPlus):
                    group.append(freqs2[i])
                    groupDeg.append(freqs2[i][1])
                else:
                    freqGroups.append(group)
                    freqGroupsDeg.append(groupDeg)
                    group = [freqs2[i]]
                    groupDeg = [freqs2[i][1]]
                groupCurrentDeg = freqs2[i][2]
                i = i + 1
            freqGroups.append(group)
            freqGroupsDeg.append(groupDeg)

            lowestInGroup = []
            for group in freqGroupsDeg:
                lowestInGroup.append(min(group))
                for i in range(len(group)):
                    if (group[i] > (1+marginFreq) * min(group)):
                        group[i] = (group[i] / (group[i] // min(group)))

            
            stdevFreqs = []
            #print (freqGroupsDeg)
            for group in freqGroupsDeg:
                if (len(group) == 1):
                    stdevFreqs.append(0)
                else:
                    stdevFreqs.append(stdev(group))
            meanFreqs = []
            #print (freqGroupsDeg)
            for group in freqGroupsDeg:
                if (len(group) == 1):
                    meanFreqs.append(group[0])
                else:
                    meanFreqs.append(mean(group))

                    
            stdevFreqsHighest = max(stdevFreqs)/meanFreqs[(stdevFreqs.index(max(stdevFreqs)))]
            degPlus = degPlus - 1
            #print (len(freqGroups))
            #print (freqGroups)
            #print (stdevFreqs)
            #print ("---------------")
        meanDistGroups = []
        meanDegGroups = []

        for group in freqGroups:
            deg = 0
            cnt = 0
            for i in range(len(group)):
                        deg = deg + group[i][2]
                        cnt = cnt + 1
            meanDegGroups.append(deg/cnt)
            
        for group in freqGroupsDeg:
            distancei = 0
            cnt = 0
            for i in range(len(group)):
                        distancei = distancei + group[i]
                        cnt = cnt + 1
            meanDistGroups.append(distancei/cnt)
        #print (meanDistGroups)
        #print (meanDegGroups)
        #print (stdevFreqs)
        #print ("DegreeRange: ")
        #print (degPlus)

        imgDistH, imgDistW = dist.shape[:2]
        for i in range(len(meanDistGroups)):
            stdevFreqs[i] = stdevFreqs[i]/meanDistGroups[i] #%
            
        units = []
        for i in range(len(meanDistGroups)):
            meanDistGroups[i] = imgDistH*pixelSize/(meanDistGroups[i])
            #print (meanDistGroups[i])
            if (meanDistGroups[i] < float(1e-06)):
                meanDistGroups[i] = meanDistGroups[i] * 10e+8
                units.append(" nm")
            elif(meanDistGroups[i] < float(1e-03)):
                meanDistGroups[i] = meanDistGroups[i] * 10e+5
                units.append(" \u03BC"+"m")

        for i in range(len(meanDistGroups)):
            stdevFreqs[i] = stdevFreqs[i]*meanDistGroups[i] #%

        font2 = ImageFont.truetype(fontpath, 20)
        dist = np.uint8(dist)
        img_pil2 = Image.fromarray(dist)
        draw = ImageDraw.Draw(img_pil2)
        #print (pixelSize)
        text = ""
        cnt = 0
        for i in range(len(meanDistGroups)):
            text = "Angle: " + str ('%.2f' % meanDegGroups[i]) + "deg : "  + " x: " + str ('%.3f' % meanDistGroups[i]) + units[i] + "  +-  "  + str ('%.5f' % stdevFreqs[i]) + units[i]
            draw.text(((int)(20),(int)(imgDistH-30-20*i)),  text, font = font2, fill = (255,255,255,1))
            cnt = i
            freqLog.write(imageName + "\t" + modus + "\t" + str ('%.2f' % meanDegGroups[i])+"\t" + str ('%.3f' % meanDistGroups[i]) + "\t" + str ('%.5f' % stdevFreqs[i])+"\t" + units[i] + "\t" + '\n')
        freqLog.write("\n")
        draw.text(((int)(20),(int)(imgDistH-60-20*cnt)),  ("Range: " + str(degPlus) + "deg"), font = font2, fill = (255,255,255,1))

        #draw axis
        draw.text(((int)(imgDistH-30),(int)(imgDistW/2)),  "0deg" , font = font2, fill = (100,100,100,1))
        draw.text(((int)(imgDistH/2+3),(int)(3)),  "90deg" , font = font2, fill = (100,100,100,1))
        dist = np.array(img_pil2)
        #vertikalLine = cv.line(dist, (int(imgDistH/2), 0), (int(imgDistH/2), imgDistW), (100, 100, 100), 1)
        #horizontalLine = cv.line(dist, (0, int(imgDistW/2)), (imgDistH,int(imgDistW/2)), (100, 100, 100), 1)
        return dist
        #cv.imshow('Freqs', SE_magI)
        #print (centers)
    #---------------------------------


    #For every image in the folder do:
    for imageName in imageNames:
        try:
            savePathSE = path + saveFolderName +  imageName +"_SE" + fileEndingSave
            savePathBSE = path + saveFolderName +  imageName +"_BSE" + fileEndingSave
            savePathSEFFT = path + saveFolderNameFFT +  imageName +"_SE_FFT" + fileEndingSave
            savePathBSEFFT = path + saveFolderNameFFT +  imageName +"_BSE_FFT" + fileEndingSave
            savePathSEFFT2 = path + saveFolderNameFFT +  imageName +"_SE_Freq" + fileEndingSave
            savePathBSEFFT2 = path + saveFolderNameFFT +  imageName +"_BSE_Freq" + fileEndingSave
            print(imageName)

            #Reset Pixelsize
            PixelSizeY = 0
            PixelSizeX = 0
            if (device == "Tescan"):
                try:
                    imageInfo = open(path + imageName +"-tif.hdr", "r")
                    imageInfoLines= imageInfo.readlines()
                    imageInfo.close()
                    PixelSizeY = float([s for s in imageInfoLines if "PixelSizeY" in s][0].strip("PixelSizeY="))
                    PixelSizeX = float([s for s in imageInfoLines if "PixelSizeX" in s][0].strip("PixelSizeX="))
                    log.write(imageName + ':Created Succesfully! \n')
                    #print(PixelSizeY)
                except FileNotFoundError:
                    if "_1k" in imageName:
                        PixelSizeY = 248.44e-9
                        PixelSizeX = 248.44e-9
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_2k" in imageName:
                        PixelSizeY = 124.22e-9
                        PixelSizeX = 124.22e-9
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_5k" in imageName:
                        PixelSizeY = 49.688e-9
                        PixelSizeX = 49.688e-9
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_10k" in imageName:
                        PixelSizeY = 24.844e-9
                        PixelSizeX = 24.844e-9
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_30k" in imageName:
                        PixelSizeY = 8.2813e-9
                        PixelSizeX = 8.2813e-9
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    else:
                        log.write(imageName + ':Could not extract Scale Value. \n')
                    #continue
                        
            elif (device == "Jeol"):
                try:
                    imageInfo = open(path + imageName +".txt", "r", encoding="ISO-8859-1",)
                    imageInfoLines = imageInfo.readlines()
                    imageInfo.close()
                    barPixel = float([s for s in imageInfoLines if "$$SM_MICRON_BAR" in s][0].strip("$$SM_MICRON_BAR "))
                    markerValue = [s for s in imageInfoLines if "$$SM_MICRON_MARKER" in s][0].strip("$$SM_MICRON_MARKER ")
                    markerValueVal = float(markerValue[:-3])
                    markerValueUnit = markerValue[-3:].strip()
                    if (markerValueUnit== "um"):
                        markerValueVal = markerValueVal * 1e-6

                    elif (markerValueUnit == "nm"):
                        markerValueVal = markerValueVal * 1e-9
                    PixelSizeY= markerValueVal/barPixel
                    PixelSizeX = PixelSizeY
                    log.write(imageName + ':Created Succesfully! \n')
                    print(PixelSizeY)
                    hCrop = 0.93
                    
                    #Percent
                except FileNotFoundError:
                    if "_1k" in imageName:
                        PixelSizeY = 9.433962264150943e-08
                        PixelSizeX = 9.433962264150943e-08
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_2k" in imageName:
                        PixelSizeY = 4.7169811320754715e-08
                        PixelSizeX = 4.7169811320754715e-08
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_3k" in imageName:
                        PixelSizeY = 3.125e-08
                        PixelSizeX = 3.125e-08
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_10k" in imageName:
                        PixelSizeY = 9.433962264150943e-09
                        PixelSizeX = 9.433962264150943e-09
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_30k" in imageName:
                        PixelSizeY = 3.1250000000000003e-09
                        PixelSizeX = 3.1250000000000003e-09
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_50k" in imageName:
                        PixelSizeY = 1.8867924528301888e-09
                        PixelSizeX = 1.8867924528301888e-09
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_100k" in imageName:
                        PixelSizeY = 9.433962264150944e-10
                        PixelSizeX = 9.433962264150944e-10
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_250k" in imageName:
                        PixelSizeY = 3.7735849056603775e-10
                        PixelSizeX = 3.7735849056603775e-10
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    elif "_300k" in imageName:
                        PixelSizeY = 3.125e-10
                        PixelSizeX = 3.125e-10
                        log.write(imageName + ':Scale was guessed by Name. \n')
                    else:
                        log.write(imageName + ':Could not extract Scale Value. \n')
                    hCrop = 0.93
                    #continue


            elif (device == "Zeiss"):
                try:
                    #imageInfo = open(path + imageName +".txt", "r", encoding="ISO-8859-1",)
                    #imageInfoLines = imageInfo.readlines()
                    #imageInfo.close()
                    #barPixel = float([s for s in imageInfoLines if "$$SM_MICRON_BAR" in s][0].strip("$$SM_MICRON_BAR "))
                    #markerValue = [s for s in imageInfoLines if "$$SM_MICRON_MARKER" in s][0].strip("$$SM_MICRON_MARKER ")
                    #markerValueVal = float(markerValue[:-3])
                    #markerValueUnit = markerValue[-3:].strip()
                    print (path + imageName + ".tif")
                    ftags = open(path + imageName + ".tif", 'rb')
                    tags = exifread.process_file(ftags)
                    ftags.close()
                    semValueList = str((tags["Image Tag 0x8546"]).values).split("\\r\\")
                    for semValue in semValueList:
                        if ("nPixel Size") in semValue:
                            markerValueVal = float(semValue.split("=")[1][1:-6])
                            markerValueUnit = semValue[-2:]
                    if (markerValueUnit== "um"):
                        markerValueVal = markerValueVal * 1e-6
                    elif (markerValueUnit == "nm"):
                        markerValueVal = markerValueVal * 1e-9
                    elif (markerValueUnit == "pm"):
                        markerValueVal = markerValueVal * 1e-12
                    PixelSizeY= markerValueVal
                    PixelSizeX = PixelSizeY
                    log.write(imageName + ':Created Succesfully! \n')
                    print(PixelSizeY)
                    hCrop = 1
                    
                    #Percent
                except FileNotFoundError:
                    log.write(imageName + ':Scale Error File not found')
                    
            elif (device == "Light"):
                if "_4x" in imageName:
                    PixelSizeY = 1.4814814814814815e-06
                    PixelSizeX = 1.4814814814814815e-06
                    log.write(imageName + ':Scale was guessed by Name. \n')
                elif "_10x" in imageName:
                    PixelSizeY = 5.91715976331361e-07
                    PixelSizeX = 5.91715976331361e-07
                    log.write(imageName + ':Scale was guessed by Name. \n')
                elif "_20x" in imageName:
                    PixelSizeY = 2.915451895043732e-07
                    PixelSizeX = 2.915451895043732e-07
                    log.write(imageName + ':Scale was guessed by Name. \n')
                elif "_40x" in imageName:
                    PixelSizeY = 1.38121546e-07
                    PixelSizeX = 1.38121546e-07
                    log.write(imageName + ':Scale was guessed by Name. \n')
                else:
                    log.write(imageName + ':Could not extract Scale Value. \n')
                hCrop = 1

            img = cv.imread((path + imageName + fileEnding),1)
            #print (path + imageName + fileEnding)
            imgH, imgW = img.shape[:2]
            if (imgW < 1.5*imgH):
                SEWFactor = 1
                flagSEAndBSE = False
                SE_img = img[ySE:ySE+((int)(imgH*hCrop)), xSE:xSE+((int)(imgW))]
                BSE_img = SE_img
            else:
                SEWFactor = 0.5
                SE_img = img[ySE:ySE+((int)(imgH*hCrop)), xSE:xSE+((int)(imgW*0.5))]
                BSE_img = img[yBSE:yBSE+((int)(imgH*hCrop)), ((int)(imgW*0.5)):imgW]
                
            SE_imgH, SE_imgW = SE_img.shape[:2]
            SE_imgHWMin = min(SE_img.shape[:2])
            BSE_imgH, BSE_imgW = BSE_img.shape[:2]
            BSE_imgHWMin = min(BSE_img.shape[:2])
            #SE_FFT_img = cv.cvtColor(SE_img, cv.COLOR_BGR2GRAY)[(int)(fftBorderCrop*SE_imgH):(int)(imgH-fftBorderCrop*SE_imgH), (int)(fftBorderCrop*BSE_imgW):(int)(imgW-fftBorderCrop*BSE_imgW)]
            #BSE_FFT_img = cv.cvtColor(BSE_img, cv.COLOR_BGR2GRAY)[(int)(fftBorderCrop*BSE_imgH):(int)(imgH-fftBorderCrop*BSE_imgH), (int)(fftBorderCrop*BSE_imgW):(int)(imgW-fftBorderCrop*BSE_imgW)]
            SE_FFT_img = cv.cvtColor(SE_img, cv.COLOR_BGR2GRAY)[(int)(abs(SE_imgHWMin-SE_imgH)/2):(int)(SE_imgH-abs(SE_imgHWMin-SE_imgH)/2), (int)(abs(SE_imgHWMin-SE_imgW)/2):(int)(SE_imgW-abs(SE_imgHWMin-SE_imgW)/2)]
            BSE_FFT_img = cv.cvtColor(BSE_img, cv.COLOR_BGR2GRAY)[(int)(abs(BSE_imgHWMin-BSE_imgH)/2):(int)(BSE_imgH-abs(BSE_imgHWMin-BSE_imgH)/2), (int)(abs(BSE_imgHWMin-BSE_imgW)/2):(int)(BSE_imgW-abs(BSE_imgHWMin-BSE_imgW)/2)]

                
            for scale in reversed(acceptableScales):
                if (scale <= (PixelSizeX*imgW*SEWFactor*scalaSizeW)):
                    rightScale = scale
                    if (rightScale < float(1e-06)):
                            rightScaleText = str(rightScale*1e+9)[:-2]+ " nm"
                    elif(rightScale < float(1e-03)):
                            rightScaleText = (str(rightScale*1e+6)[:-2]+ " \u03BC"+"m")
                    #print (str(rightScaleText))
                    break
                
            #rightScaleHeight = (int) (imgH*scalaSizeHeight)
            rightScaleWidth = (int) (rightScale/PixelSizeX)
            scaleHOffset = imgH*hCrop*scalaSizeHeight
            #scaleWOffset = 0

            ##----------------SE-Scale-----------------
            scaleInRectangleOffsetW = ((scalaSizeW*imgW*SEWFactor)-rightScaleWidth)/2
            cv.rectangle(SE_img,((int)(imgW*SEWFactor-scalaSizeW*imgW*SEWFactor),(int)(imgH*hCrop-scalaSizeH*imgH*hCrop)),((int)(imgW*SEWFactor),(int)(imgH*hCrop)),(0,0,0),thickness = -1)
            cv.rectangle(SE_img,((int)(imgW*SEWFactor-rightScaleWidth-scaleInRectangleOffsetW),(int)(imgH*hCrop-2*scaleHOffset)),((int)(imgW*SEWFactor-scaleInRectangleOffsetW),(int)(imgH*hCrop-scaleHOffset)),(255,255,255),thickness = -1)

            font = ImageFont.truetype(fontpath, 62)
            fontW = font.getsize(rightScaleText)[0]
            rectangleW = (int)(imgW*SEWFactor)-(int)(imgW*SEWFactor-scalaSizeW*imgW*SEWFactor)
            #print (PixelSizeX)
            img_pil = Image.fromarray(SE_img)
            draw = ImageDraw.Draw(img_pil)
            draw.text(((int)(imgW*SEWFactor-fontW-(rectangleW-fontW)/2), (int)(imgH*hCrop-7*scaleHOffset)),  rightScaleText, font = font, fill = (255,255,255,1))
            SE_img = np.array(img_pil)


            ##----------------BSE-Scale-----------------
            scaleInRectangleOffsetW = ((scalaSizeW*imgW*0.5)-rightScaleWidth)/2
            cv.rectangle(BSE_img,((int)(imgW*0.5-scalaSizeW*imgW*0.5),(int)(imgH*hCrop-scalaSizeH*imgH*hCrop)),((int)(imgW*0.5),(int)(imgH*hCrop)),(0,0,0),thickness = -1)
            cv.rectangle(BSE_img,((int)(imgW*0.5-rightScaleWidth-scaleInRectangleOffsetW),(int)(imgH*hCrop-2*scaleHOffset)),((int)(imgW*0.5-scaleInRectangleOffsetW),(int)(imgH*hCrop-scaleHOffset)),(255,255,255),thickness = -1)

            font = ImageFont.truetype(fontpath, 62)
            fontW = font.getsize(rightScaleText)[0]
            rectangleW = (int)(imgW*0.5)-(int)(imgW*0.5-scalaSizeW*imgW*0.5)
            img_pil = Image.fromarray(BSE_img)
            draw = ImageDraw.Draw(img_pil)
            draw.text(((int)(imgW*0.5-fontW-(rectangleW-fontW)/2),(int)(imgH*hCrop-7*scaleHOffset)),  rightScaleText, font = font, fill = (255,255,255,1))
            BSE_img = np.array(img_pil)

            #-----------------------SE-FFT-------------------------(https://docs.opencv.org/3.4/d8/d01/tutorial_discrete_fourier_transform.html)
            if (fftWanted == True):
                SE_magI = FFTImage(SE_FFT_img, modus = "SE")
                SE_blur = cv.GaussianBlur(SE_magI,(1,1),0)
                SE_magI_UINT8 = np.array(SE_blur * 255, dtype = np.uint8)
                SE_magI_thresh = cv.threshold(SE_magI_UINT8,175,255,cv.THRESH_TOZERO)
                #cv.imshow("SE_FFT", SE_magI)
                try:
                    SE_freq = frequencyDetection(SE_magI_thresh, "SE", PixelSizeX)
                except:
                    #print ("Error Processing SE-image: " + str(Error) + "\n")
                    log.write(imageName + ': Error Processing SE-image \n')
                    SE_freq = "Shrubbery"
                #cv.imshow("SE_Frequencies", SE_freq)

                #-----------------------BSE-FFT-------------------------(https://docs.opencv.org/3.4/d8/d01/tutorial_discrete_fourier_transform.html)
                BSE_magI = FFTImage(BSE_FFT_img, modus = "BSE")
                BSE_blur = cv.GaussianBlur(BSE_magI,(1,1),0)
                BSE_magI_UINT8 = np.array(BSE_blur * 255, dtype = np.uint8)
                #ret, BSE_magI_thresh = cv.threshold(BSE_magI_UINT8,175,255,cv.THRESH_TOZERO)
                BSE_magI_thresh = cv.threshold(BSE_magI_UINT8,175,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
                #cv.imshow("BSE_FFT", BSE_magI)
                try:
                    BSE_freq = frequencyDetection(BSE_magI_thresh, "BSE", PixelSizeX)
                except:
                    #print ("Error Processing BSE-image: " + str(Error) + "\n")
                    log.write(imageName + ': Error Processing BSE-image \n')
                    BSE_freq = "Shrubbery"
                #cv.imshow("BSE_Frequencies", BSE_freq)

            
            #cv.imshow("Bild", img)
            #cv.imshow("SE-Bild", SE_FFT_img)
            #cv.imshow("BSE-Bild", BSE_magI)
            if (flagSEAndBSE == True):
                cv.imwrite(savePathSE, SE_img);
                cv.imwrite(savePathBSE, BSE_img);
                if ((fftWanted == True) and (SE_freq != "Shrubbery")):
                    cv.imwrite(savePathSEFFT, np.array(SE_magI * 255, dtype = np.uint8));
                    cv.imwrite(savePathSEFFT2, SE_freq);
                if ((fftWanted == True) and (BSE_freq != "Shrubbery")):
                    cv.imwrite(savePathBSEFFT, np.array(BSE_magI * 255, dtype = np.uint8));
                    cv.imwrite(savePathBSEFFT2, BSE_freq);
            else:
                savePathSE = path + saveFolderName +  imageName + fileEndingSave
                savePathSEFFT = path + saveFolderNameFFT +  imageName +"_FFT" + fileEndingSave
                savePathSEFFT2 = path + saveFolderNameFFT +  imageName +"_Freq" + fileEndingSave
                cv.imwrite(savePathSE, SE_img);
                if (fftWanted) == True:
                    cv.imwrite(savePathSEFFT, np.array(SE_magI * 255, dtype = np.uint8));
                    if (SE_freq != "Shrubbery"):
                        cv.imwrite(savePathSEFFT2, SE_freq);
                
            cv.waitKey(0)
        except Exception as Error:
            print (traceback.format_exc())
            if (flagSEAndBSE == True):
                cv.imwrite(savePathSE, SE_img);
                cv.imwrite(savePathBSE, BSE_img);
            else:
                savePathSE = path + saveFolderName +  imageName + fileEndingSave
                cv.imwrite(savePathSE, SE_img);
            log.write(imageName + 'Error Processing \n')
    log.close()
    if (fftWanted == True):
        freqLog.close()
    buttonStart.configure(bg = "green")




    
################GUI##################
#Title   
tm.title("SEM Image Processing")
tm.configure(background='SteelBlue4')

#Row 1
labelOs = tk.Label(tm, width = 20, pady = 20, text="Os:", fg="black", bg="lightgrey").grid(row = 0, column = 0, columnspan = 2)
tk.Radiobutton(tm, 
                text="windows",
                indicatoron = 0,
                width = 20,
                padx = 0, 
                variable = tkinterOs, 
                command = ShowOsChoice(),
                value = "windows").grid(row=0, column = 2, columnspan = 2)
tk.Radiobutton(tm, 
                text="mac",
                indicatoron = 0,
                width = 20,
                padx = 0, 
                variable = tkinterOs, 
                command = ShowOsChoice(),
                value = "mac").grid(row=0, column = 4, columnspan = 2)

#Row 2
labelDevice = tk.Label(tm, width = 20, pady = 20, text="Device:", fg="black", bg="lightgrey").grid(row = 1, column = 0, columnspan = 2)
tk.Radiobutton(tm, 
                text="Tescan",
                indicatoron = 0,
                width = 20,
                padx = 0, 
                variable = tkinterDevice, 
                command = ShowDeviceChoice(),
                value = "Tescan").grid(row=1, column = 2, columnspan = 2)
tk.Radiobutton(tm, 
                text="Jeol",
                indicatoron = 0,
                width = 20,
                padx = 0, 
                variable = tkinterDevice, 
                command = ShowDeviceChoice(),
                value = "Jeol").grid(row=1, column = 4, columnspan = 2)
tk.Radiobutton(tm, 
                text="Zeiss",
                indicatoron = 0,
                width = 20,
                padx = 0, 
                variable = tkinterDevice, 
                command = ShowDeviceChoice(),
                value = "Zeiss").grid(row=1, column = 6, columnspan = 2)
tk.Radiobutton(tm, 
                text="Ligth",
                indicatoron = 0,
                width = 20,
                padx = 0, 
                variable = tkinterDevice, 
                command = ShowDeviceChoice(),
                value = "Ligth").grid(row=1, column = 8, columnspan = 2)

#Row 3
labelScaleBox = tk.Label(tm, width = 20, pady = 20, text="ScaleBox:", fg="black", bg="lightgrey").grid(row = 2, column = 0, columnspan = 2)
labelHeigth = tk.Label(tm, width = 10, text="Height:", fg="black",).grid(row = 2, column = 2, columnspan = 1)
entryHeigth = tk.Entry(tm, width = 10, textvariable=tkinterHeight, justify="center").grid(row = 2, column = 3, columnspan = 1)
labelWidth = tk.Label(tm, width = 10, text="Width:", fg="black",).grid(row = 2, column = 4, columnspan = 1)
entryWidth = tk.Entry(tm, width = 10, textvariable=tkinterWidth, justify="center").grid(row = 2, column = 5, columnspan = 1)
labelBar = tk.Label(tm, width = 10, text="Bar:", fg="black",).grid(row = 2, column = 6, columnspan = 1)
entryBar = tk.Entry(tm, width = 10, textvariable=tkinterScale, justify="center").grid(row = 2, column = 7, columnspan = 1)

#Row 4
labelFFT = tk.Label(tm, width = 20, pady = 20, text="FFT:", fg="black", bg="lightgrey").grid(row = 3, column = 0, columnspan = 2)
tk.Radiobutton(tm, 
                text="On",
                indicatoron = 0,
                width = 9,
                padx = 0, 
                variable = tkinterFFTToggle, 
                command = ShowFFTToggleChoice(),
                value = True).grid(row=3, column = 2, columnspan = 1)
tk.Radiobutton(tm, 
                text="Off",
                indicatoron = 0,
                width = 9,
                padx = 0, 
                variable = tkinterFFTToggle, 
                command = ShowFFTToggleChoice(),
                value = False).grid(row=3, column = 3, columnspan = 1)
labelSERange = tk.Label(tm, width = 10, text="SE_Range:", fg="black",).grid(row = 3, column = 4, columnspan = 1)
entrySERange = tk.Entry(tm, width = 10, textvariable=tkinterSERange, justify="center").grid(row = 3, column = 5, columnspan = 1)
labelBSERange = tk.Label(tm, width = 10, text="BSE_Range:", fg="black",).grid(row = 3, column = 6, columnspan = 1)
entryBSERange = tk.Entry(tm, width = 10, textvariable=tkinterBSERange, justify="center").grid(row = 3, column = 7, columnspan = 1)

#Row 5
labelFolderPath = tk.Label(tm, width = 20, pady = 20, text="FolderPath:", fg="black", bg="lightgrey").grid(row = 4, column = 0, columnspan = 2)
labelFolderPath2 = tk.Label(tm,textvariable=tkinterFolder_path, width = 80).grid(row=4, column=2, columnspan = 7)
button2 = tk.Button(text="Browse", command=browse_button).grid(row=4, column=9)

#Row 6
buttonStart = tk.Button(text="Start", command=startCode, bg = "green", width = 104)
buttonStart.grid(row=5, column=0, columnspan = 10)

tm.mainloop()
#tm.destroy()
