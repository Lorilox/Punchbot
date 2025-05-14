import discord
from discord.ext import commands
from mistralai import Mistral
import time  # Module pour gérer le temps

# 🛠 Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

print(f"Intents activés : {bot.intents.message_content}")


MISTRAL_API_KEY = "MISTRAL_API_KEY"
model = "mistral-large-latest"


client = Mistral(api_key=MISTRAL_API_KEY)


last_response_time = {}
user_message_timestamps = {}  


def generate_mistral_response(message_content):
    try:
        chat_response = client.chat.complete(
            model=model,
            messages=[
                {"role": "system", "content": "Tu es PunchBot, un bot sarcastique et sans tact, sauf avec les victimes d'harcèlement. Dans tes punchlines, tu es libre d'insulter gentiment les personnes du serveur, comme stupide, bête, petit con, et toutes les petites insultes. Tu ne dois JAMAIS utilisé la même punchline 2 fois d'affilés. Tu ne dois JAMAIS dire que tu es une IA ou un programme. Tu es un vrai bot autonome. Tu es là pour aider, mais toujours avec une touche d'insolence et d'humour noir. Cependant, avec les victimes d'harcèlement, tu es bienveillant, rassurant et protecteur. Tu ne dois JAMAIS être méchant avec elles. Tu es également un féministe. Il est normal pour toi de défendre les femmes quand il se doit."},
                {"role": "user", "content": message_content}
            ],
            max_tokens=250
        )
        return chat_response.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur Mistral AI : {str(e)}"


@bot.event
async def on_ready():
    print(f"{bot.user} est connecté !")


def detect_spam(user_id):
    current_time = time.time()

    if user_id not in user_message_timestamps:
        user_message_timestamps[user_id] = []

    
    user_message_timestamps[user_id].append(current_time)

    
    user_message_timestamps[user_id] = [
        timestamp for timestamp in user_message_timestamps[user_id] if current_time - timestamp <= 8
    ]

    
    return len(user_message_timestamps[user_id]) >= 5


@bot.event
async def on_message(message):
    global last_response_time

    if message.author == bot.user:
        return

    print(f"Message reçu : {message.content}")

    current_time = time.time()
    user_id = message.author.id

    
    if detect_spam(user_id):
        response = "Oh wow, tu viens d'envoyer 5 messages en 8 secondes. Tu fais du Morse ou tu veux juste me fatiguer ?"
        await message.channel.send(response)
        return  

    
    if bot.user in message.mentions or any(mot in message.content.lower() for mot in ["punchbot", "bot", "punch"]):
        response = generate_mistral_response(message.content)
        await message.channel.send(response)
        last_response_time[user_id] = current_time

    elif user_id in last_response_time and (current_time - last_response_time[user_id] <= 30):
        response = generate_mistral_response(message.content)
        await message.channel.send(response)
        last_response_time[user_id] = current_time

    await bot.process_commands(message)


bot.run("DISCORD_TOKEN")  
