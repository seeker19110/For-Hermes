# Contributing to 12-Factor Agents

First off, thank you for considering contributing to 12-Factor Agents! This project aims to help developers build reliable, production-grade LLM applications, and your contributions help make that possible.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Issues](#reporting-issues)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Documentation Improvements](#documentation-improvements)
  - [Code Contributions](#code-contributions)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [License](#license)

## Code of Conduct

By participating in this project, you agree to maintain a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## How Can I Contribute?

### Reporting Issues

If you find a bug or have a question:

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** with a clear title and description
3. **Include relevant details** like error messages, screenshots, or steps to reproduce

### Suggesting Enhancements

Have an idea for a new factor or improvement?

1. **Check the discussions** at [GitHub Discussions](https://github.com/humanlayer/12-factor-agents/discussions)
2. **Open a new discussion** to gather feedback before implementing
3. **Reference related factors** if your suggestion builds on existing content

### Documentation Improvements

Documentation contributions are highly valued! This includes:

- Fixing typos and grammatical errors
- Improving clarity of existing content
- Adding examples or use cases
- Translating content

### Code Contributions

For code contributions to the template or tools:

1. **Fork the repository**
2. **Create a feature branch** from `main`
3. **Make your changes** following our style guidelines
4. **Test your changes** thoroughly
5. **Submit a pull request**

## Development Setup

### Prerequisites

- Node.js 20+ (recommended)
- npm, yarn, or bun

### Getting Started

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/12-factor-agents.git
cd 12-factor-agents

# Install dependencies
make setup
# or manually: npm install

# For the template package
cd packages/create-12-factor-agent/template
npm install
```

### Running the Template Agent

```bash
cd packages/create-12-factor-agent/template

# Set up environment variables
export OPENAI_API_KEY=your_key_here
# or use BASETEN_API_KEY depending on your configuration

# Generate BAML client
npx baml-cli generate

# Run the agent
npx tsx src/index.ts "hello"
```

### Running Tests (walkthroughgen)

```bash
cd packages/walkthroughgen
npm install
npm test
```

## Pull Request Process

### Branch Naming

Use descriptive branch names:

- `docs/fix-readme-typos` - Documentation fixes
- `feat/add-new-factor` - New features
- `fix/template-bug` - Bug fixes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): short description

- Detailed change 1
- Detailed change 2
```

**Types:**
- `docs` - Documentation changes
- `feat` - New features
- `fix` - Bug fixes
- `chore` - Maintenance tasks
- `style` - Code style changes (formatting, etc.)
- `test` - Adding or updating tests
- `refactor` - Code refactoring

**Examples:**
```
docs(content): Fix typos in factor-03-own-your-context-window.md

- Fix spelling error 'libriaries' to 'libraries'
- Correct grammar in example code comments
```

```
feat(template): Add support for Claude as LLM provider

- Add Claude client configuration in clients.baml
- Update README with Claude setup instructions
```

### PR Checklist

Before submitting your PR:

- [ ] Code follows the project's style guidelines
- [ ] Documentation is updated if needed
- [ ] Commit messages follow conventional format
- [ ] All existing tests pass
- [ ] New functionality includes tests (if applicable)

## Style Guidelines

### Markdown

- Use ATX-style headers (`#`, `##`, etc.)
- Use fenced code blocks with language specifiers
- Keep lines under 120 characters when possible
- Use relative links for internal references

### TypeScript

- Use TypeScript for all new code
- Follow existing patterns in the codebase
- Include type annotations for function parameters and return types

### BAML

- Follow the patterns in existing `.baml` files
- Include descriptive comments for complex prompts
- Add tests for new functions

## License

By contributing to 12-Factor Agents, you agree that your contributions will be licensed under:

- **Code**: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
- **Content & Images**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

## Questions?

- Join the [Discord community](https://humanlayer.dev/discord)
- Open a [GitHub Discussion](https://github.com/humanlayer/12-factor-agents/discussions)
- Check the [README](./README.md) for more resources

Thank you for contributing! 🎉

