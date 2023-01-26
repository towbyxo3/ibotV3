import sqlite3
import discord
import psutil
import os
from discord.ext import commands
from utils import default
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
import io
import sys
import random
from discord.ext.commands.context import Context
from discord.ext.commands._types import BotT
from queries.userchatqueries import TopYearlyRank



from queries.serverchatqueries import *
from helpers.dateformatting import *
from helpers.numberformatting import *

sys.path.append("queries")
sys.path.append("helpers")



class profile(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.AutoShardedBot = bot
        self.config = default.load_json()
        self.process = psutil.Process(os.getpid())











    @commands.command()
    async def azz(self, ctx):

        # Find the member with the specified name
        member = ctx.guild.get_member_named(name)

        # Check if a member was found
        if member is not None:
            # Send a greeting message to the member
            await ctx.send(f'Hello, {member.mention}!')
        else:
            # Send an error message if no member was found
            await ctx.send(f'I could not find a member with the name "{name}"')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Sends a welcome message banner to the channel.

        member: member who joined guild
        """

        # get channel object and member url
        channel = self.bot.get_channel(1057132842259325029)
        avatar_url = member.avatar

        # Download the members's avatar and create a circular version of it
        avatar_response = requests.get(avatar_url)
        avatar_image = Image.open(io.BytesIO(avatar_response.content))
        avatar_image = avatar_image.resize((250, 250))
        mask = Image.new("L", avatar_image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + avatar_image.size, fill=255)
        avatar_image = ImageOps.fit(avatar_image, mask.size, centering=(0.5, 0.5))
        avatar_image.putalpha(mask)

        # Create a new image to draw the outline on
        outline_image = Image.new("RGBA", avatar_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(outline_image)

        # Draw an outline around the circular avatar
        draw.ellipse((0, 0) + avatar_image.size, outline=(255, 255, 255), width=5)

        # Combine the circular avatar and the outline into a single image
        avatar_outline_image = Image.alpha_composite(avatar_image, outline_image)

        # Open the base image
        base_image = Image.open(f"welcome_base_images/base_image{random.randint(0,26)}.png")

        # Paste the circular avatar with the outline onto the base image
        base_image.paste(avatar_outline_image, (387, 160), mask=mask)

        # rank, id, msgs =  TopYearlyRank(cursor, str(2022), str(member.id))

        true_member_count = len([m for m in member.guild.members if not m.bot])

        # Add the user's name to the image
        draw = ImageDraw.Draw(base_image)
        font = ImageFont.truetype("arial.ttf", 45)
        font_member_count = ImageFont.truetype("arial.ttf", 30)
        draw.text(
            (512, 90),
            f"{member.name}#{member.discriminator} just joined the server.",
            font=font,
            fill=(255, 255, 255),
            anchor="ms",
            stroke_fill=None,
            stroke_width=None
        )
        draw.text(
            (512, 140),
            f"Member #{true_member_count}",
            font=font_member_count,
            fill=(255, 255, 255),
            anchor="ms"
        )

        # Save the final image
        base_image.save("welcome_base_images/custom_image.png")

        # Send the final image to the user
        await channel.send(f"<@{member.id}>",file=discord.File("welcome_base_images/custom_image.png"))

async def setup(bot):
    await bot.add_cog(profile(bot))
