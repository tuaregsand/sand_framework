# Discord Integration

{% hint style="info" %}
Interact with Sand Framework directly from your Discord server using our powerful bot integration.
{% endhint %}

## Features

{% tabs %}
{% tab title="AI Commands" %}
* `/sand help` - Show available commands
* `/sand analyze <code>` - Analyze Solana code
* `/sand explain <error>` - Explain an error
* `/sand optimize <code>` - Suggest optimizations
{% endtab %}

{% tab title="Analytics Commands" %}
* `/price <token>` - Get token price
* `/sentiment <token>` - Get market sentiment
* `/alert set <condition>` - Set price alerts
{% endtab %}
{% endtabs %}

## Bot Setup

1. Create a Discord Application:
   * Go to [Discord Developer Portal](https://discord.com/developers/applications)
   * Create a new application
   * Add a bot user
   * Copy the bot token

2. Configure Permissions:
```
Required Permissions:
- Send Messages
- Read Messages/View Channels
- Use Slash Commands
- Embed Links
```

3. Set Environment Variables:
```bash
DISCORD_TOKEN=your_bot_token
DISCORD_PREFIX=/sand
DISCORD_GUILD_ID=your_guild_id  # Optional, for single server
```

## Command Usage

### Code Analysis
```
/sand analyze
```
```python
@program
def initialize(ctx, data):
    # Your Solana program
    pass
```

### Price Tracking
```
/price SOL
```
Response:
```
SOL/USD: $100.25 (↑2.5%)
24h Volume: $1.2B
```

## Customization

Create custom commands in `bot/cogs`:

```python
from discord.ext import commands

class CustomCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def custom(self, ctx):
        await ctx.send("Custom command!")

def setup(bot):
    bot.add_cog(CustomCog(bot))
```

## Webhooks

Configure Discord webhooks for automated notifications:

{% tabs %}
{% tab title="Price Alerts" %}
```python
async def send_price_alert(webhook_url, token, price):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        await webhook.send(f"🚨 {token} reached ${price}!")
```
{% endtab %}

{% tab title="Security Alerts" %}
```python
async def send_security_alert(webhook_url, severity, message):
    embed = discord.Embed(
        title=f"Security Alert: {severity}",
        description=message,
        color=discord.Color.red()
    )
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        await webhook.send(embed=embed)
```
{% endtab %}
{% endtabs %}

{% hint style="warning" %}
Keep your bot token secure and never share it publicly!
{% endhint %}
