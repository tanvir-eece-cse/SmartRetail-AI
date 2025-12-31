# SmartRetail-AI Contributing Guide

Thank you for your interest in contributing to SmartRetail-AI! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Commit Message Convention](#commit-message-convention)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. Please be considerate of others and follow professional conduct in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/SmartRetail-AI.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Push to your fork: `git push origin feature/your-feature-name`
6. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### ML Service Setup

```bash
cd ml-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running with Docker

```bash
docker-compose up -d
```

## Coding Standards

### Python (Backend & ML Service)

- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 88 characters
- Use Black for formatting
- Use isort for import sorting

```bash
# Format code
black .
isort .

# Check linting
flake8 .
mypy app
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- Use ESLint with Prettier
- Use functional components with hooks
- Prefer named exports

```bash
# Format and lint
npm run lint
npm run format
```

### General Guidelines

- Write self-documenting code with meaningful variable names
- Add docstrings/comments for complex logic
- Keep functions small and focused
- DRY (Don't Repeat Yourself)
- SOLID principles

## Testing Guidelines

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:coverage
```

### ML Service Tests

```bash
cd ml-service
pytest tests/ -v --cov=app
```

### Test Requirements

- All new features must include tests
- Maintain minimum 80% code coverage
- Tests must pass before PR can be merged
- Include unit tests and integration tests where appropriate

## Pull Request Process

1. **Create a descriptive PR title** following the commit convention
2. **Fill out the PR template** completely
3. **Link related issues** using `Fixes #123` or `Closes #123`
4. **Ensure all CI checks pass**
5. **Request review** from at least one maintainer
6. **Address review feedback** promptly
7. **Squash commits** before merging if requested

### PR Checklist

- [ ] Code follows the project's coding standards
- [ ] Tests are included and passing
- [ ] Documentation is updated if needed
- [ ] No sensitive information (keys, passwords) is committed
- [ ] Commit messages follow the convention

## Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Examples

```
feat(api): add product recommendation endpoint

fix(auth): resolve token refresh issue

docs(readme): update installation instructions

test(ml): add unit tests for segmentation model
```

## Questions?

If you have questions, feel free to:

- Open a GitHub issue
- Contact the maintainer

---

**Thank you for contributing to SmartRetail-AI!** 🙏

Maintained by **Md. Tanvir Hossain**
- GitHub: [@tanvir-eece-cse](https://github.com/tanvir-eece-cse)
- LinkedIn: [tanvir-eece](https://www.linkedin.com/in/tanvir-eece/)
