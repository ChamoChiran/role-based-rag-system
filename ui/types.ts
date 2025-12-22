
export enum Role {
  FINANCE = 'Finance',
  MARKETING = 'Marketing',
  HR = 'HR',
  C_LEVEL = 'C-Level',
  EMPLOYEE = 'Employee'
}

export interface MessagePart {
  text?: string;
  source?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'bot';
  content: string;
  timestamp: Date;
  sources?: string[];
  department?: Role;
}

export interface Session {
  id: string;
  title: string;
  date: Date;
  role: Role;
  summary?: string;
  history?: Message[];
}
