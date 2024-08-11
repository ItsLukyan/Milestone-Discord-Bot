import os
from dotenv import load_dotenv
from interactions import Client, Intents, slash_command, SlashContext, OptionType
import asyncio
import db_manager

load_dotenv()  # Load environment variables from the .env file

bot = Client(intents=Intents.DEFAULT)
# intents are what events we want to receive from discord, `DEFAULT` is usually fine

# Initialize the database
db = db_manager.DatabaseManager()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.me.name}')

@bot.event
async def on_shutdown():
    db.close()

# Register Command
@slash_command(
    name="register",
    description="Register with the bot",
)
async def register(ctx: SlashContext):
    if "FMF Paid Access" not in [role.name for role in ctx.author.roles]:
        await ctx.send("You don't have the required role to register.", ephemeral=True)
        return
    if db.get_user(ctx.author.id):
        await ctx.send(f"{ctx.author.mention}, you are already registered.", ephemeral=True)
    else:
        db.add_user(str(ctx.author.id), ctx.author.mention)
        await ctx.send(f"{ctx.author.mention}, you have been registered.", ephemeral=True)

# Add PR Command
@slash_command(
    name="pr",
    description="Add a new PR",
    options=[
        {
            "name": "event",
            "description": "The event for which you're adding a PR",
            "type": OptionType.STRING,
            "required": True,
        },
        {
            "name": "pr_value",
            "description": "Your PR value",
            "type": OptionType.STRING,
            "required": True,
        },
    ]
)
async def pr(ctx: SlashContext, event: str, pr_value: str):
    if not db.get_user(ctx.author.id):
        await ctx.send("You need to register first using /register.", ephemeral=True)
        return
    if not db.get_event(event):
        await ctx.send(f"{event} is not a valid event.", ephemeral=True)
        return
    
    db.add_pr(str(ctx.author.id), event, pr_value)
    await ctx.send(f"Your PR for {event} has been updated!", ephemeral=True)

    # Retrieve and post the leaderboard
    leaderboard = db.get_event_leaderboard(event)
    leaderboard_message = "\n".join([f"{i+1}. {entry[0]} - {entry[1]}" for i, entry in enumerate(leaderboard)])
    await ctx.send(f"**{event} Leaderboard:**\n{leaderboard_message}")

# Progress Command
@slash_command(
    name="progress",
    description="Check your progress in a specific event",
    options=[
        {
            "name": "event",
            "description": "The event to check progress for",
            "type": OptionType.STRING,
            "required": True,
        },
    ]
)
async def progress(ctx: SlashContext, event: str):
    if not db.get_user(ctx.author.id):
        await ctx.send("You need to register first using /register.", ephemeral=True)
        return
    if not db.get_event(event):
        await ctx.send(f"{event} is not a valid event.", ephemeral=True)
        return

    prs = db.get_user_prs(str(ctx.author.id), event)
    if prs:
        progress_message = "\n".join([f"{pr[1]}: {pr[0]}" for pr in prs])
        await ctx.send(f"**Your Progress in {event}:**\n{progress_message}", ephemeral=True)
    else:
        await ctx.send(f"You have no PRs recorded for {event}.", ephemeral=True)

# Leaderboard Command
@slash_command(
    name="leaderboard",
    description="Displays the leaderboard for a specific event",
    options=[
        {
            "name": "event",
            "description": "The event to check the leaderboard for",
            "type": OptionType.STRING,
            "required": True,
        },
    ]
)
async def leaderboard(ctx: SlashContext, event: str):
    if not db.get_event(event):
        await ctx.send(f"{event} is not a valid event.", ephemeral=True)
        return

    leaderboard = db.get_event_leaderboard(event)
    if leaderboard:
        leaderboard_message = "\n".join([f"{i+1}. {entry[0]} - {entry[1]}" for i, entry in enumerate(leaderboard)])
        await ctx.send(f"**{event} Leaderboard:**\n{leaderboard_message}")
    else:
        await ctx.send(f"No PRs recorded for {event} yet.", ephemeral=True)

# Overall Best Leaderboard Command
@slash_command(
    name="best",
    description="Check the overall best leaderboard"
)
async def best(ctx: SlashContext):
    overall_leaderboard = db.get_overall_leaderboard()
    leaderboard_message = "\n".join([f"{i+1}. {entry[0]} - {entry[1]} top ranks" for i, entry in enumerate(overall_leaderboard)])
    await ctx.send(f"**Overall Leaderboard:**\n{leaderboard_message}")
    
bot.start(os.getenv("DISCORD_BOT_TOKEN"))