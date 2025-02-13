# Frequently Asked Questions

{% hint style="info" %}
Find quick answers to common questions about Sand Framework.
{% endhint %}

## General Questions

### What is Sand Framework?
Sand Framework is a comprehensive platform for Solana development that combines AI-powered assistance, smart contract analysis, and real-time analytics.

### How do I get support?
Contact [@0xtuareg](https://x.com/0xtuareg) on Twitter for support and inquiries.

### Is Sand Framework open source?
Yes, Sand Framework is open source and welcomes contributions from the community.

## Technical Questions

{% tabs %}
{% tab title="Installation" %}
### Why won't my services start?
Common issues:
* Missing environment variables
* Port conflicts
* Insufficient permissions
* Memory constraints

### How do I update to the latest version?
```bash
git pull origin main
docker-compose pull
docker-compose up -d
```
{% endtab %}

{% tab title="Features" %}
### Which LLM providers are supported?
* OpenAI (GPT-4, GPT-3.5)
* Anthropic Claude
* DeepSeek (local deployment)

### Can I use custom models?
Yes, you can configure custom models in the `.env` file.
{% endtab %}
{% endtabs %}

## AI and Analytics

### How accurate is the contract analysis?
The analysis combines multiple techniques:
* Static analysis
* Pattern matching
* AI-powered review
* Best practice checks

While highly effective, always perform manual review for critical code.

### What data sources are used for analytics?
* On-chain data
* Twitter sentiment
* Market prices
* Developer activity

## Development

### How do I add custom features?

1. Create new module
2. Add API endpoints
3. Write tests
4. Update documentation

### Can I contribute?
Yes! See our [Contributing Guide](../development/contributing.md) for details.

## Security

### How is sensitive data handled?
* Encrypted at rest
* Secure transmission
* Regular audits
* Access controls

### What about API keys?
Never share or commit API keys. Use environment variables and secure secrets management.

## Troubleshooting

{% tabs %}
{% tab title="Common Errors" %}
### API Connection Failed
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs api_gateway
```

### Database Issues
```bash
# Check connection
docker-compose exec db psql -U user -d dbname

# Reset database
docker-compose down -v
docker-compose up -d
```
{% endtab %}

{% tab title="Performance" %}
### Slow Response Times
* Check resource usage
* Monitor API rate limits
* Review cache settings
* Scale services if needed
{% endtab %}
{% endtabs %}

## Contact

For any questions not covered here, reach out:
* Twitter: [@0xtuareg](https://x.com/0xtuareg)

{% hint style="success" %}
We're constantly updating this FAQ based on user feedback and questions!
{% endhint %}
