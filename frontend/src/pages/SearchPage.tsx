import { useState, useRef, useEffect } from 'react'
import {
  Input, Button, Tag, Spin, Divider, Tooltip, message, Typography, Tabs,
} from 'antd'

const { Text } = Typography
import {
  SearchOutlined, SendOutlined, SaveOutlined, CheckOutlined,
  BookOutlined, ThunderboltOutlined, RiseOutlined, FallOutlined,
  CalendarOutlined, BellOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { ChatMessage, TopicCard, Source, Skill, MarketSnapshot } from '../api/client'
import styles from './SearchPage.module.css'

// ── 首屏 mock 数据 ────────────────────────────────────────
const MARKET_NEWS = [
  { id: 1, tag: '债市', tagColor: '#f59e0b', text: '央行今日开展 2000 亿元 7 天逆回购，资金面维持宽松，DR007 报 1.82%' },
  { id: 2, tag: '权益', tagColor: '#3b82f6', text: '沪深 300 收涨 0.8%，科技板块领涨，半导体指数单日涨幅 2.3%' },
  { id: 3, tag: '政策', tagColor: '#10b981', text: '证监会发布公募基金费率改革第三阶段细则，管理费上限进一步下调' },
  { id: 4, tag: '信用', tagColor: '#8b5cf6', text: '城投债一级市场认购倍数回升，AA+ 品种平均认购倍数达 3.2 倍' },
  { id: 5, tag: '海外', tagColor: '#6b7280', text: '美联储 5 月议息会议维持利率不变，点阵图暗示年内仍有 1 次降息空间' },
]

const HOT_STOCKS = [
  { code: '300750.SZ', name: '宁德时代', price: '168.50', change: '+2.34%', up: true },
  { code: '600519.SH', name: '贵州茅台', price: '1682.00', change: '-0.45%', up: false },
  { code: '000858.SZ', name: '五粮液', price: '128.30', change: '+1.12%', up: true },
  { code: '002594.SZ', name: '比亚迪', price: '312.80', change: '+3.21%', up: true },
  { code: '601318.SH', name: '中国平安', price: '52.60', change: '-0.76%', up: false },
]

const HOT_BONDS = [
  { code: '240004.IB', name: '24 附息国债 04', price: '100.85', yield: '2.28%', change: '-2bp' },
  { code: '240210.IB', name: '24 国开 10', price: '101.20', yield: '2.35%', change: '-1bp' },
  { code: 'CITIC.AA+', name: '中信证券 MTN', price: '100.12', yield: '2.68%', change: '+3bp' },
  { code: 'VANKE.CR', name: '万科 2026 债', price: '98.50', yield: '4.85%', change: '-5bp' },
  { code: 'CONV.128', name: '宁德转债', price: '142.30', yield: '—', change: '+1.8%' },
]

const HOT_FUNDS = [
  { code: '110020', name: '易方达蓝筹精选', nav: '2.3841', change: '+1.25%', type: '主动权益' },
  { code: '000001', name: '华夏成长混合', nav: '1.5620', change: '+0.88%', type: '主动权益' },
  { code: '161725', name: '招商中证白酒', nav: '0.9830', change: '-0.32%', type: '指数' },
  { code: '003376', name: '中欧纯债债券', nav: '1.2156', change: '+0.05%', type: '纯债' },
  { code: '000614', name: '华安中短债', nav: '1.1890', change: '+0.03%', type: '中短债' },
]

const TODAY_EVENTS = [
  { time: '09:30', type: '财报', color: '#3b82f6', text: '台积电 2026Q1 业绩说明会' },
  { time: '10:00', type: '政策', color: '#10b981', text: '国家统计局发布 4 月 CPI/PPI 数据' },
  { time: '14:00', type: '债市', color: '#f59e0b', text: '财政部 10Y 国债招标发行（500 亿）' },
  { time: '15:00', type: '路演', color: '#8b5cf6', text: '宁德时代 2026 年中期策略路演' },
  { time: '20:30', type: '海外', color: '#6b7280', text: '美国 4 月非农就业数据公布' },
]
const SOURCE_COLOR: Record<string, string> = {
  internal_report: '#3b82f6',
  external_report: '#8b5cf6',
  external_consulting: '#f59e0b',
  web: '#6b7280',
}
const SOURCE_LABEL: Record<string, string> = {
  internal_report: '内部研报',
  external_report: '外部研报',
  external_consulting: '咨询',
  web: '网络',
}

// ── 子组件：来源列表 ──────────────────────────────────────
function SourceList({ sources }: { sources: Source[] }) {
  if (!sources.length) return null
  return (
    <div className={styles.sourceList}>
      <Text className={styles.sourceTitle}>参考资料</Text>
      {sources.map((s, i) => (
        <div key={s.id} className={styles.sourceItem}>
          <span className={styles.sourceIndex}>[{i + 1}]</span>
          <Tag
            style={{
              background: SOURCE_COLOR[s.source_type] + '22',
              border: `1px solid ${SOURCE_COLOR[s.source_type]}55`,
              color: SOURCE_COLOR[s.source_type],
              fontSize: 11,
            }}
          >
            {SOURCE_LABEL[s.source_type]}
          </Tag>
          <span className={styles.sourceText}>
            《{s.title}》
            {s.publisher && <span className={styles.sourceMeta}> — {s.publisher}</span>}
            {s.published_at && <span className={styles.sourceMeta}> ({s.published_at})</span>}
          </span>
        </div>
      ))}
    </div>
  )
}

// ── 子组件：专题卡片 ──────────────────────────────────────
function TopicCardPanel({
  card,
  onSave,
  suggestedSkills,
  allSkills,
  onUseSkill,
}: {
  card: TopicCard
  onSave: (id: string) => void
  suggestedSkills: string[]
  allSkills: Skill[]
  onUseSkill: (skill: Skill) => void
}) {
  const suggested = allSkills.filter(s => suggestedSkills.includes(s.id))

  return (
    <div className={styles.cardPanel}>
      <div className={styles.cardHeader}>
        <div>
          <div className={styles.cardScenario}>{card.scenario}</div>
          <div className={styles.cardTitle}>{card.title}</div>
          {card.subtitle && <div className={styles.cardSubtitle}>{card.subtitle}</div>}
        </div>
        <Tooltip title={card.saved ? '已保存' : '保存到卡片中心'}>
          <Button
            type={card.saved ? 'primary' : 'default'}
            icon={card.saved ? <CheckOutlined /> : <SaveOutlined />}
            size="small"
            onClick={() => onSave(card.id)}
            className={styles.saveBtn}
          >
            {card.saved ? '已保存' : '保存'}
          </Button>
        </Tooltip>
      </div>

      {card.metrics.length > 0 && (
        <div className={styles.metricsRow}>
          {card.metrics.map((m, i) => (
            <div key={i} className={styles.metricItem}>
              <div className={styles.metricValue}>{m.value}</div>
              <div className={styles.metricLabel}>{m.label}</div>
              <div className={styles.metricChange}>{m.change}</div>
            </div>
          ))}
        </div>
      )}

      <Divider style={{ borderColor: '#1f2937', margin: '12px 0' }} />

      <div className={styles.bulletList}>
        {card.bullets.map((b, i) => (
          <div key={i} className={styles.bulletItem}>
            <span className={styles.bulletDot} />
            <span>{b}</span>
          </div>
        ))}
      </div>

      {card.tags.length > 0 && (
        <div className={styles.tagRow}>
          {card.tags.map(t => (
            <Tag key={t} style={{ background: '#1f2937', border: '1px solid #374151', color: '#9ca3af', fontSize: 11 }}>
              {t}
            </Tag>
          ))}
        </div>
      )}

      {suggested.length > 0 && (
        <>
          <Divider style={{ borderColor: '#1f2937', margin: '12px 0' }} />
          <div className={styles.suggestLabel}>
            <ThunderboltOutlined style={{ color: '#f59e0b', marginRight: 4 }} />
            推荐技能
          </div>
          <div className={styles.suggestRow}>
            {suggested.map(s => (
              <Button
                key={s.id}
                size="small"
                className={styles.suggestBtn}
                onClick={() => onUseSkill(s)}
              >
                {s.icon} {s.name}
              </Button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

// ── 子组件：消息气泡 ──────────────────────────────────────
function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user'
  return (
    <div className={isUser ? styles.userBubble : styles.aiBubble}>
      {!isUser && (
        <div className={styles.aiAvatar}>AI</div>
      )}
      <div className={isUser ? styles.userText : styles.aiText}>
        {msg.content.split('\n').map((line, i) => (
          <span key={i}>{line}{i < msg.content.split('\n').length - 1 && <br />}</span>
        ))}
      </div>
    </div>
  )
}

// ── 主页面 ────────────────────────────────────────────────
export default function SearchPage({ initialSkill }: { initialSkill?: Skill }) {
  const navigate = useNavigate()
  const [skills, setSkills] = useState<Skill[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState(initialSkill?.sample_input ?? '')
  const [loading, setLoading] = useState(false)
  const [activeCard, setActiveCard] = useState<TopicCard | null>(null)
  const [suggestedSkills, setSuggestedSkills] = useState<string[]>([])
  const [savedCards, setSavedCards] = useState<TopicCard[]>([])
  const [activeSkill, setActiveSkill] = useState<Skill | null>(initialSkill ?? null)
  const [hasSearched, setHasSearched] = useState(!!initialSkill)
  const [market, setMarket] = useState<MarketSnapshot | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<any>(null)

  useEffect(() => {
    api.skills().then(setSkills).catch(() => {})
    api.cards().then(cards => setSavedCards(cards.filter(c => c.saved))).catch(() => {})
    api.marketSnapshot().then(setMarket).catch(() => {})
  }, [])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend() {
    const text = input.trim()
    if (!text || loading) return

    const userMsg: ChatMessage = { role: 'user', content: text }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setInput('')
    setLoading(true)
    setHasSearched(true)

    try {
      const res = await api.chat(newMessages, activeSkill?.id)
      setMessages(prev => [...prev, res.message])
      if (res.card) setActiveCard(res.card)
      setSuggestedSkills(res.suggested_skills)
    } catch (err) {
      console.error('[chat error]', err)
      message.error('请求失败，请确认后端服务已启动')
    } finally {
      setLoading(false)
      setActiveSkill(null)
    }
  }

  async function handleSaveCard(id: string) {
    try {
      const updated = await api.saveCard(id)
      setActiveCard(updated)
      if (updated.saved) {
        setSavedCards(prev => [updated, ...prev.filter(c => c.id !== id)])
        message.success('已保存到卡片中心')
      } else {
        setSavedCards(prev => prev.filter(c => c.id !== id))
      }
    } catch {
      message.error('保存失败')
    }
  }

  function handleUseSkill(skill: Skill) {
    setActiveSkill(skill)
    setInput(skill.sample_input ?? '')
    inputRef.current?.focus()
  }

  function handleQuickSkill(skill: Skill) {
    setActiveSkill(skill)
    setInput(skill.sample_input ?? '')
    setHasSearched(true)
    inputRef.current?.focus()
  }

  // ── 首屏（未搜索） ────────────────────────────────────
  if (!hasSearched) {
    return (
      <div className={styles.homePage}>
        {/* 顶部：Logo + 搜索框 + 快捷技能 */}
        <div className={styles.homeTop}>
          <div className={styles.homeLogo}>
            <BookOutlined style={{ fontSize: 28, color: '#3b82f6' }} />
          </div>
          <h1 className={styles.homeTitle}>智能投资研究助手</h1>
          <p className={styles.homeSubtitle}>搜索债券、股票、基金研报，或调用技能生成专题分析</p>

          <div className={styles.homeSearchWrap}>
            <Input
              ref={inputRef}
              size="large"
              placeholder="输入研究问题，或 @ 调用技能..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onPressEnter={handleSend}
              prefix={<SearchOutlined style={{ color: '#4b5563' }} />}
              suffix={
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSend}
                  loading={loading}
                  disabled={!input.trim()}
                />
              }
              className={styles.homeSearchInput}
            />
          </div>

          <div className={styles.quickSkills}>
            {skills.slice(0, 7).map(s => (
              <Button
                key={s.id}
                className={styles.quickSkillBtn}
                onClick={() => handleQuickSkill(s)}
              >
                <span>{s.icon}</span>
                <span>{s.name}</span>
              </Button>
            ))}
            <Button
              className={styles.quickSkillBtn}
              onClick={() => navigate('/skills')}
            >
              <span>＋</span>
              <span>更多技能</span>
            </Button>
          </div>
        </div>

        {/* 信息面板：三栏 */}
        <div className={styles.homeInfoGrid}>
          {/* 左：市场快讯 */}
          <div className={styles.infoCard}>
            <div className={styles.infoCardHeader}>
              <BellOutlined style={{ color: '#f59e0b', marginRight: 6 }} />
              <span className={styles.infoCardTitle}>市场快讯</span>
              <span className={styles.infoCardDate}>2026-05-19</span>
            </div>
            <div className={styles.newsList}>
              {MARKET_NEWS.map(n => (
                <div key={n.id} className={styles.newsItem}>
                  <Tag style={{
                    background: n.tagColor + '22',
                    border: `1px solid ${n.tagColor}55`,
                    color: n.tagColor,
                    fontSize: 10,
                    flexShrink: 0,
                  }}>{n.tag}</Tag>
                  <span className={styles.newsText}>{n.text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 中：热门标的 */}
          <div className={styles.infoCard}>
            <div className={styles.infoCardHeader}>
              <RiseOutlined style={{ color: '#3b82f6', marginRight: 6 }} />
              <span className={styles.infoCardTitle}>热门标的</span>
              {!market && <Spin size="small" style={{ marginLeft: 'auto' }} />}
            </div>
            <Tabs
              size="small"
              className={styles.hotTabs}
              items={[
                {
                  key: 'stock',
                  label: '股票',
                  children: (
                    <div className={styles.hotList}>
                      {(market?.hot_stocks ?? HOT_STOCKS).map(s => (
                        <div
                          key={s.code}
                          className={styles.hotItem}
                          onClick={() => { setInput(s.name + ' ' + s.code); inputRef.current?.focus() }}
                        >
                          <div className={styles.hotName}>{s.name}</div>
                          <div className={styles.hotCode}>{s.code}</div>
                          <div className={s.up ? styles.hotUp : styles.hotDown}>
                            {s.up ? <RiseOutlined /> : <FallOutlined />} {s.change}
                          </div>
                        </div>
                      ))}
                    </div>
                  ),
                },
                {
                  key: 'bond',
                  label: '债券',
                  children: (
                    <div className={styles.hotList}>
                      {market?.bond_yields ? market.bond_yields.map(b => (
                        <div
                          key={b.code}
                          className={styles.hotItem}
                          onClick={() => { setInput(b.name); inputRef.current?.focus() }}
                        >
                          <div className={styles.hotName}>{b.name}</div>
                          <div className={styles.hotCode}>收益率 {b.yield_}</div>
                          <div className={b.change.startsWith('-') ? styles.hotDown : styles.hotUp}>
                            {b.change}
                          </div>
                        </div>
                      )) : HOT_BONDS.map(b => (
                        <div
                          key={b.code}
                          className={styles.hotItem}
                          onClick={() => { setInput(b.name); inputRef.current?.focus() }}
                        >
                          <div className={styles.hotName}>{b.name}</div>
                          <div className={styles.hotCode}>收益率 {b.yield}</div>
                          <div className={b.change.startsWith('-') ? styles.hotDown : styles.hotUp}>
                            {b.change}
                          </div>
                        </div>
                      ))}
                    </div>
                  ),
                },
                {
                  key: 'fund',
                  label: '基金',
                  children: (
                    <div className={styles.hotList}>
                      {(market?.fund_navs ?? HOT_FUNDS).map(f => (
                        <div
                          key={f.code}
                          className={styles.hotItem}
                          onClick={() => { setInput(f.name + ' ' + f.code); inputRef.current?.focus() }}
                        >
                          <div className={styles.hotName}>{f.name}</div>
                          <div className={styles.hotCode}>{'type' in f ? f.type : (f as any).type}</div>
                          <div className={f.change.startsWith('+') ? styles.hotUp : styles.hotDown}>
                            {f.change}
                          </div>
                        </div>
                      ))}
                    </div>
                  ),
                },
              ]}
            />
          </div>

          {/* 右：今日日历 + 常用卡片 */}
          <div className={styles.infoCardRight}>
            <div className={styles.infoCard} style={{ marginBottom: 12 }}>
              <div className={styles.infoCardHeader}>
                <CalendarOutlined style={{ color: '#10b981', marginRight: 6 }} />
                <span className={styles.infoCardTitle}>今日日历</span>
                <span className={styles.infoCardDate}>事件催化</span>
              </div>
              <div className={styles.eventList}>
                {TODAY_EVENTS.map((e, i) => (
                  <div key={i} className={styles.eventItem}>
                    <span className={styles.eventTime}>{e.time}</span>
                    <Tag style={{
                      background: e.color + '22',
                      border: `1px solid ${e.color}55`,
                      color: e.color,
                      fontSize: 10,
                      flexShrink: 0,
                    }}>{e.type}</Tag>
                    <span className={styles.eventText}>{e.text}</span>
                  </div>
                ))}
              </div>
            </div>

            {savedCards.length > 0 && (
              <div className={styles.infoCard}>
                <div className={styles.infoCardHeader}>
                  <BookOutlined style={{ color: '#8b5cf6', marginRight: 6 }} />
                  <span className={styles.infoCardTitle}>常用卡片</span>
                  <Button type="link" size="small" onClick={() => navigate('/cards')} style={{ color: '#4b5563', padding: 0, marginLeft: 'auto' }}>
                    全部
                  </Button>
                </div>
                <div className={styles.savedGrid}>
                  {savedCards.slice(0, 4).map(card => (
                    <div
                      key={card.id}
                      className={styles.savedCard}
                      onClick={() => { setActiveCard(card); setHasSearched(true) }}
                    >
                      <div className={styles.savedCardScenario}>{card.scenario}</div>
                      <div className={styles.savedCardTitle}>{card.title}</div>
                      <div className={styles.savedCardTags}>
                        {card.tags.slice(0, 2).map(t => (
                          <Tag key={t} style={{ fontSize: 10, background: '#1f2937', border: '1px solid #374151', color: '#6b7280' }}>{t}</Tag>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // ── 搜索结果态（双栏） ────────────────────────────────
  return (
    <div className={styles.searchPage}>
      {/* 左侧：对话区 */}
      <div className={styles.chatPane}>
        <div className={styles.chatMessages}>
          {messages.map((msg, i) => (
            <MessageBubble key={i} msg={msg} />
          ))}
          {loading && (
            <div className={styles.aiBubble}>
              <div className={styles.aiAvatar}>AI</div>
              <Spin size="small" style={{ marginTop: 4 }} />
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* 来源 */}
        {activeCard && <SourceList sources={activeCard.sources} />}

        {/* 输入框 */}
        <div className={styles.chatInputWrap}>
          {activeSkill && (
            <div className={styles.activeSkillTag}>
              <Tag
                closable
                onClose={() => setActiveSkill(null)}
                style={{ background: '#1e3a5f', border: '1px solid #3b82f6', color: '#93c5fd' }}
              >
                {activeSkill.icon} {activeSkill.name}
              </Tag>
            </div>
          )}
          <Input
            ref={inputRef}
            placeholder="继续追问，或输入新问题..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onPressEnter={handleSend}
            suffix={
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSend}
                loading={loading}
                disabled={!input.trim()}
                size="small"
              />
            }
            className={styles.chatInput}
          />
        </div>
      </div>

      {/* 右侧：专题卡片 */}
      <div className={styles.cardPane}>
        {activeCard ? (
          <TopicCardPanel
            card={activeCard}
            onSave={handleSaveCard}
            suggestedSkills={suggestedSkills}
            allSkills={skills}
            onUseSkill={handleUseSkill}
          />
        ) : (
          <div className={styles.cardPlaceholder}>
            <BookOutlined style={{ fontSize: 32, color: '#374151' }} />
            <p style={{ color: '#4b5563', marginTop: 12 }}>搜索后将在此生成专题卡片</p>
          </div>
        )}
      </div>
    </div>
  )
}
