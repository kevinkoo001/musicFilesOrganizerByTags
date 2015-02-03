# musicFilesOrganizerByTags
Simple music files (mp3, wma, ogg) organizer using tag information

The DB should be created by Mp3tag (www.mp3tag.de) with the following attributes
  Title;Artist;Album;Track;Year;Length;Size;Last Modified;Path;Filename
In other words, you need sanitized tags to organize music files in advance.
You may want to update it with the 3rd party software (i.e MS Office excel)

This python script is simply to move music files into new directory using tag information like following steps.
 1) Read the tag information - Artist and Title
 2) Create new directory by artists
 3) Move the file into newly created directory
 4) If there is the same music file according to a tag, then remain the one with larger size and remove redundant one.

Note that if there is no tag information then the script will pass the file through.
