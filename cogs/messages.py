import discord
import datetime
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from io import BytesIO
from utils import default
from discord.ext import commands
import sqlite3
import re
# from wordcloud import WordCloud, STOPWORDS
# import matplotlib.pyplot as plt


def mCreateTable(m_cursor):
    m_cursor.execute('CREATE TABLE IF NOT EXISTS words(ID TEXT, word TEXT)')


def m_snipeCreateTable(m_cursor):
    m_cursor.execute(
        'CREATE TABLE IF NOT EXISTS deleted(ID TEXT, date TEXT, message TEXT, channel TEXT)'
    )


def m_editCreateTable(m_cursor):
    m_cursor.execute(
        'CREATE TABLE IF NOT EXISTS edited(ID TEXT, date_before TEXT, date_after TEXT, before_message TEXT, after_message TEXT, channel TEXT)'
    )


def mDataEntry(m_cursor, m_DB, user, list_of_words):
    for word in list_of_words:
        m_cursor.execute('INSERT INTO words VALUES(?, ?)', (user, word))
        m_DB.commit()


def m_snipeDataEntry(m_cursor, m_DB, id, date, message, channel):
    m_cursor.execute('INSERT INTO deleted VALUES(?, ?, ?, ?)',
                     (id, date, message, channel))
    m_DB.commit()


def m_editDataEntry(m_cursor, m_DB, id, date_before, date_after, before, after,
                    channel):
    m_cursor.execute('INSERT INTO edited VALUES(?, ?, ?, ?, ?, ?)',
                     (id, date_before, date_after, before, after, channel))
    m_DB.commit()


def m_editGetLast(m_cursor, m_db):
    m_cursor.execute('SELECT * FROM edited ORDER BY ROWID DESC LIMIT 1')
    data = m_cursor.fetchall()
    return data[0]


def m_snipeGetLast(m_cursor, m_db):
    m_cursor.execute('SELECT * FROM deleted ORDER BY ROWID DESC LIMIT 1')
    data = m_cursor.fetchall()
    return data[0]


def getWords(string):
    # Remove any URLs from the string
    string = re.sub(r'https?://\S+', '', string)

    # Split the string into words
    words = string.split()

    # Return a list of upperwords that contain only letters
    return [
        word.rstrip('!?.,').upper() for word in words if word[0] != '*'
    ]


def readable_timedelta(timestamp1, timestamp2):
    # Parse the timestamps and convert them to datetime objects
    datetime1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S.%f")
    datetime2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S.%f")

    # Calculate the difference between the datetime objects using the relativedelta method
    delta = relativedelta(datetime1, datetime2)

    # Format the timedelta in a readable form and remove the parts with 0
    output = f"{delta.days} day" if delta.days == 1 else f"{delta.days} days" if delta.days > 0 else ""
    if delta.days > 1:
        return output
    output += f" {delta.hours} hr" if delta.hours == 1 else f" {delta.hours} hrs" if delta.hours > 0 else ""
    output += f" {delta.minutes} min" if delta.minutes == 1 else f" {delta.minutes} mins" if delta.minutes > 0 else ""
    output += f" {delta.seconds} sec" if delta.seconds == 1 else f" {delta.seconds} secs" if delta.seconds > 0 else ""
    return output


def print_time_difference(timestamp_str):
    # Parse the input string to a datetime object
    timestamp = datetime.fromisoformat(timestamp_str)

    # Get the current time in UTC
    now = datetime.now(timezone.utc)

    # Calculate the time difference
    time_diff = now - timestamp

    # Convert the time difference to seconds
    seconds = time_diff.total_seconds()

    # Convert the seconds to a human-readable form
    if seconds < 60:
        return (f'{int(seconds)} secs ago')
    elif seconds < 3600:
        return (f'{int(seconds / 60)} mins ago')
    elif seconds < 86400:
        return (f'{int(seconds / 3600)} hours ago')
    else:
        return (f'{int(seconds / 86400)} days ago')


def m_namehistoryCreate(m_cursor):
    m_cursor.execute("""
        CREATE TABLE IF NOT EXISTS namehistory (
        Date DATE,
        Id INTEGER,
        name TEXT,
        UNIQUE (Id, name)
        )""")


def m_namehistoryEntry(m_cursor, m_DB, date, id, name):
    m_cursor.execute("""
            INSERT OR IGNORE INTO namehistory VALUES(?, ?, ?)
            """, (date, id, name))
    m_DB.commit()


class message(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot
        self.config = default.load_json()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and not message.content.startswith('*') and message.channel.id == 739175633673781262:
            m_DB = sqlite3.connect('messages.db')
            m_cursor = m_DB.cursor()
            user = message.author.id
            list_of_words = getWords(message.content)
            mCreateTable(m_cursor)
            mDataEntry(m_cursor, m_DB, user, list_of_words)

            # new##
            date = datetime.now().strftime("%Y-%m-%d")
            name = str(message.author)
            nickname = str(message.author.display_name)

            m_namehistoryCreate(m_cursor)
            m_namehistoryEntry(m_cursor, m_DB, date, user, name)
            m_namehistoryEntry(m_cursor, m_DB, date, user, nickname)

            mentionfilter = str(message.content).split()
            m_cursor.execute("""
                        CREATE TABLE IF NOT EXISTS mentions(
                           author INTEGER,
                           mention INTEGER,
                           count INTEGER,
                           UNIQUE (author, mention)
                           )
                        """)
            for w in mentionfilter:
                if w.startswith("<@") and w.endswith(">"):
                    m_cursor.execute("""
                        INSERT OR IGNORE INTO mentions 
                        VALUES(?, ?, ?)
                        """, (message.author.id, w[2:-1], 0))
                    m_cursor.execute("""
                        UPDATE mentions
                        SET count = count + 1
                        WHERE author = ? AND mention = ?
                        """, (message.author.id, w[2:-1]))
            m_DB.commit()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if len(message.content) >= 1:
            m_DB = sqlite3.connect('messages.db')
            m_cursor = m_DB.cursor()
            m_snipeCreateTable(m_cursor)
            # Get the user who deleted the message
            date = str(message.created_at)
            author = message.author.id
            message_content = message.content
            channel = message.channel.id
            m_snipeDataEntry(m_cursor, m_DB, author, date, message_content,
                             channel)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if len(before.content) >= 1 and before.content != after.content:
            m_DB = sqlite3.connect('messages.db')
            m_cursor = m_DB.cursor()
            m_editCreateTable(m_cursor)
            date_before = str(before.created_at)[:26]
            date_after = str(datetime.utcnow())
            author = before.author.id
            message_content_before = before.content
            message_content_after = after.content
            channel = before.channel.id

            m_editDataEntry(m_cursor, m_DB, author, date_before, date_after,
                            message_content_before, message_content_after,
                            channel)

    @commands.command()
    async def snip(self, ctx):
        m_DB = sqlite3.connect('messages.db')
        m_cursor = m_DB.cursor()

        id, date_before, date_after, before_content, after_content, channel = m_editGetLast(
            m_cursor, m_DB)

        edited_after = readable_timedelta(date_after, date_before)

        sniped_user = await self.bot.fetch_user(id)

        guild = ctx.guild

        print(edited_after)

        embed = discord.Embed(timestamp=ctx.message.created_at,
                              color=discord.Color.blue())
        embed.set_author(name=f"{sniped_user}   •   {sniped_user.id}", icon_url=sniped_user.avatar)
        embed.add_field(name="User", value=f"<@{id}>")
        embed.add_field(name="Channel", value=f"<#{channel}>")
        embed.add_field(name="Edit time", value=edited_after + "\n\u200b")
        embed.add_field(name="Before", value=before_content, inline=False)
        embed.add_field(name="After", value=after_content, inline=False)

        embed.set_footer(icon_url=ctx.author.avatar,
                         text=f"Sniped by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def snipe(self, ctx):
        # snipe description?
        m_DB = sqlite3.connect('messages.db')
        m_cursor = m_DB.cursor()

        id, date, message, channel = m_snipeGetLast(
            m_cursor, m_DB)

        time_deleted = print_time_difference(date)

        sniped_user = await self.bot.fetch_user(id)

        guild = ctx.guild

        embed = discord.Embed(timestamp=ctx.message.created_at,
                              color=discord.Color.blue(),
                              description=message)
        embed.set_author(name=f"{sniped_user}   •   {time_deleted}", icon_url=sniped_user.avatar)

        # embed.set_footer(icon_url=ctx.author.avatar,text=f"Sniped by {ctx.author}")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(message(bot))
