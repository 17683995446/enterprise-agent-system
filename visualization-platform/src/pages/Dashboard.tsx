import { useEffect, useState, useCallback } from 'react'
import { Layers, GitBranch, Activity, FileText, Monitor, Zap, Shield, Clock, TrendingUp, TrendingDown, Cpu, Database, Server, BarChart3, PieChart, ArrowRight, Eye, Play, RefreshCw } from 'lucide-react'

// 系统统计数据
const systemStats = [
  {
    id: 'total_files',
    label: '总文件数',
    value: '328',
    change: '+12',
    trend: 'up',
    icon: FileText,
    color: 'from-cyan-500 to-blue-600',
  },
  {
    id: 'modules',
    label: '模块数量',
    value: '12',
    change: '+3',
    trend: 'up',
    icon: Layers,
    color: 'from-purple-500 to-pink-600',
  },
  {
    id: 'test_cases',
    label: '测试用例',
    value: '26',
    change: '+10',
    trend: 'up',
    icon: Shield,
    color: 'from-emerald-500 to-teal-600',
  },
  {
    id: 'dependencies',
    label: '依赖项',
    value: '25+',
    change: '0',
    trend: 'stable',
    icon: Zap,
    color: 'from-orange-500 to-amber-600',
  },
]

// 性能指标
const performanceMetrics = [
  { label: 'API响应', value: '210ms', percentage: 85, color: 'bg-cyan-500' },
  { label: '内存使用', value: '128MB', percentage: 60, color: 'bg-purple-500' },
  { label: '系统负载', value: '0.45', percentage: 45, color: 'bg-emerald-500' },
  { label: '任务完成率', value: '98%', percentage: 98, color: 'bg-blue-500' },
]

// 最近活动
const recentActivities = [
  {
    time: '1分钟前',
    action: '更新',
    target: '架构图组件',
    type: '架构',
    status: 'success',
    icon: Layers,
  },
  {
    time: '5分钟前',
    action: '新增',
    target: '流程图',
    type: '流程',
    status: 'success',
    icon: GitBranch,
  },
  {
    time: '12分钟前',
    action: '修复',
    target: '时序图',
    type: '时序',
    status: 'warning',
    icon: Activity,
  },
  {
    time: '25分钟前',
    action: '优化',
    target: '监控页面',
    type: '监控',
    status: 'success',
    icon: Monitor,
  },
  {
    time: '1小时前',
    action: '测试',
    target: 'API集成',
    type: '测试',
    status: 'success',
    icon: Shield,
  },
]

// 系统服务状态
const services = [
  { name: 'API服务器', status: 'online', icon: Server, lastCheck: '刚刚' },
  { name: 'Redis缓存', status: 'online', icon: Database, lastCheck: '2分钟前' },
  { name: 'Agent调度', status: 'online', icon: Cpu, lastCheck: '5分钟前' },
  { name: 'LLM服务', status: 'online', icon: Zap, lastCheck: '10分钟前' },
]

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [stats, setStats] = useState(systemStats)

  // 模拟数据刷新
  const refreshData = useCallback(() => {
    setRefreshing(true)
    setTimeout(() => {
      setStats(systemStats)
      setRefreshing(false)
    }, 500)
  }, [])

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div className="relative min-h-screen">
      {/* Header */}
      <div className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold mb-2">
                <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  系统仪表盘
                </span>
              </h1>
              <p className="text-slate-400">
                监控和管理Enterprise Agent系统的关键指标和活动
              </p>
            </div>
            <div className="mt-4 md:mt-0 flex items-center space-x-3">
              <button
                onClick={refreshData}
                disabled={refreshing}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/30 transition-all disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                <span>刷新数据</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <div
                key={stat.id}
                className={`group relative p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 backdrop-blur-xl hover:border-cyan-500/50 transition-all duration-500 ${
                  mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
                }`}
                style={{ transitionDelay: `${index * 100}ms` }}
              >
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative">
                  <div className="flex items-center justify-between mb-4">
                    <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${stat.color} shadow-lg`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className={`flex items-center space-x-1 text-sm ${
                      stat.trend === 'up' ? 'text-emerald-400' :
                      stat.trend === 'down' ? 'text-rose-400' : 'text-slate-400'
                    }`}>
                      {stat.trend === 'up' ? <TrendingUp className="w-4 h-4" /> :
                       stat.trend === 'down' ? <TrendingDown className="w-4 h-4" /> : null}
                      <span>{stat.change}</span>
                    </div>
                  </div>
                  <div className="text-3xl sm:text-4xl font-bold text-white mb-2">
                    {stat.value}
                  </div>
                  <div className="text-sm text-slate-400">{stat.label}</div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Performance Metrics */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 backdrop-blur-xl">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-3 rounded-xl bg-cyan-500/20">
                  <BarChart3 className="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">性能指标</h3>
                  <p className="text-sm text-slate-400">系统关键性能实时监控</p>
                </div>
              </div>
              
              <div className="space-y-4">
                {performanceMetrics.map((metric, index) => (
                  <div key={metric.label} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-300 font-medium">{metric.label}</span>
                      <span className="text-white font-bold">{metric.value}</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${metric.color} transition-all duration-1000 ease-out`}
                        style={{
                          width: `${metric.percentage}%`,
                          transform: 'translateX(0)',
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activities */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 backdrop-blur-xl">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-3 rounded-xl bg-purple-500/20">
                  <Clock className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">最近活动</h3>
                  <p className="text-sm text-slate-400">实时追踪系统变更</p>
                </div>
              </div>
              
              <div className="space-y-3">
                {recentActivities.map((activity, index) => {
                  const Icon = activity.icon
                  return (
                    <div
                      key={index}
                      className="flex items-center space-x-4 p-4 rounded-xl bg-slate-900/50 border border-slate-700/50 hover:border-cyan-500/50 transition-colors"
                    >
                      <div className={`inline-flex p-2 rounded-lg ${
                        activity.status === 'success' ? 'bg-emerald-500/20' : 'bg-orange-500/20'
                      }`}>
                        <Icon className={`w-4 h-4 ${
                          activity.status === 'success' ? 'text-emerald-400' : 'text-orange-400'
                        }`} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-white font-medium">{activity.action}</span>
                          <span className="text-slate-300">{activity.target}</span>
                        </div>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            activity.type === '架构' ? 'bg-cyan-500/20 text-cyan-400' :
                            activity.type === '流程' ? 'bg-purple-500/20 text-purple-400' :
                            activity.type === '时序' ? 'bg-emerald-500/20 text-emerald-400' :
                            'bg-blue-500/20 text-blue-400'
                          }`}>
                            {activity.type}
                          </span>
                          <span className="text-xs text-slate-500">{activity.time}</span>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* Quick Actions */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 backdrop-blur-xl">
              <h3 className="text-xl font-bold text-white mb-6">快速操作</h3>
              <div className="grid grid-cols-2 gap-3">
                <a
                  href="/architecture"
                  className="group flex flex-col items-center justify-center p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-cyan-500/50 hover:bg-cyan-500/10 transition-all"
                >
                  <Layers className="w-8 h-8 text-cyan-400 mb-2 group-hover:scale-110 transition-transform" />
                  <span className="text-sm font-medium text-slate-300">查看架构</span>
                </a>
                <a
                  href="/workflows"
                  className="group flex flex-col items-center justify-center p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-purple-500/50 hover:bg-purple-500/10 transition-all"
                >
                  <GitBranch className="w-8 h-8 text-purple-400 mb-2 group-hover:scale-110 transition-transform" />
                  <span className="text-sm font-medium text-slate-300">浏览流程</span>
                </a>
                <a
                  href="/tasks"
                  className="group flex flex-col items-center justify-center p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-all"
                >
                  <Play className="w-8 h-8 text-emerald-400 mb-2 group-hover:scale-110 transition-transform" />
                  <span className="text-sm font-medium text-slate-300">管理任务</span>
                </a>
                <a
                  href="/monitor"
                  className="group flex flex-col items-center justify-center p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-orange-500/50 hover:bg-orange-500/10 transition-all"
                >
                  <Eye className="w-8 h-8 text-orange-400 mb-2 group-hover:scale-110 transition-transform" />
                  <span className="text-sm font-medium text-slate-300">监控系统</span>
                </a>
              </div>
            </div>

            {/* Service Status */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 backdrop-blur-xl">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-3 rounded-xl bg-emerald-500/20">
                  <Server className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">服务状态</h3>
                  <p className="text-sm text-slate-400">关键服务运行状态</p>
                </div>
              </div>
              
              <div className="space-y-3">
                {services.map((service, index) => {
                  const Icon = service.icon
                  return (
                    <div
                      key={service.name}
                      className="flex items-center justify-between p-4 rounded-xl bg-slate-900/50 border border-slate-700/50"
                    >
                      <div className="flex items-center space-x-3">
                        <Icon className="w-5 h-5 text-slate-400" />
                        <span className="text-slate-300 font-medium">{service.name}</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <div className="flex flex-col items-end">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-400">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
                            在线
                          </span>
                          <span className="text-xs text-slate-500 mt-1">{service.lastCheck}</span>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Overview Cards */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="group p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 backdrop-blur-xl hover:border-cyan-500/50 transition-all">
            <PieChart className="w-10 h-10 text-cyan-400 mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">分析概览</h3>
            <p className="text-slate-400 text-sm mb-4">系统分析和报告的完整概览</p>
            <a
              href="/docs"
              className="inline-flex items-center text-cyan-400 text-sm font-medium hover:text-cyan-300"
            >
              查看文档 <ArrowRight className="w-4 h-4 ml-1" />
            </a>
          </div>

          <div className="group p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 backdrop-blur-xl hover:border-purple-500/50 transition-all">
            <Layers className="w-10 h-10 text-purple-400 mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">架构详情</h3>
            <p className="text-slate-400 text-sm mb-4">深入了解系统架构和模块关系</p>
            <a
              href="/architecture"
              className="inline-flex items-center text-purple-400 text-sm font-medium hover:text-purple-300"
            >
              探索架构 <ArrowRight className="w-4 h-4 ml-1" />
            </a>
          </div>

          <div className="group p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 backdrop-blur-xl hover:border-emerald-500/50 transition-all">
            <Monitor className="w-10 h-10 text-emerald-400 mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">监控面板</h3>
            <p className="text-slate-400 text-sm mb-4">实时监控和性能指标追踪</p>
            <a
              href="/monitor"
              className="inline-flex items-center text-emerald-400 text-sm font-medium hover:text-emerald-300"
            >
              进入监控 <ArrowRight className="w-4 h-4 ml-1" />
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
