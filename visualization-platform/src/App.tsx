import { useState, useEffect, useCallback } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { Home, Layers, GitBranch, Activity, FileText, Monitor, Menu, X, RefreshCw, Clock, ListChecks } from 'lucide-react'
import HomePage from './pages/Home'
import ArchitecturePage from './pages/Architecture'
import WorkflowsPage from './pages/Workflows'
import SequencesPage from './pages/Sequences'
import DocsPage from './pages/Docs'
import MonitorPage from './pages/Monitor'
import TasksPage from './pages/Tasks'
import './index.css'

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const [autoRefresh, setAutoRefresh] = useState(true)

  // 手动刷新功能
  const handleRefresh = useCallback(() => {
    setLastUpdate(new Date())
  }, [])

  useEffect(() => {
    // 监听文件变化事件
    const handleFileChange = () => {
      setLastUpdate(new Date())
    }

    window.addEventListener('fileChange', handleFileChange)
    
    // 尝试连接到文件监视器服务器（使用SSE）
    let eventSource: EventSource | null = null
    try {
      eventSource = new EventSource('http://localhost:3001')
      eventSource.onmessage = (event) => {
        console.log('📁 文件变化:', event.data)
        setLastUpdate(new Date())
        // 触发自定义事件
        window.dispatchEvent(new CustomEvent('fileChange', { 
          detail: JSON.parse(event.data) 
        }))
      }
      eventSource.onerror = () => {
        console.log('🔴 文件监视器未连接，使用定时器刷新')
      }
    } catch (e) {
      console.log('ℹ️ 文件监视器不可用')
    }
    
    // 如果启用了自动刷新且没有SSE连接，使用定时器
    let interval: NodeJS.Timeout | null = null
    if (autoRefresh && !eventSource) {
      interval = setInterval(() => {
        setLastUpdate(new Date())
      }, 30000)
    }

    return () => {
      window.removeEventListener('fileChange', handleFileChange)
      if (eventSource) eventSource.close()
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh])

  const navItems = [
    { to: '/', icon: Home, label: '首页' },
    { to: '/tasks', icon: ListChecks, label: '任务管理' },
    { to: '/architecture', icon: Layers, label: '架构图' },
    { to: '/workflows', icon: GitBranch, label: '流程图' },
    { to: '/sequences', icon: Activity, label: '时序图' },
    { to: '/docs', icon: FileText, label: '文档' },
    { to: '/monitor', icon: Monitor, label: '监控' },
  ]

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        {/* Navigation */}
        <nav className="sticky top-0 z-50 backdrop-blur-xl bg-slate-900/80 border-b border-slate-700/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                  <Layers className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                    Agent System
                  </h1>
                  <p className="text-xs text-slate-400">可视化平台</p>
                </div>
              </div>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center space-x-1">
                {navItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      `flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                        isActive
                          ? 'bg-cyan-500/20 text-cyan-400 shadow-lg shadow-cyan-500/10'
                          : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'
                      }`
                    }
                  >
                    <item.icon className="w-4 h-4" />
                    <span className="text-sm font-medium">{item.label}</span>
                  </NavLink>
                ))}
              </div>

              {/* Update Status with Refresh Controls */}
      <div className="hidden lg:flex items-center space-x-4">
        <button
          onClick={handleRefresh}
          className="flex items-center space-x-1 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-300 hover:bg-slate-700/50 transition-colors"
          title="手动刷新"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
        
        <div className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center space-x-1 text-xs ${autoRefresh ? 'text-emerald-400' : 'text-slate-500'}`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>{autoRefresh ? '自动刷新' : '暂停'}</span>
          </button>
          <div className={`w-2 h-2 rounded-full ${autoRefresh ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`}></div>
        </div>
        
        <div className="px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
          <span className="text-xs text-slate-400">
            最后更新: {lastUpdate.toLocaleTimeString()}
          </span>
        </div>
      </div>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="md:hidden p-2 rounded-lg bg-slate-800/50 text-slate-300 hover:bg-slate-700/50 transition-colors"
              >
                {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {isMenuOpen && (
            <div className="md:hidden border-t border-slate-700/50 bg-slate-900/95 backdrop-blur-xl">
              <div className="px-4 py-4 space-y-2">
                {navItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={() => setIsMenuOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                        isActive
                          ? 'bg-cyan-500/20 text-cyan-400'
                          : 'text-slate-300 hover:bg-slate-700/50'
                      }`
                    }
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </NavLink>
                ))}
              </div>
            </div>
          )}
        </nav>

        {/* Main Content */}
        <main className="relative">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/architecture" element={<ArchitecturePage />} />
            <Route path="/workflows" element={<WorkflowsPage />} />
            <Route path="/sequences" element={<SequencesPage />} />
            <Route path="/docs" element={<DocsPage />} />
            <Route path="/monitor" element={<MonitorPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-700/50 bg-slate-900/50 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
              <div className="text-center md:text-left">
                <p className="text-sm text-slate-400">
                  Enterprise Agent System Visualization Platform
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  实时展示系统架构、流程和时序
                </p>
              </div>
              <div className="flex items-center space-x-4 text-xs text-slate-500">
                <span>最后更新: {lastUpdate.toLocaleString()}</span>
                <span>•</span>
                <span>版本 1.0.0</span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
