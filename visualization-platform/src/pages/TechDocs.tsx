import { useState } from 'react'
import { BookOpen, Code, FileText, Database, Server, Cpu, GitBranch, Zap, Shield, TrendingUp, Layers } from 'lucide-react'

const docs = {
  overview: {
    title: '系统概览',
    icon: BookOpen,
    content: (
      <div className="space-y-6">
        <section>
          <h3 className="text-xl font-bold text-white mb-4">Enterprise Agent System</h3>
          <p className="text-slate-400 mb-4">
            Enterprise Agent System 是一个企业级的双模式 Agent 系统，支持任务执行模式和空闲改进模式。
            该系统集成了 LLM 分析、GitHub 仓库分析、Vue 项目分析等多种功能。
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/30">
              <h4 className="font-semibold text-cyan-400 mb-2">🚀 核心特性</h4>
              <ul className="text-sm text-slate-300 space-y-1">
                <li>• 双模式 Agent 系统</li>
                <li>• 知识图谱和经验学习</li>
                <li>• 多种分析能力集成</li>
                <li>• 企业级日志系统</li>
              </ul>
            </div>
            <div className="p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30">
              <h4 className="font-semibold text-purple-400 mb-2">🛠️ 技术亮点</h4>
              <ul className="text-sm text-slate-300 space-y-1">
                <li>• 五层架构设计</li>
                <li>• 异步处理优化</li>
                <li>• 多存储后端支持</li>
                <li>• 完善的测试套件</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    )
  },
  architecture: {
    title: '系统架构',
    icon: Layers,
    content: (
      <div className="space-y-6">
        <section>
          <h3 className="text-xl font-bold text-white mb-4">五层架构设计</h3>
          <div className="space-y-4">
            {[
              { name: 'Presentation Layer', color: 'cyan', desc: '可视化平台，提供用户界面' },
              { name: 'Application Layer', color: 'blue', desc: '应用层，定义业务用例和工作流' },
              { name: 'Infrastructure Layer', color: 'purple', desc: '基础设施，提供外部服务集成' },
              { name: 'Core Layer', color: 'emerald', desc: '核心层，包含 Agent 编排和存储' },
              { name: 'Domain Layer', color: 'orange', desc: '领域层，定义数据模型和规则' },
            ].map((layer, i) => (
              <div key={i} className={`p-4 rounded-xl bg-gradient-to-r from-${layer.color}-500/10 to-${layer.color}-600/10 border border-${layer.color}-500/30`}>
                <h4 className={`font-semibold text-${layer.color}-400 mb-2`}>{layer.name}</h4>
                <p className="text-sm text-slate-400">{layer.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    )
  },
  api: {
    title: 'API 设计',
    icon: Server,
    content: (
      <div className="space-y-6">
        <section>
          <h3 className="text-xl font-bold text-white mb-4">REST API 端点</h3>
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <div className="flex items-center space-x-3 mb-2">
                <span className="px-2 py-1 rounded text-xs font-bold bg-emerald-500/20 text-emerald-400">GET</span>
                <code className="text-slate-300">/health</code>
              </div>
              <p className="text-sm text-slate-400">健康检查端点</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <div className="flex items-center space-x-3 mb-2">
                <span className="px-2 py-1 rounded text-xs font-bold bg-cyan-500/20 text-cyan-400">GET</span>
                <code className="text-slate-300">/api/v1/llm/stats</code>
              </div>
              <p className="text-sm text-slate-400">LLM 统计信息</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <div className="flex items-center space-x-3 mb-2">
                <span className="px-2 py-1 rounded text-xs font-bold bg-blue-500/20 text-blue-400">POST</span>
                <code className="text-slate-300">/api/v1/tasks</code>
              </div>
              <p className="text-sm text-slate-400">创建新任务</p>
            </div>
          </div>
        </section>
      </div>
    )
  },
  database: {
    title: '数据存储',
    icon: Database,
    content: (
      <div className="space-y-6">
        <section>
          <h3 className="text-xl font-bold text-white mb-4">存储后端设计</h3>
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <h4 className="font-semibold text-white mb-2">SQLite (默认)</h4>
              <p className="text-sm text-slate-400 mb-2">轻量级文件数据库，适合单机部署</p>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 rounded text-xs bg-slate-700 text-slate-300">文件存储</span>
                <span className="px-2 py-1 rounded text-xs bg-slate-700 text-slate-300">零配置</span>
                <span className="px-2 py-1 rounded text-xs bg-slate-700 text-slate-300">ACID</span>
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <h4 className="font-semibold text-white mb-2">内存存储</h4>
              <p className="text-sm text-slate-400 mb-2">高性能内存存储，适合测试和临时数据</p>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 rounded text-xs bg-slate-700 text-slate-300">超高性能</span>
                <span className="px-2 py-1 rounded text-xs bg-slate-700 text-slate-300">无持久化</span>
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <h4 className="font-semibold text-white mb-2">Redis 缓存</h4>
              <p className="text-sm text-slate-400 mb-2">分布式缓存，提升系统性能</p>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 rounded text-xs bg-slate-700 text-slate-300">连接池</span>
                <span className="px-2 py-1 rounded text-xs bg-slate-700 text-slate-300">LRU 淘汰</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    )
  },
  deployment: {
    title: '部署指南',
    icon: Zap,
    content: (
      <div className="space-y-6">
        <section>
          <h3 className="text-xl font-bold text-white mb-4">本地开发</h3>
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
            <pre className="text-sm text-emerald-400 overflow-x-auto">
              <code>{`# 克隆项目
git clone <repo-url>
cd enterprise_agent_system

# 安装 Python 依赖
pip install -e .

# 安装前端依赖
cd visualization-platform
npm install

# 启动后端
python -m enterprise_agent_system.start_api

# 启动前端
npm run dev`}</code>
            </pre>
          </div>
        </section>
        <section>
          <h3 className="text-xl font-bold text-white mb-4">Docker 部署</h3>
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
            <pre className="text-sm text-emerald-400 overflow-x-auto">
              <code>{`# 使用 Docker Compose
docker-compose up -d

# 访问应用
# 前端: http://localhost:5173
# 后端: http://localhost:8001
# API 文档: http://localhost:8001/docs`}</code>
            </pre>
          </div>
        </section>
      </div>
    )
  },
  testing: {
    title: '测试体系',
    icon: Shield,
    content: (
      <div className="space-y-6">
        <section>
          <h3 className="text-xl font-bold text-white mb-4">测试覆盖</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {[
              { name: '单元测试', count: '26+', color: 'cyan' },
              { name: '集成测试', count: '10+', color: 'purple' },
              { name: '高难度测试', count: '11', color: 'emerald' },
            ].map((t, i) => (
              <div key={i} className={`p-4 rounded-xl bg-gradient-to-br from-${t.color}-500/10 to-${t.color}-600/10 border border-${t.color}-500/30 text-center`}>
                <div className={`text-3xl font-bold text-${t.color}-400 mb-1`}>{t.count}</div>
                <div className="text-sm text-slate-400">{t.name}</div>
              </div>
            ))}
          </div>
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
            <h4 className="font-semibold text-white mb-2">运行测试</h4>
            <pre className="text-sm text-emerald-400 overflow-x-auto">
              <code>{`# 运行所有测试
pytest

# 运行特定测试文件
pytest test_high_difficulty_*.py

# 生成覆盖率报告
pytest --cov=enterprise_agent_system`}</code>
            </pre>
          </div>
        </section>
      </div>
    )
  },
}

export default function TechDocsPage() {
  const [activeSection, setActiveSection] = useState('overview')

  const sections = Object.entries(docs)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center space-x-4 mb-4">
            <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">技术文档</h1>
              <p className="text-sm text-slate-400">Enterprise Agent System 完整技术文档</p>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {sections.map(([key, section]) => {
              const Icon = section.icon
              return (
                <button
                  key={key}
                  onClick={() => setActiveSection(key)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                    activeSection === key
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{section.title}</span>
                </button>
              )
            })}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-slate-800/30 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8">
          {docs[activeSection as keyof typeof docs].content}
        </div>
      </div>
    </div>
  )
}
