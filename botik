import discord
import random
from discord.ext import commands
import praw
# Замените 'YOUR_BOT_TOKEN' на ваш действующий токен
TOKEN = 'MTI2MDYxNDgxODk2NTIyOTczMQ.GGq0GL.iEuipPy8wzTE6U_quPI4qf_MGAR1p0NIsWwRnQ'

reddit = praw.Reddit(
    client_id="uTaJFq_yMLk2iZVPY7H0SQ",
    client_secret="qP86opbSR2tdhzfLNxown3Ju3NAViA",
    user_agent="borik lox"
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ID роли тайм-аута (Mute)
MUTE_ROLE_ID = 1261262090379853955

# Слова, которые будет удалять бот
words = ["niga"]
words = [word.lower() for word in words]
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Проверка сообщений на наличие запрещенных слов
    message_content_lower = message.content.lower()
    if any(word in message_content_lower for word in words):
        await message.delete()
        await message.channel.send(f"{message.author.mention}, это слово запрещено!")

    # Проверяем, есть ли у автора сообщения роль тайм-аута
    if any(role.id == MUTE_ROLE_ID for role in message.author.roles):
        await message.delete()
        await message.channel.send(f"{message.author.mention}, ты в муте ебло")

    await bot.process_commands(message)

@bot.command(name='мут')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    role = discord.utils.get(ctx.guild.roles, id=MUTE_ROLE_ID)
    if role not in member.roles:
        await member.add_roles(role, reason=reason)
        await ctx.send(f"{member.mention} получил тайм-аут.")
    else:
        await ctx.send(f"{member.mention} уже имеет роль тайм-аута.")
@bot.command(name='размут')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    role = discord.utils.get(ctx.guild.roles, id=MUTE_ROLE_ID)
    if role in member.roles:
        await member.remove_roles(role, reason=reason)
        await ctx.send(f"пользователю {member.mention} сняли тайм-аут")



# Получение случайного изображения из сабреддита
def get_random_images(subreddit_name, num_images):
    subreddit = reddit.subreddit(subreddit_name)
    posts = list(subreddit.hot(limit=100))  # Получаем горячие посты
    
    # Фильтрация изображений и GIF
    image_posts = [post.url for post in posts if post.url.endswith(('.jpg', '.png', '.gif'))]
    
    if image_posts:
        # Возвращаем случайные изображения или GIF
        return random.sample(image_posts, min(num_images, len(image_posts)))
    else:
        return []

@bot.command(name='hent')
async def random_images(ctx, subreddit_name: str, num_images: int = 1):
    if num_images < 1:
        await ctx.send("Количество изображений должно быть положительным числом.")
        return

    image_urls = get_random_images(subreddit_name, num_images)
    
    if image_urls:
        for url in image_urls:
            await ctx.send(url)
    else:
        await ctx.send(f"Не удалось найти изображения в сабреддите '{subreddit_name}'.")

bot.run(TOKEN)
