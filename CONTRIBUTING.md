# 贡献指南 | Contributing Guide

感谢您考虑为企业级双模式Agent系统做出贡献！

## 中文

### 🤝 如何贡献

1. **Fork 仓库**
   ```bash
   git clone https://github.com/YOUR_USERNAME/enterprise-agent-system.git
   cd enterprise-agent-system
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **进行开发**
   - 遵循代码规范
   - 添加必要的测试
   - 更新相关文档

4. **运行测试**
   ```bash
   export PYTHONPATH=src:$PYTHONPATH
   pytest src/enterprise_agent_system/test_suite/ -v
   ```

5. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 在GitHub上创建Pull Request
   - 填写详细的PR描述
   - 等待代码审查

### 📝 代码规范

#### Python代码规范

- 使用 **Black** 格式化代码
- 使用 **Ruff** 进行代码检查
- 使用 **MyPy** 进行类型检查
- 遵循 **PEP 8** 规范

```bash
# 格式化
black src/

# 检查
ruff check src/

# 类型检查
mypy src/
```

#### TypeScript代码规范

- 使用 **ESLint** 进行代码检查
- 使用 **Prettier** 格式化代码
- 遵循 TypeScript 最佳实践

```bash
cd visualization-platform
npm run lint
npm run check
```

### ✅ 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: 添加React项目分析器
fix: 修复任务调度优先级问题
docs: 更新README使用说明
test: 添加集成测试用例
```

### 🧪 测试要求

- 所有新功能必须添加单元测试
- 保持测试覆盖率在80%以上
- 集成测试应该覆盖主要流程

```bash
# 运行所有测试
pytest src/enterprise_agent_system/test_suite/ -v

# 运行覆盖率测试
pytest src/enterprise_agent_system/test_suite/ --cov=src/enterprise_agent_system --cov-report=html
```

### 📚 文档要求

- 更新 README.md 中的相关说明
- 添加必要的代码注释
- 更新 API 文档（如有变化）

### 🐛 报告Bug

如果您发现了bug，请创建一个 [Issue](https://github.com/17683995446/enterprise-agent-system/issues)，包含：

1. Bug描述
2. 复现步骤
3. 期望行为
4. 实际行为
5. 环境信息（Python版本、操作系统等）

### 💡 提出新功能

如果您有新功能的想法，请创建一个 [Issue](https://github.com/17683995446/enterprise-agent-system/issues)，包含：

1. 功能描述
2. 使用场景
3. 预期效果
4. 可能的实现方案

---

## English

### 🤝 How to Contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/enterprise-agent-system.git
   cd enterprise-agent-system
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow code standards
   - Add necessary tests
   - Update documentation

4. **Run tests**
   ```bash
   export PYTHONPATH=src:$PYTHONPATH
   pytest src/enterprise_agent_system/test_suite/ -v
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Create PR on GitHub
   - Fill in detailed PR description
   - Wait for code review

### 📝 Code Standards

#### Python

- Use **Black** for formatting
- Use **Ruff** for linting
- Use **MyPy** for type checking
- Follow **PEP 8** standards

#### TypeScript

- Use **ESLint** for linting
- Use **Prettier** for formatting
- Follow TypeScript best practices

### ✅ Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/tool related

### 🧪 Testing Requirements

- All new features must have unit tests
- Maintain test coverage above 80%
- Integration tests should cover main workflows

### 📚 Documentation Requirements

- Update README.md with relevant information
- Add necessary code comments
- Update API documentation if changed

### 🐛 Report Bugs

If you find a bug, please create an [Issue](https://github.com/17683995446/enterprise-agent-system/issues) with:

1. Bug description
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Environment info (Python version, OS, etc.)

### 💡 Propose New Features

If you have ideas for new features, please create an [Issue](https://github.com/17683995446/enterprise-agent-system/issues) with:

1. Feature description
2. Use case
3. Expected outcome
4. Possible implementation

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
