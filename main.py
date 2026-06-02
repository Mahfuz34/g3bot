import discord
import os
import httpx

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    print(f"Message received from {message.author}: {message.content}")
    if message.author == client.user:
        return
    if client.user in message.mentions:
        print("Bot was mentioned, sending to Gemini...")
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()
        if prompt:
            async with message.channel.typing():
                try:
                    async with httpx.AsyncClient() as http:
                        r = await http.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                            json={
                                "model": "google/gemini-2.5-flash-lite",
                                "messages": [{"role": "user", "content": prompt}]
                            },
                            timeout=30
                        )
                        data = r.json()
                        print(f"OpenRouter response: {data}")
                        if "choices" in data:
                            reply = data["choices"][0]["message"]["content"]
                        else:
                            reply = str(data)
                        await message.reply(reply)
                except Exception as e:
                    print(f"Error: {str(e)}")
                    await message.reply(f"Error: {str(e)}")

client.run(os.environ["DISCORD_TOKEN"])
