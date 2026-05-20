import { useState, useEffect } from 'react'
import { Button, Tag, Empty, Spin, Popconfirm, message, Select } from 'antd'
import { DeleteOutlined, SearchOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { TopicCard } from '../api/types'
import styles from './CardsPage.module.css'

const SCENARIO_COLOR: Record<string, string> = {
  '公司深度': '#3b82f6',
  '行业研究': '#8b5cf6',
  '宏观策略': '#10b981',
  '事件跟踪': '#f59e0b',
  '综合研究': '#6b7280',
}

export default function CardsPage() {
  const navigate = useNavigate()
  const [cards, setCards] = useState<TopicCard[]>([])
  const [loading, setLoading] = useState(true)
  const [scenario, setScenario] = useState<string>('全部')

  useEffect(() => {
    api.cards()
      .then(all => setCards(all.filter(c => c.saved)))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  async function handleDelete(id: string) {
    try {
      await api.deleteCard(id)
      setCards(prev => prev.filter(c => c.id !== id))
      message.success('已删除')
    } catch {
      message.error('删除失败')
    }
  }

  const scenarios = ['全部', ...Array.from(new Set(cards.map(c => c.scenario ?? '综合研究')))]
  const filtered = scenario === '全部' ? cards : cards.filter(c => (c.scenario ?? '综合研究') === scenario)

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>卡片中心</h2>
          <p className={styles.subtitle}>已保存的专题研究卡片</p>
        </div>
        <Select
          value={scenario}
          onChange={setScenario}
          className={styles.filter}
          options={scenarios.map(s => ({ value: s, label: s }))}
          style={{ width: 140 }}
        />
      </div>

      {loading ? (
        <div className={styles.loadingWrap}><Spin /></div>
      ) : filtered.length === 0 ? (
        <div className={styles.emptyWrap}>
          <Empty
            description={
              <span style={{ color: '#4b5563' }}>
                {cards.length === 0 ? '暂无保存的卡片，去搜索页生成并保存吧' : '该分类下暂无卡片'}
              </span>
            }
          />
          {cards.length === 0 && (
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={() => navigate('/')}
              style={{ marginTop: 16 }}
            >
              去搜索
            </Button>
          )}
        </div>
      ) : (
        <div className={styles.grid}>
          {filtered.map(card => (
            <div key={card.id} className={styles.card}>
              <div className={styles.cardTop}>
                <span
                  className={styles.scenario}
                  style={{ color: SCENARIO_COLOR[card.scenario ?? '综合研究'] ?? '#6b7280' }}
                >
                  {card.scenario ?? '综合研究'}
                </span>
                <Popconfirm
                  title="确认删除这张卡片？"
                  onConfirm={() => handleDelete(card.id)}
                  okText="删除"
                  cancelText="取消"
                  okButtonProps={{ danger: true }}
                >
                  <Button
                    type="text"
                    icon={<DeleteOutlined />}
                    size="small"
                    className={styles.deleteBtn}
                  />
                </Popconfirm>
              </div>

              <div className={styles.cardTitle}>{card.title}</div>
              {card.subtitle && <div className={styles.cardSubtitle}>{card.subtitle}</div>}

              {card.metrics.length > 0 && (
                <div className={styles.metricsRow}>
                  {card.metrics.slice(0, 3).map((m, i) => (
                    <div key={i} className={styles.metric}>
                      <div className={styles.metricValue}>{m.value}</div>
                      <div className={styles.metricLabel}>{m.label}</div>
                    </div>
                  ))}
                </div>
              )}

              <div className={styles.bullets}>
                {card.bullets.slice(0, 2).map((b, i) => (
                  <div key={i} className={styles.bullet}>
                    <span className={styles.dot} />
                    <span>{b}</span>
                  </div>
                ))}
              </div>

              <div className={styles.cardFooter}>
                <div className={styles.tags}>
                  {card.tags.slice(0, 3).map(t => (
                    <Tag key={t} style={{ fontSize: 10, background: '#1f2937', border: '1px solid #374151', color: '#6b7280' }}>
                      {t}
                    </Tag>
                  ))}
                </div>
                <span className={styles.date}>
                  {new Date(card.created_at).toLocaleDateString('zh-CN')}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
