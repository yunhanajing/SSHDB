<template>
  <section class="visitor-panel" aria-labelledby="visitor-map-title">
    <div class="visitor-header">
      <div>
        <h2 id="visitor-map-title">Global Visitor Distribution</h2>
      </div>

      <div class="visitor-filter">
        <label class="period-label" for="visitor-period">Period</label>
        <el-select
          id="visitor-period"
          v-model="selectedRange"
          class="period-select"
          size="large"
          aria-label="Period"
        >
          <el-option label="Last 30 days" value="30days" />
          <el-option label="This year" value="year" />
          <el-option label="All time" value="all" />
        </el-select>
      </div>
    </div>

    <div class="visitor-stats" aria-label="Visitor statistics">
      <article>
        <span>Page views</span>
        <strong>{{ formatNumber(summary.pageViews) }}</strong>
        <small>{{ rangeLabel }}</small>
      </article>
      <article>
        <span>Unique visitors</span>
        <strong>{{ formatNumber(summary.uniqueVisitors) }}</strong>
        <small>Estimated visitors</small>
      </article>
      <article>
        <span>Countries &amp; regions</span>
        <strong>{{ summary.countries }}</strong>
        <small>Worldwide reach</small>
      </article>
    </div>

    <div class="visitor-content">
      <div class="map-column">
        <div
          ref="mapElement"
          class="visitor-map"
          role="img"
          :aria-label="mapAriaLabel"
        ></div>

        <div v-if="mapLoading || statsLoading" class="map-state">
          Loading visitor data…
        </div>
        <div v-else-if="mapError || statsError" class="map-state map-state-error">
          {{ mapError ? 'The visitor map could not be loaded.' : statsError }}
        </div>

        <div class="map-legend" aria-label="Map color scale: fewer visits to more visits">
          <span class="legend-title">Visits</span>
          <span class="legend-label">Fewer</span>
          <span class="legend-colors" aria-hidden="true">
            <i></i><i></i><i></i><i></i><i></i>
          </span>
          <span class="legend-label">More</span>
        </div>
      </div>

      <aside class="visitor-ranking" aria-label="Visitor ranking">
        <div class="ranking-heading">
          <div>
            <p>Top locations</p>
            <span>&nbsp;By page views</span>
          </div>
          <strong>{{ rangeShortLabel }}</strong>
        </div>

        <ol>
          <li v-for="(country, index) in topCountries" :key="country.name">
            <button type="button" @click="selectCountry(country)">
              <span class="rank-number">{{ String(index + 1).padStart(2, '0') }}</span>
              <span class="rank-country">
                <span>{{ country.name }}</span>
                <i :style="{ width: `${country.share}%` }"></i>
              </span>
              <strong>{{ formatCompactNumber(country.value) }}</strong>
            </button>
          </li>
        </ol>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts/core'
import { MapChart } from 'echarts/charts'
import { GeoComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import request from '@/utils/request'

echarts.use([MapChart, GeoComponent, TooltipComponent, VisualMapComponent, CanvasRenderer])

const mapElement = ref(null)
const mapLoading = ref(true)
const mapError = ref(false)
const statsLoading = ref(true)
const statsError = ref('')
const selectedRange = ref('year')
const selectedCountry = ref(null)
const visitorStats = ref({
  summary: {
    pageViews: 0,
    uniqueVisitors: 0,
    countries: 0
  },
  dateRange: {
    label: '—',
    shortLabel: '—'
  },
  locations: []
})

let mapChart = null
let resizeObserver = null
let worldMapLoaded = false

const countryData = computed(() => {
  return visitorStats.value.locations.map(location => ({
    name: location.name,
    value: Number(location.pageViews) || 0
  }))
})

const summary = computed(() => visitorStats.value.summary)

const topCountries = computed(() => {
  const sortedCountries = [...countryData.value].sort((a, b) => b.value - a.value)
  const maximum = sortedCountries[0]?.value || 1
  return sortedCountries.slice(0, 10).map(country => ({
    ...country,
    share: Math.max(7, Math.round((country.value / maximum) * 100))
  }))
})

const rangeLabel = computed(() => visitorStats.value.dateRange.label)
const rangeShortLabel = computed(() => visitorStats.value.dateRange.shortLabel)
const mapAriaLabel = computed(
  () => `World map showing ${formatNumber(summary.value.pageViews)} page views from ${summary.value.countries} countries and regions.`
)

const numberFormatter = new Intl.NumberFormat('en-US')
const compactFormatter = new Intl.NumberFormat('en-US', {
  notation: 'compact',
  maximumFractionDigits: 1
})

let statsRequestSerial = 0

function formatNumber(value) {
  return numberFormatter.format(value)
}

function formatCompactNumber(value) {
  return compactFormatter.format(value)
}

async function loadVisitorStats() {
  const requestSerial = ++statsRequestSerial
  statsLoading.value = true
  statsError.value = ''

  try {
    const response = await request.get('/tools/visitors/stats/', {
      params: { period: selectedRange.value },
      timeout: 10000
    })
    const payload = response.data?.data

    if (!response.data?.success || !payload) {
      throw new Error(response.data?.error || 'Invalid visitor statistics response.')
    }
    if (requestSerial !== statsRequestSerial) return

    visitorStats.value = {
      summary: {
        pageViews: Number(payload.summary?.pageViews) || 0,
        uniqueVisitors: Number(payload.summary?.uniqueVisitors) || 0,
        countries: Number(payload.summary?.countries) || 0
      },
      dateRange: {
        label: payload.dateRange?.label || '—',
        shortLabel: payload.dateRange?.shortLabel || '—'
      },
      locations: Array.isArray(payload.locations)
        ? payload.locations
            .filter(location => location?.name)
            .map(location => ({
              countryCode: location.countryCode || '',
              name: location.name,
              pageViews: Number(location.pageViews) || 0,
              uniqueVisitors: Number(location.uniqueVisitors) || 0
            }))
        : []
    }

    selectedCountry.value = null
    await nextTick()
    renderMap()
  } catch (error) {
    if (requestSerial !== statsRequestSerial) return
    console.error(error)
    statsError.value = 'Visitor statistics are temporarily unavailable.'
  } finally {
    if (requestSerial === statsRequestSerial) {
      statsLoading.value = false
    }
  }
}

function buildMapOption() {
  const maxValue = Math.max(...countryData.value.map(country => country.value), 1)

  return {
    animationDurationUpdate: 420,
    tooltip: {
      trigger: 'item',
      borderWidth: 0,
      padding: [10, 12],
      backgroundColor: 'rgba(7, 47, 96, 0.94)',
      textStyle: { color: '#ffffff', fontSize: 13 },
      formatter(params) {
        const value = Number(params.value)
        if (!Number.isFinite(value)) {
          return `<strong>${params.name || 'Unknown'}</strong><br/>No recorded visits`
        }
        return `<strong>${params.name}</strong><br/>${formatNumber(value)} visits`
      }
    },
    visualMap: {
      min: 0,
      max: maxValue,
      show: false,
      inRange: {
        color: ['#e9f4fb', '#c7e6f7', '#87caeb', '#3e9ed4', '#0d5da6']
      }
    },
    series: [
      {
        name: 'Visits',
        type: 'map',
        map: 'world',
        roam: true,
        scaleLimit: { min: 1, max: 6 },
        layoutCenter: ['50%', '50%'],
        layoutSize: '135%',
        selectedMode: false,
        itemStyle: {
          areaColor: '#f1f6fa',
          borderColor: '#b8d4e5',
          borderWidth: 0.7
        },
        emphasis: {
          label: { show: false },
          itemStyle: {
            areaColor: '#f2a8d3',
            borderColor: '#ffffff',
            borderWidth: 1
          }
        },
        data: countryData.value
      }
    ]
  }
}

function renderMap() {
  if (!mapChart || !worldMapLoaded) return
  mapChart.setOption(buildMapOption(), true)
}

function selectCountry(country) {
  selectedCountry.value = country
  if (!mapChart) return

  const dataIndex = countryData.value.findIndex(item => item.name === country.name)
  if (dataIndex < 0) return

  mapChart.dispatchAction({ type: 'downplay', seriesIndex: 0 })
  mapChart.dispatchAction({ type: 'highlight', seriesIndex: 0, dataIndex })
  mapChart.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex })
}

async function initialiseMap() {
  try {
    const response = await fetch('/maps/world.json')
    if (!response.ok) throw new Error(`World map request failed: ${response.status}`)

    const worldGeoJson = await response.json()
    echarts.registerMap('world', worldGeoJson)
    worldMapLoaded = true

    await nextTick()
    if (!mapElement.value) return

    mapChart = echarts.init(mapElement.value, null, { renderer: 'canvas' })
    mapChart.on('click', params => {
      if (!Number.isFinite(Number(params.value))) return
      selectedCountry.value = { name: params.name, value: Number(params.value) }
    })
    renderMap()

    resizeObserver = new ResizeObserver(() => mapChart?.resize())
    resizeObserver.observe(mapElement.value)
  } catch (error) {
    console.error(error)
    mapError.value = true
  } finally {
    mapLoading.value = false
  }
}

watch(selectedRange, () => {
  loadVisitorStats()
})

onMounted(() => {
  initialiseMap()
  loadVisitorStats()
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  mapChart?.dispose()
  mapChart = null
})
</script>

<style scoped>
.visitor-panel {
  margin-bottom: 16px;
  padding: 22px;
  overflow: hidden;
  background:
    radial-gradient(circle at 18% 4%, rgba(144, 207, 241, 0.2), transparent 28%),
    #ffffff;
  border: 1px solid #dfe8f4;
  border-radius: 12px;
  box-shadow: none;
}

.visitor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.visitor-eyebrow {
  margin: 0 0 5px;
  color: #6fa9d0;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.visitor-header h2 {
  margin: 0;
  color: #063da1;
  font-size: 18px;
  letter-spacing: -0.02em;
}

.visitor-description {
  margin: 7px 0 0;
  color: #60748a;
  font-size: 13px;
}

.visitor-filter {
  display: flex;
  align-items: center;
  gap: 9px;
  white-space: nowrap;
}

.period-label {
  color: #0750a8;
  font-size: 15px;
  font-weight: 700;
}

.period-select {
  width: 140px;
  height: 46px;
}

.period-select :deep(.el-select__wrapper) {
  height: 46px;
  min-height: 46px;
  border-radius: 5px;
  box-shadow: 0 0 0 1px #d7e2ef inset;
}

.period-select :deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px #9ec7ef inset;
}

.period-select :deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px #6aa9e9 inset;
}

.period-select :deep(.el-select__selected-item),
.period-select :deep(.el-select__placeholder) {
  color: #606266;
  font-family: Inter, "Helvetica Neue", Arial, sans-serif;
  font-size: 14px;
}

.demo-badge {
  padding: 5px 8px;
  color: #a75788;
  background: #fff0f8;
  border: 1px solid #f4cce2;
  border-radius: 999px;
  font-weight: 700;
}

.visitor-stats {
  margin: 18px 0 10px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  border-top: 1px solid #e4edf5;
  border-bottom: 1px solid #e4edf5;
}

.visitor-stats article {
  padding: 14px 18px;
  display: grid;
  grid-template-columns: 1fr;
  border-right: 1px dashed #b9d8ef;
}

.visitor-stats article:first-child {
  padding-left: 0;
}

.visitor-stats article:last-child {
  border-right: none;
}

.visitor-stats span {
  color: #0750a8;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.35;
}

.visitor-stats small {
  color: #5f89ad;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.35;
}

.visitor-stats strong {
  margin: 3px 0 2px;
  color: #ef9bd0;
  font-size: 22px;
  font-weight: bold;
  letter-spacing: -0.03em;
  line-height: 1.1;
  white-space: nowrap;
}

.visitor-content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 410px;
  gap: 24px;
  align-items: stretch;
}

.map-column {
  position: relative;
  min-width: 0;
}

.visitor-map {
  width: 100%;
  height: 500px;
}

.map-state {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #70879d;
  background: rgba(255, 255, 255, 0.86);
  font-size: 13px;
}

.map-state-error {
  color: #b4576d;
}

.map-legend {
  position: absolute;
  bottom: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 7px;
  color: #6b8197;
  font-size: 12px;
}

.legend-title {
  margin-right: 2px;
  color: #365d7e;
  font-weight: 700;
}

.legend-label {
  white-space: nowrap;
}

.legend-colors {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.legend-colors i {
  width: 10px;
  height: 10px;
  display: block;
  border-radius: 50%;
}

.legend-colors i:nth-child(1) { background: #e9f4fb; }
.legend-colors i:nth-child(2) { background: #c7e6f7; }
.legend-colors i:nth-child(3) { background: #87caeb; }
.legend-colors i:nth-child(4) { background: #3e9ed4; }
.legend-colors i:nth-child(5) { background: #0d5da6; }

.visitor-ranking {
  padding-left: 22px;
  border-left: 1px solid #e3edf5;
}

.ranking-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.ranking-heading p {
  margin: 0 0 3px;
  color: #164b78;
  font-size: 16px;
  font-weight: 700;
}

.ranking-heading span {
  color: #8b9bab;
  font-size: 13px;
}

.ranking-heading strong {
  color: #75acd1;
  font-size: 18px;
}

.visitor-ranking ol {
  margin: 12px 0 0;
  padding: 0;
  list-style: none;
}

.visitor-ranking li + li {
  margin-top: 3px;
}

.visitor-ranking button {
  width: 100%;
  min-height: 40px;
  padding: 4px 0;
  display: grid;
  grid-template-columns: 32px minmax(0, 1fr) 54px;
  align-items: center;
  gap: 7px;
  color: #294e6c;
  background: transparent;
  border: none;
  border-radius: 6px;
  text-align: left;
  cursor: pointer;
}

.visitor-ranking button:hover,
.visitor-ranking button:focus-visible {
  background: #f3f9fd;
  outline: none;
}

.rank-number {
  color: #9aacbc;
  font-size: 13px;
}

.rank-country {
  min-width: 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: 4px;
  font-size: 14px;
}

.rank-country > span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rank-country i {
  height: 4px;
  overflow: hidden;
  background: #e9f2f8;
  border-radius: 999px;
}

.rank-country i {
  display: block;
  background: linear-gradient(90deg, #8dcced, #438fc8);
}

.visitor-ranking button > strong {
  color: #0d518c;
  font-size: 14px;
  text-align: right;
}

@media (max-width: 980px) {
  .visitor-content {
    grid-template-columns: 1fr;
  }

  .visitor-ranking {
    padding: 18px 0 0;
    border-top: 1px solid #e3edf5;
    border-left: none;
  }

  .visitor-ranking ol {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 3px 18px;
  }

}

@media (max-width: 640px) {
  .visitor-panel {
    padding: 16px;
  }

  .visitor-header {
    display: block;
  }

  .visitor-filter {
    margin-top: 14px;
    flex-wrap: wrap;
  }

  .visitor-stats {
    grid-template-columns: 1fr;
  }

  .visitor-stats article,
  .visitor-stats article:first-child {
    padding: 10px 0;
    border-right: none;
    border-bottom: 1px solid #e4edf5;
  }

  .visitor-stats article:last-child {
    border-bottom: none;
  }

  .visitor-map {
    height: 310px;
  }

  .visitor-ranking ol {
    grid-template-columns: 1fr;
  }

}
</style>
