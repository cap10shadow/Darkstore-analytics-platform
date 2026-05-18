import { useState, useRef, useEffect } from 'react'
import { X, Loader2 } from 'lucide-react'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import { sendMessage } from '../../api/chat'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const quickPrompts = ['Show KPIs', 'Low stock items', 'Detect anomalies', 'Staff performance']

interface ChatPanelProps {
  open: boolean
  onClose: () => void
}

export default function ChatPanel({ open, onClose }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hello! I can help you analyze your darkstore data. Try asking about KPIs, stock levels, or anomalies.' },
  ])
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (text: string) => {
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setLoading(true)
    try {
      const res = await sendMessage(text)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.response }])
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error'
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${msg}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className={`fixed right-0 top-0 h-screen w-96 bg-navy-800 border-l border-navy-700 z-40 flex flex-col transform transition-transform duration-300 ${
        open ? 'translate-x-0' : 'translate-x-full'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-navy-700">
        <h2 className="font-semibold text-text-primary">AI Assistant</h2>
        <button onClick={onClose} className="p-1 rounded hover:bg-navy-700 text-text-secondary">
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Quick prompts */}
      <div className="flex flex-wrap gap-2 px-5 py-3 border-b border-navy-700/50">
        {quickPrompts.map((prompt) => (
          <button
            key={prompt}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="px-3 py-1 rounded-full text-xs font-medium bg-accent-violet/10 text-accent-violet hover:bg-accent-violet/20 transition-colors disabled:opacity-40"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-4">
        {messages.map((msg, i) => (
          <ChatMessage key={i} role={msg.role} content={msg.content} />
        ))}
        {loading && (
          <div className="flex justify-start mb-3">
            <div className="bg-navy-700 rounded-2xl rounded-bl-md px-4 py-3">
              <Loader2 className="h-4 w-4 animate-spin text-accent-violet" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-5 py-4 border-t border-navy-700">
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>
    </div>
  )
}
