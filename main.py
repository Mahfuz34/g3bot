import discord
import os
import httpx

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

SYSTEM_PROMPT = """You are a sharp, concise financial and market analyst assistant. 
When asked about stocks, crypto, or market moves:
- Search the web for the latest news and data first
- Give a direct, confident answer based on what you find
- Keep it short and punchy — 3 to 5 sentences max
- Lead with the actual reason, not disclaimers
- No fluff, no "I need more info", no generic lists
- Write like a trader talking to another trader"""

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if client.user in message.mentions:
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()
        if prompt:
            async with message.channel.typing():
                try:
                    async with httpx.AsyncClient() as http:
                        r = await http.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"
                            },
                            json={
                                "model": "google/gemini-2.5-flash",
                                "messages": [
                                    {"role": "system", "content": SYSTEM_PROMPT},
                                    {"role": "user", "content": prompt}
                                ],
                                "plugins": [{"id": "web"}]
                            },
                            timeout=60
                        )
                        data = r.json()
                        if "choices" in data:
                            reply = data["choices"][0]["message"]["content"]
                            if len(reply) > 1900:
                                reply = reply[:1900] + "...\n*(ask me to continue)*"
                        else:
                            reply = str(data)
                        await message.reply(reply)
                except Exception as e:
                    await message.reply(f"Error: {str(e)}")

client.run(os.environ["DISCORD_TOKEN"])
