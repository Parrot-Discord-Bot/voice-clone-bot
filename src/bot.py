#https://discord.com/api/oauth2/authorize?client_id=1095014597871804510&permissions=3196992&scope=bot
#https://discord.com/api/oauth2/authorize?client_id=1095890592753528872&permissions=3196928&scope=bot Dev
#TODO:

    #Voices to add
        #Purge  https://www.youtube.com/watch?v=BEkWdzd7ias
        #Joe Biden  https://www.youtube.com/watch?v=_J4IkbRh6W4&t=12s


        #David Goggins
        #Pierre Poilievre
        #Meg Griffin
        #Chris Griffin
        #Cleveland Brown
        #Quagmire
        #Joe Swanson
        #Lois Griffin
        #Stewie Griffin
        #Brian Griffin
        #Morty
        #Summer
        #Jerry
        #Beth
        
import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
from litellm import completion
from dataManager import DataManager
import shutil
import random
from collections import namedtuple
import functools
import asyncio
from utils import *


load_dotenv(ENV_FILE)
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # This is to allow the bot to see message content, especially useful after newer API changes
bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)
bot.remove_command('help')
dataManager = DataManager()
footer_msg = "This bot was created by abraham_jefferson"

def getHelpEmbed(title, description, example):
    toReturn = discord.Embed(title=title, color=0x0000ff, description=description)
    toReturn.add_field(name="Examples", value=example)
    return toReturn

speakHelp = getHelpEmbed('!speak',"""Parrot joins voice your channel and speaks prompt. 
                                 Use 'gpt' to use your input as a [ChatGPT](https://chat.openai.com) prompt.
                                 Each voice has a shortcut that can be used instead of the voice name.
                                 Voices and shortcuts are not case-sensetive.""",
                                 """!speak JordanPeterson | say exactly this
                                    !speak JordanPeterson gpt | tell me a story 
                                    !speak jp | say exactly this""")

addHelp = getHelpEmbed('!add', 'Add a voice to your server by uploading file(s).\nAccent required.\nNo spaces allowed in voice name.', "!add JeffKaplan American")

downloadHelp = getHelpEmbed('!download', 'View list of recent promts, click reactions to download.', """!download 
                                                                                                            !download serverName 
                                                                                                            !download all """)

replayHelp = getHelpEmbed('!replay', 'View list of recent promts, click reactions to replay.', """!replay 
                                                                                                            !replay serverName 
                                                                                                            !replay all """)

deleteHelp = getHelpEmbed('!delete', 'Delete a voice that you added to your server.',"!delete BenShapiro\n!delete bs")

def writeMessage(message):
    with open('message.txt','w') as file:
        file.write(message)
    return

def readMessage():
    with open('message.txt','r') as file:
        content = file.read()
    return content

def makeErrorMessage(reason):
    embed = discord.Embed(title="Error",color=0xff0000)
    embed.add_field(name="Reason",value=reason)
    embed.set_footer(text=footer_msg)
    return embed



def getAboutEmbed():
    embed = discord.Embed(title="About Parrot",color=0x0000ff, description="""[Add Parrot](https://discord.com/api/oauth2/authorize?client_id=1095014597871804510&permissions=3196992&scope=bot)
                                                                            [website](https://parrotbot.me/)
                                                                            [GitHub](https://github.com/Ferdinand737/voice-clone-bot)
                                                                            \nI built this bot using the [ElevenLabs](https://beta.elevenlabs.io/) and [OpenAi](https://platform.openai.com/) APIs. 
                                                                            Contact me <@273300302541881344> if you have any questions, suggestions or find any bugs.""")
    embed.add_field(name="Technologies Used", value="Implemented with python + discord library.\nMySql for data storage.\nHosted on my own server.\nIcon design by <@274019867764588544>.",inline=False)
    embed.set_footer(text=footer_msg)
    return embed


def getVoicesEmbed(serverId, serverName):
    thisServerVoices = dataManager.db.getServerVoices(serverId)
    publicVoices = dataManager.db.getPublicVoices()
    thisServerVoicesStr =''
    publicVoicesStr =''

    if thisServerVoices is not None:
        for voice in thisServerVoices:
            thisServerVoicesStr = thisServerVoicesStr + voice['name'] + " - " + voice['shortcut'] + "\n"
    else:
        thisServerVoicesStr = 'None'

    if publicVoices is not None:
        for voice in publicVoices:
            publicVoicesStr = publicVoicesStr + voice['name'] + " - " + voice['shortcut'] + "\n"
    else:
        publicVoicesStr = 'None'

    embed = discord.Embed(title="Available Voices", description="Each voice has a shortcut that can be used instead of the voice name.\nVoices and shortcuts are not case-sensetive.", color=0x0000ff)
    embed.add_field(name="Public", value=publicVoicesStr, inline=False)
    embed.add_field(name=f"In {serverName}", value=thisServerVoicesStr, inline=False)
    embed.set_footer(text=footer_msg)
    return embed


def getBuyEmbed():
    embed = discord.Embed(title="Buy Characters",color=0x0000ff,description="""Visit https://parrotbot.me to buy more characters""")
    
    embed.set_footer(text=footer_msg)
    return embed

def parseArgs(command):

    currentCommand = command.split(" ")[0]

    if currentCommand == '!speak':

        options = {'voiceName':None, 'gpt':None, 'prompt':None}

        try:
            options['prompt'] = command.split("|")[1]
        except:
            print(f"Could not find prompt in command '{currentCommand}'.")
            return None

        arguments = command.split("|")[0].split(" ")

        arguments = [arg.strip() for arg in arguments]

        try:     
            options['voiceName'] = arguments[1]
        except:
            print(f"Could not find voice name in command '{currentCommand}'.")

        arguments = [arg.lower() for arg in arguments]

        if 'gpt' in arguments:
            options['gpt'] = 'gpt'

        return options
    
    if currentCommand == '!add':
        
        options = {'voiceName':None, 'public':None}

        accents = ['american', 'british', 'african', 'australian','indian']

        arguments = [arg.strip() for arg in command.split(" ")]

        try:
            options['voiceName'] = arguments[1]
        except:
            print(f"Could not find voice name in command '{currentCommand}'.")

        arguments = [arg.lower() for arg in arguments]

        if 'public' in arguments:
            options['public'] = 'public'


        return options
    
    if currentCommand == '!delete':

        options = {'voiceName':None,'public':None}

        arguments = [arg.strip() for arg in command.split(" ")]

        try:     
            options['voiceName'] = arguments[1]
        except:
            print(f"Could not find voice name in command '{currentCommand}'.")

        arguments = [arg.lower() for arg in arguments]

        if 'public' in arguments:
            options['public'] = 'public'

        return options
    
    if currentCommand == '!replay' or currentCommand == '!download':

        options = {'serverName': None}

        words = command.split()

        if len(words) >= 2:
            options['serverName'] = ' '.join(words[1:])

        return options


def checkUser(user):

    foundUser = dataManager.db.getUser(user.id)

    if foundUser is None:
        foundUser = dataManager.db.addUser(user)

    return foundUser


def startCommand(ctx):
    
    serverId = ctx.guild.id
    serverName = ctx.guild.name
    username = f"{ctx.author.name}#{ctx.author.discriminator}"

    print(f"\nCommand '{ctx.message.content}' requested by {username} in {serverName}.")

    foundServer = dataManager.db.getServer(serverId)

    if foundServer is None:
        dataManager.db.addServer(serverId,serverName)

    user = checkUser(ctx.author)

    return user, serverId, serverName


async def playAudio(ctx, channel, source):

    try:
        voice_client = await channel.connect()
    except:
        error = 'Failed to connect to the voice channel. Please try again.'
        await ctx.send(embed=makeErrorMessage(error))
        print(error)
        return 

    audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source=source)

    if not voice_client.is_playing():
        voice_client.play(audio_source)

        while voice_client.is_playing():
            await asyncio.sleep(1)
        await voice_client.disconnect()
    else:
        error = 'I am already playing an audio file. Please wait until I finish.'
        await ctx.send(embed=makeErrorMessage(error))
        print(error)




async def run_blocking(blocking_func, *args, **kwargs):
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await bot.loop.run_in_executor(None, func)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!help"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print(f"Command not found: {ctx.message.content}")
        await help(ctx)
    else:
        print(error)


@bot.command(name='help')
async def help(ctx):

    user,serverId,serverName = startCommand(ctx)

    if user is None:
        error = "Your discord account is too new."
        await ctx.send(embed=makeErrorMessage(error))
        print(error)
        return


    commands = ['!speak','!add','!download','!replay','!voices','!delete','!about']

    helpList = []

    helpList.append(speakHelp)
    helpList.append(addHelp)
    helpList.append(downloadHelp)
    helpList.append(replayHelp)
    helpList.append(getVoicesEmbed(serverId, serverName))
    helpList.append(deleteHelp)
    helpList.append(getAboutEmbed())
   
    embed = discord.Embed(title="Help",color=0x0000ff, description="Available Commands")
    for i, command in enumerate(commands):
        embed.add_field(name=command,value=f"{i+1}\u20e3")
    
    embed.set_footer(text=footer_msg)

    msg = await ctx.send(embed=embed)

    for i in range(len(commands)):
        await msg.add_reaction(f"{i+1}\u20e3")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in [f"{i+1}\u20e3" for i in range(len(helpList))]
   

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Timed out. Please try again.")
    else:
        index = [f"{i+1}\u20e3" for i in range(len(helpList))].index(str(reaction.emoji)) 
        await ctx.send(embed=helpList[index])
        return


@bot.command(name='speak')
async def speak(ctx):
    user,serverId,servername = startCommand(ctx)

    if user['privileges'] == 'banned':
        error = 'You are not allowed to use this command'
        await ctx.send(embed=makeErrorMessage(error))
        print(error)
        return

    args = parseArgs(ctx.message.content)

    serverId = ctx.guild.id

    if args is None:
        await ctx.send(embed=speakHelp)
        return

    if args['prompt'] is None:
        await ctx.send(embed=speakHelp)
        return

    voice = ctx.author.voice

    if voice is None:
        error = 'You need to be in a voice channel to use this command.'
        await ctx.send(embed=makeErrorMessage(error))
        print(error)
        return

    #channel = ctx.author.voice.channel
    channel = voice.channel

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
   
    clonedVoice = await run_blocking(dataManager.getVoice, serverId, args['voiceName'])

    if clonedVoice is None:
        error = f"Could not find voice '{args['voiceName']}'."
        await ctx.send(embed=makeErrorMessage(error))
        print(error)
        return

    await ctx.send("Generating audio...")

    if args['gpt']:
        try:
            ollamaPrompt = args['prompt'] + " Do not cut off mid sentence."
            print(f"Requesting response from OpenAi for prompt ({args['prompt']})...")
            script = await run_blocking(completion,model="ollama/dolphin-mixtral:latest",messages=[{ "content": ollamaPrompt, "role": "user"}], api_base="http://localhost:11434")
            script = script["choices"][0]["text"]
            print(f"Received response from OpenAi!")
        except:
            error = "Problem with openAi"
            await ctx.send(embed=makeErrorMessage(error))
            print(error)
            return
    else:
        script = args['prompt']

    script = script.strip()

    outputPath = await run_blocking(dataManager.textToSpeech,args, clonedVoice['voice_id'], user['user_id'], serverId, script)

    await playAudio(ctx, channel, outputPath)
    
    
@bot.command(name='add')
async def add(ctx):
    user,serverId,servername  = startCommand(ctx)

    args = parseArgs(ctx.message.content)
    
    if args is None:
        await ctx.send(embed=addHelp)
        return

    
    if args['voiceName'] is None:
        await ctx.send(embed=addHelp)
        return

    if args['public']:
        if user['privileges'] != 'admin':
            error = "Only admins can add public voices."
            await ctx.send(embed=makeErrorMessage(error))
            print(error)
            return
        serverId = None


    files = ctx.message.attachments

    if len(files) == 0:
        error = "You need to attach files to add a new voice."
        await ctx.send(embed=makeErrorMessage(error))
        print(error)
        return

    await ctx.send("Adding voice...")

    tempPath = os.path.join(TEMP_DIR, str(random.randint(0, 2**32 - 1)))

    clonedVoice = await run_blocking(dataManager.getVoice, serverId, args['voiceName'])

    if clonedVoice:
        error = "The voice name already exists. Please choose another name."
        await ctx.send(embed=makeErrorMessage(error))
        print(error)
        return

    if not os.path.exists(tempPath):
        os.makedirs(tempPath)

    for file in files:
        if file.size >= 10000000:
            error = f"{file.filename} is too large. All files must me under 10Mb."
            await ctx.send(embed=makeErrorMessage(error))
            print(error)
            shutil.rmtree(tempPath)
            return
            
        allowedTypes = ['audio/aac', 'audio/x-aac', 'audio/x-aiff', 'audio/ogg', 'audio/mpeg', 'audio/mp3', 'audio/mpeg3', 
                        'audio/x-mpeg-3', 'audio/opus', 'audio/wav', 'audio/x-wav', 'audio/webm', 'audio/flac', 'audio/x-flac', 'audio/mp4']
        if file.content_type not in allowedTypes:
            error = "Input file must be an audio file"
            await ctx.send(embed=makeErrorMessage(error))
            print(error)
            shutil.rmtree(tempPath)
            return

       
        file_path = os.path.join(tempPath, file.filename)
        await file.save(file_path)

    newVoice = dataManager.addVoice(args['voiceName'], serverId, user['user_id'], tempPath)


    embed = discord.Embed(title="Saved!", description=f"Voice '{args['voiceName']}' saved successfully.", color=0x00ff00)
    embed.add_field(name="Commands to play",value=f"""!speak {args['voiceName']} | your message
                                                        !speak {newVoice['shortcut']} | your message
                                                        !speak {args['voiceName']} gpt | your prompt""")
    embed.set_footer(text=footer_msg)

    await ctx.send(embed=embed)


@bot.command(name='voices')
async def add(ctx):
    user,serverId,serverName = startCommand(ctx)
    await ctx.send(embed=getVoicesEmbed(serverId, serverName))


Result = namedtuple('Result', ['paths', 'check'])

async def replayAndDownloadHelper(ctx):
    user,serverId,servername  = startCommand(ctx)

    args = parseArgs(ctx.message.content)

    if user is None:
        error = "Your discord account is too new"
        await ctx.send(embed=makeErrorMessage(error))
        print(error)
        return
    
    if args['serverName'] is None:
        prompts = dataManager.db.getServerPrompts(user['user_id'], serverId, 9)
        where = servername
    
    elif args['serverName'] != 'all':
        server = dataManager.db.getServerByName(args['serverName'])

        if server is None:
            error = f"Could not find server '{args['serverName']}'."
            await ctx.send(embed=makeErrorMessage(error))
            print(error)
            return

        prompts = dataManager.db.getServerPrompts(user['user_id'], server['server_id'], 9)

        where = server['server_name']

    else:
        prompts = dataManager.db.getUserPrompts(user['user_id'], 9)
        where = 'all servers'

    if prompts is None:
        error = "No prompts found"
        await ctx.send(embed=makeErrorMessage(error))
        print(error)
        return
    
    paths = []
    embed = discord.Embed(title=f"Your recent prompts in {where}.",description="React to replay.", color=0x0000ff)
    for i, prompt in enumerate(prompts):
        try:
            paths.append(prompt['path'])
            embed.add_field(name=f"{i+1}\u20e3  {prompt['command']}",value=f">  {prompt['prompt'][:40]}...",inline=False)
        except FileNotFoundError:
            pass
    
    if len(paths) == 0:
        error = "No prompts found"
        await ctx.send(embed=makeErrorMessage(error))
        print(error)
        return
   
    embed.set_footer(text=footer_msg)
    msg = await ctx.send(embed=embed)

    for i in range(len(paths)):
        await msg.add_reaction(f"{i+1}\u20e3")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in [f"{i+1}\u20e3" for i in range(len(paths))]


    return Result(paths=paths, check=check)

@bot.command(name='download')
async def download(ctx):
   
    result = await replayAndDownloadHelper(ctx)
    paths = result.paths

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=result.check)
    except asyncio.TimeoutError:
        pass
    else:
        index = [f"{i+1}\u20e3" for i in range(len(paths))].index(str(reaction.emoji)) 
        await ctx.send(file=discord.File(paths[index]))
        await ctx.send("File sent.")


@bot.command(name='replay')
async def replay(ctx):

    result = await replayAndDownloadHelper(ctx)
    paths = result.paths

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=result.check)
    except asyncio.TimeoutError:
        pass
    else:
        index = [f"{i+1}\u20e3" for i in range(len(paths))].index(str(reaction.emoji)) 

        voice = ctx.author.voice

        if voice is None:
            error = 'You need to be in a voice channel to use this command.'
            await ctx.send(embed=makeErrorMessage(error))
            print(error)
            return

        channel = voice.channel

        await playAudio(ctx, channel, paths[index])
        

@bot.command(name='delete')
async def delete(ctx):
    user,serverId,serverName = startCommand(ctx)

    args = parseArgs(ctx.message.content)


    if args['public'] and user['privileges'] != 'admin':
        error = "Only admins can delete public voices"
        await ctx.send(embed=makeErrorMessage(error))
        print(error)
        return
     

    if user['privileges'] == 'admin':

        if args['public']:

            voiceToDelete = await run_blocking(dataManager.getVoice, None, args['voiceName'])

            if voiceToDelete is None:
                error = f"Could not find {args['voiceName']}."
                await ctx.send(embed=makeErrorMessage(error))
                print(error)
                return
        else:

            voiceToDelete = await run_blocking(dataManager.getVoice, serverId, args['voiceName'])

            if voiceToDelete is None:
                error = f"Could not find {args['voiceName']} in {serverName}"
                await ctx.send(embed=makeErrorMessage(error))
                print(error)
                return

    else:

        voiceToDelete = await run_blocking(dataManager.getVoice, serverId, args['voiceName'])

        if voiceToDelete is None:
            error = f"Could not find {args['voiceName']}."
            await ctx.send(embed=makeErrorMessage(error))
            print(error)
            return

        if voiceToDelete['user_id'] != user['user_id']:
            error = "You can only delete voices that you added."
            await ctx.send(embed=makeErrorMessage(error))
            print(error)
            return

    dataManager.deleteVoice(voiceToDelete)
   
    embed = discord.Embed(title="Deleted!", description=f"Voice '{voiceToDelete['name']}' deleted successfully.", color=0x00ff00)
    embed.set_footer(text=footer_msg)
    await ctx.send(embed=embed)


@bot.command(name='about')
async def about(ctx):
    startCommand(ctx)
    await ctx.send(embed=getAboutEmbed())


bot.run(TOKEN)