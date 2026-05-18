import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import ChatPanel from '../chat/ChatPanel'

export default function Layout() {
  const [chatOpen, setChatOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-navy-900">
      <Sidebar onToggleChat={() => setChatOpen((o) => !o)} chatOpen={chatOpen} />
      <div className="flex-1 ml-64">
        <TopBar />
        <main className="p-6">
          <Outlet />
        </main>
      </div>
      <ChatPanel open={chatOpen} onClose={() => setChatOpen(false)} />
    </div>
  )
}
