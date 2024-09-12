import discord
from updates import update
from discord import Client
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from dotenv import find_dotenv
from selenium.webdriver.common.by import By

load_dotenv("C:\\Users\\chenz\\OneDrive\\Desktop\\Github\Mangabot\\variable.env")

token = os.getenv('BOT_TOKEN')
userid = os.getenv('userid')


intents = discord.Intents.default()
# Enable the specific intents you need
intents.messages = True  # Enable message-related events
intents.guilds = True    # Enable guild-related events


# dict for series' release dates
manga_dates = {
    "Sunday": ["Jujutsu Kaisen", "One Piece", "SAKAMOTO DAYS"], 
    "Monday": ["Dandadan"], 
    "Tuesday": ["Chainsaw Man"], 
    "Wednesday": ["OSHI NO KO"],

}

# a subclass of the client class, to handle user's input and correctly send user the link
class mangabot(Client):
    async def on_ready(self):
        print("Bot has connected to Discord")


    async def get_update(self, user):
        nowday = datetime.now()
        weekday = nowday.strftime("%A")
        date = nowday.strftime("%Y-%m-%d")
            
        if weekday in manga_dates:
                    # fetch link for each manga
            titles = manga_dates[weekday]
            for title in titles:
                try:
                    manga = update(title)
                    # here it exists again

                    release_date = manga.chapter_page()
                    url, chapnum = manga.get_chapter()

                    manga.driver.quit()
                    if release_date == date:
                        await user.send(url)
                        await user.send(f"This is the chapter {chapnum} for {title}")
                    else:
                        await user.send(f"There is no new chaper for {title} this week")
                except Exception as e:
                    print(f"Skill Issue: {e}")

    # check if there is a break this week
    async def check_break(self, user, name):
        manga = update(name)

        # to get rid of pop up and cookies, switch langugae
        unformat = manga.check_break()
        release_date = datetime.strptime(unformat, "%Y-%m-%d")
    
        datenow = datetime.now()
        
        seven_days = datenow + timedelta(days=7) 

        manga.driver.quit()

        print(datenow)
        print(release_date)
        print(seven_days)
        
        
        # check if release date is between current and seven days later
        if datenow <= release_date <= seven_days:
            await user.send(f"There is no break this week for {name}")
        else:
            await user.send(f"There is a break this week for {name}")



    async def on_message(self, message):
        # dm user
        if message.author == self.user:
            return
        
        user_message = message.content

        user = message.author


        if user_message == "update":
            # check date
            await self.get_update(user)

        elif user_message[:5] == "check":
            name = user_message[6:]
            await self.check_break(user, name)
        
            
            

bot = mangabot(intents=intents)
bot.run(token)