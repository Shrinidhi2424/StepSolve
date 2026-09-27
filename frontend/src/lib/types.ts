export interface Step {
  step_number: number;
  title: string;
  description: string;
  formula: string;
  substitution?: string | null;
  value?: any;
}

export interface SolveResponse {
  topic_id: string;
  inputs_echo: Record<string, any>;
  steps: Step[];
  result: Record<string, any>;
  result_summary: string;
  iterations_table?: Record<string, any>[] | null;
  plot_data?: any;
  warnings: string[];
}

export interface TopicField {
  name: string;
  type: 'number' | 'function' | 'table' | 'matrix';
  label: string;
  default?: any;
}

export interface Topic {
  id: string;
  module: number;
  title: string;
  short_description: string;
  input_schema: TopicField[];
}
