import { useState } from 'react'
import { Monitor as MonitorIcon, Clock, FileText, RefreshCw, Activity, AlertCircle, CheckCircle2 } from 'lucide-react'

const recentChanges = [
  { time: '2分钟前', file: 'src/core/agent_orchestrator.py', type: '修改', lines: '+12 -3', status: 'success' },
  { time: '5分钟前', file: 'src/domain/models.py', type: '新增', lines: '+45', status: 'success' },
  { time: '10分钟前', file: 'src/infrastructure/api.py', type: '修改', lines: '+8 -2', status: 'success' },
  { time: '15分钟前', file: 'tests/test_agent.py', type: '修改', lines: '+20 -5', status: 'success' },
  { time: '30分钟前', file: 'README.md', type: '修改', lines: '+15 -3', status: 'success' },
  { time: '1小时前', file: 'src/core/storage.py', type: '重构', lines: '+100 -80', status: 'success' },
]

const systemStatus = [
  { name: 'Agent服务', status: 'operational', uptime: '99.9%' },
  { name: '存储服务', status: 'operational', uptime: '99.8%' },
  { name: '日志系统', status: 'operational', uptime: '99.9%' },
  { name: 'GitHub集成', status: 'operational', uptime: '99.5%' },
]

const metrics = [
  { label: '文件变更数', value: '156', change: '+12%', icon: FileText },
  { label: '系统运行时间', value: '7天', change: '稳定', icon: Clock },
  { label: 'API调用次数', value: '2.3K', change: '+5%', icon: Activity },
  { label: '错误率', value: '0.1%', change: '-2%', icon: AlertCircle },
]

export default function MonitorPage() {
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const [isAutoRefresh, setIsAutoRefresh] = useState(false)

  const handleRefresh = () => {
    setLastUpdate(new Date())
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-rose-500 to-red-600">
                <MonitorIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">实时监控</h1>
                <p className="text-sm text-slate-400">文件变化监控和更新历史追踪</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleRefresh}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700 text-slate-300 hover:bg-slate-700/50 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>刷新</span>
              </button>
              <button
                onClick={() => setIsAutoRefresh(!isAutoRefresh)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                  isAutoRefresh
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50'
                    : 'bg-slate-800/50 border border-slate-700 text-slate-300'
                }`}
              >
                <div className={`w-2 h-2 rounded-full ${isAutoRefresh ? 'bg-emerald-500 animate-pulse' : 'bg-slate-500'}`} />
                <span>{isAutoRefresh ? '自动刷新中' : '自动刷新'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metrics.map((metric) => (
            <div
              key={metric.label}
              className="group p-6 rounded-2xl bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 hover:border-cyan-500/50 transition-all duration-300"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 rounded-xl bg-cyan-500/20 group-hover:bg-cyan-500/30 transition-colors">
                  <metric.icon className="w-6 h-6 text-cyan-400" />
                </div>
                <span className={`text-xs px-3 py-1 rounded-full ${
                  metric.change.includes('+') 
                    ? 'bg-emerald-500/20 text-emerald-400' 
                    : metric.change.includes('-')
                    ? 'bg-red-500/20 text-red-400'
                    : 'bg-slate-700/50 text-slate-400'
                }`}>
                  {metric.change}
                </span>
              </div>
              <div className="text-3xl font-bold text-white mb-1">{metric.value}</div>
              <div className="text-sm text-slate-400">{metric.label}</div>
            </div>
          ))}
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* System Status */}
          <div className="lg:col-span-1 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-6">系统状态</h3>
            <div className="space-y-4">
              {systemStatus.map((system) => (
                <div
                  key={system.name}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-900/50 border border-slate-700/50"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      system.status === 'operational' ? 'bg-emerald-500' : 'bg-red-500'
                    }`} />
                    <span className="text-slate-300">{system.name}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {system.status === 'operational' ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-red-400" />
                    )}
                    <span className="text-sm text-slate-400">{system.uptime}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
              <div className="flex items-center space-x-2 text-emerald-400 font-semibold mb-2">
                <Activity className="w-5 h-5" />
                <span>所有系统正常运行</span>
              </div>
              <p className="text-sm text-slate-400">上次检查: {lastUpdate.toLocaleTimeString()}</p>
            </div>
          </div>

          {/* Recent Changes */}
          <div className="lg:col-span-2 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-6">最近变更</h3>
            <div className="space-y-3">
              {recentChanges.map((change, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-900/50 border border-slate-700/50 hover:border-cyan-500/30 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                      change.type === '新增' 
                        ? 'bg-emerald-500/20 text-emerald-400' 
                        : change.type === '修改'
                        ? 'bg-cyan-500/20 text-cyan-400'
                        : 'bg-purple-500/20 text-purple-400'
                    }`}>
                      {change.type}
                    </div>
                    <div>
                      <div className="text-slate-300 font-medium">{change.file}</div>
                      <div className="text-xs text-slate-500 mt-1">{change.lines}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-slate-400">{change.time}</div>
                    <div className={`text-xs mt-1 ${
                      change.status === 'success' ? 'text-emerald-400' : 'text-red-400'
                    }`}>
                      {change.status === 'success' ? '成功' : '失败'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Activity Timeline */}
        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-6">活动时间线</h3>
          <div className="relative">
            {/* Timeline Line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-cyan-500 via-emerald-500 to-slate-600" />
            
            <div className="space-y-6">
              {[
                { time: '现在', event: '架构图页面已更新', type: 'success' },
                { time: '5分钟前', event: '新文件监控已启动', type: 'info' },
                { time: '10分钟前', event: '系统自检完成', type: 'success' },
                { time: '15分钟前', event: 'GitHub集成已连接', type: 'info' },
                { time: '30分钟前', event: '存储后端初始化', type: 'success' },
              ].map((item, index) => (
                <div key={index} className="relative flex items-start space-x-6">
                  {/* Icon */}
                  <div className={`relative z-10 w-16 h-16 rounded-full flex items-center justify-center ${
                    item.type === 'success'
                      ? 'bg-gradient-to-br from-emerald-500 to-teal-600'
                      : 'bg-gradient-to-br from-cyan-500 to-blue-600'
                  }`}>
                    {item.type === 'success' ? (
                      <CheckCircle2 className="w-8 h-8 text-white" />
                    ) : (
                      <Activity className="w-8 h-8 text-white" />
                    )}
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 pt-3">
                    <div className="text-slate-300 font-medium">{item.event}</div>
                    <div className="text-sm text-slate-500 mt-1">{item.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
