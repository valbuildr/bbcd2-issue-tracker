import discord, logging, config
from github import Auth, Github
from discord.ext import commands
from simplejsondb import DatabaseFolder

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
log = logging.getLogger('discord.bbcd2it')
db = DatabaseFolder(folder="db", default_factory=lambda _: list())

gh_auth = Auth.Token(config.github_personal_access_token)
gh = Github(auth=gh_auth)

@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user.display_name}.")

@bot.command()
@commands.dm_only()
@commands.is_owner()
async def sync(ctx: commands.Context):
    a = await ctx.send(content="Syncing...")
    await bot.tree.sync()
    await a.edit(content="Synced!")

banners = [1191850547138007132, 794083740862644235]

@bot.command()
@commands.dm_only()
async def ban(ctx: commands.Context, user: discord.User):
    if ctx.author.id in banners:
        db["banned"].append(user.id)
        if user.id in banners: banners.pop(banners.index(user.id))

        await ctx.send(content=f"Banned {user.mention}. ({user.id})")

@bot.command()
@commands.dm_only()
async def unban(ctx: commands.Context, user: discord.User):
    if ctx.author.id in banners:
        if user.id in db["banned"]:
            db['banned'].pop(db['banned'].index(user.id))
            await ctx.send(content=f"Unbanned {user.mention}. ({user.id})")
        else:
            await ctx.send(content=f"{user.mention} isn't banned.")

@bot.hybrid_command(name="ping", description="Checks the bot's latency")
async def ping(interaction: commands.Context):
    await interaction.reply(content=f"My ping is {round(bot.latency * 1000)} ms!", ephemeral=True, mention_author=False)

tags = {
    'bug': 1237750431946379296,
    'feature-request': 1237750443313201284,
    'outage': 1237750469795905596
}

@bot.event
async def on_thread_create(thread: discord.Thread):
    if thread.parent.id == 1237750129637855262 and bot.get_guild(1237748599606083605).get_channel(1237750129637855262).get_tag(1237750431946379296) in thread.applied_tags:
        sm = await thread.fetch_message(thread.id)

        ghrepo = gh.get_repo(f"{config.github_repo}")
        issue = ghrepo.create_issue(
            title=thread.name,
            body=f"> This is an automated report.\n> This was actually reported by {sm.author.name} ({sm.author.id}) on Discord.\n\n{sm.content}"
        )

        embed = discord.Embed(title=f"Created issue #{issue.id}!")
        embed.url = issue.html_url
        embed.colour = discord.Colour.green()

        aa = await thread.send(content=f"{issue.html_url}")
        await aa.pin()

@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id == 1237748599606083605:
        await member.add_roles(discord.abc.Snowflake(1237749395206832159))


bot.run(config.discord_token)