import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { 
  MessageCircle, 
  Users, 
  Bot, 
  Phone, 
  TrendingUp, 
  Activity, 
  Send, 
  Settings,
  BarChart3,
  Zap,
  Shield,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Mic,
  FileText,
  Target,
  Gift,
  Mail,
  Download,
  Plus,
  Search,
  Filter,
  MoreVertical,
  RefreshCw
} from 'lucide-react'
import ApiService from './components/ApiService.js'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [selectedChat, setSelectedChat] = useState(null)
  const [messageInput, setMessageInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [loading, setLoading] = useState(false)

  // State for API data
  const [dashboardStats, setDashboardStats] = useState({})
  const [whatsappNumbers, setWhatsappNumbers] = useState([])
  const [doctors, setDoctors] = useState([])
  const [aiAgents, setAiAgents] = useState([])
  const [chatMessages, setChatMessages] = useState([])

  // Load data on component mount
  useEffect(() => {
    loadDashboardData()
  }, [])

  // Load chat messages when a doctor is selected
  useEffect(() => {
    if (selectedChat) {
      loadChatMessages(selectedChat)
    }
  }, [selectedChat])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [stats, numbers, doctorsList, agents] = await Promise.all([
        ApiService.getDashboardStats(),
        ApiService.getWhatsAppNumbers(),
        ApiService.getDoctors(),
        ApiService.getAIAgents()
      ])
      
      setDashboardStats(stats)
      setWhatsappNumbers(numbers)
      setDoctors(doctorsList)
      setAiAgents(agents)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadChatMessages = async (doctorId) => {
    try {
      const messages = await ApiService.getChatMessages(doctorId)
      setChatMessages(messages)
    } catch (error) {
      console.error('Failed to load chat messages:', error)
    }
  }

  const sendMessage = async () => {
    if (messageInput.trim() && selectedChat) {
      try {
        setIsTyping(true)
        await ApiService.sendMessage(selectedChat, messageInput)
        setMessageInput('')
        // Reload messages to show the new one
        await loadChatMessages(selectedChat)
      } catch (error) {
        console.error('Failed to send message:', error)
      } finally {
        setIsTyping(false)
      }
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'blocked': return 'bg-red-500'
      case 'standby': return 'bg-yellow-500'
      default: return 'bg-gray-500'
    }
  }

  const getTagColor = (tag) => {
    switch (tag) {
      case 'hot_lead': return 'bg-red-100 text-red-800'
      case 'warm_lead': return 'bg-orange-100 text-orange-800'
      case 'cold_lead': return 'bg-blue-100 text-blue-800'
      case 'registered': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const getSelectedDoctor = () => {
    return doctors.find(d => d.id === selectedChat)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <MessageCircle className="h-8 w-8 text-green-600" />
              <h1 className="text-2xl font-bold text-gray-900">SurgiAI Dashboard</h1>
            </div>
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              <Activity className="h-3 w-3 mr-1" />
              System Active
            </Badge>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="outline" size="sm" onClick={loadDashboardData} disabled={loading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
            <Avatar>
              <AvatarFallback>AD</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-gray-200 p-4">
          <nav className="space-y-2">
            <Button 
              variant={activeTab === 'dashboard' ? 'default' : 'ghost'} 
              className="w-full justify-start"
              onClick={() => setActiveTab('dashboard')}
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              Dashboard
            </Button>
            <Button 
              variant={activeTab === 'chat' ? 'default' : 'ghost'} 
              className="w-full justify-start"
              onClick={() => setActiveTab('chat')}
            >
              <MessageCircle className="h-4 w-4 mr-2" />
              Chat Interface
            </Button>
            <Button 
              variant={activeTab === 'numbers' ? 'default' : 'ghost'} 
              className="w-full justify-start"
              onClick={() => setActiveTab('numbers')}
            >
              <Phone className="h-4 w-4 mr-2" />
              WhatsApp Numbers
            </Button>
            <Button 
              variant={activeTab === 'agents' ? 'default' : 'ghost'} 
              className="w-full justify-start"
              onClick={() => setActiveTab('agents')}
            >
              <Bot className="h-4 w-4 mr-2" />
              AI Agents
            </Button>
            <Button 
              variant={activeTab === 'leads' ? 'default' : 'ghost'} 
              className="w-full justify-start"
              onClick={() => setActiveTab('leads')}
            >
              <Users className="h-4 w-4 mr-2" />
              Lead Management
            </Button>
            <Button 
              variant={activeTab === 'analytics' ? 'default' : 'ghost'} 
              className="w-full justify-start"
              onClick={() => setActiveTab('analytics')}
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              Analytics
            </Button>
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-hidden">
          {activeTab === 'dashboard' && (
            <div className="p-6 space-y-6">
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Active Numbers</CardTitle>
                    <Phone className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardStats.active_numbers || '0/0'}</div>
                    <p className="text-xs text-muted-foreground">WhatsApp connections</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Doctors</CardTitle>
                    <Users className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardStats.total_doctors || '0'}</div>
                    <p className="text-xs text-muted-foreground">Registered leads</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Messages Today</CardTitle>
                    <MessageCircle className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardStats.messages_today || '0'}</div>
                    <p className="text-xs text-muted-foreground">Conversations handled</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">AI Performance</CardTitle>
                    <Bot className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardStats.ai_performance || '0%'}</div>
                    <p className="text-xs text-muted-foreground">Response accuracy</p>
                  </CardContent>
                </Card>
              </div>

              {/* Recent Activity */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Conversations</CardTitle>
                    <CardDescription>Latest doctor interactions</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {doctors.slice(0, 3).map((doctor) => (
                        <div key={doctor.id} className="flex items-center space-x-4">
                          <Avatar>
                            <AvatarFallback>{doctor.avatar}</AvatarFallback>
                          </Avatar>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {doctor.name}
                            </p>
                            <p className="text-sm text-gray-500 truncate">
                              {doctor.city}
                            </p>
                          </div>
                          <div className="flex flex-col items-end">
                            <Badge className={getTagColor(doctor.tag)}>
                              {doctor.tag.replace('_', ' ')}
                            </Badge>
                            <span className="text-xs text-gray-500">Score: {doctor.score}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>AI Agent Status</CardTitle>
                    <CardDescription>Current agent performance</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {aiAgents.slice(0, 4).map((agent, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                            <span className="text-sm font-medium">{agent.name}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            {agent.status === 'active' ? (
                              <span className="text-sm text-green-600">{agent.performance}%</span>
                            ) : (
                              <span className="text-sm text-yellow-600">Standby</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="flex h-full">
              {/* Chat List */}
              <div className="w-80 border-r border-gray-200 bg-white">
                <div className="p-4 border-b border-gray-200">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input placeholder="Search doctors..." className="pl-10" />
                  </div>
                </div>
                <ScrollArea className="h-[calc(100vh-200px)]">
                  <div className="p-2">
                    {doctors.map((doctor) => (
                      <div
                        key={doctor.id}
                        className={`p-3 rounded-lg cursor-pointer hover:bg-gray-50 ${
                          selectedChat === doctor.id ? 'bg-blue-50 border border-blue-200' : ''
                        }`}
                        onClick={() => setSelectedChat(doctor.id)}
                      >
                        <div className="flex items-center space-x-3">
                          <Avatar>
                            <AvatarFallback>{doctor.avatar}</AvatarFallback>
                          </Avatar>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {doctor.name}
                              </p>
                              <span className="text-xs text-gray-500">{formatTime(doctor.last_interaction)}</span>
                            </div>
                            <p className="text-sm text-gray-500 truncate">
                              {doctor.city}
                            </p>
                            <div className="flex items-center justify-between mt-1">
                              <Badge className={getTagColor(doctor.tag)} variant="secondary">
                                {doctor.tag.replace('_', ' ')}
                              </Badge>
                              <span className="text-xs text-gray-400">Score: {doctor.score}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>

              {/* Chat Area */}
              <div className="flex-1 flex flex-col">
                {selectedChat ? (
                  <>
                    {/* Chat Header */}
                    <div className="p-4 border-b border-gray-200 bg-white">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <Avatar>
                            <AvatarFallback>
                              {getSelectedDoctor()?.avatar}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <h3 className="font-medium">
                              {getSelectedDoctor()?.name}
                            </h3>
                            <p className="text-sm text-gray-500">
                              {getSelectedDoctor()?.city} • Online
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button variant="outline" size="sm">
                            <Mic className="h-4 w-4" />
                          </Button>
                          <Button variant="outline" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>

                    {/* Messages */}
                    <ScrollArea className="flex-1 p-4">
                      <div className="space-y-4">
                        {chatMessages.map((message) => (
                          <div
                            key={message.id}
                            className={`flex ${message.sender === 'doctor' ? 'justify-end' : 'justify-start'}`}
                          >
                            <div
                              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                                message.sender === 'doctor'
                                  ? 'bg-blue-500 text-white'
                                  : message.sender === 'ai'
                                  ? 'bg-green-100 text-gray-900'
                                  : 'bg-gray-100 text-gray-900'
                              }`}
                            >
                              <p className="text-sm">{message.message}</p>
                              <div className="flex items-center justify-between mt-1">
                                <span className="text-xs opacity-70">{message.timestamp}</span>
                                {message.via && (
                                  <span className="text-xs opacity-70">via {message.via}</span>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                        {isTyping && (
                          <div className="flex justify-start">
                            <div className="bg-gray-100 px-4 py-2 rounded-lg">
                              <div className="flex space-x-1">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </ScrollArea>

                    {/* Message Input */}
                    <div className="p-4 border-t border-gray-200 bg-white">
                      <div className="flex space-x-2">
                        <Input
                          placeholder="Type your message..."
                          value={messageInput}
                          onChange={(e) => setMessageInput(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                          className="flex-1"
                        />
                        <Button onClick={sendMessage} disabled={!messageInput.trim() || isTyping}>
                          <Send className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center bg-gray-50">
                    <div className="text-center">
                      <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Select a conversation</h3>
                      <p className="text-gray-500">Choose a doctor from the list to start chatting</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'numbers' && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">WhatsApp Numbers</h2>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Number
                </Button>
              </div>
              <div className="grid gap-4">
                {whatsappNumbers.map((number) => (
                  <Card key={number.id}>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className={`w-3 h-3 rounded-full ${getStatusColor(number.status)}`}></div>
                          <div>
                            <h3 className="font-medium">{number.number}</h3>
                            <p className="text-sm text-gray-500">
                              {number.connection_type} Connection • {number.messages_count} messages • Last active: {number.last_active}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={number.status === 'active' ? 'default' : number.status === 'blocked' ? 'destructive' : 'secondary'}>
                            {number.status}
                          </Badge>
                          <Button variant="outline" size="sm">
                            <Settings className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'agents' && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">AI Agents</h2>
                <Button variant="outline">
                  <Shield className="h-4 w-4 mr-2" />
                  Health Check
                </Button>
              </div>
              <div className="grid gap-4">
                {aiAgents.map((agent, index) => (
                  <Card key={index}>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className={`w-3 h-3 rounded-full ${agent.status === 'active' ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                          <div>
                            <h3 className="font-medium">{agent.name}</h3>
                            <p className="text-sm text-gray-500">
                              Last crash: {agent.last_crash}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          {agent.status === 'active' ? (
                            <div className="text-right">
                              <p className="text-sm font-medium text-green-600">{agent.performance}%</p>
                              <p className="text-xs text-gray-500">Performance</p>
                            </div>
                          ) : (
                            <Badge variant="secondary">Standby Active</Badge>
                          )}
                          <Button variant="outline" size="sm">
                            <Activity className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'leads' && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Lead Management</h2>
                <div className="flex space-x-2">
                  <Button variant="outline">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                  <Button variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
              <div className="grid gap-4">
                {doctors.map((doctor) => (
                  <Card key={doctor.id}>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Avatar>
                            <AvatarFallback>{doctor.avatar}</AvatarFallback>
                          </Avatar>
                          <div>
                            <h3 className="font-medium">{doctor.name}</h3>
                            <p className="text-sm text-gray-500">{doctor.city}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <div className="text-center">
                            <p className="text-lg font-bold">{doctor.score}</p>
                            <p className="text-xs text-gray-500">Score</p>
                          </div>
                          <Badge className={getTagColor(doctor.tag)}>
                            {doctor.tag.replace('_', ' ')}
                          </Badge>
                          <Button variant="outline" size="sm">
                            View Details
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-6">Analytics & Reports</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Message Volume</CardTitle>
                    <CardDescription>Daily message statistics</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64 flex items-center justify-center text-gray-500">
                      Chart placeholder - Message volume over time
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Lead Conversion</CardTitle>
                    <CardDescription>Conversion funnel analysis</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64 flex items-center justify-center text-gray-500">
                      Chart placeholder - Lead conversion rates
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>AI Performance</CardTitle>
                    <CardDescription>Agent response accuracy</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64 flex items-center justify-center text-gray-500">
                      Chart placeholder - AI performance metrics
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Top Responses</CardTitle>
                    <CardDescription>Most effective AI replies</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">"Want me to block your seat?"</span>
                        <Badge>48% conversion</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">"Doctor, limited time offer..."</span>
                        <Badge>42% conversion</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">"Free PDF guide available"</span>
                        <Badge>38% conversion</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App

