import { useCallback, useState, useMemo } from 'react'
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Node,
  Edge,
  MarkerType,
  Panel,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { Download, Maximize2, RefreshCw, Info, Code, Database, Layers } from 'lucide-react'

const initialNodes: Node[] = [
  // Presentation Layer
  {
    id: '1',
    position: { x: 400, y: 0 },
    data: { label: 'Presentation Layer\n可视化平台' },
    style: { background: '#06b6d4', color: 'white', border: 'none', borderRadius: '12px', padding: '20px', fontWeight: 'bold', fontSize: '16px', boxShadow: '0 10px 30px rgba(6, 182, 212, 0.3)', width: '200px', textAlign: 'center' },
  },
  
  // Application Layer
  {
    id: '2',
    position: { x: 100, y: 150 },
    data: { label: 'Application Layer\n应用层' },
    style: { background: '#0891b2', color: 'white', border: 'none', borderRadius: '12px', padding: '16px', fontSize: '14px', boxShadow: '0 8px 25px rgba(8, 145, 178, 0.3)', width: '180px', textAlign: 'center' },
  },
  {
    id: '2a',
    position: { x: 300, y: 150 },
    data: { label: 'CLI App\n命令行应用' },
    style: { background: '#0e7490', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(14, 116, 144, 0.3)', width: '160px', textAlign: 'center' },
  },
  {
    id: '2b',
    position: { x: 500, y: 150 },
    data: { label: 'Vue Analyzer\nVue分析器' },
    style: { background: '#0e7490', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(14, 116, 144, 0.3)', width: '160px', textAlign: 'center' },
  },
  {
    id: '2c',
    position: { x: 700, y: 150 },
    data: { label: 'Reactivity System\n响应式系统' },
    style: { background: '#0e7490', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(14, 116, 144, 0.3)', width: '160px', textAlign: 'center' },
  },
  
  // Infrastructure Layer
  {
    id: '3',
    position: { x: 100, y: 300 },
    data: { label: 'Infrastructure Layer\n基础设施层' },
    style: { background: '#7c3aed', color: 'white', border: 'none', borderRadius: '12px', padding: '16px', fontSize: '14px', boxShadow: '0 8px 25px rgba(124, 58, 237, 0.3)', width: '180px', textAlign: 'center' },
  },
  {
    id: '3a',
    position: { x: 300, y: 300 },
    data: { label: 'GitHub Analyzer\nGitHub分析器' },
    style: { background: '#6d28d9', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(109, 40, 217, 0.3)', width: '160px', textAlign: 'center' },
  },
  {
    id: '3b',
    position: { x: 500, y: 300 },
    data: { label: 'Logging System\n日志系统' },
    style: { background: '#6d28d9', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(109, 40, 217, 0.3)', width: '160px', textAlign: 'center' },
  },
  {
    id: '3c',
    position: { x: 700, y: 300 },
    data: { label: 'Config Manager\n配置管理' },
    style: { background: '#6d28d9', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(109, 40, 217, 0.3)', width: '160px', textAlign: 'center' },
  },
  {
    id: '3d',
    position: { x: 900, y: 300 },
    data: { label: 'FastAPI REST API' },
    style: { background: '#6d28d9', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(109, 40, 217, 0.3)', width: '160px', textAlign: 'center' },
  },
  
  // Core Layer
  {
    id: '4',
    position: { x: 200, y: 480 },
    data: { label: 'Core Layer\n核心层' },
    style: { background: '#2563eb', color: 'white', border: 'none', borderRadius: '12px', padding: '16px', fontSize: '14px', boxShadow: '0 8px 25px rgba(37, 99, 235, 0.3)', width: '180px', textAlign: 'center' },
  },
  {
    id: '4a',
    position: { x: 420, y: 480 },
    data: { label: 'Agent Orchestrator\nAgent编排器' },
    style: { background: '#1d4ed8', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(29, 78, 216, 0.3)', width: '160px', textAlign: 'center' },
  },
  {
    id: '4b',
    position: { x: 640, y: 480 },
    data: { label: 'Storage Backend\n存储后端' },
    style: { background: '#1d4ed8', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(29, 78, 216, 0.3)', width: '160px', textAlign: 'center' },
  },
  
  // Domain Layer
  {
    id: '5',
    position: { x: 200, y: 650 },
    data: { label: 'Domain Layer\n领域层' },
    style: { background: '#059669', color: 'white', border: 'none', borderRadius: '12px', padding: '16px', fontSize: '14px', boxShadow: '0 8px 25px rgba(5, 150, 105, 0.3)', width: '180px', textAlign: 'center' },
  },
  {
    id: '5a',
    position: { x: 420, y: 650 },
    data: { label: 'Task Model\n任务模型' },
    style: { background: '#047857', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(4, 120, 87, 0.3)', width: '160px', textAlign: 'center' },
  },
  {
    id: '5b',
    position: { x: 640, y: 650 },
    data: { label: 'Memory Model\n记忆模型' },
    style: { background: '#047857', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(4, 120, 87, 0.3)', width: '160px', textAlign: 'center' },
  },
  
  // Test Suite
  {
    id: '6',
    position: { x: 900, y: 480 },
    data: { label: 'Test Suite\n测试套件' },
    style: { background: '#dc2626', color: 'white', border: 'none', borderRadius: '12px', padding: '16px', fontSize: '14px', boxShadow: '0 8px 25px rgba(220, 38, 38, 0.3)', width: '180px', textAlign: 'center' },
  },
  {
    id: '6a',
    position: { x: 900, y: 650 },
    data: { label: 'Unit Tests\n单元测试' },
    style: { background: '#b91c1c', color: 'white', border: 'none', borderRadius: '12px', padding: '14px', fontSize: '13px', boxShadow: '0 8px 25px rgba(185, 28, 28, 0.3)', width: '160px', textAlign: 'center' },
  },
]

const initialEdges: Edge[] = [
  // Presentation Layer connections
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#06b6d4', strokeWidth: 3 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#06b6d4' } },
  
  // Application Layer internal connections
  { id: 'e2-2a', source: '2', target: '2a', animated: true, style: { stroke: '#0891b2', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#0891b2' } },
  { id: 'e2-2b', source: '2', target: '2b', animated: true, style: { stroke: '#0891b2', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#0891b2' } },
  { id: 'e2-2c', source: '2', target: '2c', animated: true, style: { stroke: '#0891b2', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#0891b2' } },
  
  // Application Layer to Infrastructure Layer
  { id: 'e2a-3', source: '2a', target: '3', animated: true, style: { stroke: '#0e7490', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#0e7490' } },
  { id: 'e2b-3a', source: '2b', target: '3a', animated: true, style: { stroke: '#0e7490', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#0e7490' } },
  
  // Infrastructure Layer internal connections
  { id: 'e3-3a', source: '3', target: '3a', animated: true, style: { stroke: '#7c3aed', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#7c3aed' } },
  { id: 'e3-3b', source: '3', target: '3b', animated: true, style: { stroke: '#7c3aed', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#7c3aed' } },
  { id: 'e3-3c', source: '3', target: '3c', animated: true, style: { stroke: '#7c3aed', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#7c3aed' } },
  { id: 'e3-3d', source: '3', target: '3d', animated: true, style: { stroke: '#7c3aed', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#7c3aed' } },
  
  // Infrastructure Layer to Core Layer
  { id: 'e3-4', source: '3', target: '4', animated: true, style: { stroke: '#6d28d9', strokeWidth: 3 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#6d28d9' } },
  
  // Core Layer internal connections
  { id: 'e4-4a', source: '4', target: '4a', animated: true, style: { stroke: '#2563eb', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#2563eb' } },
  { id: 'e4-4b', source: '4', target: '4b', animated: true, style: { stroke: '#2563eb', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#2563eb' } },
  { id: 'e4a-4b', source: '4a', target: '4b', animated: true, style: { stroke: '#1d4ed8', strokeWidth: 2, strokeDasharray: '3,3' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#1d4ed8' } },
  
  // Core Layer to Domain Layer
  { id: 'e4-5', source: '4', target: '5', animated: true, style: { stroke: '#1d4ed8', strokeWidth: 3 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#1d4ed8' } },
  
  // Domain Layer internal connections
  { id: 'e5-5a', source: '5', target: '5a', animated: true, style: { stroke: '#059669', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#059669' } },
  { id: 'e5-5b', source: '5', target: '5b', animated: true, style: { stroke: '#059669', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#059669' } },
  
  // Core Layer to Test Suite
  { id: 'e4-6', source: '4', target: '6', animated: true, style: { stroke: '#2563eb', strokeWidth: 2, strokeDasharray: '5,5' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#2563eb' } },
  { id: 'e6-6a', source: '6', target: '6a', animated: true, style: { stroke: '#dc2626', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#dc2626' } },
]

const moduleDetails = {
  // Presentation Layer
  '1': {
    name: 'Presentation Layer',
    description: '可视化平台，提供用户界面和展示功能',
    modules: ['架构图可视化', '流程图展示', '时序图分析', '文档查看'],
    tech: ['React', 'TypeScript', 'Tailwind CSS', '@xyflow/react', 'Mermaid'],
    filePath: 'visualization-platform/'
  },
  // Application Layer
  '2': {
    name: 'Application Layer',
    description: '应用层，定义应用程序的用例和流程',
    modules: ['CLI应用', 'Vue分析器', '响应式系统分析'],
    tech: ['Python', 'asyncio'],
    filePath: 'src/enterprise_agent_system/application/'
  },
  '2a': {
    name: 'CLI App',
    description: '命令行应用程序，提供用户交互接口',
    modules: ['命令解析', '任务管理', '报告生成'],
    tech: ['Python', 'asyncio', 'argparse'],
    filePath: 'src/enterprise_agent_system/application/command_line_interface_application.py'
  },
  '2b': {
    name: 'Vue Analyzer',
    description: 'Vue项目分析器，专门用于分析Vue.js项目结构',
    modules: ['项目结构扫描', '依赖分析', '质量评估'],
    tech: ['Python', 'Pathlib'],
    filePath: 'src/enterprise_agent_system/infrastructure/typescript_vue_project_analyzer.py'
  },
  '2c': {
    name: 'Reactivity System',
    description: '深度分析Vue.js响应式系统的组件',
    modules: ['Proxy分析', 'Effect系统', '依赖追踪'],
    tech: ['Python', 'JSON'],
    filePath: 'src/enterprise_agent_system/application/vue_reactivity_system_analyzer.py'
  },
  // Infrastructure Layer
  '3': {
    name: 'Infrastructure Layer',
    description: '基础设施层，提供外部服务和技术支持',
    modules: ['日志系统', '配置管理', 'GitHub分析器', 'FastAPI'],
    tech: ['FastAPI', 'SQLAlchemy', 'Redis', 'Docker'],
    filePath: 'src/enterprise_agent_system/infrastructure/'
  },
  '3a': {
    name: 'GitHub Analyzer',
    description: 'GitHub仓库分析器，支持在线和离线模式',
    modules: ['API客户端', '数据缓存', '报告生成'],
    tech: ['Python', 'requests', 'JSON'],
    filePath: 'src/enterprise_agent_system/infrastructure/github_repository_analyzer.py'
  },
  '3b': {
    name: 'Logging System',
    description: '企业级日志系统，支持多种日志级别和输出',
    modules: ['日志记录', '级别管理', '格式化输出'],
    tech: ['Python', 'logging'],
    filePath: 'src/enterprise_agent_system/infrastructure/enterprise_logging_system.py'
  },
  '3c': {
    name: 'Config Manager',
    description: '应用配置管理，使用Pydantic Settings',
    modules: ['配置加载', '类型验证', '环境变量支持'],
    tech: ['Python', 'Pydantic Settings'],
    filePath: 'src/enterprise_agent_system/infrastructure/application_configuration_management.py'
  },
  '3d': {
    name: 'FastAPI REST API',
    description: 'REST API服务，提供HTTP接口访问',
    modules: ['路由管理', '请求处理', '响应序列化'],
    tech: ['Python', 'FastAPI', 'Uvicorn'],
    filePath: 'src/enterprise_agent_system/infrastructure/fastapi_rest_api_application.py'
  },
  // Core Layer
  '4': {
    name: 'Core Layer',
    description: '核心业务逻辑层，包含Agent编排器和存储后端',
    modules: ['Agent Orchestrator', 'Storage Backend', 'Factory'],
    tech: ['Python', 'Dataclasses', 'asyncio'],
    filePath: 'src/enterprise_agent_system/core/'
  },
  '4a': {
    name: 'Agent Orchestrator',
    description: 'Agent编排和执行器，负责任务调度和执行',
    modules: ['任务队列', '优先级调度', '执行引擎'],
    tech: ['Python', 'asyncio', 'Queues'],
    filePath: 'src/enterprise_agent_system/core/agent_orchestrator_and_executor.py'
  },
  '4b': {
    name: 'Storage Backend',
    description: '存储后端，支持内存和数据库两种模式',
    modules: ['数据存储', '内存缓存', '数据库接口'],
    tech: ['Python', 'SQLAlchemy', 'WeakMap'],
    filePath: 'src/enterprise_agent_system/core/storage_backend_interface.py'
  },
  // Domain Layer
  '5': {
    name: 'Domain Layer',
    description: '领域层，定义核心数据模型和业务枚举',
    modules: ['Task Model', 'Memory Model', 'Knowledge Graph', 'Experience Learning'],
    tech: ['Python', 'Enum', 'Dataclass'],
    filePath: 'src/enterprise_agent_system/domain/'
  },
  '5a': {
    name: 'Task Model',
    description: '任务数据模型，定义任务的状态和属性',
    modules: ['任务状态枚举', '优先级枚举', '任务数据结构'],
    tech: ['Python', 'Enum', 'Dataclasses'],
    filePath: 'src/enterprise_agent_system/domain/core_data_models_and_enumerations.py'
  },
  '5b': {
    name: 'Memory Model',
    description: '记忆数据模型，支持知识图谱和经验学习',
    modules: ['记忆结构', '分类枚举', '关联关系'],
    tech: ['Python', 'Dataclasses', 'WeakMap'],
    filePath: 'src/enterprise_agent_system/domain/core_data_models_and_enumerations.py'
  },
  // Test Suite
  '6': {
    name: 'Test Suite',
    description: '测试套件，确保系统质量和稳定性',
    modules: ['单元测试', '集成测试', '系统测试'],
    tech: ['pytest', 'pytest-asyncio'],
    filePath: 'src/enterprise_agent_system/test_suite/'
  },
  '6a': {
    name: 'Unit Tests',
    description: '单元测试，测试各个模块的独立功能',
    modules: ['领域模型测试', '存储后端测试', '基础工具测试'],
    tech: ['pytest', 'pytest-asyncio'],
    filePath: 'src/enterprise_agent_system/test_suite/unit/'
  }
}

export default function ArchitecturePage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [showDetails, setShowDetails] = useState(false)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node.id)
    setShowDetails(true)
  }, [])

  const selectedNodeData = selectedNode ? moduleDetails[selectedNode as keyof typeof moduleDetails] : null

  const nodeColor = useMemo(() => {
    if (!selectedNode) return 'slate'
    const colors: Record<string, string> = {
      '1': 'cyan',
      '2': 'cyan',
      '3': 'purple',
      '4': 'blue',
      '5': 'emerald',
      '6': 'red',
    }
    return colors[selectedNode] || 'slate'
  }, [selectedNode])

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600">
              <Layers className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">系统架构图</h1>
              <p className="text-sm text-slate-400">五层架构 - 清晰展示模块依赖关系</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700 text-slate-300 hover:bg-slate-700/50 transition-colors">
              <RefreshCw className="w-4 h-4" />
              <span>刷新</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700 text-slate-300 hover:bg-slate-700/50 transition-colors">
              <Download className="w-4 h-4" />
              <span>导出</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Graph Area */}
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            fitView
            attributionPosition="bottom-left"
            className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"
          >
            <Controls className="bg-slate-800 border border-slate-700 rounded-lg shadow-xl" />
            <Background color="#475569" gap={20} className="opacity-20" />
            
            <Panel position="top-right" className="bg-slate-800/90 backdrop-blur-xl border border-slate-700 rounded-lg p-4 shadow-xl">
              <div className="text-xs text-slate-400 space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-cyan-500" />
                  <span>Presentation Layer</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-purple-500" />
                  <span>Infrastructure Layer</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500" />
                  <span>Core Layer</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-500" />
                  <span>Domain Layer</span>
                </div>
              </div>
            </Panel>
          </ReactFlow>
        </div>

        {/* Details Panel */}
        {showDetails && selectedNodeData && (
          <div className="w-96 bg-slate-900/95 backdrop-blur-xl border-l border-slate-700/50 overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">{selectedNodeData.name}</h2>
                <button
                  onClick={() => setShowDetails(false)}
                  className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>

              <p className="text-slate-400 mb-6">{selectedNodeData.description}</p>

              <div className="space-y-6">
                {/* Modules */}
                <div>
                  <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center space-x-2">
                    <Code className="w-4 h-4 text-cyan-400" />
                    <span>包含模块</span>
                  </h3>
                  <div className="space-y-2">
                    {selectedNodeData.modules.map((mod, i) => (
                      <div key={i} className="px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50 text-sm text-slate-300">
                        {mod}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Tech Stack */}
                <div>
                  <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center space-x-2">
                    <Database className="w-4 h-4 text-purple-400" />
                    <span>技术栈</span>
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedNodeData.tech.map((tech, i) => (
                      <span
                        key={i}
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          nodeColor === 'cyan' ? 'bg-cyan-500/20 text-cyan-400' :
                          nodeColor === 'purple' ? 'bg-purple-500/20 text-purple-400' :
                          nodeColor === 'blue' ? 'bg-blue-500/20 text-blue-400' :
                          nodeColor === 'emerald' ? 'bg-emerald-500/20 text-emerald-400' :
                          'bg-slate-500/20 text-slate-400'
                        }`}
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Code Link */}
                <div className="pt-4 border-t border-slate-700/50">
                  <a
                    href={`#${selectedNode}`}
                    className="flex items-center justify-center space-x-2 w-full px-4 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-medium hover:shadow-lg hover:shadow-cyan-500/30 transition-all"
                  >
                    <Code className="w-4 h-4" />
                    <span>查看源码</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="bg-slate-900/80 backdrop-blur-xl border-t border-slate-700/50 px-6 py-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-cyan-500" />
              <span className="text-slate-400">表现层</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-purple-500" />
              <span className="text-slate-400">基础设施层</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-blue-500" />
              <span className="text-slate-400">核心层</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-emerald-500" />
              <span className="text-slate-400">领域层</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-slate-400">测试套件</span>
            </div>
          </div>
          <div className="text-slate-500">
            点击节点查看详情 | 拖拽重新布局
          </div>
        </div>
      </div>
    </div>
  )
}
