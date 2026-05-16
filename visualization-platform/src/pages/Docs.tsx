import { useState } from 'react'
import { FileText, Search, Download, BookOpen, Code, Lightbulb, Zap, ChevronDown, ChevronUp } from 'lucide-react'

const docs = [
  {
    id: 'overview',
    title: '系统概述',
    icon: BookOpen,
    description: '了解Enterprise Agent系统的核心概念和架构',
    sections: [
      { title: '什么是双模式Agent？', content: '双模式Agent是一种能够同时处理任务执行和自我优化的智能代理系统。' },
      { title: '核心特性', content: '包括任务调度、记忆系统、知识图谱、实时监控等功能。' },
    ],
  },
  {
    id: 'architecture',
    title: '架构指南',
    icon: Code,
    description: '深入了解系统的五层架构设计',
    sections: [
      { title: 'Domain Layer', content: '定义核心数据模型和业务枚举，确保类型安全。' },
      { title: 'Core Layer', content: '包含Agent编排器和存储后端，实现核心业务逻辑。' },
      { title: 'Infrastructure Layer', content: '提供外部服务集成，如日志、配置、GitHub分析等。' },
    ],
  },
  {
    id: 'development',
    title: '开发指南',
    icon: Lightbulb,
    description: '如何开发、测试和部署Agent系统',
    sections: [
      { title: '快速开始', content: '克隆项目，安装依赖，运行演示。' },
      { title: '测试驱动', content: '使用pytest进行单元测试和集成测试。' },
    ],
  },
  {
    id: 'api',
    title: 'API参考',
    icon: Zap,
    description: '完整的API接口文档',
    sections: [
      { title: 'Agent API', content: '创建任务、执行任务、管理记忆等核心API。' },
      { title: '存储API', content: 'CRUD操作的完整接口定义。' },
    ],
  },
]

export default function DocsPage() {
  const [expandedCards, setExpandedCards] = useState<string[]>([])

  const toggleCard = (id: string) => {
    setExpandedCards(prev => {
      if (prev.includes(id)) {
        return prev.filter(cardId => cardId !== id)
      } else {
        return [...prev, id]
      }
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-orange-500 to-amber-600">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">系统文档</h1>
                <p className="text-sm text-slate-400">完整的开发者指南和API参考</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700 text-slate-300 hover:bg-slate-700/50 transition-colors">
                <Search className="w-4 h-4" />
                <span>搜索文档</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700 text-slate-300 hover:bg-slate-700/50 transition-colors">
                <Download className="w-4 h-4" />
                <span>导出PDF</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Bar */}
        <div className="mb-8">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="搜索文档..."
              className="w-full pl-12 pr-4 py-4 rounded-xl bg-slate-800/50 border border-slate-700 text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500/50 transition-colors"
            />
          </div>
        </div>

        {/* Docs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {docs.map((doc) => {
            const isExpanded = expandedCards.includes(doc.id)
            
            return (
            <div
              key={doc.id}
              className="group p-8 rounded-3xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 hover:border-cyan-500/50 transition-all duration-300"
            >
              <div className="flex items-start space-x-4 mb-6">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-orange-500/20 to-amber-500/20 group-hover:from-orange-500/30 group-hover:to-amber-500/30 transition-colors">
                  <doc.icon className="w-8 h-8 text-orange-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-white mb-2 group-hover:text-cyan-400 transition-colors">
                    {doc.title}
                  </h3>
                  <p className="text-slate-400 text-sm">{doc.description}</p>
                </div>
              </div>

              {isExpanded && (
                <div className="space-y-4 mb-6">
                  {doc.sections.map((section, index) => (
                    <div
                      key={index}
                      className="p-4 rounded-xl bg-slate-900/50 border border-slate-700/50 hover:border-cyan-500/30 transition-colors"
                    >
                      <h4 className="font-semibold text-white mb-2">{section.title}</h4>
                      <p className="text-sm text-slate-400 leading-relaxed">{section.content}</p>
                    </div>
                  ))}
                </div>
              )}

              <div className="pt-4 border-t border-slate-700/50">
                <button 
                  onClick={() => toggleCard(doc.id)}
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-orange-500 to-amber-600 text-white font-semibold hover:shadow-lg hover:shadow-orange-500/30 transition-all flex items-center justify-center space-x-2"
                >
                  <span>{isExpanded ? '收起' : '阅读更多'}</span>
                  {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
              </div>
            </div>
          )})}
        </div>

        {/* Quick Links */}
        <div className="mt-12 p-8 rounded-3xl bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/30">
          <h3 className="text-2xl font-bold text-white mb-6">快速链接</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a href="#" className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-cyan-500/50 transition-colors">
              <div className="text-cyan-400 font-semibold mb-2">安装指南</div>
              <div className="text-sm text-slate-400">快速开始使用系统</div>
            </a>
            <a href="#" className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-cyan-500/50 transition-colors">
              <div className="text-cyan-400 font-semibold mb-2">示例代码</div>
              <div className="text-sm text-slate-400">查看完整示例</div>
            </a>
            <a href="#" className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-cyan-500/50 transition-colors">
              <div className="text-cyan-400 font-semibold mb-2">视频教程</div>
              <div className="text-sm text-slate-400">观看教学视频</div>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
