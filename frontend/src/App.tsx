import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Employees from './pages/Employees'
import Schedule from './pages/Schedule'
import CommandCenter from './pages/CommandCenter'
import Analytics from './pages/Analytics'
import Agent from './pages/Agent'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/employees" element={<Employees />} />
          <Route path="/schedule" element={<Schedule />} />
          <Route path="/command-center" element={<CommandCenter />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/agent" element={<Agent />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
