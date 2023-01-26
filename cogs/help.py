import sqlite3
import discord
import psutil
import os
from discord import ui
import sqlite3
import datetime
from typing import Union

from discord.ext import commands
from utils import default
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
import io
import aiohttp


def embedFormat(list):
    return '\n'.join([f"`{i}`" for i in list])


class help(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot
        self.config = default.load_json()
        self.process = psutil.Process(os.getpid())

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="B40 Commands", color=discord.Color.blue())


        moderation = ["ban", "kick", "find", "massban", "mute", "nickname", "prune", "unban", "unmute"]
        embed.add_field(
            name="Moderation",
            value=embedFormat(moderation),
            inline= False
            )

        Info = ["userinfo", "serverinfo", "avatar", "about", "names", "invite", "country", "covid", "ping", "roles"]
        embed.add_field(
            name="Info",
            value=embedFormat(Info),
            inline= False
            )

        Leaderboards = ["leaderboard", "userpeak", "serverpeak", "age", "crowns", "country"]
        embed.add_field(
            name="Leaderboard",
            value=embedFormat(Leaderboards)
            )
        Vocabulary = ["vocab", "vocabuser", "said", "wordcloud", "wordcloudserver"]
        embed.add_field(
            name="Vocabulary",
            value=embedFormat(Vocabulary),
            inline= False
            )

        VC = ["massmove", "massmoveall"]
        embed.add_field(
            name="VC",
            value=embedFormat(VC),
            inline= False
            )

        Fun = ["snipe", "snip", "dm", "compare"]
        embed.add_field(
            name="Fun",
            value=embedFormat(Fun),
            inline= False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(help(bot))
