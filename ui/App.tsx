import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Send, 
  TrendingUp, 
  Users, 
  ShieldCheck, 
  UserCircle,
  Menu,
  X,
  Plus,
  Search,
  MessageSquare,
  ChevronDown,
  Sparkles,
  Link as LinkIcon,
  Lock,
  Unlock,
  Shield,
  Clock,
  History
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Role, Message, Session } from './types';
import { fetchSessions } from './services/backendService';

// --- Types & Constants ---

interface RoleInfo {
  label: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  level: 'Restricted' | 'Internal' | 'Unrestricted';
}

const ROLE_DETAILS: Record<Role, RoleInfo> = {
  [Role.FINANCE]: {
    label: 'Finance',
    description: 'P&L, audits & tax records',
    icon: <TrendingUp size={16} />,
    color: 'blue',
    level: 'Internal'
  },
  [Role.MARKETING]: {
    label: 'Marketing',
    description: 'Ad spend & ROI metrics',
    icon: <Search size={16} />,
    color: 'purple',
    level: 'Internal'
  },
  [Role.HR]: {
    label: 'HR',
    description: 'Payroll & benefit structures',
    icon: <Users size={16} />,
    color: 'emerald',
    level: 'Restricted'
  },
  [Role.ENGINEERING]: {
    label: 'Engineering',
    description: 'Product dev & roadmaps',
    icon: <ShieldCheck size={16} />,
    color: 'amber',
    level: 'Restricted'
  },
  [Role.GENERAL]: {
    label: 'General',
    description: 'General info & news',
    icon: <UserCircle size={16} />,
    color: 'slate',
    level: 'Internal'
  }
};

const getSolidColorClasses = (color: string) => {
  switch (color) {
    case 'blue': return 'text-blue-400 bg-blue-900/40 border-blue-800/60';
    case 'purple': return 'text-purple-400 bg-purple-900/40 border-purple-800/60';
    case 'emerald': return 'text-emerald-400 bg-emerald-900/40 border-emerald-800/60';
    case 'amber': return 'text-amber-400 bg-amber-900/40 border-amber-800/60';
    default: return 'text-slate-400 bg-slate-800 border-slate-700';
  }
};

// --- Sub-Components ---

const BackgroundGradients: React.FC<{ roleColor: string }> = ({ roleColor }) => {
  const getGradient = (color: string) => {
    switch (color) {
      case 'blue': return 'from-blue-600/10 via-transparent to-transparent';
      case 'purple': return 'from-purple-600/10 via-transparent to-transparent';
      case 'emerald': return 'from-emerald-600/10 via-transparent to-transparent';
      case 'amber': return 'from-amber-600/10 via-transparent to-transparent';
      default: return 'from-slate-600/10 via-transparent to-transparent';
    }
  };

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
      <div className={`absolute -top-1/4 -left-1/4 w-1/2 h-1/2 bg-gradient-to-br ${getGradient(roleColor)} blur-[120px] rounded-full`} />
      <div className={`absolute -bottom-1/4 -right-1/4 w-1/2 h-1/2 bg-gradient-to-tl ${getGradient(roleColor)} blur-[120px] rounded-full opacity-50`} />
    </div>
  );
};

const SidebarItem: React.FC<{
  session: Session;
  isActive: boolean;
  onClick: () => void;
}> = ({ session, isActive, onClick }) => (
  <button 
    onClick={onClick}
    className={`flex items-center gap-3.5 p-3 rounded-lg transition-all text-left group border font-normal w-full
      ${isActive 
        ? 'bg-[#1E293B] text-white border-slate-700 shadow-sm' 
        : 'text-slate-300 hover:text-white hover:bg-[#1E293B] border-transparent hover:border-slate-800'}
    `}
  >
    <div className={`p-1.5 rounded-md transition-colors ${isActive ? 'bg-[#2D3748] text-blue-400' : 'bg-[#1E293B] text-slate-400 group-hover:bg-[#2D3748] group-hover:text-blue-400'}`}>
      <MessageSquare size={14} />
    </div>
    <div className="flex-1 truncate">
      <span className="truncate block font-normal text-sm">{session.title}</span>
      <span className="text-[10px] text-slate-500 block uppercase tracking-tight">{ROLE_DETAILS[session.role].label}</span>
    </div>
  </button>
);

const RoleSwitcher: React.FC<{ currentRole: Role, setRole: (r: Role) => void }> = ({ currentRole, setRole }) => {
  const [isOpen, setIsOpen] = useState(false);
  const roles = Object.values(Role);
  const current = ROLE_DETAILS[currentRole];

  return (
    <div className="relative w-full font-normal">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full flex items-center justify-between p-4 bg-[#1E293B] rounded-xl hover:bg-[#2D3748] transition-all duration-200 border border-[#334155] group ${isOpen ? 'ring-2 ring-blue-500/50' : ''}`}
      >
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg border ${getSolidColorClasses(current.color)}`}>
            {current.icon}
          </div>
          <div className="text-left">
            <p className="text-[10px] text-slate-400 uppercase tracking-widest font-normal mb-0.5">Access Authority</p>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-white tracking-tight">{current.label}</span>
              <span className={`text-[9px] px-2 py-0.5 rounded-full border font-normal uppercase shadow-sm ${current.level === 'Restricted' ? 'text-amber-400 border-amber-900 bg-amber-950' : 'text-blue-400 border-blue-900 bg-blue-950'}`}>
                {current.level}
              </span>
            </div>
          </div>
        </div>
        <ChevronDown size={14} className={`text-slate-500 transition-transform duration-200 ${isOpen ? 'rotate-180 text-white' : 'group-hover:text-slate-300'}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
            <motion.div 
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 5 }}
              transition={{ duration: 0.15 }}
              className="absolute top-full left-0 right-0 mt-2 p-1.5 bg-[#0F172A] rounded-xl z-50 shadow-2xl border border-[#334155] overflow-hidden"
            >
              <div className="max-h-[360px] overflow-y-auto custom-scrollbar">
                {roles.map((roleKey) => {
                  const role = ROLE_DETAILS[roleKey];
                  const isActive = roleKey === currentRole;
                  return (
                    <button
                      key={roleKey}
                      disabled={isActive}
                      onClick={() => {
                        setRole(roleKey);
                        setIsOpen(false);
                      }}
                      className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all mb-1 text-left relative group font-normal ${isActive ? 'bg-[#1E293B] border border-slate-600 cursor-default' : 'hover:bg-[#1E293B] active:bg-[#334155]'}`}
                    >
                      <div className={`p-2 rounded-md border ${isActive ? 'bg-slate-700 border-slate-600 text-slate-400' : getSolidColorClasses(role.color)}`}>
                        {role.icon}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className={`text-sm font-normal ${isActive ? 'text-slate-200' : 'text-slate-100 group-hover:text-white'}`}>{role.label}</span>
                        </div>
                        <p className={`text-[11px] leading-tight ${isActive ? 'text-slate-400' : 'text-slate-500 group-hover:text-slate-300'} line-clamp-1`}>{role.description}</p>
                      </div>
                      {isActive && <div className="absolute right-3 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-blue-500" />}
                    </button>
                  );
                })}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

const Sidebar: React.FC<{ 
  currentRole: Role, 
  setRole: (r: Role) => void,
  sessions: Session[],
  activeSessionId: string | null,
  onSessionSelect: (id: string | null) => void,
  isMobileOpen: boolean,
  toggleMobile: () => void
}> = ({ currentRole, setRole, sessions, activeSessionId, onSessionSelect, isMobileOpen, toggleMobile }) => (
  <aside className={`fixed inset-y-0 left-0 z-40 w-80 bg-[#0B1220] border-r border-[#1E293B] p-6 flex flex-col gap-6 transition-transform duration-300 md:relative md:translate-x-0 ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'}`}>
    <div className="flex items-center justify-between px-1">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-900/20">
          <Sparkles className="text-white" size={24} />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">FinSolve</h1>
          <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-[0.2em] -mt-1.5">Intelligence</p>
        </div>
      </div>
      <button onClick={toggleMobile} className="md:hidden text-slate-400 hover:text-white p-2 bg-[#1E293B] rounded-lg">
        <X size={24} />
      </button>
    </div>

    <div className="space-y-4">
      <RoleSwitcher currentRole={currentRole} setRole={setRole} />
      <button 
        onClick={() => onSessionSelect(null)}
        className={`w-full flex items-center justify-center gap-2 p-3.5 rounded-xl border font-normal text-xs uppercase tracking-widest transition-all active:scale-[0.98] ${activeSessionId === null ? 'bg-blue-600 text-white border-blue-500 shadow-md shadow-blue-900/20' : 'bg-[#1E293B] text-slate-300 border-slate-700 hover:bg-[#2D3748]'}`}
      >
        <Plus size={16} />
        New Chat
      </button>
    </div>

    <div className="flex-1 overflow-y-auto custom-scrollbar flex flex-col gap-1.5 mt-2">
      <p className="text-[11px] text-slate-500 uppercase tracking-widest font-semibold px-2 mb-2 flex items-center justify-between">
        <span>Recent Chats</span>
        <span className="w-2 h-2 rounded-full bg-emerald-500" />
      </p>
      {sessions.length === 0 ? (
        <div className="px-2 py-8 text-center">
          <p className="text-xs text-slate-600 font-normal italic">No recent activity detected.</p>
        </div>
      ) : (
        sessions.map(s => (
          <SidebarItem 
            key={s.id} 
            session={s} 
            isActive={activeSessionId === s.id} 
            onClick={() => onSessionSelect(s.id)} 
          />
        ))
      )}
    </div>

    <div className="mt-auto pt-6 border-t border-slate-800">
      <div className="flex items-center gap-4 px-2">
        <div className="w-10 h-10 rounded-xl bg-[#1E293B] border border-slate-700 flex items-center justify-center overflow-hidden">
          <img src="https://picsum.photos/40/40" alt="Avatar" className="w-full h-full object-cover grayscale opacity-90" />
        </div>
        <div className="flex-1 overflow-hidden">
          <div className="flex items-center gap-1.5 mb-0.5">
            <p className="text-sm font-semibold text-white truncate leading-none">Chamodh P.</p>
            <Unlock size={11} className="text-blue-500" />
          </div>
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-normal">AI Systems Lead</p>
        </div>
      </div>
    </div>
  </aside>
);

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isBot = message.role === 'bot';
  const roleInfo = message.department ? ROLE_DETAILS[message.department] : null;
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex flex-col ${isBot ? 'items-start' : 'items-end'} mb-10 group font-normal`}>
      <div className={`max-w-[85%] md:max-w-[78%] p-6 rounded-2xl relative shadow-xl ${isBot ? 'bg-[#1E293B] border border-slate-700 text-slate-100' : 'bg-blue-600 text-white rounded-tr-none'}`}>
        <div className="whitespace-pre-wrap text-sm md:text-[15px] leading-relaxed mb-4 font-normal">{message.content}</div>
        {isBot && message.sources && message.sources.length > 0 && (
          <div className="mt-6 pt-5 border-t border-slate-700 flex flex-wrap gap-2">
             <div className="w-full flex items-center justify-between mb-2">
               <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-widest flex items-center gap-2"><LinkIcon size={12} className="text-blue-400" /> Sources Reference</p>
               <span className="text-[9px] text-emerald-400 font-normal uppercase flex items-center gap-1.5 px-2 py-0.5 bg-emerald-950/30 border border-emerald-900 rounded-full"><ShieldCheck size={11} /> Verified</span>
             </div>
             {message.sources.map((src, i) => (
               <span key={i} className="text-[11px] px-3 py-1 bg-slate-800 border border-slate-700 text-slate-300 rounded-lg font-normal">{src}</span>
             ))}
          </div>
        )}
        <div className="flex items-center gap-4 mt-4 opacity-50 font-normal">
          <p className="text-[10px] font-normal uppercase">{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
          {isBot && roleInfo && (
            <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-slate-700 bg-slate-800`}>
              {roleInfo.icon}
              <span className="text-[9px] font-normal uppercase">{roleInfo.label} Silo</span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

const ContextHeader: React.FC<{ 
  title: string; 
  role: Role; 
  onToggleSidebar: () => void 
}> = ({ title, role, onToggleSidebar }) => (
  <header className="md:hidden bg-[#0B1220] border-b border-slate-800 p-6 flex items-center justify-between z-30 font-normal">
    <div className="flex items-center gap-4">
       <button onClick={onToggleSidebar} className="p-3 bg-[#1E293B] rounded-xl text-slate-300">
         <Menu size={20} />
       </button>
       <h1 className="font-bold text-2xl tracking-tight text-white">FinSolve</h1>
    </div>
    <div className="px-4 py-2 bg-[#1E293B] rounded-xl text-[10px] font-normal border border-slate-700 flex items-center gap-2.5">
      <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
      {role}
    </div>
  </header>
);

const EmptyConversationState: React.FC<{ 
  title: string; 
  role: Role; 
  onAction: (text: string) => void 
}> = ({ title, role, onAction }) => (
  <div className="flex-1 flex flex-col items-center justify-center text-center p-8 space-y-12 h-full">
    <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="w-20 h-20 bg-[#0F172A] rounded-2xl flex items-center justify-center relative shadow-2xl border border-slate-800">
      <History className="text-slate-500" size={32} />
    </motion.div>
    <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1 }}>
      <p className="text-[10px] text-blue-500 font-bold uppercase tracking-[0.3em] mb-4">Secure Discussion Initialized</p>
      <h2 className="text-4xl font-bold text-white mb-4 tracking-tighter leading-tight">{title}</h2>
      <p className="text-slate-500 max-w-md mx-auto leading-relaxed text-sm font-normal">
        Your query will instantiate a new contextual chat thread. Authentication silo: <span className="text-slate-300 font-semibold">{ROLE_DETAILS[role].label}</span>. 
      </p>
    </motion.div>
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl pt-4 font-normal">
      {[
        `Analyze current ${ROLE_DETAILS[role].label} parameters`,
        "Extract key strategic highlights",
      ].map((tip, idx) => (
        <button key={idx} onClick={() => onAction(tip)} className="p-5 bg-[#0F172A]/50 rounded-xl hover:bg-[#1E293B] transition-all text-sm text-slate-400 hover:text-white border border-slate-800 text-left group flex items-start gap-4 shadow-lg font-normal">
          <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 group-hover:bg-blue-600 group-hover:border-blue-500 group-hover:text-white transition-all"><MessageSquare size={16} /></div>
          <div>
            <p className="font-normal text-[9px] uppercase tracking-widest text-slate-600 mb-1 group-hover:text-blue-400 transition-colors">Start Prompt</p>
            <p className="leading-snug font-normal">{tip}</p>
          </div>
        </button>
      ))}
    </motion.div>
  </div>
);

const MainContent: React.FC<{
  activeSession: Session | null;
  isLoading: boolean;
  currentRole: Role;
  onSend: (msg: string) => void;
  chatEndRef: React.RefObject<HTMLDivElement>;
}> = ({ activeSession, isLoading, currentRole, onSend, chatEndRef }) => {
  const currentMessages = activeSession ? (activeSession.history || []) : [];
  const effectiveRole = activeSession ? activeSession.role : currentRole;

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar px-6 md:px-14 py-12 scroll-smooth bg-[#020617]">
      <div className="max-w-4xl mx-auto min-h-full flex flex-col">
        {!activeSession || currentMessages.length === 0 ? (
          <EmptyConversationState 
            title={activeSession ? activeSession.title : "New Enterprise Query"} 
            role={effectiveRole} 
            onAction={onSend} 
          />
        ) : (
          <div className="pb-12">
             <div className="mb-12 pb-8 border-b border-slate-900">
                <div className="flex items-center gap-5">
                  <div className={`p-3.5 rounded-2xl border ${getSolidColorClasses(ROLE_DETAILS[activeSession.role].color)} shadow-lg`}>
                    {ROLE_DETAILS[activeSession.role].icon}
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold text-white tracking-tight">{activeSession.title}</h2>
                    <div className="flex items-center gap-3 mt-1.5 text-[10px] text-slate-500 font-semibold uppercase tracking-widest">
                      <span className="flex items-center gap-1.5"><Clock size={12}/> Interaction: {activeSession.date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      <div className="w-1 h-1 rounded-full bg-slate-800" />
                      <span className="text-blue-500">Secure Thread</span>
                    </div>
                  </div>
                </div>
             </div>
            {currentMessages.map((msg) => <MessageBubble key={msg.id} message={msg} />)}
            {isLoading && (
              <div className="flex items-center gap-4 text-slate-500 mb-12 pl-4">
                <div className="flex gap-1.5">{[0, 1, 2].map(i => <motion.div key={i} animate={{ y: [0, -6, 0] }} transition={{ repeat: Infinity, duration: 1, delay: i * 0.2 }} className={`w-1.5 h-1.5 rounded-full ${i === 0 ? 'bg-blue-500' : 'bg-slate-700'}`} />)}</div>
                <span className="text-[11px] font-normal tracking-[0.3em] uppercase">Processing intelligence query...</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        )}
      </div>
    </div>
  );
};

const InputArea: React.FC<{ onSend: (msg: string) => void, disabled: boolean }> = ({ onSend, disabled }) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [text]);
  const handleSubmit = () => {
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText('');
  };
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
  };
  return (
    <div className="p-4 md:p-10 bg-[#020617] font-normal border-t border-slate-900">
      <div className="max-w-4xl mx-auto relative group">
        <div className="relative bg-[#0F172A] border border-[#334155] rounded-2xl overflow-hidden flex items-end gap-3 p-4 shadow-2xl focus-within:border-blue-500/50 transition-colors">
          <div className="hidden md:flex p-3 text-slate-500"><Sparkles size={22} /></div>
          <textarea ref={textareaRef} rows={1} value={text} onChange={(e) => setText(e.target.value)} onKeyDown={handleKeyDown} placeholder="Ask the corporate intelligence..." className="w-full bg-transparent text-white text-base placeholder:text-slate-600 focus:outline-none py-3 px-1 resize-none custom-scrollbar min-h-[52px] font-normal" />
          <button onClick={handleSubmit} disabled={!text.trim() || disabled} className={`p-4 rounded-xl transition-all duration-200 flex items-center justify-center font-normal ${text.trim() && !disabled ? 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95 shadow-lg' : 'bg-slate-800 text-slate-600 cursor-not-allowed'}`}><Send size={20} /></button>
        </div>
      </div>
      <div className="flex items-center justify-center gap-6 mt-5 text-[10px] font-normal uppercase tracking-widest text-slate-600">
        <div className="flex items-center gap-2"><ShieldCheck size={14} className="text-emerald-500" /> Secure Node</div>
        <div className="w-1.5 h-1.5 rounded-full bg-slate-800" />
        <div className="flex items-center gap-2"><Unlock size={14} className="text-blue-500" /> RBAC Validated</div>
      </div>
    </div>
  );
};

// --- Main App Component ---

export default function App() {
  const [currentRole, setCurrentRole] = useState<Role>(Role.FINANCE);
  const [isLoading, setIsLoading] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const [sessions, setSessions] = useState<Session[]>([]);

  // Sorting sessions by last updated date (chronological)
  const sortedSessions = useMemo(() => {
    return [...sessions].sort((a, b) => b.date.getTime() - a.date.getTime());
  }, [sessions]);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [sessions, isLoading, activeSessionId]);

  const handleSend = async (content: string) => {
    const isFirstMessageInNewChat = !activeSessionId;
    let targetId = activeSessionId;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content, timestamp: new Date() };
    
    // Lifecycle: Convert draft to real session on first message
    if (isFirstMessageInNewChat) {
      targetId = Date.now().toString();
      const newSession: Session = {
        id: targetId,
        title: content.length > 30 ? content.substring(0, 30) + '...' : content,
        date: new Date(),
        role: currentRole,
        history: [userMsg]
      };
      setSessions(prev => [newSession, ...prev]);
      setActiveSessionId(targetId);
    } else {
      // Append to existing session
      setSessions(prev => prev.map(s => s.id === targetId ? { 
        ...s, 
        history: [...(s.history || []), userMsg],
        date: new Date() // Updates chronological sort order
      } : s));
    }
    
    setIsLoading(true);

    const botMsgId = (Date.now() + 1).toString();
    const effectiveRole = isFirstMessageInNewChat ? currentRole : (sessions.find(s => s.id === targetId)?.role || currentRole);
    
    const botMsg: Message = { 
      id: botMsgId, 
      role: 'bot', 
      content: '', 
      timestamp: new Date(), 
      department: effectiveRole, 
      sources: [] 
    };

    // Use backend service to get AI response
    setSessions(prev => prev.map(s => s.id === targetId ? { ...s, history: [...(s.history || []), botMsg] } : s));

    try {
      let fullContent = "";
      const backendResponse = await fetchSessions(content, effectiveRole, (chunk: string) => {
        fullContent += chunk;
        setSessions(prev => prev.map(s => s.id === targetId
          ? { ...s, history: s.history?.map(m => m.id === botMsgId ? { ...m, content: fullContent } : m)}
          : s
        ));
      });

      const sources = backendResponse.sources || [];

      setSessions(prev => prev.map(s => s.id === targetId 
        ? { ...s, history: s.history?.map(m => m.id === botMsgId ? { ...m, sources: sources } : m) } 
        : s
      ));

    } catch (error) {
      const errorText = "Sync failure: Node handshake timed out. Re-verify authority credentials for this silo.";
      setSessions(prev => prev.map(s => s.id === targetId
        ? { ...s, history: s.history?.map(m => m.id === botMsgId ? { ...m, content: errorText } : m) }
        : s
      ));
    } finally {
      setIsLoading(false);
    }

  };

  const handleSessionSelect = (id: string | null) => {
    setActiveSessionId(id);
    setIsMobileSidebarOpen(false);
    if (id) {
      const found = sessions.find(s => s.id === id);
      if (found) setCurrentRole(found.role);
    }
  };

  const activeSession = activeSessionId ? sessions.find(s => s.id === activeSessionId) || null : null;

  return (
    <div className={`flex h-screen bg-[#020617] text-slate-100 overflow-hidden font-normal`}>
      <BackgroundGradients roleColor={ROLE_DETAILS[activeSession ? activeSession.role : currentRole].color} />
      
      <Sidebar 
        currentRole={currentRole} 
        setRole={setCurrentRole} 
        sessions={sortedSessions}
        activeSessionId={activeSessionId}
        onSessionSelect={handleSessionSelect}
        isMobileOpen={isMobileSidebarOpen}
        toggleMobile={() => setIsMobileSidebarOpen(false)}
      />

      <main className="flex-1 flex flex-col relative h-full overflow-hidden">
        <ContextHeader 
          title={activeSession ? activeSession.title : "Corporate Intelligence"} 
          role={activeSession ? activeSession.role : currentRole} 
          onToggleSidebar={() => setIsMobileSidebarOpen(true)} 
        />

        <MainContent 
          activeSession={activeSession}
          isLoading={isLoading}
          currentRole={currentRole}
          onSend={handleSend}
          chatEndRef={chatEndRef}
        />

        <InputArea onSend={handleSend} disabled={isLoading} />
      </main>

      <AnimatePresence>
        {isMobileSidebarOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-[#020617]/95 z-30 md:hidden"
            onClick={() => setIsMobileSidebarOpen(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
