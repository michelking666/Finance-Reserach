import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { BookOutlined, LogoutOutlined, UserOutlined } from '@ant-design/icons'
import { Tooltip } from 'antd'
import { api } from '../api/client'
import styles from './NavBar.module.css'

export default function NavBar() {
  const [username, setUsername] = useState<string>('')

  useEffect(() => {
    api.me().then(u => setUsername(u.username)).catch(() => {})
  }, [])

  return (
    <nav className={styles.nav}>
      <div className={styles.brand}>
        <BookOutlined style={{ color: '#3b82f6', fontSize: 18 }} />
        <span className={styles.brandName}>研究助手</span>
        <span className={styles.brandBadge}>BETA</span>
      </div>
      <div className={styles.links}>
        <NavLink to="/" className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}>
          智能搜索
        </NavLink>
        <NavLink to="/skills" className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}>
          技能广场
        </NavLink>
        <NavLink to="/cards" className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}>
          卡片中心
        </NavLink>
      </div>
      <div className={styles.right}>
        {username && (
          <span className={styles.username}>
            <UserOutlined style={{ marginRight: 4 }} />{username}
          </span>
        )}
        <Tooltip title="登出">
          <LogoutOutlined className={styles.logout} onClick={() => api.logout()} />
        </Tooltip>
      </div>
    </nav>
  )
}
