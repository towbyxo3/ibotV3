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


class PastWeek(discord.ui.View):
    def __init__(self, ctx, member, year, week):
        super().__init__()
        self.ctx = ctx
        self.member = member
        self.year = year
        self.week = week


    @discord.ui.button(label=f"Server", style=discord.ButtonStyle.blurple)
    async def Server(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = self.member.id

        c_DB = sqlite3.connect("chat.db")
        c_cursor = c_DB.cursor()

        year, week = self.year, self.week
        print(year)
        print(week)
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




        for date in get_dates_for_week(int(year), int(week))[::-1]:
            ids = []
            topten_text=""
            rank = 1
            distinct_day = distinctChattersDay(c_cursor, date)
            daily_sv_msgs, daily_sv_chars = dailyServerMessages(c_cursor, date)
            if daily_sv_msgs is None:
                continue
            name=f"{DbYYYformat(date)} | {abbreviate_number(daily_sv_msgs)} Messages by {distinct_day} Members\n"
            for id, msgs in TopDaily(c_cursor, date):
                if id == self.member.id:
                    topten_text +=f"`{rank}.` <@{id}> **{msgs}** Messages | **{round(msgs*100/daily_sv_msgs, 1)}%** of Server\n"
                    ids.append(id)
                    rank+=1
                    continue
                ids.append(id)
                topten_text +=f"`{rank}.` <@{id}> {msgs}\n"
                rank+=1
            user_rank_d, id, user_msgs_d = TopDailyRank(c_cursor, date, self.member.id)
            if id not in ids:
                topten_text +=f"`{user_rank_d}.` <@{id}> **{user_msgs_d}** Messages | **{round(user_msgs_d*100/daily_sv_msgs, 1)}%** of Server "




            embed.add_field(
            name=name,
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
        year, week =get_previous_week(int(self.year), int(self.week))
        self.year, self.week = year, week
        await interaction.response.defer()


class pastweek(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot
        self.config = default.load_json()
        self.process = psutil.Process(os.getpid())

    @commands.command()
    async def recent(self, ctx, member: discord.Member = None):
        """
        Chat leaderboards of current periods
        """
        if member == None:
            member = ctx.author
        user = member.id

        embed = discord.Embed(
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at,
            title="B40 Messages",
            description="Recent Data")
        embed.set_thumbnail(url="https://i.imgur.com/7dyGz0S.jpg")
        embed.set_footer(
            text=f"Server ID: {ctx.guild.id}"
        )


        year, month, week = get_todays_date()
        print(year, month, week)
        await ctx.send(embed=embed, view=PastWeek(ctx, member, year, week))


async def setup(bot):
    await bot.add_cog(pastweek(bot))
