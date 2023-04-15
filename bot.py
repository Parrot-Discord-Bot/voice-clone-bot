#https://discord.com/api/oauth2/authorize?client_id=1095014597871804510&permissions=3196992&scope=bot
#https://discord.com/api/oauth2/authorize?client_id=1095890592753528872&permissions=3196928&scope=bot Dev

import os
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import asyncio
from dotenv import load_dotenv
from elevenLabs import ElevenLabs
import openai
from database import DataBase
from datetime import datetime, timedelta, timezone
import shutil

footer_msg = "This bot was created by: JEFF#1778"
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',help_command=None,intents=intents)
bot.remove_command('help')
eLabs = ElevenLabs(os.getenv('ELEVENLABS_TOKEN'))
openai.api_key = os.getenv('OPENAI_TOKEN')


def makeErrorMessage(reason):
    embed = discord.Embed(title="Error",color=0xff0000)
    embed.add_field(name="Reason",value=reason)
    embed.set_footer(text=footer_msg)
    return embed

def getUsageEmbed(user, username):
    embed = discord.Embed(title=username + "'s usage", color=0x0000ff, description="First Prompt: " + str(user['date_time'].strftime('%b %-d, %Y')))
    embed.add_field(name='Privilages',value=str(user['privileges']))
    embed.add_field(name="Total Characters Used", value=str(user['total_chars_used']))
    embed.add_field(name="Monthly Characters Used", value=str(user['monthly_chars_used']))
    embed.add_field(name="Monthly Character Limit", value=str(user['monthly_char_limit']))
    embed.add_field(name="Monthly Characters Remaining", value= str(user['monthly_char_limit'] - user['monthly_chars_used']))
    embed.add_field(name="Character Credit", value=user['char_credit'])
    embed.add_field(name="Next Character Reset", value=str(datetime.fromtimestamp(eLabs.getCharCountResetDate()).strftime('%b %-d, %Y')))
    embed.set_footer(text=footer_msg)
    return embed

def getAboutEmbed():
    embed = discord.Embed(title="About Parrot",color=0x0000ff, description="[Add Parrot to your server](https://discord.com/api/oauth2/authorize?client_id=1095014597871804510&permissions=3196992&scope=bot)\n\nI built this bot using the [ElevenLabs](https://beta.elevenlabs.io/) and [OpenAi](https://platform.openai.com/) APIs. Contact me <@273300302541881344> if you have any questions, suggestions or find any bugs.")
    embed.add_field(name="Membership", value="Unfortunatly I cant give everyone membership because of the limits on my ElevenLabs account. If enough people pay, I can add more voices, increase character limits and add members. Contact me if you want to become a member.",inline=False)
    embed.add_field(name="Technologies Used", value="Implemented with python + discord library.\nMySql for data storage.\nHosted on my own server in the garage.\nIcon design by <@274019867764588544>.",inline=False)
    embed.set_footer(text=footer_msg)
    return embed

def getVoicesEmbed(serverId, serverName):
    thisServerVoices = db.getServerVoices(serverId)
    publicVoices = db.getPublicVoices()
    thisServerVoicesStr =''
    publicVoicesStr =''

    if thisServerVoices is not None:
        for voice in thisServerVoices:
            thisServerVoicesStr = thisServerVoicesStr + voice['name'] + "\n"
    else:
        thisServerVoicesStr = 'None'

    if publicVoices is not None:
        for voice in publicVoices:
            publicVoicesStr = publicVoicesStr + voice['name'] + "\n"
    else:
        publicVoicesStr = 'None'

    embed = discord.Embed(title="Available Voices", color=0x0000ff)
    embed.add_field(name="Public", value=publicVoicesStr, inline=False)
    embed.add_field(name="In " + str(serverName), value=thisServerVoicesStr, inline=False)
    embed.set_footer(text=footer_msg)
    return embed

def getBuyEmbed():
    embed = discord.Embed(title="Buy More Characters",color=0x0000ff,description='Please have patience, I may not be able to credit your account immediately.')
    embed.add_field(name='Buy 10,000 Characters', value='$6.00 CAD')
    embed.add_field(name='Buy 20,000 Characters', value='$10.00 CAD')

    embed.add_field(name='e-Transfer',value='9112274@gmail.com\nSend discord User ID in the message eg: 273300302541881344.',inline=False)
    embed.add_field(name='Pay pal', value='9112274@gmail.com\nSend discord User ID in the message eg: 273300302541881344.',inline=False)

    embed.add_field(name='Crypto',value="""Send me <@273300302541881344> a message from the account you want credited with the blockchain transaction ID.\n
                                            BTC:   bc1qg944svjz7wydutldlzzfyxt04jaf5l3gvdquln\n
                                            ETH:   0x4C5B8E063A2b23926B9621619e90B5560B0F8AFc\n
                                            XMR:   48fMCSTJqZxFNY5RSwkfoa1GsffjxzZu6Wnk2x49VxKd3UGaaHWd86jTte6fWrtS7m2y6mTFKCCRMBxAVU51zNceAADkLpZ""",inline=False)
    embed.set_footer(text=footer_msg)
    return embed

def checkUser(user):

    discordAccountDate = user.created_at

    now = datetime.now(timezone.utc)
    
    date_difference = now - discordAccountDate
    
    if date_difference < timedelta(days=30):
        return None

    foundUser = db.getUser(user)

    if foundUser is None:
        foundUser = db.addUser(user)

    return foundUser

def parseArgs(command):

    commands = {
        '!speak':['voice','gpt','prompt'],
        '!add':['voice','accent','public'],
        '!delete':['voice','public'],
    }

    accents = ['American', 'British', 'African', 'Australian','Indian']

    args0 = command.split("|")

    args1 = args0[0].split(" ")

    args2 = [arg for arg in args1 if arg != '']

    args3 = [arg.strip() for arg in args2]

    if args3[0] not in commands.keys():
        return None

    currentCommand = args3[0]

    args4 = args3[1:]

    if currentCommand == '!speak':
        if len(args4) == 0:
            return None

        if len(args4) == 1:
            args4.insert(1, None)
        
        try:
            args4.insert(2,command.split("|")[1].strip())
        except IndexError:
            return None

        if args4[1] != 'gpt':
            args4[1] == None
       
           
    if currentCommand == '!add':
        if len(args4) == 0:
            return None

        if len(args4) == 3:
            if args4[2] != 'public':
                args4[2] = None 
        else:
            args4.insert(2, None)

        if args4[1] not in accents:
            args4[1] = None
        
    if currentCommand == '!delete':
        if len(args4) == 0:
            return None
        if len(args4) == 2:
            if args4[1] != 'public':
                args4[1] = None 
        if len(args4) == 1:
            args4.insert(1, None)

    allowedArgs = commands.get(currentCommand)

    outDict = {key: args4[i] if i < len(args4) else None for i, key in enumerate(allowedArgs)}

    return outDict

@bot.command(name='help')
async def help(ctx):
    serverId = ctx.guild.id
    serverName = ctx.guild.name

    user = checkUser(ctx.author)
    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new."))
        return


    commands = ['!speak','!add','!list','!voices','!delete','!usage','!buy','!about']

    def getHelpEmbed(title, description, example):
        toReturn = discord.Embed(title=title, color=0x0000ff, description=description)
        toReturn.add_field(name="Example", value=example)
        return toReturn

    helpList = []

    helpList.append(getHelpEmbed('!speak',"Bot joins voice channel and speaks prompt. 'gpt' is optional","""!speak JordanPeterson | say exactly this\nor
                                                                                                                   !speak JordanPeterson gpt | tell me a story """))
    helpList.append(getHelpEmbed('!add', 'Add a voice to your server by uploading file(s). Accent required. No spaces allowed', """!add Jeff American"""))
    helpList.append(getHelpEmbed('!list', 'View list of recent promts, click reactions to download.', "!list"))
    helpList.append(getVoicesEmbed(serverId, serverName))
    helpList.append(getHelpEmbed('!delete', 'Delete a voice that you added to your server.',"!delete Jeff"))
    helpList.append(getUsageEmbed(user,ctx.author.display_name))
    helpList.append(getBuyEmbed())
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
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Timed out. Please try again.")
    else:
        index = [f"{i+1}\u20e3" for i in range(len(helpList))].index(str(reaction.emoji)) 
        await ctx.send(embed=helpList[index])
        return


#add clickable emoji for replay?
@bot.command(name='speak')
async def speak(ctx):

    args = parseArgs(ctx.message.content)

    serverId = ctx.guild.id

    if args is None:
        await ctx.send(embed=makeErrorMessage('Unable to parse input. Use !help for assistance.'))
        return

    if args['prompt'] is None:
        await ctx.send(embed=makeErrorMessage('Unable to parse prompt. Use !help for assistance.'))
        return

    voice = ctx.author.voice

    if voice is None:
        await ctx.send(embed=makeErrorMessage('You need to be in a voice channel to use this command.'))
        return

    channel = voice.channel

    user = checkUser(ctx.author)
    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new."))
        return

    nextCharReset = datetime.fromtimestamp(eLabs.getCharCountResetDate())
    lastCharReset = user['last_char_reset']

    days_difference = nextCharReset - lastCharReset

    if days_difference > timedelta(days=30):
        db.resetMonthlyUserCharCount(user['user_id'])

    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
   
    eLabsVoice = db.getVoice(serverId, args['voice'])

    if eLabsVoice is None:
        await ctx.send(embed=makeErrorMessage("could not find voice '" + str(args['voice']) + "' in database."))
        return

    await ctx.send("Generating audio...")

    try:
        voice_client: VoiceClient = await channel.connect()
    except:
        return await ctx.send(embed=makeErrorMessage('Failed to connect to the voice channel. Please try again.'))

    if args['gpt']:
        try:
            openaiInput = args['prompt'] + " Do not cut off mid sentence"
            script = openai.Completion.create(model="text-davinci-003",prompt=openaiInput,temperature=0.7,max_tokens=150)["choices"][0]["text"]
        except:
            await ctx.send(embed=makeErrorMessage("Problem with openAi"))
            return
    else:
        script = args['prompt']

    availableMonthlyChars = user['monthly_char_limit'] - user['monthly_chars_used']
    availableCharCredit = user['char_credit']
    availableCharTotal = availableMonthlyChars + availableCharCredit

    if len(script) > availableCharTotal:
       
        await voice_client.disconnect()
        embed = discord.Embed(title="Error", color=0xff0000)
        embed.add_field(name="Reason", value="You have used all of your characters.\n" + str(user['monthly_char_limit']) + " characters will be added on " + nextCharReset.strftime('%b %-d, %Y') + ".\n\nWait or click \U0001F4B0 to buy more characters.")
        embed.set_footer(text=footer_msg)

        msg = await ctx.send(embed=embed)

        money_bag_emoji = "\U0001F4B0"
        await msg.add_reaction(money_bag_emoji)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == money_bag_emoji
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            await ctx.send(embed=getBuyEmbed())
        return
  
    prompt = db.addPrompt(args, eLabsVoice['voice_id'], user['user_id'], serverId, script, len(script))
           
    outputPath = prompt['path']
    eLabs.textToSpeech(script, eLabsVoice['voice_id'], outputPath)

    if len(script) > availableMonthlyChars:
        db.updateUserMonthlyCharCount(user['user_id'], 0)
        remainingChars = len(script) - availableMonthlyChars
        db.updateUserCreditCount(user['user_id'],availableCharCredit-remainingChars)
    else:
        db.updateUserMonthlyCharCount(user['user_id'], user['monthly_chars_used'] + len(script))

    db.updateUserTotalCharCount(user['user_id'], user['total_chars_used'] + len(script))
    audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source=outputPath)

    if not voice_client.is_playing():
        voice_client.play(audio_source, after=lambda e: print('Finished playing', e))

        while voice_client.is_playing():
            await asyncio.sleep(1)
        await voice_client.disconnect()
    else:
        await ctx.send(embed=makeErrorMessage('I am already playing an audio file. Please wait until I finish.'))
    
#members can have 2 custom voices
@bot.command(name='add')
async def add(ctx):
    args = parseArgs(ctx.message.content)
    user = checkUser(ctx.author)
    serverId = ctx.guild.id
    serverName = ctx.guild.name

    if args is None:
        await ctx.send(embed=makeErrorMessage('Unable to parse input. Use !help for assistance.'))
        return

    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new."))
        return
    
    if user['privileges'] == 'normal_user':
        await ctx.send(embed=makeErrorMessage("Only members can add voices to their server."))
        return
    
    if args['voice'] is None:
        await ctx.send(embed=makeErrorMessage('Unable to parse voice name. Use !help for assistance.'))
        return

    if args['public']:
        if user['privileges'] != 'admin':
            await ctx.send(embed=makeErrorMessage("Only admins can add public voices."))
            return
        path = f"voices/public/{args['voice']}"
        serverId = None
        serverName = None
    else:
        path = f"voices/{serverId}/{args['voice']}"

    if args['accent'] is None:
        await ctx.send(embed=makeErrorMessage("""Invalid accent. Choose one of the following\n
                                                American\n
                                                British\n
                                                African\n
                                                Australian\n
                                                Indian\n
                                                Try:\n
                                                !add """ + str(args['voice'] + " American")))
        return

    files = ctx.message.attachments

    if len(files) == 0:
        await ctx.send(embed=makeErrorMessage("You need to attach files to add a new voice."))
        return

    await ctx.send("Adding voice...")

    if not os.path.exists(path):
        os.makedirs(path)
    else:
        await ctx.send(embed=makeErrorMessage("The voice name already exists. Please choose another name."))
        return

    for file in files:
        if file.size >= 10000000:
            await ctx.send(embed=makeErrorMessage("Input file too large. All files must me under 10Mb"))
            shutil.rmtree(path)
            return
            
        allowedTypes = ['audio/aac', 'audio/x-aac', 'audio/x-aiff', 'audio/ogg', 'audio/mpeg', 'audio/mp3', 'audio/mpeg3', 'audio/x-mpeg-3', 'audio/opus', 'audio/wav', 'audio/x-wav', 'audio/webm', 'audio/flac', 'audio/x-flac', 'audio/mp4']
        if file.content_type not in allowedTypes:
            await ctx.send(embed=makeErrorMessage("Input file must be an audio file"))
            shutil.rmtree(path)
            return


        file_path = os.path.join(path, file.filename)
        await file.save(file_path)

    voice_id = eLabs.addVoice(path, args['voice'], args['accent'])

    db.addVoice(voice_id, args['voice'], args['accent'], serverId, serverName, user['user_id'], path)

    embed = discord.Embed(title="Saved!", description=f"Voice '{args['voice']}' saved successfully.", color=0x00ff00)
    embed.add_field(name="Command to play",value=f"!speak {args['voice']} | your message")
    embed.set_footer(text=footer_msg)

    await ctx.send(embed=embed)


@bot.command(name='voices')
async def add(ctx):
    serverId = ctx.guild.id
    serverName = ctx.guild.name
    await ctx.send(embed=getVoicesEmbed(serverId, serverName))
    

#clickable emoji to replay
@bot.command(name='list')
async def list(ctx):
    serverId = ctx.guild.id
    serverName = ctx.guild.name

    user = checkUser(ctx.author)

    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new"))
        return

    thisUserPrompts = db.getUserPrompts(user['user_id'], serverId, 5)

    if thisUserPrompts is None:
        await ctx.send(embed=makeErrorMessage("No prompts found"))
        return

   
    files = []
    embed = discord.Embed(title=f"Your recent prompts in {serverName}.",description="React to download.", color=0x0000ff)
    for i, prompt in enumerate(thisUserPrompts):
        try:
            files.append(discord.File(prompt['path']))
            embed.add_field(name=f"{i+1}\u20e3  {prompt['command']}",value=f">  {prompt['prompt'][:30]}...",inline=False)
        except FileNotFoundError:
            pass
    
    if len(files) == 0:
        await ctx.send(embed=makeErrorMessage("No files found"))
        return
   
    embed.set_footer(text=footer_msg)
    msg = await ctx.send(embed=embed)

    for i in range(len(files)):
        await msg.add_reaction(f"{i+1}\u20e3")

   
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in [f"{i+1}\u20e3" for i in range(len(files))]

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        pass
    else:
        index = [f"{i+1}\u20e3" for i in range(len(files))].index(str(reaction.emoji)) 
        await ctx.send(file=files[index])
        await ctx.send("File sent.")


@bot.command(name='delete')
async def delete(ctx):
    serverId = ctx.guild.id
    serverName = ctx.guild.name

    user = checkUser(ctx.author)

    args = parseArgs(ctx.message.content)

    if user['privileges'] == 'normal_user':
        await ctx.send(embed=makeErrorMessage("Only members can delete voices."))
        return

    if args['public'] and user['privileges'] != 'admin':
        await ctx.send(embed=makeErrorMessage("Only admins can delete public voices"))
        return
     

    if user['privileges'] == 'admin':

        if args['public']:

            voiceToDelete = db.getPublicVoice(args['voice'])

            if voiceToDelete is None:
                await ctx.send(embed=makeErrorMessage("Could not find " + str(args['voice'])))
                return
        else:

            voiceToDelete = db.getServerVoice(serverId, args['voice'])

            if voiceToDelete is None:
                await ctx.send(embed=makeErrorMessage("Could not find " + str(args['voice']) + " in " + str(serverName)))
                return

    else:

        voiceToDelete = db.getServerVoice(serverId, args['voice'])

        if voiceToDelete is None:
            await ctx.send(embed=makeErrorMessage("Could not find " + str(args['voice'])))
            return

        if voiceToDelete['user_id'] != user['user_id']:
            await ctx.send(embed=makeErrorMessage("You can only delete voices that you created"))
            return

    db.deleteVoice(voiceToDelete['voice_id'])
    eLabs.deleteVoice(voiceToDelete['voice_id'])
    shutil.rmtree(voiceToDelete['path'])
    embed = discord.Embed(title="Deleted!", description=f"Voice '{args['voice']}' deleted successfully.", color=0x00ff00)
    embed.set_footer(text=footer_msg)
    await ctx.send(embed=embed)

@bot.command(name='usage')
async def usage(ctx):
    user = checkUser(ctx.author)
    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new."))
        return
    await ctx.send(embed=getUsageEmbed(user,ctx.author.display_name))


@bot.command(name='about')
async def about(ctx):
    await ctx.send(embed=getAboutEmbed())

@bot.command(name='buy')
async def buy(ctx):
    await ctx.send(embed=getBuyEmbed())


db = DataBase()
db.connect()
bot.run(TOKEN)