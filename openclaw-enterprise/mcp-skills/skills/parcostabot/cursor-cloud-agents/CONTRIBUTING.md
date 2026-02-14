# Contributing to Cursor Cloud Agents Skill

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. Fork and clone the repository
2. Ensure you have the required dependencies:
   ```bash
   brew install bats-core jq shellcheck  # macOS
   # or
   apt-get install bats jq shellcheck    # Debian/Ubuntu
   ```
3. Make the script executable:
   ```bash
   chmod +x scripts/cursor-api.sh
   ```

## Testing

Run the test suite before submitting changes:

```bash
# Run all tests
./tests/run-tests.sh

# Run with coverage report
./tests/run-tests.sh --coverage

# Run integration tests (requires CURSOR_API_KEY)
CURSOR_API_KEY=xxx ./tests/run-tests.sh --integration
```

### Writing Tests

- Add unit tests to `tests/test_cursor_api.bats`
- Add integration tests to `tests/integration.bats`
- Ensure all code paths are covered
- Mock external API calls in unit tests

## Code Style

- Follow the existing code style
- Use `shellcheck` to check for issues
- Use 4-space indentation
- Use descriptive variable names
- Add comments for complex logic

### Shellcheck

All code must pass shellcheck:

```bash
shellcheck scripts/cursor-api.sh
```

### Code Guidelines

1. **Input sanitization**: Always sanitize user inputs
2. **Error handling**: Use `set -euo pipefail` and proper error messages
3. **Exit codes**: Use defined exit codes for different error types
4. **Documentation**: Update SKILL.md and README.md for user-facing changes

## Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes with clear, focused commits

3. Add/update tests as needed

4. Update documentation:
   - SKILL.md for usage changes
   - README.md for installation/setup changes
   - references/api-reference.md for API changes

5. Run the full test suite

6. Push your branch and create a Pull Request

## Pull Request Template

```markdown
## Description
Brief description of the change

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] shellcheck clean

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No secrets in code
```

## Reporting Issues

When reporting issues, please include:

1. OpenClaw version
2. Operating system
3. Shell version (`bash --version`)
4. Steps to reproduce
5. Expected vs actual behavior
6. Error messages (if any)

## Security

See [SECURITY.md](SECURITY.md) for security-related information.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
