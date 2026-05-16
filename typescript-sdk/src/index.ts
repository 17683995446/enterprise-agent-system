/**
 * Enterprise Agent System - TypeScript SDK
 * 企业级Agent系统TypeScript SDK
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// ==================== 类型定义 ====================

export enum TaskPriority {
  URGENT = 'urgent',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export interface Task {
  task_id: string;
  task_title: string;
  task_description: string;
  priority: TaskPriority;
  status: TaskStatus;
  progress: number;
  created_at: string;
  updated_at: string;
  tags: string[];
  result?: Record<string, any>;
  error?: string;
}

export interface Agent {
  agent_id: string;
  agent_name: string;
  agent_mode: string;
  status: string;
  created_at: string;
  total_tasks: number;
  completed_tasks: number;
  success_rate: number;
}

export interface Memory {
  memory_id: string;
  memory_title: string;
  memory_content: string;
  memory_category: string;
  memory_tags: string[];
  created_at: string;
  access_count: number;
  last_accessed: string;
}

export interface CreateTaskRequest {
  task_title: string;
  task_description: string;
  priority?: TaskPriority;
  tags?: string[];
}

export interface CreateAgentRequest {
  agent_name: string;
  agent_mode?: string;
}

export interface CreateMemoryRequest {
  memory_title: string;
  memory_content: string;
  memory_category?: string;
  memory_tags?: string[];
}

// ==================== SDK客户端 ====================

export class EnterpriseAgentSDK {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(config: SDKConfig) {
    this.baseURL = config.baseURL || 'http://localhost:8000';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...(config.apiKey && { 'X-API-Key': config.apiKey }),
      },
    });

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 429) {
          // Rate limit - wait and retry
          const retryAfter = error.response.headers['retry-after'] || 60;
          await this.delay(retryAfter * 1000);
          return this.client.request(error.config);
        }
        throw error;
      }
    );
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // Tasks API
  readonly tasks = {
    create: async (request: CreateTaskRequest): Promise<Task> => {
      const response = await this.client.post<Task>('/api/tasks', request);
      return response.data;
    },

    get: async (taskId: string): Promise<Task> => {
      const response = await this.client.get<Task>(`/api/tasks/${taskId}`);
      return response.data;
    },

    list: async (params?: {
      status?: TaskStatus;
      priority?: TaskPriority;
      page?: number;
      page_size?: number;
    }): Promise<Task[]> => {
      const response = await this.client.get<Task[]>('/api/tasks', { params });
      return response.data;
    },

    update: async (
      taskId: string,
      request: Partial<CreateTaskRequest>
    ): Promise<Task> => {
      const response = await this.client.put<Task>(`/api/tasks/${taskId}`, request);
      return response.data;
    },

    delete: async (taskId: string): Promise<void> => {
      await this.client.delete(`/api/tasks/${taskId}`);
    },

    start: async (taskId: string): Promise<Task> => {
      await this.client.post(`/api/tasks/${taskId}/start`);
      return this.tasks.get(taskId);
    },

    complete: async (
      taskId: string,
      result?: Record<string, any>
    ): Promise<Task> => {
      await this.client.post(`/api/tasks/${taskId}/complete`, { result });
      return this.tasks.get(taskId);
    },

    statistics: async (): Promise<{
      total: number;
      pending: number;
      running: number;
      completed: number;
      failed: number;
      success_rate: string;
    }> => {
      const response = await this.client.get('/api/tasks/statistics/summary');
      return response.data;
    },
  };

  // Agents API
  readonly agents = {
    create: async (request: CreateAgentRequest): Promise<Agent> => {
      const response = await this.client.post<Agent>('/api/agents', request);
      return response.data;
    },

    get: async (agentId: string): Promise<Agent> => {
      const response = await this.client.get<Agent>(`/api/agents/${agentId}`);
      return response.data;
    },

    list: async (): Promise<Agent[]> => {
      const response = await this.client.get<Agent[]>('/api/agents');
      return response.data;
    },

    start: async (agentId: string): Promise<void> => {
      await this.client.post(`/api/agents/${agentId}/start`);
    },

    stop: async (agentId: string): Promise<void> => {
      await this.client.post(`/api/agents/${agentId}/stop`);
    },
  };

  // Memory API
  readonly memory = {
    create: async (request: CreateMemoryRequest): Promise<Memory> => {
      const response = await this.client.post<Memory>('/api/memory', request);
      return response.data;
    },

    get: async (memoryId: string): Promise<Memory> => {
      const response = await this.client.get<Memory>(`/api/memory/${memoryId}`);
      return response.data;
    },

    list: async (params?: {
      category?: string;
      tag?: string;
    }): Promise<Memory[]> => {
      const response = await this.client.get<Memory[]>('/api/memory', { params });
      return response.data;
    },

    search: async (query: string): Promise<Memory[]> => {
      const response = await this.client.get<Memory[]>('/api/memory/search', {
        params: { query },
      });
      return response.data;
    },

    knowledgeGraphSummary: async (): Promise<{
      total_memories: number;
      categories: Record<string, number>;
      total_nodes: number;
      total_edges: number;
    }> => {
      const response = await this.client.get('/api/memory/knowledge-graph/summary');
      return response.data;
    },
  };

  // Projects API
  readonly projects = {
    analyze: async (
      projectPath: string,
      analysisType: string = 'auto'
    ): Promise<{
      project_name: string;
      project_path: string;
      project_type: string;
      analysis_time: string;
      statistics: Record<string, any>;
      quality_score: number;
    }> => {
      const response = await this.client.post('/api/projects/analyze', {
        project_path: projectPath,
        analysis_type: analysisType,
      });
      return response.data;
    },

    analyzeGithub: async (
      owner: string,
      repo: string
    ): Promise<Record<string, any>> => {
      const response = await this.client.post('/api/projects/analyze-github', null, {
        params: { owner, repo },
      });
      return response.data;
    },

    supportedTypes: async (): Promise<{
      types: Array<{
        id: string;
        name: string;
        extensions: string[];
      }>;
    }> => {
      const response = await this.client.get('/api/projects/supported-types');
      return response.data;
    },
  };

  // System API
  readonly system = {
    health: async (): Promise<{ status: string }> => {
      const response = await this.client.get('/health');
      return response.data;
    },

    info: async (): Promise<{
      name: string;
      version: string;
      status: string;
      endpoints: Record<string, string>;
    }> => {
      const response = await this.client.get('/');
      return response.data;
    },

    statistics: async (): Promise<Record<string, any>> => {
      const response = await this.client.get('/api/statistics');
      return response.data;
    },
  };
}

export interface SDKConfig {
  baseURL?: string;
  apiKey?: string;
  timeout?: number;
}

// ==================== React Hooks ====================

export function useTasks() {
  // React Hook实现将在后面添加
  return null;
}

export function useAgents() {
  return null;
}

export function useMemory() {
  return null;
}

// ==================== 导出 ====================

export default EnterpriseAgentSDK;
