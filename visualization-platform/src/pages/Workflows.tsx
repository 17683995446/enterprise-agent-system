import { useState } from 'react'
import { GitBranch, Play, Pause, RotateCcw, ChevronRight, CheckCircle2, Circle, Activity } from 'lucide-react'

const workflows = [
  {
    id: 'task-execution',
    title: '任务执行流程',
    description: '双模式Agent系统的核心任务执行流程',
    steps: [
      { id: 1, title: '任务创建', description: '用户创建新任务并设置优先级', duration: '~100ms' },
      { id: 2, title: '任务入队', description: '任务被添加到优先级队列', duration: '~50ms' },
      { id: 3, title: '任务调度', description: '调度器根据优先级选择任务', duration: '~20ms' },
      { id: 4, title: '任务执行', description: 'Agent执行任务并更新状态', duration: '~500ms' },
      { id: 5, title: '结果记录', description: '保存执行结果到记忆系统', duration: '~30ms' },
      { id: 6, title: '知识更新', description: '从任务中提取知识更新图谱', duration: '~100ms' },
    ],
  },
  {
    id: 'memory-system',
    title: '记忆系统流程',
    description: '记忆的创建、存储、检索和更新流程',
    steps: [
      { id: 1, title: '记忆创建', description: '系统自动或手动创建记忆', duration: '~80ms' },
      { id: 2, title: '分类标记', description: '为记忆添加类别和标签', duration: '~20ms' },
      { id: 3, title: '存储持久化', description: '保存到存储后端', duration: '~100ms' },
      { id: 4, title: '索引构建', description: '构建搜索索引', duration: '~50ms' },
      { id: 5, title: '关联更新', description: '更新知识图谱关联', duration: '~80ms' },
    ],
  },
  {
    id: 'knowledge-graph',
    title: '知识图谱构建',
    description: '从任务和记忆中提取知识构建图谱',
    steps: [
      { id: 1, title: '文本提取', description: '从记忆中提取关键文本', duration: '~200ms' },
      { id: 2, title: '实体识别', description: '识别关键实体和概念', duration: '~300ms' },
      { id: 3, title: '关系抽取', description: '提取实体间关系', duration: '~250ms' },
      { id: 4, title: '节点创建', description: '创建或更新图谱节点', duration: '~100ms' },
      { id: 5, title: '边构建', description: '建立节点间的边', duration: '~80ms' },
      { id: 6, title: '图谱优化', description: '图谱结构优化和去重', duration: '~150ms' },
    ],
  },
]

export default function WorkflowsPage() {
  const [activeWorkflow, setActiveWorkflow] = useState('task-execution')
  const [currentStep, setCurrentStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)

  const workflow = workflows.find(w => w.id === activeWorkflow) || workflows[0]

  const handlePlay = () => {
    if (isPlaying) {
      setIsPlaying(false)
    } else {
      setIsPlaying(true)
      if (currentStep >= workflow.steps.length) {
        setCurrentStep(0)
      }
    }
  }

  const handleReset = () => {
    setCurrentStep(0)
    setIsPlaying(false)
  }

  const handleNext = () => {
    if (currentStep < workflow.steps.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4 sticky top-16 z-40">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600">
                <GitBranch className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">流程图展示</h1>
                <p className="text-sm text-slate-400">任务执行、记忆系统、知识图谱的完整流程</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handlePlay}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-600 text-white font-medium hover:shadow-lg hover:shadow-purple-500/30 transition-all"
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                <span>{isPlaying ? '暂停' : '播放'}</span>
              </button>
              <button
                onClick={handleReset}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700 text-slate-300 hover:bg-slate-700/50 transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>重置</span>
              </button>
            </div>
          </div>

          {/* Workflow Tabs */}
          <div className="flex items-center space-x-2 mt-4">
            {workflows.map((wf) => (
              <button
                key={wf.id}
                onClick={() => {
                  setActiveWorkflow(wf.id)
                  setCurrentStep(0)
                  setIsPlaying(false)
                }}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeWorkflow === wf.id
                    ? 'bg-purple-500/20 text-purple-400 border border-purple-500/50'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                {wf.title}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Workflow Info */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">{workflow.title}</h2>
          <p className="text-slate-400">{workflow.description}</p>
        </div>

        {/* Timeline */}
        <div className="relative">
          {/* Timeline Line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-purple-500 via-pink-500 to-purple-500" />

          {/* Steps */}
          <div className="space-y-6">
            {workflow.steps.map((step, index) => {
              const isCompleted = index < currentStep
              const isActive = index === currentStep
              const isPending = index > currentStep

              return (
                <div key={step.id} className="relative flex items-start space-x-6">
                  {/* Icon */}
                  <div className={`relative z-10 flex-shrink-0 w-16 h-16 rounded-full flex items-center justify-center transition-all duration-500 ${
                    isCompleted
                      ? 'bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/30'
                      : isActive
                      ? 'bg-gradient-to-br from-purple-500 to-pink-600 shadow-lg shadow-purple-500/30 scale-110'
                      : 'bg-slate-800/80 border-2 border-slate-700'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle2 className="w-8 h-8 text-white" />
                    ) : isActive ? (
                      <Activity className="w-8 h-8 text-white animate-pulse" />
                    ) : (
                      <Circle className="w-8 h-8 text-slate-600" />
                    )}
                  </div>

                  {/* Content */}
                  <div className={`flex-1 p-6 rounded-2xl border transition-all duration-500 ${
                    isCompleted
                      ? 'bg-emerald-500/10 border-emerald-500/30'
                      : isActive
                      ? 'bg-purple-500/10 border-purple-500/30 shadow-lg shadow-purple-500/10'
                      : 'bg-slate-800/50 border-slate-700/50'
                  }`}>
                    <div className="flex items-start justify-between mb-2">
                      <h3 className={`text-xl font-bold transition-colors ${
                        isCompleted
                          ? 'text-emerald-400'
                          : isActive
                          ? 'text-purple-400'
                          : 'text-slate-300'
                      }`}>
                        {step.title}
                      </h3>
                      <span className={`text-xs px-3 py-1 rounded-full ${
                        isCompleted
                          ? 'bg-emerald-500/20 text-emerald-400'
                          : isActive
                          ? 'bg-purple-500/20 text-purple-400'
                          : 'bg-slate-700/50 text-slate-500'
                      }`}>
                        {step.duration}
                      </span>
                    </div>
                    <p className={`text-sm leading-relaxed transition-colors ${
                      isCompleted || isActive ? 'text-slate-300' : 'text-slate-500'
                    }`}>
                      {step.description}
                    </p>

                    {/* Progress Bar for Active Step */}
                    {isActive && (
                      <div className="mt-4">
                        <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full animate-pulse" style={{ width: '60%' }} />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Connector */}
                  {index < workflow.steps.length - 1 && (
                    <ChevronRight className={`absolute -left-3 top-1/2 -translate-y-1/2 w-6 h-6 transition-colors ${
                      isCompleted ? 'text-emerald-500' : 'text-slate-600'
                    }`} />
                  )}
                </div>
              )
            })}
          </div>

          {/* Summary */}
          <div className="mt-12 p-8 rounded-3xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-white">流程概览</h3>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-500" />
                  <span className="text-sm text-slate-400">已完成</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-purple-500" />
                  <span className="text-sm text-slate-400">进行中</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-slate-700" />
                  <span className="text-sm text-slate-400">待处理</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-4xl font-bold text-emerald-400 mb-2">{workflow.steps.filter((_, i) => i < currentStep).length}</div>
                <div className="text-sm text-slate-400">已完成步骤</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-purple-400 mb-2">{currentStep > 0 && currentStep < workflow.steps.length ? 1 : 0}</div>
                <div className="text-sm text-slate-400">当前步骤</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-slate-400 mb-2">{workflow.steps.filter((_, i) => i >= currentStep).length - (currentStep > 0 && currentStep < workflow.steps.length ? 1 : 0)}</div>
                <div className="text-sm text-slate-400">剩余步骤</div>
              </div>
            </div>

            {/* Total Duration */}
            <div className="mt-6 pt-6 border-t border-purple-500/30 text-center">
              <div className="text-slate-400 text-sm">预计总时长</div>
              <div className="text-3xl font-bold text-white mt-1">
                ~{workflow.steps.reduce((acc, step) => {
                  const ms = parseInt(step.duration.replace(/[~ms]/g, ''))
                  return acc + ms
                }, 0)}ms
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
