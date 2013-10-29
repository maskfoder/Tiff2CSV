# -*- coding: utf8 -*-

# Tiff2CSV.py - Extracts EXIF tags and preview images from a directory of tiff/tif-files. 
# Version 0.5
# Contact: micke.lind@gmail.com
# 
# Required: Python 2.7 and external library pyexiv2 ( http://tilloy.net/dev/pyexiv2/download.html )
#
# Version history:
# 0.5 First acceptable version
#
# Usage: Copy the script and the EXIF.txt to the image directory. Launch using 'python Tiff2CSV.py'
# You can modify the EXIF tags extracted by adding or removing lines from the EXIF.txt file.
#
# To do:
# * Add argument parser
# * Better error handling for broken image files.
# * More verbose handling

import os
import pyexiv2
import csv

#Reads a line separated textfile of EXIF TAGS and returns them as a list
def getEXIFList(textFile):
    tagsList = []
    f = open(textFile, 'r')
    for line in f.readlines():
        tagsList.append(line.strip('\n'))
    f.close()
    return tagsList

#Returns a list of all tif/tiff-files in the given directory
def getTiffFiles(directory):
    tiffList = []
    for f in os.listdir(directory):
        if (os.path.splitext(f)[1].lower() == '.tif') or (os.path.splitext(f)[1].lower() == '.tiff'):
            tiffList.append(f)
    return tiffList

#Returns all the tag values from all the tiff files in a given list
#Extract previews, if any, and save them in a subdirectory
def getTagValuesFromTiffList(tiffList, tagsList, directory):
    try:
        os.mkdir(os.getcwd()+'/previews')
    except:
        if os.path.exists(os.getcwd()+'/previews'):
            pass
        
    tagValuesMatrix = []
    for tiff in tiffList:
        print('Extracting tags from '+ tiff)
        
        metadata = pyexiv2.ImageMetadata(directory + '/' +tiff)
        metadata.read()
        rowValues = []
        rowValues.append(directory + '/' +tiff)

        #Extract image, if any
        previews = metadata.previews
        if (len(previews) > 0):
            print('Extracting preview image from ' + tiff +'\n')
            preview = sorted(previews, reverse=True)[0]
            preview.write_to_file(os.getcwd()+'/previews/'+tiff.split('.')[0])
            rowValues.append(os.getcwd()+'/previews/'+tiff.split('.')[0]+preview.extension)
        else:
            print('No preview image found in ' + tiff +'\n')
            rowValues.append('-')
            
        for tag in tagsList:
            try:
                rowValues.append(metadata[tag].raw_value)
            except KeyError or TypeError:
                rowValues.append('-')
        tagValuesMatrix.append(rowValues)
    return tagValuesMatrix
    
def main():
    directory = os.getcwd()
    #Reads all the EXIF tags from the EXIF.txt file and returns them in a python list
    tagsList = getEXIFList('EXIF.txt')

    #Get all the tiff files in the directory
    tiffList = getTiffFiles(directory)

    #Get a matrix with all the exif values from the tiff list
    tagValueMatrix = getTagValuesFromTiffList(tiffList, tagsList, directory)

    #Insert tags at the beginning of the tags list
    tagsList.insert(0, 'Preview')
    tagsList.insert(0, 'File')
    
    #Insertlist of tags at the top of the matrix
    tagValueMatrix.insert(0, tagsList)

    #Create a CSV file from output
    with open('output.csv','wb') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(tagValueMatrix)

    print('\nFinished!')
    print('Tag output written to output.csv.')
    print('Previews written to /previews/ directory.')

if  __name__ =='__main__':main()
