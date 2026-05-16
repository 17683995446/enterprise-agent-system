import { useEffect, useState } from 'react'
import { Layers, GitBranch, Activity, FileText, Monitor, ArrowRight, Zap, Shield, Clock } from 'lucide-react'

const features = [
  {
    icon: Layers,
    title: '架构可视化',
    description: '清晰展示系统的五层架构，模块依赖关系一目了然',
    color: 'from-cyan-500 to-blue-600',
  },
  {
    icon: GitBranch,
    title: '流程图展示',
    description: '任务执行、记忆系统、知识图谱的完整流程图',
    color: 'from-purple-500 to-pink-600',
  },
  {
    icon: Activity,
    title: '时序图分析',
    description: '系统初始化、任务执行、GitHub分析的完整时序',
    color: 'from-emerald-500 to-teal-600',
  },
  {
    icon: FileText,
    title: '文档管理',
    description: '完整的系统文档和开发者指南',
    color: 'from-orange-500 to-amber-600',
  },
  {
    icon: Monitor,
    title: '实时监控',
    description: '文件变化监控和更新历史追踪',
    color: 'from-rose-500 to-red-600',
  },
]

const stats = [
  { label: '总文件数', value: '328', icon: FileText },
  { label: '模块数量', value: '12', icon: Layers },
  { label: '测试用例', value: '16', icon: Shield },
  { label: '依赖项', value: '25+', icon: Zap },
]

const recentUpdates = [
  { time: '2分钟前', message: '更新了架构图组件', type: '架构' },
  { time: '15分钟前', message: '添加了新的流程图', type: '流程' },
  { time: '1小时前', message: '完成了时序图更新', type: '时序' },
  { time: '2小时前', message: '修复了监控页面Bug', type: '监控' },
]

export default function HomePage() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div className="relative">
      {/* Hero Section */}
      <section className="relative min-h-[70vh] flex items-center justify-center overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-900/20 via-transparent to-purple-900/20" />
        <div className="absolute inset-0 backdrop-blur-3xl" />
        
        {/* Animated Grid */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0)',
            backgroundSize: '40px 40px'
          }} />
        </div>

        {/* Floating Orbs */}
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000" />

        {/* Content */}
        <div className={`relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 mb-8">
            <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
            <span className="text-sm text-cyan-400 font-medium">实时更新中</span>
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6">
            <span className="bg-gradient-to-r from-white via-cyan-200 to-slate-300 bg-clip-text text-transparent">
              Enterprise Agent
            </span>
            <br />
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
              System Visualization
            </span>
          </h1>

          <p className="text-xl sm:text-2xl text-slate-400 mb-12 max-w-3xl mx-auto leading-relaxed">
            专业的交互式可视化平台，全面展示双模式永续Agent系统的架构、流程和时序
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <a
              href="/architecture"
              className="group relative inline-flex items-center space-x-2 px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 transition-all duration-300 hover:scale-105"
            >
              <span>开始探索</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 opacity-0 hover:opacity-100 transition-opacity -z-10 blur-xl" />
            </a>
            <a
              href="/docs"
              className="inline-flex items-center space-x-2 px-8 py-4 rounded-xl border border-slate-700 text-slate-300 font-semibold hover:bg-slate-800/50 hover:border-slate-600 transition-all duration-300"
            >
              <FileText className="w-5 h-5" />
              <span>查看文档</span>
            </a>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <div
                key={stat.label}
                className={`group relative p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 backdrop-blur-xl hover:border-cyan-500/50 transition-all duration-500 ${
                  mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
                }`}
                style={{ transitionDelay: `${index * 100}ms` }}
              >
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative">
                  <stat.icon className="w-8 h-8 text-cyan-400 mb-4" />
                  <div className="text-3xl sm:text-4xl font-bold text-white mb-2">{stat.value}</div>
                  <div className="text-sm text-slate-400">{stat.label}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-bold mb-6">
              <span className="bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                核心功能特性
              </span>
            </h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              全面覆盖系统架构的各个方面，提供专业的可视化展示
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <a
                key={feature.title}
                href={`/${feature.title === '架构可视化' ? 'architecture' : feature.title === '流程图展示' ? 'workflows' : feature.title === '时序图分析' ? 'sequences' : feature.title === '文档管理' ? 'docs' : 'monitor'}`}
                className={`group relative p-8 rounded-3xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 backdrop-blur-xl hover:border-cyan-500/50 transition-all duration-500 hover:scale-105 ${
                  mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
                }`}
                style={{ transitionDelay: `${index * 150}ms` }}
              >
                <div className={`absolute inset-0 rounded-3xl bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity`} />
                
                <div className="relative">
                  <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${feature.color} mb-6 shadow-lg`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  
                  <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-cyan-400 transition-colors">
                    {feature.title}
                  </h3>
                  
                  <p className="text-slate-400 leading-relaxed mb-6">
                    {feature.description}
                  </p>
                  
                  <div className="flex items-center text-cyan-400 font-medium group-hover:text-cyan-300">
                    <span>探索更多</span>
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* Recent Updates Section */}
      <section className="relative py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-3xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 backdrop-blur-xl p-8 sm:p-12">
            <div className="flex items-center space-x-3 mb-8">
              <div className="p-3 rounded-xl bg-emerald-500/20">
                <Clock className="w-6 h-6 text-emerald-400" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">最近更新</h3>
                <p className="text-sm text-slate-400">实时追踪系统的最新变化</p>
              </div>
            </div>

            <div className="space-y-4">
              {recentUpdates.map((update, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-900/50 border border-slate-700/50 hover:border-cyan-500/50 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                      update.type === '架构' ? 'bg-cyan-500/20 text-cyan-400' :
                      update.type === '流程' ? 'bg-purple-500/20 text-purple-400' :
                      update.type === '时序' ? 'bg-emerald-500/20 text-emerald-400' :
                      'bg-rose-500/20 text-rose-400'
                    }`}>
                      {update.type}
                    </div>
                    <span className="text-slate-300">{update.message}</span>
                  </div>
                  <span className="text-sm text-slate-500">{update.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl sm:text-5xl font-bold mb-6">
            <span className="bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
              准备好开始了吗？
            </span>
          </h2>
          <p className="text-xl text-slate-400 mb-12">
            点击下方按钮，立即探索系统的完整架构和功能
          </p>
          <a
            href="/architecture"
            className="group inline-flex items-center space-x-3 px-10 py-5 rounded-2xl bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 text-white font-bold text-lg shadow-2xl shadow-cyan-500/30 hover:shadow-cyan-500/50 transition-all duration-300 hover:scale-105"
          >
            <span>立即探索系统架构</span>
            <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
          </a>
        </div>
      </section>
    </div>
  )
}
