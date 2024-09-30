import discord
import random
from discord.ext import commands
import praw
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env

TOKEN = os.getenv('TOKEN')

reddit= praw.Reddit(
    CLIENT_ID="uTaJFq_yMLk2iZVPY7H0SQ",
    CLIENT_SECRET="qP86opbSR2tdhzfLNxown3Ju3NAViA",
    user_agent="borik lox"
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ID роли тайм-аута (Mute)
MUTE_ROLE_ID = 1261262090379853955

ALLOWED_ROLE_IDS = [1101454647794876417, 1101455245176995950]

def has_allowed_role():
    """ Проверка наличия одной из разрешенных ролей у пользователя. """
    async def predicate(ctx):
        return any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles)
    return commands.check(predicate)

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




# Путь к файлу для сохранения списка пользователей
USERS_FILE = 'users.json'
POINTS_FILE = 'points.json'
# Загружаем список пользователей из файла
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Сохраняем список пользователей в файл
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def load_points():
    try:
        with open(POINTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
def save_points(points):
    with open(POINTS_FILE, 'w') as f:
        json.dump(points, f)

async def list_users(ctx):
    users = load_users()
    points = load_points()  # Загружаем баллы пользователей
    if users:
        user_info = []
        for user_id in users:
            user_name = f'<@{user_id}>'
            user_points = points.get(user_id, 0)  # Получаем баллы пользователя, если нет - 0
            user_info.append(f'{user_name} has {user_points} points')
        await ctx.send('В списке следующие пользователи:\n' + '\n'.join(user_info))
    else:
        await ctx.send('Список пользователей пуст.')

# Добавляем команду для добавления пользователя в список и создание баллов
@bot.command(name='list_add')
async def add_user(ctx, member: discord.Member):
    users = load_users()
    points = load_points()

    if member.id not in users:
        users.append(member.id)
        points[member.id] = 0  # Добавляем пользователя с нулевыми баллами
        save_users(users)
        save_points(points)
        await ctx.send(f'{member.name} был добавлен в список!')
    else:
        await ctx.send(f'{member.name} уже в списке.')

# Команда для отображения списка пользователей (каждый на новой строке)
@bot.command(name='list')
async def list_users(ctx):
    users = load_users()
    points = load_points()  # Загружаем баллы пользователей
    if users:
        user_info = []
        for user_id in users:
            user_name = f'<@{user_id}>'
            user_points = points.get(str(user_id), 0)  # Получаем баллы пользователя, если нет - 0
            user_info.append(f'{user_name} has {user_points} points')
        await ctx.send('В списке следующие пользователи:\n' + '\n'.join(user_info))
    else:
        await ctx.send('Список пользователей пуст.')

# Команда для удаления пользователя из списка и удаления их баллов
@bot.command(name='list_remove')
async def remove_user(ctx, member: discord.Member):
    users = load_users()
    points = load_points()

    if member.id in users:
        users.remove(member.id)
        points.pop(str(member.id), None)  # Убираем пользователя из баллов
        save_users(users)
        save_points(points)
        await ctx.send(f'{member.name} был удалён из списка.')
    else:
        await ctx.send(f'{member.name} нет в списке.')

# Команда для добавления баллов пользователю (печенька)
@bot.command(name='печенька')
@has_allowed_role()  # Ограничение по ролям
async def give_cookie(ctx, member: discord.Member, points_to_add: int = 1):
    points = load_points()

    if str(member.id) in points:
        points[str(member.id)] += points_to_add
        save_points(points)
        await ctx.send(f'{member.name} получил {points_to_add} балл(ов)! Теперь у него {points[str(member.id)]} баллов.')
    else:
        await ctx.send(f'{member.name} не найден в списке пользователей.')

@bot.command(name='забрать_печеньку')
@has_allowed_role()  # Ограничение по ролям
async def take_cookie(ctx, member: discord.Member, points_to_remove: int = 1):
    points = load_points()

    if str(member.id) in points:
        points[str(member.id)] = max(points[str(member.id)] - points_to_remove, 0)  # Не допускаем отрицательные баллы
        save_points(points)
        await ctx.send(f'У {member.name} было снято {points_to_remove} балл(ов). Теперь у него {points[str(member.id)]} баллов.')
    else:
        await ctx.send(f'{member.name} не найден в списке пользователей.')

# Обработка ошибок
@give_cookie.error
@take_cookie.error
async def cookie_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('У вас нет прав на выполнение этой команды.')







bot.run(TOKEN)
