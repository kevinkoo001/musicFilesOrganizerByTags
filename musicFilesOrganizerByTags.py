#-*- coding: utf-8 -*-
import sys
import os
import shutil
import stat
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp3 import MP3

# This DB is created by Mp3tag (www.mp3tag.de) with the following attributes
# Title;Artist;Album;Track;Year;Length;Size;Last Modified;Path;Filename
# You may want to update it with the 3rd party software (i.e MS Office excel)
dbFile="mpdb.txt"

###############################
##  SEVERAL HELPER FUNCTIONS ##
###############################

def is_hangul(s): 
	for c in unicode(s): 
		if u'\uac00' <= c <= u'\ud7a3': 
			return True 
	return False 
	
def copyFile(src, dst):
	os.system("xcopy %s %s" % (src, dst))
	#if os.path.isfile(dst): print ".",

def moveFile(src, dst):
	shutil.move(src, dst)
	
def makeDir(dir):
	dirStatus = os.path.isdir(dir)
	if dirStatus == False:
		os.mkdir(dir)

def isFile(file):
	return os.path.exists(file)
	
def getFileSize(file):
	# return file size in bytes
	return os.stat(file)[stat.ST_SIZE]
	
def removeFile(file):
	os.remove(file)

###################################
	
def readMp3db():
	titles = []
	artists = []
	paths = []
	filenames = []
	albums = []
	
	# Delimeter in DB is semicolon (;)
	with open(dbFile, 'r') as f:
		for line in f:
			data = line.split(';')
			title = 	unicode(data[0])
			artist = 	unicode(data[1])
			album = 	unicode(data[2])
			track =		unicode(data[3])
			year =		unicode(data[4])
			length =	unicode(data[5])
			size = 		unicode(data[6])
			path =		unicode(data[8])
			filename =	unicode(data[9].rstrip())
			#print path + filename
			titles.append(title)
			artists.append(artist)
			paths.append(path)
			filenames.append(filename)
			albums.append(album)
			
	return titles, artists, paths, filenames, albums

def checkID3Hdr(file):
	header = True
	try:
		tags = ID3(file)
	except ID3NoHeaderError:
		print "\tNo ID3 Header Found for " + file
		header = False
	return header

def updateTag(targetDir):
	# Get all ID3 information to update
	(titles, artists, paths, filenames, albums) = readMp3db()
	filesDB = []
	for i in range(0, len(filenames)):
		filesDB.append(os.path.join(paths[i], filenames[i]))
	
	totalDBcnt = len(filenames)
	updatedCnt = 0
	# Walk all target (sub)directories and update ID3 tag information
	for (root, dirs, files) in os.walk(targetDir):
		for fileName in files:
			if fileName.endswith("mp3") or fileName.endswith("wma") or fileName.endswith("ogg"):
				fullpath = os.path.join(root, fileName)
				headerStatus = checkID3Hdr(fullpath)
				if fullpath in filesDB and headerStatus == True:
					index = filesDB.index(fullpath)
					print "[" + str(filesDB.index(fullpath)) + "] " + fullpath
					audio = EasyID3(fullpath)
					updatedArtist = unicode(artists[index])
					updatedTitle = unicode(titles[index])
					updatedAlbum = unicode(albums[index])
					if updatedTitle is not "" and updatedArtist is not "":
						audio["artist"] = updatedArtist
						audio["title"] = updatedTitle
						audio["album"] = updatedAlbum
						try:
							audio.save(v2_version=3, v23_sep=None)
						except:
							print "\tCould not be saved for " + fullpath
						updatedCnt = updatedCnt + 1
					else:
						pass
	
	return totalDBcnt, updatedCnt
	
def moveData(targetDir, dstDir):
	cnt = 0
	errCnt = 0
	# Walk all target (sub)directories and move music files
	for (root, dirs, files) in os.walk(targetDir):
		for fileName in files:
			oldFile = os.path.join(root, fileName)
			if checkID3Hdr(oldFile) and (fileName.endswith("mp3") or fileName.endswith("wma") or fileName.endswith("ogg")):
				audio = EasyID3(oldFile)
				try:
					artist = unicode(audio["artist"][0])
					title = unicode(audio["title"][0])
					cnt = cnt + 1
					newDir = dstDir + "\\" + artist
					makeDir(newDir)
					newName = artist + " - " + title + os.path.splitext(oldFile)[1]
					newFile = os.path.join(newDir, newName)
					print "[ %s ] (%05d) %s - %s " % (targetDir, cnt, artist, title)
					print "\t %s --> %s" % (oldFile, newFile)
					#copyFile(oldFile, newFile)
					if isFile(newFile) and getFileSize(newFile) >= getFileSize(oldFile):
						removeFile(oldFile)
						print "\tRedudant file %s has been removed!!!!" % (oldFile)
					else:
						moveFile(oldFile, newFile)
						#print "\t%s Moved!!!" % (newFile)
				except:
					print "\tAn error occured while processing " + oldFile
					errCnt = errCnt + 1
	return cnt, errCnt 
	
if __name__ == '__main__':
		
	reload(sys)
	sys.setdefaultencoding('utf-8')
	
	targetDirs = [u'D:\\Music\\target']
	dstDir = u'D:\\Music\\new'
	
	# A. Tag updates
	for targetDir in targetDirs:
		(totalDBcnt, updatedCnt) = updateTag(targetDir)
		print "================================================"
		print "Successfully Updated Files in Total: " + str(updatedCnt) + "/" + str(totalDBcnt)
		print "================================================"
	
	# B. Data Move
	for targetDir in targetDirs:
		(totalCnt, errCnt) = moveData(targetDir, dstDir)
		print "================================================"
		print "Successfully Moved Files in Total (%s) %d " % (targetDir, totalCnt)
		print "Error occured Files in Total (%s) %d " % (targetDir, errCnt)
		print "================================================"
		
