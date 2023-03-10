import sqlite3
import discord
import psutil
import os
import sqlite3
import datetime
from discord.ext import commands
from utils import default

import sys
sys.path.append("queries")
sys.path.append("helpers")
from queries.userchatqueries import *
from queries.serverchatqueries import *
from helpers.dateformatting import *
from helpers.numberformatting import *

"""
def get_last_week(year, week):
    # Create a datetime object for the given year and week
    dt = datetime.datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w')

    # Subtract one week from the datetime object
    last_week = dt - datetime.timedelta(weeks=1)

    # Return the year and week number of the previous week
    return last_week.year, last_week.strftime('%U')

prev_year, prev_week = get_last_week(year, week)

prev_user_rank = TopWeeklyRank(c_cursor, str(prev_year), (prev_week), id)[0]

rank_diff = prev_user_rank-rank
change_symbol = '🟩' if rank_diff > 0 else '🟥' if rank_diff < 0 else '⬛'
change = '+' + str(rank_diff) if rank_diff > 0 else str(rank_diff) if rank_diff < 0 else '-0'
"""


class MessageLeaderboard(discord.ui.View):
    def __init__(self, ctx, member):
        super().__init__()
        self.ctx = ctx
        self.member = member

    @discord.ui.button(label="Weekly", style=discord.ButtonStyle.blurple)
    async def Weekly(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = self.member.id

        c_DB = sqlite3.connect("chat.db")
        c_cursor = c_DB.cursor()

        year, month, week = get_todays_date()
        first_day, last_day = get_week_dates(year, week)

        unique_chatters_week = distinctChattersWeek(c_cursor, year, week)
        user_rank, id, user_msgs = TopWeeklyRank(c_cursor, year, week, user)
        weekly_server_messages, weekly_server_chars = weeklyServerMessages(c_cursor, year, week)

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_thumbnail(url="https://i.imgur.com/7dyGz0S.jpg")
        embed.set_author(
            name=f"""
                WEEK {week} | {first_day} - {last_day}
                """,
            icon_url=self.ctx.guild.icon)

        top_10_total_msgs = 0
        topten_text = ""
        rank = 1


        for id, msgs in TopWeekly(c_cursor, year, week):
            topten_text += f"`{rank}.` <@{id}> **{abbreviate_number(msgs)}** Msgs | {round(msgs*100/weekly_server_messages, 1)}%\n"

            rank += 1
            top_10_total_msgs += msgs

        topten_text += f"\n**TOP 10 sent  {round(top_10_total_msgs*100/weekly_server_messages, 1)}% of weekly messages**"

        embed.add_field(
            name="Rank | Msgs | % of Weekly Server Msgs",
            value=topten_text, inline=False
        )
        embed.add_field(
            name=f"Server: {unique_chatters_week} Unique Chatters",
            value=f"""
                **{abbreviate_number(weekly_server_messages)}** Messages | {abbreviate_number(weekly_server_chars)} Chars | {int(weekly_server_chars/weekly_server_messages)} Chars/Msg
                    """)
        embed.set_footer(
            icon_url=self.member.avatar,
            text=(
                f"{user_rank}. {self.member.name}#{self.member.discriminator} |"
                f" {abbreviate_number(user_msgs)} Msgs | "
                f"{round(user_msgs*100/weekly_server_messages, 1)}% of the weeks server messages"
                    ))

        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="Monthly", style=discord.ButtonStyle.blurple)
    async def monthly(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = self.member.id

        c_DB = sqlite3.connect("chat.db")
        c_cursor = c_DB.cursor()

        year, month, week = get_todays_date_actually()
        month_name = get_month_name(month)

        unique_chatters_month = distinctChattersMonth(c_cursor, year, month)
        user_rank, id, user_msgs = TopMonthlyRank(c_cursor, year, month, user)
        monthly_server_msgs, monthly_server_chars = monthlyServerMessages(c_cursor, year, month)

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_thumbnail(url="https://i.imgur.com/7dyGz0S.jpg")
        embed.set_author(
            name=f"""
                {month_name} {year}\n
                """,
            icon_url=self.ctx.guild.icon)

        top_10_total_msgs = 0
        topten_text = ""
        rank = 1

        for id, msgs in TopMonthly(c_cursor, year, month):
            top_10_total_msgs += msgs
            topten_text += f"`{rank}.`  <@{id}> **{abbreviate_number(msgs)}** Msgs | {round(msgs*100/monthly_server_msgs, 1)}%\n"
            rank += 1

        topten_text += f"\n**TOP 10 sent  {round(top_10_total_msgs*100/monthly_server_msgs, 1)}% of monthly messages**"

        embed.add_field(
            name="Rank | Msgs | % of Monthly Server Msgs",
            value=topten_text, inline=False
        )
        embed.add_field(
            name=f"Server: {unique_chatters_month} Unique Chatters",
            value=f"""
                **{abbreviate_number(monthly_server_msgs)}** Messages | {abbreviate_number(monthly_server_chars)} Chars | {int(monthly_server_chars/monthly_server_msgs)} Chars/Msg
                    """)
        embed.set_footer(
            icon_url=self.member.avatar,
            text=f"""
                {user_rank}. {self.member.name}#{self.member.discriminator} | {abbreviate_number(user_msgs)} Msgs | {round(user_msgs*100/monthly_server_msgs, 1)}% of the months server messages 
                    """)

        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="Yearly", style=discord.ButtonStyle.blurple)
    async def yearly(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = self.member.id

        c_DB = sqlite3.connect("chat.db")
        c_cursor = c_DB.cursor()

        year, month, week = get_todays_date_actually()

        unique_chatters_year = distinctChattersYear(c_cursor, year)
        user_rank, id, user_msgs = TopYearlyRank(c_cursor, year, user)
        yearly_server_msgs, yearly_server_chars = yearlyServerMessages(c_cursor, year)

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_thumbnail(url="https://i.imgur.com/7dyGz0S.jpg")
        embed.set_author(
            name=f"""
                {year}
                """,
            icon_url=self.ctx.guild.icon)

        top_10_total_msgs = 0
        topten_text = ""
        rank = 1

        for id, msgs in TopYearly(c_cursor, year):
            top_10_total_msgs += msgs
            topten_text += f"`{rank}.`  <@{id}> **{abbreviate_number(msgs)}** Msgs | {round(msgs*100/yearly_server_msgs, 1)}%\n"
            rank += 1

        topten_text += f"\n**TOP 10 sent  {round(top_10_total_msgs*100/yearly_server_msgs, 1)}% of yearly messages**"

        embed.add_field(
            name="Rank | Msgs | % of Yearly Server Msgs",
            value=topten_text, inline=False
        )
        embed.add_field(
            name=f"Server: {unique_chatters_year} Unique Chatters",
            value=f"""
                **{abbreviate_number(yearly_server_msgs)}** Messages | {abbreviate_number(yearly_server_chars)} Chars | {int(yearly_server_chars/yearly_server_msgs)} Chars/Msg
                    """)
        embed.set_footer(
            icon_url=self.member.avatar,
            text=f"""
                {user_rank}. {self.member.name}#{self.member.discriminator} | {abbreviate_number(user_msgs)} Msgs | {round(user_msgs*100/yearly_server_msgs, 1)}% of the years server messages 
                    """)

        await interaction.message.edit(embed=embed)
        await interaction.response.defer()

    @discord.ui.button(label="All-Time", style=discord.ButtonStyle.gray)
    async def alltime(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = self.member.id

        c_DB = sqlite3.connect("chat.db")
        c_cursor = c_DB.cursor()

        unique_chatters = distinctChattersAllTime(c_cursor)
        user_rank, id, user_msgs = TopAllTimeRank(c_cursor, user)
        server_msgs, server_chars = ServerMessages(c_cursor)

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_thumbnail(url="https://i.imgur.com/7dyGz0S.jpg")
        embed.set_author(
            name=f"""
                {"ALL TIME"} CHAT LEADERBOARD
                """,
            icon_url=self.ctx.guild.icon)

        top_10_total_msgs = 0
        topten_text = ""
        rank = 1

        for id, msgs in TopAllTime(c_cursor):
            top_10_total_msgs += msgs
            topten_text += f"`{rank}.` <@{id}> **{abbreviate_number(msgs)}** Msgs | {round(msgs*100/server_msgs, 1)}%\n"
            rank += 1

        topten_text += f"\n**TOP 10 sent  {round(top_10_total_msgs*100/server_msgs, 1)}% of all server messages**"

        embed.add_field(
            name="Rank | Msgs | % of all Server Msgs",
            value=topten_text, inline=False
        )
        embed.add_field(
            name=f"Server: {unique_chatters} Unique Chatters",
            value=f"""
                **{abbreviate_number(server_msgs)}** Messages | {abbreviate_number(server_chars)} Chars | {int(server_chars/server_msgs)} Chars/Msg
                    """)
        embed.set_footer(
            icon_url=self.member.avatar,
            text=f"""
                {user_rank}. {self.member.name}#{self.member.discriminator} | {abbreviate_number(user_msgs)} Msgs | {round(user_msgs*100/server_msgs, 1)}% of all server messages 
                    """)

        await interaction.message.edit(embed=embed)
        await interaction.response.defer()


class userchatleaderboards(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot
        self.config = default.load_json()
        self.process = psutil.Process(os.getpid())

    @commands.command(aliases=['lb', 'leader'])
    async def leaderboard(self, ctx, member: discord.Member = None):
        """
        Chat leaderboards of current periods
        """
        if member == None:
            member = ctx.author
        user = member.id

        embed = discord.Embed(
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at,
            title="B40 Chat Leaderboard",
            description="Most Messages by Member")
        embed.set_thumbnail(url="https://i.imgur.com/7dyGz0S.jpg")
        embed.set_footer(
            text=f"Server ID: {ctx.guild.id}"
        )
        await ctx.send(embed=embed, view=MessageLeaderboard(ctx, member))


async def setup(bot):
    await bot.add_cog(userchatleaderboards(bot))
