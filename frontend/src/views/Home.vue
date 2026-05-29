<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1>SSHDB</h1>
          <p>
            A specialized database for symbiotic nitrogen fixation (SNF) protein homologs across species. It integrates sequence and structure-based homology
            search results from more than 300 organisms, providing sequence similarity, structural similarity, sequence alignment, and structural alignment information.
            SSHDB aims to support evolutionary analysis and engineering research of SNF in non-leguminous crops.
          </p>

          <div class="search-box">
            <el-select
              v-model="searchType"
              class="search-select"
              placeholder="Gene"
              size="large"
            >
              <el-option label="Gene" value="gene" />
              <el-option label="Organism" value="organism" />
            </el-select>

            <el-input
              v-model="keyword"
              class="search-input"
              size="large"
              placeholder="Search by gene or organism"
              clearable
              @keyup.enter="handleSearch"
            />

            <el-button
              class="search-button"
              plain
              type="primary"
              size="middle"
              @click="handleSearch"
            >
              Search
            </el-button>
          </div>

          <div class="search-example">
            eg. ACP, NIN, Lotus japonicus, Glycine max
          </div>
        </div>

        <!-- Statistics moved to original image position -->
        <div class="hero-stats" aria-label="Database statistics">
          <div class="stat-row stat-row-top">
            <article
              v-for="item in topStatistics"
              :key="item.label"
              class="stat-card"
            >
              <div class="stat-image-wrap">
                <img class="stat-image" :src="item.image" :alt="item.label" />
              </div>
              <div>
                <p class="stat-label">{{ item.label }}</p>
                <strong>{{ item.value }}</strong>
                <p class="stat-unit">{{ item.unit }}</p>
              </div>
            </article>
          </div>

          <div class="stat-row stat-row-bottom">
            <article
              v-for="item in bottomStatistics"
              :key="item.label"
              class="stat-card"
            >
              <div class="stat-image-wrap">
                <img class="stat-image" :src="item.image" :alt="item.label" />
              </div>
              <div>
                <p class="stat-label">{{ item.label }}</p>
                <strong>{{ item.value }}</strong>
                <p class="stat-unit">{{ item.unit }}</p>
              </div>
            </article>
          </div>
        </div>
      </div>
    </section>

    <main class="main-content">
      <!-- Representative Species 1 -->
      <section class="panel-section">
        <div class="section-header">
          <h2>Representative Poaceae Species</h2>
          <div class="carousel-controls">
            <button @click="scrollSpecies('left', 'speciesTrack1')" aria-label="Scroll left">‹</button>
            <button @click="scrollSpecies('right', 'speciesTrack1')" aria-label="Scroll right">›</button>
          </div>
        </div>

        <div ref="speciesTrack1" class="species-track">
          <article
            v-for="species in speciesList1"
            :key="species.scientificName"
            class="species-card"
          >
            <img :src="species.image" :alt="species.scientificName" />
            <div>
              <h3>{{ species.scientificName }}</h3>
              <p>{{ species.commonName }}</p>
            </div>
          </article>
        </div>
      </section>

      <!-- Representative Species 2 -->
      <section class="panel-section">
        <div class="section-header">
          <h2>Representative Fabaceae Species</h2>
          <div class="carousel-controls">
            <button @click="scrollSpecies('left', 'speciesTrack2')" aria-label="Scroll left">‹</button>
            <button @click="scrollSpecies('right', 'speciesTrack2')" aria-label="Scroll right">›</button>
          </div>
        </div>

        <div ref="speciesTrack2" class="species-track">
          <article
            v-for="species in speciesList2"
            :key="species.scientificName"
            class="species-card"
          >
            <img :src="species.image" :alt="species.scientificName" />
            <div>
              <h3>{{ species.scientificName }}</h3>
              <p>{{ species.commonName }}</p>
            </div>
          </article>
        </div>
      </section>

      <!-- Explore SSHDB -->
      <section class="panel-section">
        <div class="section-header">
          <h2>Explore SSHDB</h2>
        </div>

        <div class="feature-grid">
          <article
            v-for="feature in features"
            :key="feature.title"
            class="feature-card"
          >
            <div class="feature-image-wrap">
              <img class="feature-image" :src="feature.image" :alt="feature.title" />
            </div>

            <div>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
            </div>
          </article>
        </div>
      </section>

      <!-- Featured Examples -->
      <section class="panel-section">
        <div class="section-header">
          <h2>Featured Examples</h2>
        </div>

        <div class="example-grid">
          <article
            v-for="(example, index) in examples"
            :key="example.title"
            class="example-card"
          >
            <el-image
              class="example-image"
              :src="example.image"
              :alt="example.title"
              :preview-src-list="examplePreviewImages"
              :initial-index="index"
              fit="contain"
              preview-teleported
              hide-on-click-modal
            />
            <h3>{{ example.title }}</h3>
          </article>
          <p class="example-copyright">&copy; 2025 SSHDB. All rights reserved.</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const keyword = ref('')
const searchType = ref('gene')
const speciesTrack1 = ref(null)
const speciesTrack2 = ref(null)

const topStatistics = [
  {
    label: 'Organisms',
    value: '279',
    unit: 'species',
    image: '/image/1.png'
  },
  {
    label: 'Taxonomic Families',
    value: '66',
    unit: 'families',
    image: '/image/17.png'
  },
  {
    label: 'SNF-related Genes',
    value: '248',
    unit: 'genes',
    image: '/image/2.png'
  }
]

const bottomStatistics = [
  {
    label: 'Remote Homologs ',
    value: '1,128,711',
    unit: '< 30% identity',
    image: '/image/13.png'
  },
  {
    label: 'Intermediate Homologs',
    value: '826,970',
    unit: '30% - 50% identity',
    image: '/image/14.png'
  },
  {
    label: 'Close Homologs ',
    value: '709,144',
    unit: '> 50% identity',
    image: '/image/15.png'
  }
]

const speciesList1 = [
  {
    scientificName: 'Oryza sativa',
    commonName: 'Rice',
    image: '/image/species/oryza-sativa.jpg'
  },
  {
    scientificName: 'Zea mays',
    commonName: 'Maize',
    image: '/image/species/zea-mays.jpg'
  },
  {
    scientificName: 'Triticum aestivum',
    commonName: 'Bread wheat',
    image: '/image/species/triticum-aestivum.jpg'
  },
  {
    scientificName: 'Hordeum vulgare',
    commonName: 'Barley',
    image: '/image/species/hordeum-vulgare.jpg'
  },
  {
    scientificName: 'Sorghum bicolor',
    commonName: 'Sorghum',
    image: '/image/species/sorghum-bicolor.jpg'
  },
  {
    scientificName: 'Setaria italica',
    commonName: 'Foxtail millet',
    image: '/image/species/setaria-italica.jpg'
  },
  {
    scientificName: 'Brachypodium distachyon',
    commonName: 'Purple false brome',
    image: '/image/species/brachypodium-distachyon.jpg'
  },
  {
    scientificName: 'Panicum virgatum',
    commonName: 'Switchgrass',
    image: '/image/species/panicum-virgatum.jpg'
  },
  {
    scientificName: 'Eragrostis tef',
    commonName: 'Teff',
    image: '/image/species/eragrostis-tef.jpg'
  },
  {
    scientificName: 'Eleusine coracana',
    commonName: 'Finger millet',
    image: '/image/species/eleusine-coracana.jpg'
  }
]

const speciesList2 = [
  {
    scientificName: 'Glycine max',
    commonName: 'Soybean',
    image: '/image/species/glycine-max.jpg'
  },
  {
    scientificName: 'Arachis hypogaea',
    commonName: 'Peanut',
    image: '/image/species/arachis-hypogaea.jpg'
  },
  {
    scientificName: 'Cicer arietinum',
    commonName: 'Chickpea',
    image: '/image/species/cicer-arietinum.jpg'
  },
  {
    scientificName: 'Pisum sativum',
    commonName: 'Pea',
    image: '/image/species/pisum-sativum.jpg'
  },
  {
    scientificName: 'Phaseolus vulgaris',
    commonName: 'Common bean',
    image: '/image/species/phaseolus-vulgaris.jpg'
  },
  {
    scientificName: 'Medicago truncatula',
    commonName: 'Barrel medic',
    image: '/image/species/medicago-truncatula.jpg'
  },
  {
    scientificName: 'Lotus japonicus',
    commonName: 'Japanese trefoil',
    image: '/image/species/lotus-japonicus.jpg'
  },
  {
    scientificName: 'Vigna radiata',
    commonName: 'Mung bean',
    image: '/image/species/vigna-radiata.jpg'
  },
  {
    scientificName: 'Vigna angularis',
    commonName: 'Adzuki bean',
    image: '/image/species/vigna-angularis.jpg'
  },
  {
    scientificName: 'Vigna unguiculata',
    commonName: 'Cowpea',
    image: '/image/species/vigna-unguiculata.jpg'
  },
  {
    scientificName: 'Cajanus cajan',
    commonName: 'Pigeon pea',
    image: '/image/species/cajanus-cajan.jpg'
  }
]

const features = [
  {
    title: 'Sequence Similarity',
    description: 'Explore proteins with similar sequences across species.',
    image: '/image/5.png'
  },
  {
    title: 'Structural Similarity',
    description: 'Explore proteins with similar structures across species.',
    image: '/image/6.png'
  },
  {
    title: 'Sequence Alignment',
    description: 'View and download multiple sequence alignments.',
    image: '/image/7.png'
  },
  {
    title: 'Structural Alignment',
    description: 'Visualize and analyze structural alignments.',
    image: '/image/8.png'
  }
]

const examples = [
  {
    title: 'Sequence Alignment Example',
    image: '/image/examples/seq-align.jpg'
  },
  {
    title: 'Structural Alignment Example',
    image: '/image/examples/structure-alignment.png'
  },
]

const examplePreviewImages = examples.map(example => example.image)

function handleSearch() {
  const query = keyword.value.trim()

  if (!query) {
    ElMessage.warning('Please input keyword')
    return
  }

  router.push({
    path: '/gene-info',
    query: {
      from: 'home',
      type: searchType.value,
      keyword: query
    }
  })
}

function scrollSpecies(direction, trackName) {
  const track = trackName === 'speciesTrack1' ? speciesTrack1.value : speciesTrack2.value

  if (!track) return

  const distance = direction === 'left' ? -320 : 320

  track.scrollBy({
    left: distance,
    behavior: 'smooth'
  })
}
</script>

<style scoped>
:root {
  --primary: #0b3c75;
  --primary-dark: #082a52;
  --text-main: #10213d;
  --text-muted: #52627a;
  --line: #dfe8f4;
  --background: #f6fbff;
  --card: #ffffff;
  --shadow: 0 8px 24px rgba(20, 62, 112, 0.09);
}

* {
  box-sizing: border-box;
}

.home-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f7fbff 0%, #ffffff 60%);
  color: var(--text-main);
  font-family: Inter, "Helvetica Neue", Arial, sans-serif;
}

/* Header */
.site-header {
  position: sticky;
  top: 0;
  z-index: 20;
  height: 64px;
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(14px);
}

.header-inner {
  max-width: 1480px;
  height: 100%;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-logo {
  width: 38px;
  height: 38px;
  object-fit: contain;
}

.nav-menu {
  border-bottom: none;
  background: transparent;
  display: flex;
  justify-content: center;
  min-width: 620px;
}

.nav-menu :deep(.el-menu-item) {
  height: 64px;
  padding: 0 28px;
  color: #10213d;
  font-size: 15px;
  font-weight: 600;
  border-bottom: none;
}

.nav-menu :deep(.el-menu-item:hover) {
  color: #075bd8;
  background: transparent;
}

.nav-menu :deep(.el-menu-item.is-active) {
  color: #075bd8;
  border-bottom: 3px solid #075bd8;
}

.nav-menu.el-menu--horizontal {
  border-bottom: none;
}

/* Hero */
.hero-section {
  width: 100%;
  padding: 0 10px;
  border-bottom: none;
  box-sizing: border-box;
}

.hero-content {
  max-width: 1480px;
  min-height: 430px;
  margin: 0 auto;
  padding: 10px 12px;
  display: grid;
  grid-template-columns: minmax(460px, 0.9fr) minmax(620px, 1.1fr);
  align-items: center;
  gap: 40px;
  box-sizing: border-box;
  border-radius: 0 0 14px 14px;
  background:
    radial-gradient(circle at 72% 40%, rgba(53, 164, 215, 0.2), transparent 24%),
    linear-gradient(90deg, #f8fcff 0%, #eef9ff 100%);
}

.hero-text h1 {
  max-width: 720px;
  margin: 0 0 18px;
  color: #0b4bb8;
  font-size: clamp(34px, 4vw, 46px);
  line-height: 1.1;
  letter-spacing: -0.04em;
}

.hero-text p {
  max-width: 720px;
  margin: 0;
  color: #1c2e4a;
  font-size: 16px;
  line-height: 1.75;
}

/* Search */
.search-box {
  width: min(760px, 100%);
  margin-top: 24px;
  padding: 10px 12px;
  display: grid;
  grid-template-columns: 120px 1fr 140px;
  gap: 10px;
  align-items: center;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 6px;
  box-shadow: 0 10px 25px rgba(16, 69, 129, 0.12);
}

.search-select,
.search-input,
.search-button {
  height: 46px;
}

.search-box :deep(.el-select__wrapper),
.search-box :deep(.el-input__wrapper),
.search-button {
  height: 46px;
  min-height: 46px;
  border-radius: 5px;
  box-sizing: border-box;
}

.search-box :deep(.el-select__wrapper),
.search-box :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #d7e2ef inset;
}

.search-box :deep(.el-select__wrapper:hover),
.search-box :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #9ec7ef inset;
}

.search-box :deep(.el-select__wrapper.is-focused),
.search-box :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #6aa9e9 inset;
}

.search-button {
  width: 100%;
  border: none;
  background: #8fc8f2;
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
}

.search-button:hover,
.search-button:focus {
  background: #76b8ea;
  color: #ffffff;
}

.search-button:active {
  background: #5fa8df;
}

.search-example {
  margin-top: 20px;
  color: #85b5d7;
  font-size: 14px;
  font-style: italic;
}

/* Statistics：第一行 2 个，第二行 3 个 */
.hero-stats {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  row-gap: 35px;
  column-gap: 44px;
  align-self: center;
}

/* 取消原来每一行自己的 grid */
.stat-row {
  display: contents;
}

/* 第一行 */
.stat-row-top .stat-card:nth-child(1) {
  grid-column: 1;
  grid-row: 1;
}

.stat-row-top .stat-card:nth-child(2) {
  grid-column: 2;
  grid-row: 1;
}
.stat-row-top .stat-card:nth-child(3) {
  grid-column: 3;
  grid-row: 1;
}
/* 第二行 */
.stat-row-bottom .stat-card:nth-child(1) {
  grid-column: 1;
  grid-row: 2;
}

.stat-row-bottom .stat-card:nth-child(2) {
  grid-column: 2;
  grid-row: 2;
}

.stat-row-bottom .stat-card:nth-child(3) {
  grid-column: 3;
  grid-row: 2;
}

.stat-card {
  min-width: 0;
  min-height: 132px;
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: var(--shadow);
}

.stat-image-wrap {
  flex: 0 0 64px;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #f2f8ff;
  border-radius: 50%;
}

.stat-image {
  width: 64px;
  height: 64px;
  object-fit: cover;
  display: block;
  border-radius: 50%;
}

.stat-card > div:last-child {
  min-width: 0;
}

.stat-label {
  margin: 0 0 6px;
  color: #2e5491;
  font-size: 15px;
  font-weight: bold;
  white-space: nowrap;
}

.stat-card strong {
  display: block;
  color: #ef9bd0;
  font-size: 30px;
  letter-spacing: -0.03em;
  white-space: nowrap;
  font-weight: bold;
}

.stat-unit {
  margin: 4px 0 0;
  color: #5f89ad;
  font-size: 13px;
  font-weight: bold;
}

/* Main content */
.main-content {
  max-width: 1480px;
  margin: 0 auto;
  padding: 20px 10px 24px;
}

.panel-section {
  margin-bottom: 16px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: var(--shadow);
}

.section-header {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-header h2 {
  margin: 0;
  color: #063da1;
  font-size: 18px;
  letter-spacing: -0.02em;
}

/* Carousel controls */
.carousel-controls {
  display: flex;
  gap: 14px;
  align-items: center;
}

.carousel-controls button {
  width: auto;
  height: auto;
  padding: 0 4px;
  border: none;
  border-radius: 0;
  background: transparent;
  color: #95c3f0;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
}

.carousel-controls button:hover,
.carousel-controls button:focus {
  color: #acd6f4;
  background: transparent;
  outline: none;
}

/* Species */
.species-track {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 210px;
  gap: 10px;
  overflow-x: auto;
  padding: 2px 2px 10px;
  scroll-snap-type: x proximity;
  scrollbar-width: thin;
  scrollbar-color: #d8ecfb #f3faff;
}

.species-track::-webkit-scrollbar {
  height: 8px;
}

.species-track::-webkit-scrollbar-track {
  background: #f3faff !important;
  border-radius: 999px;
}

.species-track::-webkit-scrollbar-thumb {
  background-color: #d8ecfb !important;
  border-radius: 999px;
  border: 2px solid #f3faff;
}

.species-track::-webkit-scrollbar-thumb:hover {
  background-color: #c7e5f8 !important;
}

.species-card {
  display: grid;
  grid-template-columns: 88px 1fr;
  gap: 14px;
  min-height: 118px;
  padding: 10px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 10px;
  scroll-snap-align: start;
  align-items: center;
}

.species-card > div {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 98px;
}

.species-card img {
  width: 88px;
  height: 98px;
  object-fit: cover;
  border-radius: 8px;
  background: #e9f2ee;
}

.species-card h3 {
  margin: 4px 0 6px;
  color: #0750a8;
  font-size: 13px;
  font-style: italic;
  line-height: 1.25;
}

.species-card p {
  margin: 0 0 10px;
  color: #52627a;
  font-size: 12px;
}

.species-card strong {
  display: block;
  color: #071b3f;
  font-size: 16px;
}

.species-card span {
  color: #52627a;
  font-size: 12px;
}

/* Features */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 10px;
}

.feature-card {
  min-height: 96px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border-right: 1px solid var(--line);
}

.feature-card:last-child {
  border-right: none;
}

.feature-image-wrap {
  flex: 0 0 50px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: white;
  border: 1px solid #cbe1f4;
  border-radius: 14px;
  box-shadow: 0 8px 18px rgba(20, 62, 112, 0.08);
  transform: rotate(45deg);
}

.feature-image {
  width: 76%;
  height: 76%;
  object-fit: contain;
  display: block;
  transform: rotate(-45deg);
}

.feature-card h3 {
  margin: 0 0 6px;
  color: #0750a8;
  font-size: 15px;
}

.feature-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.35;
}

/* Examples */
.example-grid {
  width: 100%;
  margin: 0;
  display: grid;
  grid-template-columns: minmax(220px, 360px) minmax(220px, 360px) 1fr;
  gap: clamp(16px, 2.6vw, 40px);
  align-items: end;
}

.example-card {
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  text-align: left;
}

.example-image {
  width: 100%;
  height: clamp(180px, 13vw, 220px);
  display: block;
  margin-bottom: 12px;
  padding: 12px;
  border: 1px solid #e4eef8;
  border-radius: 5px;
  background: #fff;
  cursor: zoom-in;
}

.example-image :deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.example-card h3 {
  margin: 0;
  color: #071b3f;
  font-size: 15px;
  line-height: 1.4;
  font-weight: 700;
}

.example-copyright {
  justify-self: end;
  margin: 0;
  color: #52627a;
  font-size: 14px;
  line-height: 1.4;
  white-space: nowrap;
}

/* Medium screen */
@media (max-width: 1180px) {
  .hero-content {
    grid-template-columns: 1fr;
  }

  .hero-stats {
    max-width: 100%;
  }

  .stat-row-top {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .stat-row-bottom {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .feature-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .feature-card {
    border-right: none;
    border-bottom: 1px solid var(--line);
  }

  .feature-card:nth-child(3),
  .feature-card:nth-child(4) {
    border-bottom: none;
  }

  .example-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 18px;
  }

  .example-copyright {
    grid-column: 1 / -1;
    justify-self: end;
  }

  .example-image {
    height: clamp(170px, 26vw, 220px);
  }
}

/* Small screen */
@media (max-width: 820px) {
  .header-inner {
    padding: 0 18px;
  }

  .nav-menu {
    gap: 16px;
    overflow-x: auto;
  }

  .hero-section {
    padding: 0 18px;
  }

  .hero-content,
  .main-content {
    padding-left: 18px;
    padding-right: 18px;
  }

  .hero-content {
    gap: 26px;
  }

  .search-box {
    grid-template-columns: 1fr;
  }

  .stat-row-top,
  .stat-row-bottom {
    grid-template-columns: 1fr;
  }

  .stat-card {
    min-height: 120px;
  }

  .stat-card strong {
    white-space: normal;
  }

  .feature-grid,
  .example-grid {
    grid-template-columns: 1fr;
  }

  .example-card {
    padding: 0;
  }

  .example-image {
    height: clamp(150px, 48vw, 210px);
    padding: 8px;
  }

  .example-copyright {
    grid-column: 1 / -1;
    justify-self: start;
    font-size: 12px;
  }

  .feature-card {
    border-right: none;
    border-bottom: 1px solid var(--line);
  }

  .feature-card:last-child {
    border-bottom: none;
  }

  .example-copyright {
    white-space: normal;
  }
}
</style>
