import sqlite3
import discord
import psutil
import os
import sqlite3
import datetime
from discord.ext import commands
from utils import default
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
import io

import sys
sys.path.append("queries")
sys.path.append("helpers")
from queries.userchatqueries import *
from queries.serverchatqueries import *
from helpers.dateformatting import *
from helpers.numberformatting import *


class messagegraph(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot
        self.config = default.load_json()
        self.process = psutil.Process(os.getpid())


    @commands.command()
    async def last(self, ctx, int):
        pass












async def setup(bot):
    await bot.add_cog(messagegraph(bot))
