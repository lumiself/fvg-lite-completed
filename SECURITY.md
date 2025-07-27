# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible receiving such patches depend on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Please report vulnerabilities by emailing [security@fvg-silver-bullet-lite.com](mailto:security@fvg-silver-bullet-lite.com). Please include:

- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Possible impact** of the vulnerability
- **Suggested fix** (if any)

## Response Time

We aim to respond to security reports within 48 hours. Our process:

1. **Acknowledgment** - Within 24 hours
2. **Assessment** - Within 48 hours
3. **Fix Development** - Within 7 days
4. **Release** - Within 14 days
5. **Disclosure** - Coordinated disclosure after fix

## Security Best Practices

### For Users
- Always use the latest version
- Run on trusted networks only
- Use strong passwords for any authentication
- Keep Python and dependencies updated

### For Developers
- Never commit sensitive data (API keys, passwords)
- Use environment variables for configuration
- Validate all user inputs
- Follow secure coding practices
- Regular dependency updates

## Vulnerability Types We Care About

### High Priority
- Remote code execution
- SQL injection
- Authentication bypass
- Data exposure

### Medium Priority
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Information disclosure
- Denial of service

### Low Priority
- Missing security headers
- Weak SSL/TLS configuration
- Information leakage in error messages

## Security Headers

Our application includes:
- Content-Security-Policy
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection

## Contact

For security-related questions or concerns:
- Email: [security@fvg-silver-bullet-lite.com](mailto:security@fvg-silver-bullet-lite.com)
- Do not use GitHub issues for security reports

## Acknowledgments

We appreciate security researchers who help keep our community safe. Security researchers who responsibly disclose vulnerabilities will be acknowledged in our security advisories.
