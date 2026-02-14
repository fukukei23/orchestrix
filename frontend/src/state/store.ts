import { create } from 'zustand';

// 型定義
export interface Task {
  id: string;
  title: string;
  description: string;
  goal?: string;
  complexity_score: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  priority: number;
  created_at: string;
  cron_expression?: string;
}

export interface Agent {
  id: string;
  name: string;
  cli_command: string;
  default_model: string;
  supports_features: string[];
  cost_per_1k_input: number;
  cost_per_1k_output: number;
  enabled: boolean;
}

export interface Execution {
  id: string;
  task_id: string;
  agent_type: string;
  model_used: string;
  status: string;
  start_time: string;
  end_time: string;
  cost_usd: number;
  output_tokens: number;
}

export interface OrchestrixState {
  tasks: Task[];
  agents: Agent[];
  executions: Execution[];
  apiBaseUrl: string;
  selectedTask: Task | null;
  isLoading: boolean;
  setTasks: (tasks: Task[]) => void;
  setAgents: (agents: Agent[]) => void;
  setExecutions: (executions: Execution[]) => void;
  setApiBaseUrl: (url: string) => void;
  setSelectedTask: (task: Task | null) => void;
  setIsLoading: (loading: boolean) => void;
  fetchTasks: () => Promise<void>;
  fetchAgents: () => Promise<void>;
  fetchExecutions: () => Promise<void>;
  createTask: (task: Partial<Task>) => Promise<unknown>;
  executeTask: (taskId: string) => Promise<unknown>;
  toggleAgent: (agentId: string, enabled: boolean) => Promise<unknown>;
  initializeStore: () => Promise<void>;
}

// 初期状態
const initialState = {
  tasks: [],
  agents: [],
  executions: [],
  apiBaseUrl: 'http://localhost:8000/api/v1',
  selectedTask: null,
  isLoading: false,
};

// ストア作成
export const useStore = create<OrchestrixState>((set, get) => ({
  ...initialState,

  // アクション
  setTasks: (tasks: Task[]) => set({ tasks }),
  setAgents: (agents: Agent[]) => set({ agents }),
  setExecutions: (executions: Execution[]) => set({ executions }),
  setApiBaseUrl: (url: string) => set({ apiBaseUrl: url }),
  setSelectedTask: (task: Task | null) => set({ selectedTask: task }),
  setIsLoading: (loading: boolean) => set({ isLoading: loading }),

  // データ取得アクション
  fetchTasks: async () => {
    set({ isLoading: true });
    try {
      const state = get();
      const response = await fetch(`${state.apiBaseUrl}/tasks`);
      const data = await response.json();
      set({ tasks: data, isLoading: false });
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
      set({ isLoading: false });
    }
  },

  fetchAgents: async () => {
    set({ isLoading: true });
    try {
      const state = get();
      const response = await fetch(`${state.apiBaseUrl}/agents`);
      const data = await response.json();
      set({ agents: data, isLoading: false });
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      set({ isLoading: false });
    }
  },

  fetchExecutions: async () => {
    set({ isLoading: true });
    try {
      const state = get();
      const response = await fetch(`${state.apiBaseUrl}/analytics/executions/summary`);
      const data = await response.json();
      set({ executions: data.executions || [], isLoading: false });
    } catch (error) {
      console.error('Failed to fetch executions:', error);
      set({ isLoading: false });
    }
  },

  // タスク操作
  createTask: async (task: Partial<Task>) => {
    set({ isLoading: true });
    try {
      const state = get();
      const response = await fetch(`${state.apiBaseUrl}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task),
      });
      const data = await response.json();
      await get().fetchTasks();
      set({ isLoading: false });
      return data;
    } catch (error) {
      console.error('Failed to create task:', error);
      set({ isLoading: false });
      throw error;
    }
  },

  executeTask: async (taskId: string) => {
    set({ isLoading: true });
    try {
      const state = get();
      const response = await fetch(`${state.apiBaseUrl}/tasks/${taskId}/execute`, {
        method: 'POST',
      });
      const data = await response.json();
      await get().fetchTasks();
      set({ isLoading: false });
      return data;
    } catch (error) {
      console.error('Failed to execute task:', error);
      set({ isLoading: false });
      throw error;
    }
  },

  // エージェント操作
  toggleAgent: async (agentId: string, enabled: boolean) => {
    try {
      const state = get();
      const response = await fetch(`${state.apiBaseUrl}/agents/${agentId}/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled }),
      });
      const data = await response.json();
      await get().fetchAgents();
      return data;
    } catch (error) {
      console.error('Failed to toggle agent:', error);
      throw error;
    }
  },

  // ストア初期化
  initializeStore: async () => {
    await get().fetchTasks();
    await get().fetchAgents();
    await get().fetchExecutions();
  },
}));
