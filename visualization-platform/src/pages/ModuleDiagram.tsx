import { useCallback, useState } from 'react'
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
  MiniMap,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { Package, Layers, Database, Code, FileText, Zap, GitBranch, RefreshCw, Download } from 'lucide-react'

const initialNodes: Node[] = [
  {
    id: 'application',
    type: 'default',
    position: { x: 400, y: 50 },
    data: { label: 'Application Layer\n应用层' },
    style: {
      background: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '16px',
      padding: '20px',
      fontWeight: 'bold',
      fontSize: '16px',
      boxShadow: '0 10px 30px rgba(6, 182, 212, 0.3)',
      width: '180px',
      textAlign: 'center'
    },
  },
  {
    id: 'cli',
    type: 'default',
    position: { x: 100, y: 180 },
    data: { label: 'CLI\n命令行应用' },
    style: {
      background: 'linear-gradient(135deg, #0e7490 0%, #065f77 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(14, 116, 144, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
  {
    id: 'llm-analysis',
    type: 'default',
    position: { x: 300, y: 180 },
    data: { label: 'LLM Analysis\n分析系统' },
    style: {
      background: 'linear-gradient(135deg, #0e7490 0%, #065f77 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(14, 116, 144, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
  {
    id: 'data-pipeline',
    type: 'default',
    position: { x: 500, y: 180 },
    data: { label: 'Data Pipeline\n数据管道' },
    style: {
      background: 'linear-gradient(135deg, #0e7490 0%, #065f77 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(14, 116, 144, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
  {
    id: 'vue-analyzer',
    type: 'default',
    position: { x: 700, y: 180 },
    data: { label: 'Vue Analyzer\nVue分析器' },
    style: {
      background: 'linear-gradient(135deg, #0e7490 0%, #065f77 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(14, 116, 144, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
  {
    id: 'infrastructure',
    type: 'default',
    position: { x: 400, y: 330 },
    data: { label: 'Infrastructure Layer\n基础设施层' },
    style: {
      background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '16px',
      padding: '20px',
      fontWeight: 'bold',
      fontSize: '16px',
      boxShadow: '0 10px 30px rgba(124, 58, 237, 0.3)',
      width: '200px',
      textAlign: 'center'
    },
  },
  {
    id: 'github',
    type: 'default',
    position: { x: 100, y: 460 },
    data: { label: 'GitHub Analyzer\nGitHub分析器' },
    style: {
      background: 'linear-gradient(135deg, #6d28d9 0%, #5b21b6 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(109, 40, 217, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
  {
    id: 'logging',
    type: 'default',
    position: { x: 300, y: 460 },
    data: { label: 'Logging System\n日志系统' },
    style: {
      background: 'linear-gradient(135deg, #6d28d9 0%, #5b21b6 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(109, 40, 217, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
  {
    id: 'fastapi',
    type: 'default',
    position: { x: 500, y: 460 },
    data: { label: 'FastAPI\nREST API' },
    style: {
      background: 'linear-gradient(135deg, #6d28d9 0%, #5b21b6 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(109, 40, 217, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
  {
    id: 'config',
    type: 'default',
    position: { x: 700, y: 460 },
    data: { label: 'Config Manager\n配置管理' },
    style: {
      background: 'linear-gradient(135deg, #6d28d9 0%, #5b21b6 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(109, 40, 217, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
  {
    id: 'core',
    type: 'default',
    position: { x: 400, y: 610 },
    data: { label: 'Core Layer\n核心层' },
    style: {
      background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '16px',
      padding: '20px',
      fontWeight: 'bold',
      fontSize: '16px',
      boxShadow: '0 10px 30px rgba(37, 99, 235, 0.3)',
      width: '180px',
      textAlign: 'center'
    },
  },
  {
    id: 'orchestrator',
    type: 'default',
    position: { x: 250, y: 740 },
    data: { label: 'Agent Orchestrator\nAgent编排器' },
    style: {
      background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(29, 78, 216, 0.3)',
      width: '150px',
      textAlign: 'center'
    },
  },
  {
    id: 'storage',
    type: 'default',
    position: { x: 550, y: 740 },
    data: { label: 'Storage Backend\n存储后端' },
    style: {
      background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(29, 78, 216, 0.3)',
      width: '150px',
      textAlign: 'center'
    },
  },
  {
    id: 'domain',
    type: 'default',
    position: { x: 400, y: 890 },
    data: { label: 'Domain Layer\n领域层' },
    style: {
      background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '16px',
      padding: '20px',
      fontWeight: 'bold',
      fontSize: '16px',
      boxShadow: '0 10px 30px rgba(5, 150, 105, 0.3)',
      width: '180px',
      textAlign: 'center'
    },
  },
  {
    id: 'task-model',
    type: 'default',
    position: { x: 250, y: 1020 },
    data: { label: 'Task Model\n任务模型' },
    style: {
      background: 'linear-gradient(135deg, #047857 0%, #065f46 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(4, 120, 87, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
  {
    id: 'memory-model',
    type: 'default',
    position: { x: 550, y: 1020 },
    data: { label: 'Memory Model\n记忆模型' },
    style: {
      background: 'linear-gradient(135deg, #047857 0%, #065f46 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(4, 120, 87, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
  {
    id: 'test',
    type: 'default',
    position: { x: 900, y: 50 },
    data: { label: 'Test Suite\n测试套件' },
    style: {
      background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '16px',
      padding: '20px',
      fontWeight: 'bold',
      fontSize: '16px',
      boxShadow: '0 10px 30px rgba(220, 38, 38, 0.3)',
      width: '160px',
      textAlign: 'center'
    },
  },
  {
    id: 'unit-tests',
    type: 'default',
    position: { x: 900, y: 200 },
    data: { label: 'Unit Tests\n单元测试' },
    style: {
      background: 'linear-gradient(135deg, #b91c1c 0%, #991b1b 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(185, 28, 28, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
  {
    id: 'integration-tests',
    type: 'default',
    position: { x: 900, y: 350 },
    data: { label: 'Integration Tests\n集成测试' },
    style: {
      background: 'linear-gradient(135deg, #b91c1c 0%, #991b1b 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      padding: '16px',
      fontSize: '13px',
      boxShadow: '0 8px 25px rgba(185, 28, 28, 0.3)',
      width: '140px',
      textAlign: 'center'
    },
  },
]

const initialEdges: Edge[] = [
  { id: 'app-cli', source: 'application', target: 'cli', animated: true, style: { stroke: '#06b6d4', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#06b6d4' } },
  { id: 'app-llm', source: 'application', target: 'llm-analysis', animated: true, style: { stroke: '#06b6d4', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#06b6d4' } },
  { id: 'app-pipeline', source: 'application', target: 'data-pipeline', animated: true, style: { stroke: '#06b6d4', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#06b6d4' } },
  { id: 'app-vue', source: 'application', target: 'vue-analyzer', animated: true, style: { stroke: '#06b6d4', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#06b6d4' } },
  { id: 'app-infra', source: 'application', target: 'infrastructure', animated: true, style: { stroke: '#0891b2', strokeWidth: 3 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#0891b2' } },
  { id: 'infra-github', source: 'infrastructure', target: 'github', animated: true, style: { stroke: '#7c3aed', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#7c3aed' } },
  { id: 'infra-logging', source: 'infrastructure', target: 'logging', animated: true, style: { stroke: '#7c3aed', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#7c3aed' } },
  { id: 'infra-fastapi', source: 'infrastructure', target: 'fastapi', animated: true, style: { stroke: '#7c3aed', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#7c3aed' } },
  { id: 'infra-config', source: 'infrastructure', target: 'config', animated: true, style: { stroke: '#7c3aed', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#7c3aed' } },
  { id: 'infra-core', source: 'infrastructure', target: 'core', animated: true, style: { stroke: '#6d28d9', strokeWidth: 3 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#6d28d9' } },
  { id: 'core-orchestrator', source: 'core', target: 'orchestrator', animated: true, style: { stroke: '#2563eb', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#2563eb' } },
  { id: 'core-storage', source: 'core', target: 'storage', animated: true, style: { stroke: '#2563eb', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#2563eb' } },
  { id: 'orchestrator-storage', source: 'orchestrator', target: 'storage', animated: true, style: { stroke: '#1d4ed8', strokeWidth: 2, strokeDasharray: '5,5' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#1d4ed8' } },
  { id: 'core-domain', source: 'core', target: 'domain', animated: true, style: { stroke: '#1d4ed8', strokeWidth: 3 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#1d4ed8' } },
  { id: 'domain-task', source: 'domain', target: 'task-model', animated: true, style: { stroke: '#059669', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#059669' } },
  { id: 'domain-memory', source: 'domain', target: 'memory-model', animated: true, style: { stroke: '#059669', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#059669' } },
  { id: 'core-test', source: 'core', target: 'test', animated: true, style: { stroke: '#2563eb', strokeWidth: 2, strokeDasharray: '8,8' }, markerEnd: { type: MarkerType.ArrowClosed, color: '#2563eb' } },
  { id: 'test-unit', source: 'test', target: 'unit-tests', animated: true, style: { stroke: '#dc2626', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#dc2626' } },
  { id: 'test-integration', source: 'test', target: 'integration-tests', animated: true, style: { stroke: '#dc2626', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#dc2626' } },
]

const moduleDetails: Record<string, { name: string; description: string; tech: string[]; features: string[] }> = {
  'application': {
    name: 'Application Layer',
    description: '应用层负责协调各个子系统，定义业务用例和工作流程',
    tech: ['Python', 'asyncio', 'dataclasses'],
    features: ['命令行界面', 'LLM分析', '数据处理', 'Vue项目分析']
  },
  'cli': {
    name: 'CLI Application',
    description: '提供用户友好的命令行接口，支持多种操作模式',
    tech: ['argparse', 'rich', 'click'],
    features: ['任务创建', '状态查询', '报告生成', '交互模式']
  },
  'llm-analysis': {
    name: 'LLM Analysis System',
    description: '集成大语言模型进行智能分析和报告生成',
    tech: ['OpenAI API', '硅基流动', 'Prompt Engineering'],
    features: ['代码分析', '文档生成', '智能建议', '摘要总结']
  },
  'data-pipeline': {
    name: 'Data Pipeline',
    description: '处理和转换数据的管道系统',
    tech: ['Pandas', 'NumPy', 'JSON'],
    features: ['数据导入', '清洗转换', '验证', '持久化']
  },
  'vue-analyzer': {
    name: 'Vue Analyzer',
    description: '专门用于分析Vue.js项目的组件',
    tech: ['AST', '正则表达式', 'Pathlib'],
    features: ['组件扫描', '依赖分析', '性能评估', '质量检查']
  },
  'infrastructure': {
    name: 'Infrastructure Layer',
    description: '提供基础设施和外部服务集成',
    tech: ['FastAPI', 'SQLAlchemy', 'Redis', 'Docker'],
    features: ['API服务', '日志记录', '配置管理', '缓存']
  },
  'github': {
    name: 'GitHub Analyzer',
    description: 'GitHub仓库分析器，支持在线和离线模式',
    tech: ['requests', 'PyGithub', 'GitPython'],
    features: ['仓库克隆', '代码分析', '贡献统计', 'Issue追踪']
  },
  'logging': {
    name: 'Enterprise Logging System',
    description: '企业级日志系统，支持多种输出和级别',
    tech: ['logging', 'structlog', 'Sentry'],
    features: ['多级别日志', '文件输出', '控制台输出', '错误追踪']
  },
  'fastapi': {
    name: 'FastAPI REST API',
    description: '高性能的REST API服务',
    tech: ['FastAPI', 'Uvicorn', 'Pydantic'],
    features: ['自动文档', '类型验证', '异步处理', 'CORS支持']
  },
  'config': {
    name: 'Configuration Manager',
    description: '应用程序配置管理系统',
    tech: ['Pydantic Settings', 'YAML', '环境变量'],
    features: ['配置加载', '类型安全', '环境覆盖', '热重载']
  },
  'core': {
    name: 'Core Layer',
    description: '核心业务逻辑层，包含Agent编排和存储',
    tech: ['Python', 'dataclasses', 'asyncio'],
    features: ['任务调度', '存储抽象', '工厂模式', '事件驱动']
  },
  'orchestrator': {
    name: 'Agent Orchestrator',
    description: '负责Agent的编排、调度和执行',
    tech: ['asyncio', 'Queues', 'ThreadPoolExecutor'],
    features: ['优先级队列', '并发执行', '任务依赖', '错误重试']
  },
  'storage': {
    name: 'Storage Backend',
    description: '抽象存储接口，支持多种实现',
    tech: ['SQLAlchemy', 'SQLite', '内存存储'],
    features: ['多后端支持', '统一接口', '事务处理', '查询优化']
  },
  'domain': {
    name: 'Domain Layer',
    description: '领域层，定义核心数据模型和业务规则',
    tech: ['dataclasses', 'Enum', 'TypedDict'],
    features: ['任务模型', '记忆模型', '知识图谱', '领域规则']
  },
  'task-model': {
    name: 'Task Model',
    description: '任务数据模型和状态管理',
    tech: ['Enum', 'dataclasses', 'datetime'],
    features: ['状态追踪', '优先级', '依赖关系', '时间戳']
  },
  'memory-model': {
    name: 'Memory Model',
    description: '记忆和知识存储模型',
    tech: ['dataclasses', 'WeakMap', 'JSON'],
    features: ['记忆分类', '关联关系', '知识提取', '持久化']
  },
  'test': {
    name: 'Test Suite',
    description: '全面的测试套件',
    tech: ['pytest', 'pytest-asyncio', 'hypothesis'],
    features: ['单元测试', '集成测试', '性能测试', '覆盖率']
  },
  'unit-tests': {
    name: 'Unit Tests',
    description: '单元测试，测试独立组件',
    tech: ['pytest', 'unittest.mock', 'fixtures'],
    features: ['模型测试', '逻辑测试', 'Mock依赖', '边界测试']
  },
  'integration-tests': {
    name: 'Integration Tests',
    description: '集成测试，测试组件间交互',
    tech: ['pytest', 'testcontainers', 'pytest-asyncio'],
    features: ['API测试', '数据库测试', '端到端测试', '场景测试']
  },
}

export default function ModuleDiagramPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node.id)
  }, [])

  const selectedDetail = selectedNode ? moduleDetails[selectedNode] : null

  return (
    <div className="h-screen flex flex-col">
      <div className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600">
              <Package className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">模块依赖图</h1>
              <p className="text-sm text-slate-400">交互式展示系统模块及其依赖关系</p>
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

      <div className="flex-1 flex">
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
            <MiniMap 
              className="bg-slate-800 border border-slate-700 rounded-lg shadow-xl"
              nodeStrokeColor={(n) => {
                if (n.style?.background) return (n.style.background as string).split(',')[0].replace('linear-gradient(135deg, ', '');
                return '#06b6d4';
              }}
              nodeColor={(n) => {
                if (n.style?.background) return (n.style.background as string).split(',')[0].replace('linear-gradient(135deg, ', '');
                return '#06b6d4';
              }}
            />
            
            <Panel position="top-right" className="bg-slate-800/90 backdrop-blur-xl border border-slate-700 rounded-lg p-4 shadow-xl">
              <div className="text-xs text-slate-400 space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-cyan-500" />
                  <span>Application Layer</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-purple-500" />
                  <span>Infrastructure</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500" />
                  <span>Core Layer</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-500" />
                  <span>Domain Layer</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <span>Test Suite</span>
                </div>
              </div>
            </Panel>
          </ReactFlow>
        </div>

        {selectedDetail && (
          <div className="w-96 bg-slate-900/95 backdrop-blur-xl border-l border-slate-700/50 overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">{selectedDetail.name}</h2>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>

              <p className="text-slate-400 mb-6">{selectedDetail.description}</p>

              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center space-x-2">
                    <Code className="w-4 h-4 text-purple-400" />
                    <span>技术栈</span>
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedDetail.tech.map((tech, i) => (
                      <span
                        key={i}
                        className="px-3 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center space-x-2">
                    <Zap className="w-4 h-4 text-cyan-400" />
                    <span>主要功能</span>
                  </h3>
                  <div className="space-y-2">
                    {selectedDetail.features.map((feature, i) => (
                      <div key={i} className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
                        <GitBranch className="w-4 h-4 text-slate-500" />
                        <span className="text-sm text-slate-300">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
