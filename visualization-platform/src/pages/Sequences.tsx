import { useState } from 'react'
import { Activity, Download, Copy, Check, MessageSquare, Clock, Zap } from 'lucide-react'

const sequences = [
  {
    id: 'initialization',
    title: '系统初始化时序',
    description: 'Agent系统启动和初始化的完整流程',
    participants: ['User', 'CLI', 'Factory', 'Agent', 'Storage', 'Logger'],
    messages: [
      { from: 0, to: 1, text: 'python -m agent', type: 'sync' },
      { from: 1, to: 2, text: 'createAgent()', type: 'call' },
      { from: 2, to: 3, text: 'Agent()', type: 'call' },
      { from: 3, to: 4, text: 'getStorageBackend()', type: 'call' },
      { from: 4, to: 5, text: 'Logger init', type: 'call' },
      { from: 3, to: 5, text: 'Agent initialized', type: 'return' },
    ],
  },
  {
    id: 'task-execution',
    title: '任务执行时序',
    description: '从任务创建到完成的全过程',
    participants: ['User', 'CLI', 'Agent', 'Storage', 'Memory', 'Graph'],
    messages: [
      { from: 0, to: 1, text: 'createTask()', type: 'sync' },
      { from: 1, to: 2, text: 'create_and_queue_task()', type: 'call' },
      { from: 2, to: 3, text: 'create_new_task_entry()', type: 'call' },
      { from: 3, to: 2, text: 'task_id', type: 'return' },
      { from: 2, to: 1, text: 'task_id', type: 'return' },
      { from: 2, to: 3, text: 'execute_task()', type: 'async' },
      { from: 3, to: 4, text: 'create_memory()', type: 'call' },
      { from: 3, to: 5, text: 'add_node()', type: 'call' },
    ],
  },
  {
    id: 'github-analysis',
    title: 'GitHub分析时序',
    description: '真实项目分析的全过程',
    participants: ['Agent', 'Analyzer', 'GitHub API', 'Cache', 'Storage'],
    messages: [
      { from: 0, to: 1, text: 'analyze_repo()', type: 'call' },
      { from: 1, to: 2, text: 'GET /repos/:owner/:repo', type: 'call' },
      { from: 2, to: 1, text: 'repo_data', type: 'return' },
      { from: 1, to: 4, text: 'generate_report()', type: 'call' },
      { from: 1, to: 3, text: 'save_analysis()', type: 'call' },
      { from: 3, to: 4, text: 'memory_content', type: 'return' },
    ],
  },
]

export default function SequencesPage() {
  const [activeSequence, setActiveSequence] = useState('initialization')
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const sequence = sequences.find(s => s.id === activeSequence) || sequences[0]

  const handleCopyMermaid = () => {
    const mermaidCode = generateMermaidCode(sequence)
    navigator.clipboard.writeText(mermaidCode)
    setCopiedId(sequence.id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const generateMermaidCode = (seq: typeof sequences[0]) => {
    const lines = [
      'sequenceDiagram',
      `    title ${seq.title}`,
      ''
    ]

    seq.participants.forEach((p, i) => {
      lines.push(`    participant ${p}`)
    })

    lines.push('')

    seq.messages.forEach(msg => {
      const from = seq.participants[msg.from]
      const to = seq.participants[msg.to]
      if (msg.type === 'call') {
        lines.push(`    ${from}->>+${to}: ${msg.text}`)
      } else if (msg.type === 'return') {
        lines.push(`    ${from}-->>-${to}: ${msg.text}`)
      } else {
        lines.push(`    ${from}->${to}: ${msg.text}`)
      }
    })

    return lines.join('\n')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4 sticky top-16 z-40">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">时序图分析</h1>
                <p className="text-sm text-slate-400">系统初始化、任务执行、GitHub分析的完整时序</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleCopyMermaid}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-medium hover:shadow-lg hover:shadow-emerald-500/30 transition-all"
              >
                {copiedId === sequence.id ? (
                  <>
                    <Check className="w-4 h-4" />
                    <span>已复制</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    <span>复制Mermaid</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Sequence Tabs */}
          <div className="flex items-center space-x-2 mt-4">
            {sequences.map((seq) => (
              <button
                key={seq.id}
                onClick={() => setActiveSequence(seq.id)}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeSequence === seq.id
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                {seq.title}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Sequence Info */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">{sequence.title}</h2>
          <p className="text-slate-400">{sequence.description}</p>
        </div>

        {/* Sequence Diagram */}
        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">时序图</h3>
            <div className="flex items-center space-x-4 text-xs text-slate-400">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-0.5 bg-emerald-500" />
                <span>同步调用</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-0.5 bg-cyan-500 border-dashed" style={{ borderTop: '2px dashed #06b6d4' }} />
                <span>异步调用</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-0.5 bg-purple-500" />
                <span>返回</span>
              </div>
            </div>
          </div>

          {/* Participants Header */}
          <div className="grid gap-4 mb-4" style={{ gridTemplateColumns: `repeat(${sequence.participants.length}, 1fr)` }}>
            {sequence.participants.map((p, i) => (
              <div key={i} className="text-center">
                <div className="inline-flex px-4 py-2 rounded-lg bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 text-emerald-400 font-semibold">
                  {p}
                </div>
              </div>
            ))}
          </div>

          {/* Lifelines */}
          <div className="relative">
            <div 
              className="absolute top-8 bottom-0 w-0.5 bg-gradient-to-b from-slate-600 to-slate-800"
              style={{ 
                left: `calc(${100 / (sequence.participants.length * 2)}% + 48px)`,
                right: `calc(${100 / (sequence.participants.length * 2)}% + 48px)`
              }}
            />

            {/* Messages */}
            <div className="space-y-6">
              {sequence.messages.map((msg, index) => {
                const fromPos = (msg.from / (sequence.participants.length - 1)) * 100
                const toPos = (msg.to / (sequence.participants.length - 1)) * 100
                const isForward = toPos > fromPos
                
                return (
                  <div key={index} className="relative">
                    {/* Activation Box */}
                    <div
                      className="absolute top-1/2 -translate-y-1/2 w-16 h-10 bg-slate-700/50 border border-slate-600/50 rounded"
                      style={{
                        left: `calc(${fromPos}% + ${48 - 8}px)`,
                      }}
                    />

                    {/* Message Arrow */}
                    <div className="flex items-center relative z-10">
                      <div 
                        className="text-right pr-4"
                        style={{ width: `${fromPos}%` }}
                      >
                        <span className="text-xs text-slate-500">
                          {sequence.participants[msg.from]}
                        </span>
                      </div>
                      
                      <div 
                        className={`flex-shrink-0 px-3 py-2 rounded-lg text-sm font-medium ${
                          msg.type === 'call' 
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                            : msg.type === 'return'
                            ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                            : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        }`}
                      >
                        {msg.text}
                      </div>

                      <div 
                        className="text-left pl-4"
                        style={{ width: `${100 - toPos}%` }}
                      >
                        <span className="text-xs text-slate-500">
                          {sequence.participants[msg.to]}
                        </span>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Mermaid Code */}
        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-white">Mermaid 代码</h3>
            <button
              onClick={handleCopyMermaid}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-700/50 text-slate-300 hover:bg-slate-600/50 transition-colors"
            >
              <Copy className="w-4 h-4" />
              <span className="text-sm">复制</span>
            </button>
          </div>
          
          <pre className="bg-slate-900/80 rounded-xl p-6 overflow-x-auto">
            <code className="text-sm text-emerald-400 font-mono">
              {generateMermaidCode(sequence)}
            </code>
          </pre>
        </div>

        {/* Stats */}
        <div className="mt-8 grid grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border border-emerald-500/30 rounded-2xl p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 rounded-lg bg-emerald-500/20">
                <MessageSquare className="w-5 h-5 text-emerald-400" />
              </div>
              <span className="text-slate-400 text-sm">消息数量</span>
            </div>
            <div className="text-4xl font-bold text-white">{sequence.messages.length}</div>
          </div>

          <div className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-2xl p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 rounded-lg bg-cyan-500/20">
                <Zap className="w-5 h-5 text-cyan-400" />
              </div>
              <span className="text-slate-400 text-sm">参与者</span>
            </div>
            <div className="text-4xl font-bold text-white">{sequence.participants.length}</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-2xl p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 rounded-lg bg-purple-500/20">
                <Clock className="w-5 h-5 text-purple-400" />
              </div>
              <span className="text-slate-400 text-sm">估计时长</span>
            </div>
            <div className="text-4xl font-bold text-white">~500ms</div>
          </div>
        </div>
      </div>
    </div>
  )
}
