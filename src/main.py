import discord, logging, config
from github import Auth, Github
from discord.ext import commands
from simplejsondb import DatabaseFolder

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
log = logging.getLogger('discord.bbcd2it')
db = DatabaseFolder(folder="db", default_factory=lambda _: list())

db['issues'] = dict()

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

@bot.tree.command(name="create-issue", description="Create an issue.")
async def create_issue(interaction: discord.Interaction, name: str, description: str):
    await interaction.response.defer(ephemeral=True)
    
    title = name
    description = f"> This is an automated report.\n> This was actually reported by {interaction.user.name} ({interaction.user.id}) on Discord.\n\n{description}"

    repo = gh.get_repo(f"{config.github_repo}")
    issue = repo.create_issue(title=title, body=description)

    embed = discord.Embed(title=f"Created issue #{issue.id}!")
    embed.url = issue.url
    embed.colour = discord.Colour.green()

    db["issues"][issue.url] = {interaction.user.id}
    
    await interaction.followup.send(embed=embed)

bot.run(config.discord_token)