<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  fundName: string
  fundCode: string
  boughtShares: number
  totalShares: number
  currentDropPercent: number
  triggerPercent: number
}

const props = withDefaults(defineProps<Props>(), {
  fundName: '华夏沪深300ETF联接A',
  fundCode: '510300',
  boughtShares: 3,
  totalShares: 10,
  currentDropPercent: 8.5,
  triggerPercent: 4,
})

const remainingShares = computed(() => props.totalShares - props.boughtShares)

const triggerStatus = computed(() => {
  const nextTrigger = (props.boughtShares + 1) * props.triggerPercent
  const diff = nextTrigger - props.currentDropPercent
  if (diff <= 0) {
    return {
      type: 'buy' as const,
      text: `已触发 -${nextTrigger.toFixed(1)}% 推荐买入`,
      diff: 0,
    }
  }
  return {
    type: 'wait' as const,
    text: `距下一次加仓还差 ${diff.toFixed(1)}%`,
    diff,
  }
})

const statusColor = computed(() => {
  const currentLevel = Math.floor(props.currentDropPercent / props.triggerPercent)
  if (currentLevel >= props.totalShares - 1) return 'red'
  if (currentLevel >= Math.floor(props.totalShares * 0.7)) return 'red'
  if (currentLevel >= Math.floor(props.totalShares * 0.4)) return 'blue'
  return 'green'
})

const isAlert = computed(() => triggerStatus.value.type === 'buy')

const gridItems = computed(() => {
  return Array.from({ length: props.totalShares }, (_, i) => {
    const triggerAt = (i + 1) * props.triggerPercent
    return {
      index: i,
      triggerAt,
      isBought: i < props.boughtShares,
      isCurrent: i === props.boughtShares && triggerStatus.value.type === 'buy',
      isNext: i === props.boughtShares && triggerStatus.value.type === 'wait',
    }
  })
})
</script>

<template>
  <div class="card-wrapper">
    <div class="card">
      <div class="card-header">
        <div class="fund-info">
          <h3 class="fund-name">{{ fundName }}</h3>
          <span class="fund-code">{{ fundCode }}</span>
        </div>
        <div
          class="status-badge"
          :class="[`status-${statusColor}`, { 'alert-pulse': isAlert }]"
        >
          <span class="status-dot"></span>
          <span class="status-text">
            {{ triggerStatus.type === 'buy' ? '触发买入' : '持有观望' }}
          </span>
        </div>
      </div>

      <div class="progress-section">
        <div class="progress-label">
          <span>网格进度</span>
          <span class="progress-count">
            <span class="bought-count">{{ boughtShares }}</span>
            <span class="total-count">/{{ totalShares }} 份</span>
          </span>
        </div>

        <div class="grid-bar">
          <div
            v-for="item in gridItems"
            :key="item.index"
            class="grid-segment"
            :class="{
              'segment-bought': item.isBought,
              'segment-current': item.isCurrent,
              'segment-next': item.isNext,
              'segment-green': item.isBought && item.index < Math.floor(totalShares * 0.4),
              'segment-blue': item.isBought && item.index >= Math.floor(totalShares * 0.4) && item.index < Math.floor(totalShares * 0.7),
              'segment-red': (item.isBought && item.index >= Math.floor(totalShares * 0.7)) || item.isCurrent,
              'pulse-glow': item.isCurrent,
            }"
          >
            <span class="segment-label" v-if="item.index % 2 === 0">
              -{{ item.triggerAt }}%
            </span>
          </div>
        </div>
      </div>

      <div class="trigger-section">
        <div class="trigger-banner" :class="[`trigger-${triggerStatus.type}`]">
          <div class="trigger-icon">
            <svg v-if="triggerStatus.type === 'buy'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12l7 7 7-7"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 16v-4M12 8h.01"/>
            </svg>
          </div>
          <div class="trigger-text">
            {{ triggerStatus.text }}
          </div>
          <div class="trigger-remaining">
            剩余 {{ remainingShares }} 份资金
          </div>
        </div>
      </div>

      <div class="card-footer">
        <div class="footer-item">
          <span class="footer-label">当前回撤</span>
          <span class="footer-value" :class="`value-${statusColor}`">
            -{{ currentDropPercent.toFixed(2) }}%
          </span>
        </div>
        <div class="footer-divider"></div>
        <div class="footer-item">
          <span class="footer-label">网格间距</span>
          <span class="footer-value value-blue">{{ triggerPercent }}%</span>
        </div>
        <div class="footer-divider"></div>
        <div class="footer-item">
          <span class="footer-label">已投入</span>
          <span class="footer-value value-green">{{ (boughtShares / totalShares * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-wrapper {
  width: 100%;
  max-width: 380px;
}

.card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.12);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.fund-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.fund-name {
  font-size: 17px;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.2px;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.fund-code {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #3B82F6;
}

.status-green .status-dot {
  background: #10B981;
}

.status-blue .status-dot {
  background: #3B82F6;
}

.status-red .status-dot {
  background: #EF4444;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
}

.alert-pulse .status-dot {
  animation: statusPulse 2s ease-in-out infinite;
}

@keyframes statusPulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.3);
  }
}

.progress-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.progress-count {
  font-size: 14px;
}

.bought-count {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
}

.total-count {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
  margin-left: 2px;
}

.grid-bar {
  display: flex;
  gap: 3px;
  height: 44px;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.08);
  padding: 3px;
}

.grid-segment {
  flex: 1;
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.segment-bought.segment-green {
  background: linear-gradient(180deg, #34D399 0%, #10B981 100%);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.segment-bought.segment-blue {
  background: linear-gradient(180deg, #60A5FA 0%, #3B82F6 100%);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.segment-bought.segment-red {
  background: linear-gradient(180deg, #F87171 0%, #EF4444 100%);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.segment-next {
  background: rgba(59, 130, 246, 0.25);
  border: 1px dashed rgba(59, 130, 246, 0.6);
}

.segment-current {
  background: linear-gradient(180deg, #F87171 0%, #EF4444 100%);
}

.segment-label {
  font-size: 9px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  white-space: nowrap;
}

.segment-bought .segment-label {
  color: rgba(255, 255, 255, 0.95);
}

.pulse-glow {
  animation: pulseGlow 2s ease-in-out infinite;
}

@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3), 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.5), 0 0 12px 4px rgba(239, 68, 68, 0.35);
  }
}

.trigger-section {
  margin-top: 4px;
}

.trigger-banner {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.trigger-buy {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.25);
}

.trigger-wait {
  background: rgba(59, 130, 246, 0.12);
  border-color: rgba(59, 130, 246, 0.2);
}

.trigger-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
}

.trigger-buy .trigger-icon {
  background: rgba(239, 68, 68, 0.25);
  color: #F87171;
}

.trigger-wait .trigger-icon {
  background: rgba(59, 130, 246, 0.25);
  color: #60A5FA;
}

.trigger-icon svg {
  width: 18px;
  height: 18px;
}

.trigger-text {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.1px;
}

.trigger-buy .trigger-text {
  color: #FCA5A5;
}

.trigger-wait .trigger-text {
  color: #93C5FD;
}

.trigger-remaining {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.card-footer {
  display: flex;
  align-items: center;
  padding-top: 4px;
}

.footer-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.footer-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.footer-value {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.2px;
}

.value-green {
  color: #34D399;
}

.value-blue {
  color: #60A5FA;
}

.value-red {
  color: #F87171;
}

.footer-divider {
  width: 1px;
  height: 28px;
  background: rgba(255, 255, 255, 0.1);
}
</style>
