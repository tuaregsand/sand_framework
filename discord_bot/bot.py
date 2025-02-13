import os
import discord
from discord.ext import commands, tasks
import aiohttp
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class SolanaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        
        # Configuration
        self.api_base_url = os.getenv("API_BASE_URL", "http://api:8000")
        self.api_key = os.getenv("API_KEY")
        self.alert_channel_id = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
        
        # Initialize HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Add commands
        self.setup_commands()
        
        # Start background tasks
        self.check_alerts.start()

    async def setup_hook(self):
        """Set up bot hooks and initialize session."""
        self.session = aiohttp.ClientSession(headers={"X-API-Key": self.api_key})

    def setup_commands(self):
        """Set up bot commands."""
        
        @self.command(name="price")
        async def price(ctx):
            """Get current Solana price."""
            try:
                async with self.session.get(f"{self.api_base_url}/analytics/price") as response:
                    if response.status == 200:
                        data = await response.json()
                        await ctx.send(f"🚀 Current Solana price: ${data['price_usd']:.2f} USD")
                    else:
                        await ctx.send("❌ Failed to fetch price data")
            except Exception as e:
                logger.error(f"Error in price command: {str(e)}")
                await ctx.send("❌ An error occurred while fetching the price")

        @self.command(name="sentiment")
        async def sentiment(ctx):
            """Get current Solana sentiment analysis."""
            try:
                async with self.session.get(f"{self.api_base_url}/analytics/sentiment") as response:
                    if response.status == 200:
                        data = await response.json()
                        score = data['sentiment_score']
                        emoji = "🟢" if score > 0 else "🔴" if score < 0 else "⚪"
                        await ctx.send(
                            f"{emoji} Current Solana sentiment: {score:.2f}\n"
                            f"Confidence: {data.get('confidence', 0):.2f}"
                        )
                    else:
                        await ctx.send("❌ Failed to fetch sentiment data")
            except Exception as e:
                logger.error(f"Error in sentiment command: {str(e)}")
                await ctx.send("❌ An error occurred while fetching sentiment data")

        @self.command(name="ask")
        async def ask(ctx, *, question: str):
            """Ask a Solana development question."""
            try:
                async with self.session.post(
                    f"{self.api_base_url}/dev/ask",
                    json={"question": question}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Split long responses into multiple messages if needed
                        answer = data['answer']
                        if len(answer) > 1900:  # Discord message limit is 2000
                            parts = [answer[i:i+1900] for i in range(0, len(answer), 1900)]
                            for i, part in enumerate(parts):
                                await ctx.send(f"Part {i+1}/{len(parts)}:\n{part}")
                        else:
                            await ctx.send(answer)
                    else:
                        await ctx.send("❌ Failed to get an answer")
            except Exception as e:
                logger.error(f"Error in ask command: {str(e)}")
                await ctx.send("❌ An error occurred while processing your question")

        @self.command(name="create")
        async def create_project(ctx, name: str, *, description: str = None):
            """Create a new Solana project scaffold."""
            try:
                payload = {
                    "name": name,
                    "description": description
                }
                async with self.session.post(
                    f"{self.api_base_url}/dev/project/new",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        await ctx.send(
                            f"✅ Project created successfully!\n"
                            f"📁 Path: {data.get('path', 'N/A')}\n"
                            f"ℹ️ {data.get('result', '')}"
                        )
                    else:
                        await ctx.send("❌ Failed to create project")
            except Exception as e:
                logger.error(f"Error in create_project command: {str(e)}")
                await ctx.send("❌ An error occurred while creating the project")

        @self.command(name="help")
        async def help_command(ctx):
            """Show help information."""
            help_text = """
            🤖 **Solana Multi-Agent Bot Commands**
            
            📊 **Analytics**
            • `!price` - Get current Solana price
            • `!sentiment` - Get current market sentiment
            
            💻 **Development**
            • `!ask <question>` - Ask a Solana development question
            • `!create <name> [description]` - Create a new Solana project
            
            ℹ️ **System**
            • `!help` - Show this help message
            """
            await ctx.send(help_text)

    @tasks.loop(minutes=5.0)
    async def check_alerts(self):
        """Check for new alerts periodically."""
        if not self.alert_channel_id:
            return

        try:
            channel = self.get_channel(self.alert_channel_id)
            if not channel:
                logger.error("Alert channel not found")
                return

            async with self.session.get(f"{self.api_base_url}/analytics/alerts") as response:
                if response.status == 200:
                    alerts = await response.json()
                    for alert in alerts:
                        emoji = "💰" if alert["type"] == "price_alert" else "📊"
                        await channel.send(f"{emoji} **Alert**: {alert['message']}")
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")

    async def close(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
        await super().close()

def run_bot():
    """Run the Discord bot."""
    bot = SolanaBot()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN not found in environment variables")
    
    bot.run(token)

if __name__ == "__main__":
    run_bot()
