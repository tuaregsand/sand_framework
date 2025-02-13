# Contributing

{% hint style="info" %}
Thank you for your interest in contributing to Sand Framework! This guide will help you get started.
{% endhint %}

## Contact

For all inquiries, feature requests, and discussions, please reach out via Twitter:
* [@0xtuareg](https://x.com/0xtuareg)

## Getting Started

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone <your-fork-url>
cd sand-framework

# Set up development environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## Code Standards

{% tabs %}
{% tab title="Python" %}
* Follow PEP 8
* Use type hints
* Write docstrings
* Add unit tests
{% endtab %}

{% tab title="Documentation" %}
* Clear and concise
* Include examples
* Keep up-to-date
* Use proper markdown
{% endtab %}
{% endtabs %}

## Pull Request Process

1. **Branch Naming**
   ```
   feature/description
   fix/issue-description
   docs/update-section
   ```

2. **Commit Messages**
   ```
   feat: add new analytics feature
   fix: resolve memory leak in AI service
   docs: update installation guide
   ```

3. **Testing**
   ```bash
   # Run tests
   pytest tests/
   
   # Check code style
   black .
   flake8
   ```

4. **Documentation**
   * Update relevant docs
   * Add inline comments
   * Update changelog

## Feature Requests

Have an idea for a new feature? Contact [@0xtuareg](https://x.com/0xtuareg) on Twitter to discuss it!

{% hint style="warning" %}
Please make sure to check existing issues and discussions before proposing new features.
{% endhint %}
