import { ConfigProvider, theme } from 'antd'
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import NavBar from './components/NavBar'
import SearchPage from './pages/SearchPage'
import SkillsPage from './pages/SkillsPage'
import CardsPage from './pages/CardsPage'
import type { Skill } from './api/types'

// 处理从技能广场跳转过来时携带的 skill state
function SearchPageWrapper() {
  const location = useLocation()
  const navigate = useNavigate()
  const skill = location.state?.skill as Skill | undefined

  useEffect(() => {
    if (skill) {
      // 清除 state，避免刷新时重复触发
      navigate('/', { replace: true, state: null })
    }
  }, [])

  return <SearchPage initialSkill={skill} />
}

export default function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#3b82f6',
          colorBgBase: '#080c14',
          colorBgContainer: '#0f1929',
          colorBgElevated: '#111827',
          colorBorder: '#1f2937',
          colorText: '#e2e8f0',
          colorTextSecondary: '#9ca3af',
          borderRadius: 8,
          fontFamily: "-apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif",
        },
      }}
    >
      <BrowserRouter>
        <NavBar />
        <Routes>
          <Route path="/" element={<SearchPageWrapper />} />
          <Route path="/skills" element={<SkillsPage />} />
          <Route path="/cards" element={<CardsPage />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  )
}
