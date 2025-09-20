# 🔒 Security Policy

## 🛡️ Supported Versions

We take security seriously and actively maintain security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability in Chess Analyzer, please help us by reporting it responsibly.

### 📧 How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:
- **Email**: [security@chess-analyzer.dev](mailto:security@chess-analyzer.dev)
- **Subject**: `[SECURITY] Vulnerability Report - Chess Analyzer`

### 📋 What to Include

When reporting a security vulnerability, please include:

1. **Description**: A clear description of the vulnerability
2. **Impact**: What an attacker could achieve by exploiting this vulnerability
3. **Steps to Reproduce**: Detailed steps to reproduce the issue
4. **Proof of Concept**: Code or detailed instructions demonstrating the vulnerability
5. **Environment**: Your system details (OS, Python version, etc.)
6. **Contact Information**: How we can reach you for follow-up questions

### ⏱️ Response Timeline

We will acknowledge your report within **48 hours** and provide a more detailed response within **7 days** indicating our next steps.

We will keep you informed about our progress throughout the process of fixing the vulnerability.

### 🎯 Our Commitment

- We will investigate all legitimate reports
- We will keep you informed about our progress
- We will credit you (if desired) once the issue is resolved
- We will not pursue legal action against security researchers

## 🔧 Security Considerations

### For Users

#### API Keys and Credentials
- **xAI API Key**: Store securely, never commit to version control
- **Chess.com Credentials**: Optional for future premium features, stored locally in `config.local.ini`
- **Local Config File**: `config.local.ini` is automatically excluded from Git commits
- **Database**: Local SQLite files contain your game data

#### Network Communications
- All API calls use HTTPS encryption
- No sensitive data is transmitted except API keys
- Rate limiting prevents abuse
- Local credentials are never sent over network (used for future authenticated features)

#### Local Security
- Chess Analyzer runs locally on your machine
- No remote code execution capabilities
- Stockfish engine runs as a local process
- Credentials stored securely in local config file

### For Developers

#### Code Security
- Regular dependency updates and security scans
- Input validation on all user inputs
- Secure handling of API keys and credentials
- No hardcoded secrets in source code

#### Development Security
- Use virtual environments for development
- Never commit sensitive data to repository
- Regular security audits of dependencies
- Follow secure coding practices

## 🛠️ Security Best Practices

### For Contributors
1. **Never commit API keys or secrets**
2. **Use environment variables for sensitive configuration**
3. **Validate all inputs and sanitize outputs**
4. **Follow the principle of least privilege**
5. **Keep dependencies updated**

### For Maintainers
1. **Regular security audits**
2. **Dependency vulnerability scanning**
3. **Prompt response to security reports**
4. **Transparent communication with users**
5. **Security-focused code reviews**

## 📊 Security Updates

Security updates will be:
- **Released as soon as possible** after verification
- **Documented in the changelog** with appropriate severity levels
- **Communicated through GitHub Security Advisories**
- **Tagged with security-related labels**

## 🆘 Emergency Contacts

- **Security Issues**: security@chess-analyzer.dev
- **General Support**: support@chess-analyzer.dev
- **GitHub Issues**: For non-security related bugs

## 🙏 Recognition

We appreciate security researchers who help keep Chess Analyzer safe. With your permission, we will acknowledge your contribution in our security hall of fame.

---

**Thank you for helping keep Chess Analyzer secure! 🛡️**