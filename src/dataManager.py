import os
import shutil
from database import DataBase
from openVoice import OpenVoice
from utils import *


class DataManager:

    def __init__(self):
        self.openVoice = OpenVoice()
        self.db = DataBase()

    
    def getVoice(self, serverId, voiceName):

        print(f"Getting voice {voiceName}...")

        dbVoice = self.db.getVoice(serverId, voiceName)

        return dbVoice


    def addVoice(self, voiceName, serverId, userId, tempPath):
        print(f"Adding voice {voiceName}...")

        shortcut = self.getShortcut(voiceName)

        voice = self.db.addVoice(voiceName, shortcut, serverId, userId)

        path = os.path.join(VOICE_DIR, os.path.join(str(serverId) if serverId else 'Public', str(voice['voice_id'])))

        if not os.path.exists(path):
            os.makedirs(path)

        for filename in os.listdir(tempPath):
            if os.path.isfile(os.path.join(tempPath, filename)):
                shutil.move(os.path.join(tempPath, filename), path)

        shutil.rmtree(tempPath)

        print(f"Successfully added {voiceName}!")
        return voice
    


    def getShortcut(self, voiceName):
        shortcut = ""

        for char in voiceName: 
            if char.isupper():
                shortcut += char
        
        if len(shortcut)==0:
            shortcut += voiceName[0]
            shortcut += voiceName[len(voiceName)//2]

        return shortcut


    def textToSpeech(self, args, voiceId, userId, serverId, script):

        debug = script[:40].replace('\n','') + '...'

        print(f"Adding response ({debug}) to database...")
        path = self.db.addPrompt(args, voiceId, userId, serverId, script)['path']      

        parent_dir = os.path.dirname(path)

        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        print(f"Generating Audio with OpenVoice...")
        self.openVoice.textToSpeech(script, self.db.getVoiceById(voiceId), path)
        print(f"Audio file generated!")

        return path


    def deleteVoice(self, voice):
        print(f"Deleting {voice['name']}...")
        self.db.deleteVoice(voice['voice_id'])
        shutil.rmtree(voice['path'])
        print(f"Successfully deleted {voice['name']}!")
        return
    
    
