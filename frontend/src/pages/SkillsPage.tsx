import { useState, useEffect } from 'react'
import { Input, Tabs, Button, Tag, Empty, Spin } from 'antd'
import { SearchOutlined, ArrowRightOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { Skill } from '../api/types'
import styles from './SkillsPage.module.css'

const CATEGORY_ORDER = ['全部', '公司分析', '行业分析', '宏观策略', '债券分析', '基金研究', '数据', '写作']

const CATEGORY_COLOR: Record<string, string> = {
  '公司分析': '#3b82f6',
  '行业分析': '#8b5cf6',
  '宏观策略': '#10b981',
  '债券分析': '#f59e0b',
  '基金研究': '#06b6d4',
  '数据': '#6366f1',
  '写作': '#ec4899',
}

export default function SkillsPage() {
  const navigate = useNavigate()
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('全部')
  const [search, setSearch] = useState('')

  useEffect(() => {
    api.skills()
      .then(setSkills)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const filtered = skills.filter(s => {
    const matchCat = category === '全部' || s.category === category
    const matchSearch = !search || s.name.includes(search) || s.description.includes(search)
    return matchCat && matchSearch
  })

  const categories = CATEGORY_ORDER.filter(c =>
    c === '全部' || skills.some(s => s.category === c)
  )

  function useSkill(skill: Skill) {
    navigate('/', { state: { skill } })
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>技能广场</h2>
          <p className={styles.subtitle}>选择技能，快速生成结构化研究分析</p>
        </div>
        <Input
          placeholder="搜索技能..."
          prefix={<SearchOutlined style={{ color: '#4b5563' }} />}
          value={search}
          onChange={e => setSearch(e.target.value)}
          className={styles.searchInput}
          style={{ width: 220 }}
        />
      </div>

      <Tabs
        activeKey={category}
        onChange={setCategory}
        className={styles.tabs}
        items={categories.map(c => ({ key: c, label: c }))}
      />

      {loading ? (
        <div className={styles.loadingWrap}>
          <Spin />
        </div>
      ) : filtered.length === 0 ? (
        <Empty description={<span style={{ color: '#4b5563' }}>暂无匹配技能</span>} />
      ) : (
        <div className={styles.grid}>
          {filtered.map(skill => (
            <div key={skill.id} className={styles.card}>
              <div className={styles.cardTop}>
                <div className={styles.iconWrap}>{skill.icon}</div>
                <Tag
                  style={{
                    background: (CATEGORY_COLOR[skill.category] ?? '#6b7280') + '22',
                    border: `1px solid ${(CATEGORY_COLOR[skill.category] ?? '#6b7280')}55`,
                    color: CATEGORY_COLOR[skill.category] ?? '#9ca3af',
                    fontSize: 11,
                  }}
                >
                  {skill.category}
                </Tag>
              </div>
              <div className={styles.cardName}>{skill.name}</div>
              <div className={styles.cardDesc}>{skill.description}</div>
              {skill.sample_input && (
                <div className={styles.sampleWrap}>
                  <span className={styles.sampleLabel}>示例：</span>
                  <span className={styles.sampleText}>{skill.sample_input}</span>
                </div>
              )}
              <Button
                type="primary"
                icon={<ArrowRightOutlined />}
                className={styles.useBtn}
                onClick={() => useSkill(skill)}
                block
              >
                立即使用
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
