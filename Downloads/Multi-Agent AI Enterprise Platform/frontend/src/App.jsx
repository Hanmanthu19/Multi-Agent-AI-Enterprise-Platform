import React, { useState, useRef } from 'react';
import { 
  Bot, Zap, Cpu, Database, Mail, FileText, Terminal, 
  ArrowRight, Check, Plus, Minus, Send, X, Users, RefreshCw, Briefcase, Paperclip, Sparkles
} from 'lucide-react';

const API_ORCHESTRATE_URL = "http://127.0.0.1:8000/api/orchestrate";

export default function App() {
  // Navigation & Modal States
  const [isDashboardOpen, setIsDashboardOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [activeFaq, setActiveFaq] = useState(0);

  // Interactive Chat & File Attachment State
  const [chatPrompt, setChatPrompt] = useState('');
  const [attachedFile, setAttachedFile] = useState(null);
  const fileInputRef = useRef(null);

  const [chatHistory, setChatHistory] = useState([
    { 
      sender: 'ai', 
      department: 'SUPERVISOR', 
      text: 'Hello! I am the Super Agent Supervisor. Enter your query or prompt, and I will route it to our specialized Finance, HR, Sales, or Research AI Employee.' 
    }
  ]);
  const [sendingTask, setSendingTask] = useState(false);

  // File Attachment Handlers
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setAttachedFile(e.target.files[0]);
    }
  };

  const removeAttachedFile = () => {
    setAttachedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Main Submit Handler - Sends FormData to /api/orchestrate
  const handleSendChatTask = async (e) => {
    e.preventDefault();
    if (!chatPrompt.trim() && !attachedFile) return;

    const userText = chatPrompt.trim();
    const currentFile = attachedFile;

    // Display user message in UI
    let displayUserText = userText;
    if (currentFile) {
      displayUserText = `[File Attached: ${currentFile.name}]\n${userText}`;
    }

    setChatPrompt('');
    setAttachedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";

    setChatHistory(prev => [...prev, { sender: 'user', text: displayUserText }]);
    setSendingTask(true);

    try {
      // Build FormData for multipart POST request
      const formData = new FormData();
      if (userText) {
        formData.append('user_prompt', userText);
      }
      if (currentFile) {
        formData.append('file', currentFile);
      }

      const res = await fetch(API_ORCHESTRATE_URL, {
        method: 'POST',
        body: formData
      });

      if (res.ok) {
        const jsonResult = await res.json();
        const dept = jsonResult.department || 'GENERAL';
        const data = jsonResult.data || {};

        // Extract human-readable text from sub-agent data
        let formattedText = "";
        if (typeof data === 'string') {
          formattedText = data;
        } else if (data.summary) {
          formattedText = data.summary;
        } else if (data.response) {
          formattedText = data.response;
        } else if (data.output_text) {
          formattedText = data.output_text;
        } else {
          formattedText = JSON.stringify(data, null, 2);
        }

        setChatHistory(prev => [
          ...prev, 
          { 
            sender: 'ai', 
            department: dept, 
            data: data,
            text: formattedText 
          }
        ]);
      } else {
        const errData = await res.json().catch(() => ({}));
        setChatHistory(prev => [
          ...prev, 
          { 
            sender: 'ai', 
            department: 'ERROR', 
            text: `Server returned error (${res.status}): ${errData.detail || 'Failed to orchestrate task.'}` 
          }
        ]);
      }
    } catch (err) {
      setChatHistory(prev => [
        ...prev, 
        { 
          sender: 'ai', 
          department: 'OFFLINE', 
          text: "Backend connection error. Please ensure FastAPI server is running on http://127.0.0.1:8000." 
        }
      ]);
    } finally {
      setSendingTask(false);
    }
  };

  return (
    <div className="bg-black text-white min-h-screen font-sans selection:bg-[#00FFA3] selection:text-black">
      
      {/* 1. TOP NAVIGATION */}
      <nav className="border-b border-neutral-900 bg-black/80 backdrop-blur-md sticky top-0 z-40 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-[#00FFA3] text-black p-1.5 rounded-lg">
            <Bot className="w-5 h-5" />
          </div>
          <span className="font-bold tracking-tight text-lg">AI EMPLOYEE <span className="text-xs bg-neutral-900 text-[#00FFA3] px-2 py-0.5 rounded border border-neutral-800 ml-1">FACTORY</span></span>
        </div>

        <div className="hidden md:flex items-center gap-2 text-xs text-neutral-400">
          <span className="w-2 h-2 rounded-full bg-[#00FFA3] animate-pulse"></span>
          Super Agent Routing Active (port 8000)
        </div>

        <button 
          onClick={() => setIsChatOpen(true)}
          className="bg-[#00FFA3] hover:bg-[#00e08f] text-black text-xs font-semibold px-4 py-2 rounded-full flex items-center gap-2 transition shadow-md shadow-[#00FFA3]/20"
        >
          <Zap className="w-3.5 h-3.5 fill-black" />
          Launch AI Router ⚡
        </button>
      </nav>

      {/* 2. HERO SECTION */}
      <section className="relative pt-20 pb-16 px-6 text-center max-w-5xl mx-auto">
        <div className="absolute inset-0 -z-10 flex items-center justify-center">
          <div className="w-[500px] h-[300px] bg-[#00FFA3]/10 blur-[120px] rounded-full"></div>
        </div>

        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-neutral-900 border border-[#00FFA3]/30 text-[#00FFA3] text-xs font-mono mb-6">
          <Sparkles className="w-3.5 h-3.5" /> Autonomous Super Agent Orchestrator
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 leading-tight">
          Unified <span className="text-[#00FFA3] underline decoration-[#00FFA3]/40 underline-offset-8">AI Employee</span> Platform
        </h1>

        <p className="text-neutral-400 text-base md:text-lg max-w-2xl mx-auto mb-10 leading-relaxed">
          Instantly classify and route business workflows to specialized AI Workers across Finance, HR, Sales, and Research departments.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <button 
            onClick={() => setIsChatOpen(true)}
            className="w-full sm:w-auto bg-white hover:bg-neutral-200 text-black font-semibold text-sm px-8 py-3.5 rounded-full flex items-center justify-center gap-2 transition"
          >
            Talk to AI Employees <ArrowRight className="w-4 h-4" />
          </button>

          <button 
            onClick={() => setIsDashboardOpen(true)}
            className="w-full sm:w-auto bg-neutral-950 border border-[#00FFA3]/40 hover:border-[#00FFA3] text-white font-medium text-sm px-8 py-3.5 rounded-full flex items-center justify-center gap-2 transition"
          >
            <Zap className="w-4 h-4 text-[#00FFA3]" /> View System Architecture
          </button>
        </div>
      </section>

      {/* 3. ABOUT US SECTION */}
      <section className="py-16 px-6 border-t border-neutral-900 max-w-6xl mx-auto">
        <div className="text-xs font-mono text-[#00FFA3] mb-4">// ABOUT US</div>
        
        <div className="grid md:grid-cols-12 gap-8 items-center">
          <div className="md:col-span-5 grid grid-cols-2 gap-4">
            <div className="bg-neutral-950 border border-neutral-900 rounded-2xl p-6 flex flex-col justify-between h-40 hover:border-[#00FFA3]/40 transition">
              <Cpu className="w-6 h-6 text-[#00FFA3]" />
              <div>
                <div className="text-xs text-neutral-500 font-mono">// 01 SUPERVISOR</div>
                <div className="text-sm font-semibold mt-1">Gemini 2.5 Router</div>
              </div>
            </div>

            <div className="bg-neutral-950 border border-neutral-900 rounded-2xl p-6 flex flex-col justify-between h-40 hover:border-[#00FFA3]/40 transition">
              <Database className="w-6 h-6 text-[#00FFA3]" />
              <div>
                <div className="text-xs text-neutral-500 font-mono">// 02 SUB-AGENTS</div>
                <div className="text-sm font-semibold mt-1">4 Department Workers</div>
              </div>
            </div>
          </div>

          <div className="md:col-span-7">
            <h2 className="text-2xl md:text-4xl font-bold leading-tight mb-4">
              Autonomous AI employees unified under one central orchestrator.
            </h2>
            <p className="text-neutral-400 text-sm leading-relaxed mb-6">
              Our FastAPI central orchestrator routes requests dynamically to specialized agents for Finance, HR, Sales, and Research with zero friction.
            </p>
            <div className="flex flex-wrap gap-4 text-xs font-mono text-neutral-300">
              <span className="flex items-center gap-1.5 bg-neutral-900 px-3 py-1.5 rounded-full border border-neutral-800">
                <Check className="w-3.5 h-3.5 text-[#00FFA3]" /> Dynamic Path Routing
              </span>
              <span className="flex items-center gap-1.5 bg-neutral-900 px-3 py-1.5 rounded-full border border-neutral-800">
                <Check className="w-3.5 h-3.5 text-[#00FFA3]" /> Gemini 2.5 Flash Classification
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 4. FEATURES BENTO GRID */}
      <section className="py-16 px-6 border-t border-neutral-900 max-w-6xl mx-auto">
        <div className="text-xs font-mono text-[#00FFA3] mb-2">// FEATURES</div>
        <h2 className="text-3xl font-bold mb-10">Intelligent Workforce Management</h2>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-neutral-950 border border-neutral-900 rounded-2xl p-6 flex flex-col justify-between h-72 hover:border-[#00FFA3]/40 transition">
            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                <div className="p-2 bg-neutral-900 rounded-lg text-neutral-400"><Cpu className="w-4 h-4" /></div>
                <div className="p-2 bg-neutral-900 rounded-lg text-neutral-400"><Zap className="w-4 h-4" /></div>
              </div>
              <span className="text-xs font-mono text-neutral-500">SUPERVISOR</span>
            </div>
            <div>
              <h3 className="text-lg font-bold mb-2">Super Agent Supervisor</h3>
              <p className="text-xs text-neutral-400 leading-relaxed">
                Uses Gemini 2.5 Flash to automatically detect user intent and categorize requests into proper department channels.
              </p>
            </div>
          </div>

          <div className="bg-[#00FFA3] text-black rounded-2xl p-6 flex flex-col justify-between h-72">
            <div>
              <div className="text-xs font-mono font-bold mb-2">// HIGHLIGHT PLATFORM</div>
              <h3 className="text-xl font-extrabold mb-4">Unified FastAPI Backend</h3>
              <ul className="text-xs font-medium space-y-2">
                <li className="flex items-center gap-2"><Check className="w-4 h-4" /> Single POST /api/orchestrate Endpoint</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4" /> Multipart Form Data File Uploads</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4" /> Automatic CORS & Error Isolation</li>
              </ul>
            </div>
            <div 
              onClick={() => setIsChatOpen(true)}
              className="flex items-center justify-between text-xs font-bold pt-4 border-t border-black/10 cursor-pointer"
            >
              <span>Test Orchestrator Now -&gt;</span>
              <div className="bg-black text-white p-2 rounded-full"><ArrowRight className="w-4 h-4" /></div>
            </div>
          </div>

          <div className="bg-neutral-950 border border-neutral-900 rounded-2xl p-6 flex flex-col justify-between h-72 hover:border-[#00FFA3]/40 transition">
            <div className="flex gap-2 text-[#00FFA3]">
              <div className="p-2.5 bg-neutral-900 rounded-xl"><Mail className="w-4 h-4" /></div>
              <div className="p-2.5 bg-neutral-900 rounded-xl"><Database className="w-4 h-4" /></div>
              <div className="p-2.5 bg-neutral-900 rounded-xl"><FileText className="w-4 h-4" /></div>
              <div className="p-2.5 bg-neutral-900 rounded-xl"><Terminal className="w-4 h-4" /></div>
            </div>
            <div>
              <div className="text-xs font-mono text-neutral-500 mb-1">// DEPARTMENTS</div>
              <h3 className="text-lg font-bold mb-2">4 Sub-Agent Workers</h3>
              <p className="text-xs text-neutral-400 leading-relaxed">
                Finance Agent, HR Agent, Sales Agent, and Research Agent execute specialized tasks independently.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. VISION SECTION: 4 AI AGENTS SHOWCASE */}
      <section className="py-16 px-6 border-t border-neutral-900 max-w-6xl mx-auto">
        <div className="text-xs font-mono text-[#00FFA3] mb-2">// HIERARCHY</div>
        <h2 className="text-3xl font-bold mb-10">Department AI Agent Network</h2>

        <div className="grid md:grid-cols-4 gap-6">
          <div className="bg-neutral-950 border border-neutral-900 p-6 rounded-2xl md:col-span-4 bg-gradient-to-r from-neutral-950 via-neutral-900 to-neutral-950 border-[#00FFA3]/40 shadow-lg shadow-[#00FFA3]/5">
            <div className="flex items-center gap-3 mb-2">
              <div className="bg-[#00FFA3] text-black p-2.5 rounded-xl font-bold"><Bot className="w-6 h-6" /></div>
              <div>
                <h3 className="text-xl font-bold flex items-center gap-2">
                  SUPERVISOR AI <span className="text-xs bg-[#00FFA3]/20 text-[#00FFA3] px-2.5 py-0.5 rounded-full border border-[#00FFA3]/30 font-mono">(Gemini 2.5 Flash Router)</span>
                </h3>
                <p className="text-xs text-neutral-400 mt-1">Classifies inputs into FINANCE, HR, SALES, or RESEARCH departments.</p>
              </div>
            </div>
          </div>

          {/* HR AI */}
          <div className="bg-neutral-950 border border-neutral-900 p-6 rounded-2xl hover:border-[#00FFA3]/40 transition">
            <div className="p-2 bg-neutral-900 rounded-xl w-fit mb-3"><Users className="w-5 h-5 text-[#00FFA3]" /></div>
            <h4 className="font-bold text-base mb-1">HR AGENT</h4>
            <p className="text-xs text-neutral-400 leading-relaxed">Handles leave requests, PTO limits, and HR policy queries.</p>
          </div>

          {/* FINANCE AI */}
          <div className="bg-neutral-950 border border-neutral-900 p-6 rounded-2xl hover:border-[#00FFA3]/40 transition">
            <div className="p-2 bg-neutral-900 rounded-xl w-fit mb-3"><Briefcase className="w-5 h-5 text-[#00FFA3]" /></div>
            <h4 className="font-bold text-base mb-1">FINANCE AGENT</h4>
            <p className="text-xs text-neutral-400 leading-relaxed">Evaluates claims in INR, SOP thresholds, and auto-approvals.</p>
          </div>

          {/* RESEARCH AI */}
          <div className="bg-neutral-950 border border-neutral-900 p-6 rounded-2xl hover:border-[#00FFA3]/40 transition">
            <div className="p-2 bg-neutral-900 rounded-xl w-fit mb-3"><FileText className="w-5 h-5 text-[#00FFA3]" /></div>
            <h4 className="font-bold text-base mb-1">RESEARCH AGENT</h4>
            <p className="text-xs text-neutral-400 leading-relaxed">Scans datasets, computes confidence scores, and extracts facts.</p>
          </div>

          {/* SALES AI */}
          <div className="bg-neutral-950 border border-neutral-900 p-6 rounded-2xl hover:border-[#00FFA3]/40 transition">
            <div className="p-2 bg-neutral-900 rounded-xl w-fit mb-3"><Zap className="w-5 h-5 text-[#00FFA3]" /></div>
            <h4 className="font-bold text-base mb-1">SALES AGENT</h4>
            <p className="text-xs text-neutral-400 leading-relaxed">Detects deal intent, generates pricing quotes, and qualifies leads.</p>
          </div>
        </div>
      </section>

      {/* 6. FAQ ACCORDION SECTION */}
      <section className="py-16 px-6 border-t border-neutral-900 max-w-6xl mx-auto">
        <div className="text-xs font-mono text-[#00FFA3] mb-2">// FAQ</div>
        
        <div className="grid md:grid-cols-12 gap-8">
          <div className="md:col-span-4">
            <h2 className="text-3xl font-bold mb-3">Frequently Asked Questions</h2>
            <p className="text-xs text-neutral-400 leading-relaxed">Everything about our unified orchestrator platform.</p>
          </div>

          <div className="md:col-span-8 space-y-4">
            {[
              {
                q: "How does the Super Agent route queries?",
                a: "The Super Agent uses Gemini 2.5 Flash to analyze incoming text or file attachments and classify them into FINANCE, HR, SALES, or RESEARCH."
              },
              {
                q: "Which endpoint is called by the frontend?",
                a: "All chat prompts are submitted via multipart FormData directly to POST http://127.0.0.1:8000/api/orchestrate."
              },
              {
                q: "Are the sub-agents imported dynamically?",
                a: "Yes. The backend uses sys.path.append to include all 4 sub-agent directories and invokes their process_*_query handler functions."
              }
            ].map((faq, idx) => (
              <div 
                key={idx} 
                className="bg-neutral-950 border border-neutral-900 rounded-xl overflow-hidden cursor-pointer transition hover:border-neutral-800"
                onClick={() => setActiveFaq(activeFaq === idx ? null : idx)}
              >
                <div className="p-5 flex justify-between items-center">
                  <span className="font-semibold text-sm">{faq.q}</span>
                  {activeFaq === idx ? <Minus className="w-4 h-4 text-[#00FFA3]" /> : <Plus className="w-4 h-4 text-neutral-500" />}
                </div>
                {activeFaq === idx && (
                  <div className="px-5 pb-5 text-xs text-neutral-400 border-t border-neutral-900/50 pt-3 leading-relaxed">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 7. FOOTER */}
      <footer className="border-t border-neutral-900 bg-black pt-12 pb-16 px-6 max-w-6xl mx-auto">
        <div className="grid md:grid-cols-12 gap-8 mb-12">
          <div className="md:col-span-6">
            <div className="flex items-center gap-2 mb-3">
              <div className="bg-[#00FFA3] text-black p-1 rounded"><Bot className="w-4 h-4" /></div>
              <span className="font-bold text-base">AI EMPLOYEE FACTORY</span>
            </div>
            <p className="text-xs text-neutral-500 max-w-sm leading-relaxed">
              Unified multi-agent platform connecting React Vite frontend with FastAPI orchestrator.
            </p>
          </div>

          <div className="md:col-span-6 text-xs text-right">
            <div className="font-mono text-[#00FFA3] mb-2">// SYSTEM STATUS</div>
            <div className="text-neutral-400 font-mono">
              API Endpoint: <span className="text-white">http://127.0.0.1:8000/api/orchestrate</span>
            </div>
          </div>
        </div>

        <div className="text-center text-xs text-neutral-600 border-t border-neutral-900 pt-8">
          © 2026 AI Employee Factory. All rights reserved.
        </div>
      </footer>

      {/* FLOATING ACTION BUTTON */}
      <div className="fixed bottom-6 right-6 z-30">
        <button 
          onClick={() => setIsChatOpen(true)}
          className="bg-[#00FFA3] hover:bg-[#00e08f] text-black font-bold text-xs px-5 py-3 rounded-full shadow-lg shadow-[#00FFA3]/20 flex items-center gap-2 transition"
        >
          <Zap className="w-4 h-4 fill-black" /> Open Chat Studio
        </button>
      </div>

      {/* ========================================================================= */}
      {/* 🛠 MODAL 1: SYSTEM DASHBOARD SLIDE-OVER */}
      {/* ========================================================================= */}
      {isDashboardOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex justify-end">
          <div className="bg-neutral-950 border-l border-neutral-800 w-full max-w-2xl h-full overflow-y-auto p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-neutral-800 pb-4 mb-6">
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-[#00FFA3]" />
                  <h2 className="text-lg font-bold">System Architecture & Connections</h2>
                </div>
                <button onClick={() => setIsDashboardOpen(false)} className="text-neutral-400 hover:text-white"><X className="w-5 h-5" /></button>
              </div>

              <div className="space-y-4 text-xs">
                <div className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl">
                  <h3 className="font-bold text-sm text-[#00FFA3] mb-1">Frontend Server</h3>
                  <p className="text-neutral-400">React Vite App running on <span className="text-white font-mono">http://localhost:5173</span></p>
                </div>

                <div className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl">
                  <h3 className="font-bold text-sm text-[#00FFA3] mb-1">FastAPI Backend</h3>
                  <p className="text-neutral-400">Main Orchestrator running on <span className="text-white font-mono">http://127.0.0.1:8000</span></p>
                  <p className="text-neutral-400 mt-1">Endpoint: <span className="text-[#00FFA3] font-mono">POST /api/orchestrate</span></p>
                </div>

                <div className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl">
                  <h3 className="font-bold text-sm text-[#00FFA3] mb-2">Connected Sub-Agents</h3>
                  <ul className="space-y-1 text-neutral-300 font-mono text-[11px]">
                    <li>• 1-finance-agent (process_finance_query)</li>
                    <li>• 3-hr-agent (process_hr_query)</li>
                    <li>• 4-sales-agent (process_sales_query)</li>
                    <li>• 5-research-agent (process_research_query)</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-neutral-800 text-[10px] text-neutral-500">
              End-to-End Orchestrator Pipeline Ready
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 💬 MODAL 2: CHAT STUDIO INTERFACE (FULL SCREEN) */}
      {/* ========================================================================= */}
      {isChatOpen && (
        <div className="fixed inset-0 z-50 w-full h-full bg-neutral-950 flex flex-col">
          {/* Header */}
          <div className="p-4 md:px-8 border-b border-neutral-800 bg-neutral-900/60 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-[#00FFA3] text-black p-2 rounded-lg"><Bot className="w-5 h-5" /></div>
              <div>
                <h3 className="font-bold text-base md:text-lg">Super Agent Orchestrator Studio</h3>
                <div className="text-xs text-neutral-400">Submits to http://127.0.0.1:8000/api/orchestrate</div>
              </div>
            </div>
            <button onClick={() => setIsChatOpen(false)} className="p-2 rounded-lg bg-neutral-900 text-neutral-400 hover:text-white hover:bg-neutral-800 transition">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Chat Body */}
          <div className="p-4 md:p-8 flex-1 overflow-y-auto space-y-4 max-w-5xl w-full mx-auto">
            {chatHistory.map((msg, i) => (
              <div key={i} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] md:max-w-[75%] rounded-2xl p-4 text-xs md:text-sm leading-relaxed ${
                  msg.sender === 'user' ? 'bg-[#00FFA3] text-black font-medium shadow-md' : 'bg-neutral-900 border border-neutral-800 text-neutral-200'
                }`}>
                  {msg.sender === 'ai' && msg.department && (
                    <div className="mb-2 flex items-center gap-1.5">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                        msg.department === 'FINANCE' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                        msg.department === 'HR' ? 'bg-purple-500/10 text-purple-400 border-purple-500/30' :
                        msg.department === 'SALES' ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' :
                        msg.department === 'RESEARCH' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                        'bg-[#00FFA3]/10 text-[#00FFA3] border-[#00FFA3]/30'
                      }`}>
                        DEPARTMENT: {msg.department}
                      </span>
                    </div>
                  )}

                  <div className="whitespace-pre-wrap font-mono text-xs md:text-sm">
                    {msg.text}
                  </div>

                  {msg.data && typeof msg.data === 'object' && Object.keys(msg.data).length > 0 && (
                    <details className="mt-3 pt-2 border-t border-neutral-800 text-[11px]">
                      <summary className="cursor-pointer text-neutral-400 hover:text-white font-mono">View raw agent payload</summary>
                      <pre className="mt-2 p-2.5 bg-black/60 rounded border border-neutral-800 overflow-x-auto text-[10px] text-[#00FFA3]">
                        {JSON.stringify(msg.data, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            ))}

            {sendingTask && (
              <div className="text-xs font-mono text-[#00FFA3] animate-pulse flex items-center gap-2 p-3 bg-neutral-900/40 border border-[#00FFA3]/20 rounded-xl w-fit">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Super Agent is classifying prompt and invoking department agent...
              </div>
            )}
          </div>

          {/* Input Area Container */}
          <div className="p-4 md:p-6 border-t border-neutral-800 bg-neutral-900/40">
            <div className="max-w-5xl mx-auto space-y-2">

              {/* Attached File Badge */}
              {attachedFile && (
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-neutral-900 border border-[#00FFA3]/40 text-[#00FFA3] text-xs font-mono shadow-md backdrop-blur-md">
                  <FileText className="w-3.5 h-3.5" />
                  <span>📄 {attachedFile.name}</span>
                  <button type="button" onClick={removeAttachedFile} className="hover:text-white p-0.5 ml-1">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              {/* Hidden File Input */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.csv"
                className="hidden"
              />

              {/* Input Form */}
              <form onSubmit={handleSendChatTask} className="flex gap-2 items-center bg-black border border-neutral-800 focus-within:border-[#00FFA3] rounded-2xl p-2 transition">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2.5 text-neutral-400 hover:text-[#00FFA3] hover:bg-neutral-900 rounded-xl transition"
                  title="Attach file (.pdf, .doc, .docx, .xls, .xlsx, .txt, .csv)"
                >
                  <Paperclip className="w-5 h-5" />
                </button>

                <input
                  type="text"
                  placeholder="Ask a question or request a task (e.g. Check refund policy for ₹1500 INR claim)..."
                  value={chatPrompt}
                  onChange={(e) => setChatPrompt(e.target.value)}
                  className="flex-1 bg-transparent px-2 py-1 text-xs md:text-sm text-white placeholder-neutral-500 outline-none"
                />

                <button
                  type="submit"
                  disabled={sendingTask}
                  className="bg-[#00FFA3] hover:bg-[#00e08f] text-black font-bold px-5 py-2.5 rounded-xl text-xs transition flex items-center gap-1.5 shadow-md shadow-[#00FFA3]/20 shrink-0"
                >
                  <Send className="w-4 h-4 fill-black text-black" />
                  <span>Send</span>
                </button>
              </form>

            </div>
          </div>
        </div>
      )}

    </div>
  );
}
