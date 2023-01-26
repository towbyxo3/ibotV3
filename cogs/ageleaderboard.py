import time
import discord
import psutil
import os

from discord.ext.commands.context import Context
from discord.ext.commands._types import BotT
from discord.ext import commands
from utils import default, http
import sys
sys.path.append("helpers")
from helpers.dateformatting import *


class Age(discord.ui.View):
    def __init__(self, ctx, num):
        super().__init__()
        self.ctx = ctx
        self.num = num

    @discord.ui.button(label="Registration Date", style=discord.ButtonStyle.blurple)
    async def Registration(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Returns the oldest discord users of the server.
        """
        true_member_count = len([m for m in self.ctx.guild.members if not m.bot])
        print(true_member_count)
        member_list = {}
        guild = self.ctx.guild
        for member in guild.members:
            if not member.bot:
                member_name = member.id
                member_register = str(member.created_at)[:16]
                member_list[member_name] = member_register
        sorted_list = sorted(member_list.items(), key=lambda x: x[1])
        embed = discord.Embed(
            title="Oldest Discord Users in B40",
            timestamp=self.ctx.message.created_at,
            color=discord.Color.red())
        embed.set_author(name="B40 Leaderboard", icon_url="https://i.ibb.co/yqfYjPK/image.png")
        embed.set_thumbnail(url="https://i.imgur.com/7dyGz0S.jpg")

        leaderboard_text = ""
        rank = 1
        for data in sorted_list[:self.num]:
            date = DbYYYformat(data[1][:10])
            user = f"<@{data[0]}>"
            leaderboard_text += f"`{rank}.` | {user} {date}\n"
            rank += 1

        embed.add_field(name="Rank | Member | Created Account on",
                        value=leaderboard_text, inline=False)
        embed.set_footer(text=f"{rank-1} out of {true_member_count} Members")

        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="Join Date", style=discord.ButtonStyle.blurple)
    async def Join(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Returns the oldest members of the server.
        """
        true_member_count = len([m for m in self.ctx.guild.members if not m.bot])

        member_list = {}
        guild = self.ctx.guild
        for member in guild.members:
            if not member.bot:
                member_name = member.id
                member_register = str(member.joined_at)[:16]
                member_list[member_name] = member_register
        sorted_list = sorted(member_list.items(), key=lambda x: x[1])
        embed = discord.Embed(
            title="Oldest B40 Members",
            timestamp=self.ctx.message.created_at,
            color=discord.Color.red())
        embed.set_author(name="B40 Leaderboard", icon_url="https://i.ibb.co/yqfYjPK/image.png")
        embed.set_thumbnail(url="https://i.imgur.com/7dyGz0S.jpg")
        leaderboard_text = ""
        rank = 1
        for data in sorted_list[:self.num]:
            date = DbYYYformat(data[1][:10])
            user = f"<@{data[0]}>"
            leaderboard_text += f"`{rank}.` | {user} {date}\n"
            rank += 1

        embed.add_field(name="Rank | Member | Joined B40 on", value=leaderboard_text, inline=False)
        embed.set_footer(text=f"{rank-1} out of {true_member_count} Members")

        await interaction.message.edit(embed=embed)
        await interaction.response.defer()


class AgeLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot
        self.config = default.load_json()
        self.process = psutil.Process(os.getpid())

    @commands.command()
    async def age(self, ctx, num=10):
        """
        Oldest Users in B40 by Registration Date and B40 Join Date
        """
        true_member_count = len([m for m in ctx.guild.members if not m.bot])

        embed = discord.Embed(
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at,
            title="Select Age Criteria",
            description="Oldest B40 Members by Registration Date or B40 Join Date"
        )
        embed.set_thumbnail(url="https://i.imgur.com/7dyGz0S.jpg")
        embed.set_footer(
            text=f"Server ID: {ctx.guild.id} | {true_member_count} Members"
        )

        await ctx.send(embed=embed, view=Age(ctx, num))


async def setup(bot):
    await bot.add_cog(AgeLeaderboard(bot))
