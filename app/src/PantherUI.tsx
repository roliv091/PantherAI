import React, { useState, useRef, useEffect } from 'react';
import { Send, Plus, FileText, MapPin, BookOpen, DollarSign, ChevronRight, ChevronLeft, Image, Upload } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { api } from './api';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  sources?: string[];
  timestamp: Date;
}

interface Task {
  title: string;
  due?: string;
  weight?: number;
}

interface FinanceSummary {
  totals: Record<string, number>;
  roundups: number;
  runway_days: number;
}


const PantherUI: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(false);
  const [isRightPanelOpen, setIsRightPanelOpen] = useState(true);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [financeSummary, setFinanceSummary] = useState<FinanceSummary | null>(null);
  const [showUploadMenu, setShowUploadMenu] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await api.post('/chat', { message: inputValue });
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.answer,
        isUser: false,
        sources: response.data.sources,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const uploadFile = async (file: File, endpoint: string) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (endpoint === '/ingest/campus-doc' && response.data.tasks) {
        setTasks(response.data.tasks);
      }
      
      return response.data;
    } catch (error) {
      console.error('Upload error:', error);
      return null;
    }
  };

  const handleFileUpload = async (fileType: 'pdf' | 'image' | 'csv') => {
    const input = document.createElement('input');
    input.type = 'file';
    input.style.display = 'none';
    
    if (fileType === 'pdf') {
      input.accept = '.pdf';
    } else if (fileType === 'image') {
      input.accept = 'image/*';
    } else if (fileType === 'csv') {
      input.accept = '.csv';
    }

    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      if (file.type === 'application/pdf') {
        // Upload PDF as campus document (syllabus)
        const result = await uploadFile(file, '/ingest/campus-doc');
        if (result && result.ok && result.tasks) {
          setTasks(result.tasks);
        }
      } else if (file.type.startsWith('image/')) {
        uploadFile(file, '/ingest/vision');
      } else if (file.type === 'text/csv') {
        // Show placeholder message for CSV files
        alert('Finance feature coming soon! CSV upload will be available in a future update.');
      }
      
      // Close the menu after upload
      setShowUploadMenu(false);
    };

    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
  };

  const quickActions = [
    { icon: BookOpen, label: 'Course Help', action: () => setInputValue('I need help with my course') },
    { icon: DollarSign, label: 'Finance', action: () => setInputValue('Show me my finance summary') },
    { icon: MapPin, label: 'Campus Info', action: () => setInputValue('Tell me about campus services') },
  ];

  return (
    <div className="h-screen bg-gray-50 flex relative">
      {/* Main Chat Area - Shifts left when panel is open */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ease-in-out ${
        isRightPanelOpen ? 'mr-80' : 'mr-0'
      }`}>
        {/* Header */}
        <div className="bg-go-blue text-white p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold">PANTHER AI</h1>
            <div className="flex items-center gap-2">
              <img 
                src="/fiu-logo.png" 
                alt="FIU Logo" 
                className="h-8 w-auto"
              />
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white p-4 border-b">
          <div className="flex gap-3">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={action.action}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-go-blue hover:text-white rounded-lg transition-colors"
              >
                <action.icon size={16} />
                <span className="text-sm font-medium">{action.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              <p className="text-lg">Welcome to PantherAI!</p>
              <p className="text-sm">Ask me anything about FIU campus life, courses, or upload documents for help.</p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`px-4 py-2 rounded-lg ${
                    message.isUser
                      ? 'bg-go-blue text-white max-w-[60%] ml-[40%]'
                      : 'bg-white text-gray-800 border border-gray-200 max-w-[60%] mr-[40%]'
                  }`}
                >
                  {message.isUser ? (
                    <p className="text-sm">{message.text}</p>
                  ) : (
                    <div className="text-sm prose prose-sm max-w-none">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                          em: ({ children }) => <em className="italic">{children}</em>,
                          ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
                          li: ({ children }) => <li className="mb-1">{children}</li>,
                          code: ({ children }) => (
                            <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono">
                              {children}
                            </code>
                          ),
                          pre: ({ children }) => (
                            <pre className="bg-gray-100 p-2 rounded text-xs font-mono overflow-x-auto mb-2">
                              {children}
                            </pre>
                          ),
                          h1: ({ children }) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
                          h2: ({ children }) => <h2 className="text-base font-bold mb-2">{children}</h2>,
                          h3: ({ children }) => <h3 className="text-sm font-bold mb-1">{children}</h3>,
                        }}
                      >
                        {message.text}
                      </ReactMarkdown>
                    </div>
                  )}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-300">
                      <p className="text-xs font-medium">Sources:</p>
                      <ul className="text-xs">
                        {message.sources.map((source, index) => (
                          <li key={index}>• {source}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 border border-gray-200 px-4 py-2 rounded-lg max-w-[60%] mr-[40%]">
                <p className="text-sm">Thinking...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-4 relative">
          <div className="flex items-center gap-2">
            <div className="relative">
              <button
                onClick={() => setShowUploadMenu(!showUploadMenu)}
                className="p-2 text-gray-600 hover:text-go-blue transition-colors"
              >
                <Plus size={20} />
              </button>
              
              {/* Upload Menu */}
              {showUploadMenu && (
                <div className="absolute bottom-full left-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg p-2 min-w-[200px] z-50">
                  <div className="space-y-1">
                    <button
                      onClick={() => handleFileUpload('pdf')}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                    >
                      <FileText size={16} />
                      <span>Upload PDF</span>
                    </button>
                    <button
                      onClick={() => handleFileUpload('image')}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                    >
                      <Image size={16} />
                      <span>Upload Image</span>
                    </button>
                    <button
                      onClick={() => handleFileUpload('csv')}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                    >
                      <Upload size={16} />
                      <span>Upload CSV</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
            
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask PantherAI anything..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-go-blue"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="p-2 bg-go-blue text-white rounded-lg hover:bg-go-blue-light transition-colors disabled:opacity-50"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Right Panel - Fixed position, slides in/out */}
      <div 
        className={`fixed top-0 right-0 h-full w-80 bg-white border-l border-gray-200 p-4 overflow-y-auto transform transition-transform duration-300 ease-in-out z-20 ${
          isRightPanelOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="space-y-6">
          {/* Tasks from Syllabus */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Tasks from Syllabus</h3>
            {tasks.length > 0 ? (
              <div className="space-y-2">
                {tasks.map((task, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium text-sm">{task.title}</p>
                    {task.due && (
                      <p className="text-xs text-gray-600">Due: {task.due}</p>
                    )}
                    {task.weight && (
                      <p className="text-xs text-gray-600">Weight: {task.weight}%</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No tasks found. Upload a syllabus to get started.</p>
            )}
          </div>

          {/* Finance Summary - Future Feature */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Finance Summary</h3>
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500 mb-2">🚧 Coming Soon</p>
              <p className="text-xs text-gray-400">
                Upload CSV files or bank statements to track expenses, calculate roundups, and estimate runway.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Toggle Button - Moves with panel edge */}
      <button
        onClick={() => setIsRightPanelOpen(!isRightPanelOpen)}
        className={`fixed top-1/3 z-30 bg-blue-600 border-2 border-yellow-400 text-white p-2 rounded-l-lg hover:bg-blue-700 transition-all duration-300 ease-in-out ${
          isRightPanelOpen ? 'right-80' : 'right-0'
        }`}
        style={{
          backgroundColor: '#1e40af', // Blue inside
          borderColor: '#fbbf24', // Gold outline
          color: 'white',
          transform: 'translateY(-50%)'
        }}
      >
        {isRightPanelOpen ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
      </button>
    </div>
  );
};

export default PantherUI;