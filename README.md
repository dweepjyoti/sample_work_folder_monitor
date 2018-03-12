# Folder Monitor

Program to continuously monitor a folder and perform actions on files such as decompression, 
moving them etc. 

**Working of the script**:
1) Define "DropboxDir", "LocalImageDir", "NASDir" according to your convenience in parameters.json file
  "DropboxDir": The folder from which the files has to be moved
  "LocalImageDir" : The folder where the images should be moved for ortho generation
  "NASDir" : Local file storing server
2) Also define "SleepTime" : Time for which the script will go for sleep after a successful batch of file movement in the same parameters.json file
3) Run main.py
