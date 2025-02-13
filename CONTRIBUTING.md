# Contributing to Smart Contract Analysis Framework

## Welcome!

Thank you for considering contributing to our Smart Contract Analysis Framework. This document provides guidelines and best practices for contributing.

## Code of Conduct

This project adheres to the Contributor Covenant code of conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps to reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed and what behavior you expected to see
* Include any relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* A clear and descriptive title
* A detailed description of the proposed functionality
* Any possible drawbacks or alternatives you've considered
* If possible, a code sketch of how you envision the feature working

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the test suite
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Process

### Setting Up Development Environment

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Code Style

This project follows strict code style guidelines:

1. **Python Code Style**
   * Follow PEP 8
   * Use type hints
   * Maximum line length: 88 characters
   * Use docstrings for all public methods and classes

2. **Documentation**
   * Keep documentation up-to-date
   * Use clear and concise language
   * Include examples where appropriate

3. **Testing**
   * Write unit tests for all new features
   * Maintain test coverage above 90%
   * Include integration tests for complex features

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
Add smart contract gas optimization detection

- Implement pattern matching for common gas inefficiencies
- Add unit tests for optimization detection
- Update documentation with new feature
- Fixes #123
```

### Testing Guidelines

1. **Unit Tests**
   * Place tests in the `tests/` directory
   * Name test files with `test_` prefix
   * Use descriptive test method names
   * Include both positive and negative test cases

2. **Integration Tests**
   * Test interaction between components
   * Include performance tests where relevant
   * Test edge cases and error conditions

3. **Running Tests**
   ```bash
   pytest
   pytest --cov=sandframework tests/
   ```

### Documentation

1. **Code Documentation**
   * Use clear and concise docstrings
   * Include type hints
   * Document exceptions and return values
   * Add examples for complex functionality

2. **API Documentation**
   * Keep API documentation up-to-date
   * Include request/response examples
   * Document all parameters and return values

### Review Process

1. **Code Review Checklist**
   * Code follows style guidelines
   * Tests are included and passing
   * Documentation is updated
   * No security vulnerabilities introduced
   * Performance impact is considered

2. **Security Review**
   * Check for common vulnerabilities
   * Review access control
   * Validate input handling
   * Verify error handling

## Release Process

1. **Version Numbering**
   * Follow semantic versioning (MAJOR.MINOR.PATCH)
   * Document all changes in CHANGELOG.md

2. **Release Checklist**
   * All tests passing
   * Documentation updated
   * CHANGELOG.md updated
   * Version number updated
   * Release notes prepared

## Getting Help

* Join our Discord channel
* Check the documentation
* Open an issue for questions
* Tag questions with appropriate labels

## Recognition

Contributors will be recognized in:
* CONTRIBUTORS.md file
* Release notes
* Project documentation

Thank you for contributing to making our Smart Contract Analysis Framework better!
