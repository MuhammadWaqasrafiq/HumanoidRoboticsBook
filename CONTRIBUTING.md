# Contributing to Physical AI & Humanoid Robotics Book

Thank you for your interest in contributing to this educational resource! This document provides guidelines for contributing to the project.

## 📋 Code of Conduct

- Be respectful and inclusive in all interactions
- Focus on constructive feedback and collaboration
- Help create a welcoming environment for learners and contributors

## 🎯 Ways to Contribute

### 1. Report Issues

Found a bug, typo, or technical inaccuracy? Please open an issue with:

- **Clear title**: Describe the problem concisely
- **Location**: Chapter number, section, or file path
- **Description**: What's wrong and why it matters
- **Expected behavior**: What should happen instead
- **Environment** (if relevant): OS, ROS version, hardware specs

### 2. Improve Documentation

- Fix typos, grammar, or unclear explanations
- Add missing alt text to images
- Improve code comments or examples
- Update outdated information (hardware prices, software versions)

### 3. Enhance Code Examples

- Test code examples on different platforms
- Add error handling or edge cases
- Provide C++ alternatives to Python examples (or vice versa)
- Optimize performance or memory usage

### 4. Add Troubleshooting Entries

Encountered an error not in Appendix B? Contribute your solution:

- **Symptom**: Error message or behavior
- **Root cause**: Technical explanation
- **Solution steps**: Ordered, testable fix procedure
- **Prevention tips**: How to avoid this error

### 5. Create Diagrams or Visualizations

- Convert complex concepts to Mermaid.js diagrams
- Add flowcharts, architecture diagrams, or decision trees
- Ensure diagrams have descriptive alt text (accessibility)

## 🔧 Development Workflow

### Prerequisites

- Node.js 20 LTS or higher
- Git installed and configured
- Familiarity with Markdown/MDX

### Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/physical-ai-book.git
   cd physical-ai-book
   ```

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Start local development server**:
   ```bash
   npm start
   ```
   Opens `http://localhost:3000` with hot reload.

### Making Changes

1. **Follow the spec-first approach**: For significant changes, update or create a spec in `/specs/` first

2. **Maintain consistency**:
   - Use existing chapter structure and formatting
   - Follow Flesch-Kincaid grade 8-10 readability target
   - Include proper frontmatter in MDX files (see existing chapters)

3. **Test your changes**:
   ```bash
   npm run build          # Verify site builds successfully
   npm run lint           # Check Markdown formatting
   npm run link-check     # Validate all links work
   ```

4. **Verify accessibility**:
   - All images must have descriptive alt text
   - Maintain proper heading hierarchy (h1 → h2 → h3)
   - Test with keyboard navigation
   - Ensure color contrast meets WCAG 2.2 AA (4.5:1 minimum)

5. **Test code examples** (if adding/modifying code):
   ```bash
   cd code-examples/your-example
   ./test.sh  # Or python3 test.py
   ```
   All code examples must be tested on Ubuntu 22.04 + ROS 2 Iron.

### Commit Guidelines

Write clear, descriptive commit messages:

```
<type>: <short summary> (max 72 chars)

<optional detailed description>

<optional footer with references>
```

**Types**:
- `feat`: New feature or chapter content
- `fix`: Bug fix or error correction
- `docs`: Documentation improvements
- `style`: Formatting, typos (no content changes)
- `refactor`: Code restructuring without behavior change
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, configs)

**Example**:
```
feat: Add OpenVLA-7B integration example for Chapter 10

- Implement model loading and inference code
- Add 8-bit quantization guide for VRAM-constrained systems
- Test on RTX 4070 Ti with 12GB VRAM
- Document expected latency and accuracy trade-offs
```

### Submitting a Pull Request

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: your descriptive message"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Open a Pull Request** on GitHub with:
   - **Clear title**: Summarize the change
   - **Description**: What changed and why
   - **Testing**: How you verified it works
   - **Screenshots** (if UI/visual changes)
   - **Related issues**: Reference issue numbers (#123)

4. **Wait for review**: Maintainers will review and may request changes

5. **Address feedback**: Make requested changes and push updates

6. **Merge**: Once approved, maintainers will merge your PR

## 📐 Content Guidelines

### Writing Style

- **Target audience**: Intermediate-to-advanced AI/ML engineers
- **Tone**: Helpful mentor, not academic textbook - conversational yet precise
- **Readability**: Flesch-Kincaid grade 8-10 (test with readability tools)
- **Avoid jargon**: Explain technical terms on first use
- **Be specific**: "RTX 4070 Ti with 12GB VRAM" not "a powerful GPU"

### Technical Accuracy

- **Cite sources**: Link to official docs, papers, or canonical repos
- **Verify commands**: Test all terminal commands on clean Ubuntu 22.04
- **Current pricing**: Use Q4 2025/Q1 2026 verified prices with ±20% ranges
- **Version specificity**: "ROS 2 Iron Irwini" not "ROS 2"
- **No speculation**: State facts or clearly mark assumptions

### Code Examples

- **Tested**: Must run successfully on Ubuntu 22.04 + ROS 2 Iron + Isaac Sim 2025.1+
- **Self-contained**: Include all imports and dependencies
- **Commented**: Explain non-obvious logic
- **Expected output**: Document what running the code produces
- **Error handling**: Include basic error handling where appropriate

### Diagrams (Mermaid.js)

All diagrams must be in Mermaid.js format for live editing:

```markdown
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```‍```

- Keep diagrams focused (max 10-12 nodes)
- Use descriptive labels
- Include legend if symbols/colors have meaning
- Provide alt text in surrounding prose

## ✅ Quality Checklist

Before submitting a PR, verify:

- [ ] Changes tested locally (`npm start` works)
- [ ] Site builds successfully (`npm run build`)
- [ ] All links valid (`npm run link-check`)
- [ ] Markdown linted (`npm run lint`)
- [ ] Images have descriptive alt text
- [ ] Code examples tested on Ubuntu 22.04
- [ ] Headings follow proper hierarchy (no skipped levels)
- [ ] Commit messages are clear and descriptive
- [ ] No sensitive information (API keys, credentials)

## 🔒 Security

- **Never commit secrets**: Use `.env` files (already in `.gitignore`)
- **No personal data**: Avoid including personal information in examples
- **Safe code**: No command injection, XSS, or SQL injection vulnerabilities
- **Report security issues**: Email security@example.com (not public issues)

## 📜 Licensing

By contributing, you agree that your contributions will be licensed under:

- **Code**: MIT License (code examples, scripts)
- **Content**: CC-BY-4.0 (prose, documentation)

Ensure you have the right to contribute any code or content you submit.

## 🤝 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Chat**: Join our community (link TBD)
- **Stuck?**: Tag maintainers in your PR for guidance

## 🙏 Thank You!

Every contribution makes this resource better for learners worldwide. We appreciate your time and effort!

---

**Project**: Physical AI & Humanoid Robotics Book
**License**: MIT (code) + CC-BY-4.0 (content)
**Maintainers**: See [GitHub Contributors](https://github.com/your-username/physical-ai-book/graphs/contributors)
