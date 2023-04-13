import mysql.connector
from dotenv import load_dotenv
import os

class DataBase:

    def connect(self):
        user = os.getenv('DATABASE_USER')
        password = os.getenv('DATABASE_PASSWORD')
        host = os.getenv('DATABASE_HOST')
        name = os.getenv('DATABASE_NAME')

        try:
            print("Connecting to database.")
            self.cnx = mysql.connector.connect(user=user, password=password, host=host, database=name)
            print("Connected!")
            cursor = self.cnx.cursor()
            sql = "SELECT count(*) as count FROM information_schema.TABLES WHERE (TABLE_SCHEMA = %s);"
            cursor.execute(sql, (name,))

            row = cursor.fetchone()
            count = row[0]
        
            if count != 3:
                self.init()

            return self.cnx
        except mysql.connector.Error as err:  
            print(err)  
        

    def init(self):
        fileName = "database.sql"
        print("Loading data")
        
        try:
            cursor = self.cnx.cursor()
            with open(fileName, "r") as infile:
                st = infile.read()
                commands = st.split(";")
                for line in commands:                   
                    # print(line.strip("\n"))
                    line = line.strip()
                    if line == "":  # Skip blank lines
                        continue 
                        
                    cursor.execute(line)                    
                        
            cursor.close()
            self.cnx.commit()            
            print("Database load complete")
        except mysql.connector.Error as err:  
            print(err)
            self.cnx.rollback()  


    def cursorToDict(self, cursor):
        column_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))

        return result


    def getUser(self, user):
        cursor = self.cnx.cursor()
        sql = "SELECT * FROM users WHERE user_id=%s"
        cursor.execute(sql,(user.id,))
        result = self.cursorToDict(cursor)
        if len(result) == 0:
            return None
        return result[0]


    def addUser(self,user):
        username = user.display_name + user.discriminator
        user_id = user.id
        cursor = self.cnx.cursor()
        sql = "INSERT INTO users (user_id, username) VALUES (%s,%s)"
        cursor.execute(sql,(user_id,username))
        cursor.close()
        self.cnx.commit()
        return self.getUser(user)


    def getVoice(self,user_id,voice):
        cursor = self.cnx.cursor()
        sql = "SELECT * FROM voices WHERE name=%s AND is_private=0 OR name=%s AND user_id=%s;"
        cursor.execute(sql,(voice,voice,user_id))
        result = self.cursorToDict(cursor)
        if len(result) == 0:
            return None
        return result[0]


    def addVoice(self, voice_id, voiceName, isPrivate, user_id, path):
        cursor = self.cnx.cursor()
        sql = "INSERT INTO voices (voice_id,name,is_private,user_id,path) VALUES (%s,%s,%s,%s,%s)"
        cursor.execute(sql,(voice_id, voiceName, isPrivate, user_id, path))
        cursor.close()
        self.cnx.commit()
        return


    def getPrompt(self, prompt_id):
        cursor = self.cnx.cursor()
        sql = "SELECT * FROM prompts WHERE prompt_id = %s;"
        cursor.execute(sql, (prompt_id,))
        result = self.cursorToDict(cursor)
        cursor.close()

        if len(result) == 0:
            return None
        return result[0]


    def addPrompt(self, command, user_id, username, prompt, response, numChars):
        cursor = self.cnx.cursor()
        sql = "INSERT INTO prompts (command, user_id, username, prompt, response, num_chars) VALUES (%s,%s,%s,%s,%s,%s);"
        cursor.execute(sql, (command, user_id, username, prompt, response, numChars))
        self.cnx.commit()

        cursor = self.cnx.cursor()
        sql = "UPDATE prompts SET path = CONCAT('audioOutput/', %s, '/', LAST_INSERT_ID(),'_',%s,'.mp3') WHERE prompt_id = LAST_INSERT_ID();"
        cursor.execute(sql, (user_id,command))
        self.cnx.commit()

        cursor.execute("SELECT LAST_INSERT_ID();")
        prompt_id = cursor.fetchone()[0]
        return self.getPrompt(prompt_id)


    def resetMonthlyUserCharCount(self,user_id):
        cursor = self.cnx.cursor()
        sql = """
        UPDATE users
        SET monthly_chars_used = 0,
            last_char_reset = NOW()
        WHERE user_id = %s;
        """
        cursor.execute(sql, (user_id,))
        self.cnx.commit()
        cursor.close()
        return


    def updateUserCharCount(self,user_id, addedChars):
        cursor = self.cnx.cursor()
        sql = """
        UPDATE users
        SET monthly_chars_used = monthly_chars_used + %s,
            total_chars_used = total_chars_used + %s
        WHERE user_id = %s;
        """
        cursor.execute(sql, (addedChars, addedChars, user_id))
        self.cnx.commit()
        cursor.close()
        return

    def getAllVoices(self):
        return