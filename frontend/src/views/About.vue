<template>
  <div class="about-page">
    <div class="page-container">

      <!-- Research Group -->
      <section class="panel-card group-card">
        <div class="panel-tag">Research Group</div>

      <div class="group-layout">
        <div class="group-intro">
          <div class="large-icon">👥</div>
          <p>
            We are a research group in the College of Life Sciences dedicated to integrating
            biological data resources and computational tools for plant science research. Our team
            combines expertise in genomics, bioinformatics, and molecular biology to facilitate
            data-driven discoveries in plant biology.
          </p>
        </div>

        <div class="group-info">
          <div class="info-line">
            <span class="line-icon">🏛</span>
            <strong>Affiliation:</strong>
            <span>College of Life Sciences</span>
          </div>
          <div class="info-line">
            <span class="line-icon">🧪</span>
            <strong>Laboratory:</strong>
            <span>Plant Bioinformatics Lab</span>
          </div>
          <div class="info-line">
            <span class="line-icon">🌿</span>
            <strong>Research Areas:</strong>
            <span>Plant genomics, protein analysis, bioinformatics</span>
          </div>
          <div class="info-line">
            <span class="line-icon">✉</span>
            <strong>Email:</strong>
            <a href="mailto:contact@plantgenedb.org">contact@plantgenedb.org</a>
          </div>
          <div class="info-line">
            <span class="line-icon">🌐</span>
            <strong>Website:</strong>
            <a href="https://www.plantgenedb.org" target="_blank">www.plantgenedb.org</a>
          </div>
        </div>
      </div>
      </section>

      <!-- Bottom Row -->
      <section class="bottom-grid">
        <div class="panel-card bottom-card">
          <div class="panel-tag">Data Resources</div>

        <div class="bottom-content">
          <div class="large-icon blue-text">▱</div>
          <p>
            Our platform integrates multiple data resources including genome assemblies, gene
            annotations, protein sequences, functional annotation, expression-related resources,
            and structure analysis data, providing comprehensive support for plant genomics research.
          </p>
        </div>
      </div>

        <div class="panel-card bottom-card">
          <div class="panel-tag">Citation</div>

        <div class="citation-layout">
          <div class="quote-box">
            <span class="quote-mark">“</span>
            <p>
              PlantGenomics Database: a comprehensive resource for plant gene and protein information
              and analysis. <em>Plant Genomics Database</em>, 2024.
            </p>
          </div>

          <button class="outline-btn" @click="copyCitation">
            Copy Citation
          </button>
        </div>
      </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'About',

  methods: {
    copyCitation() {
      const citation =
        'PlantGenomics Database: a comprehensive resource for plant gene and protein information and analysis. Plant Genomics Database, 2024.'

      if (navigator.clipboard) {
        navigator.clipboard.writeText(citation)
      }

      this.$message?.success?.('Citation copied.')
    }
  }
}
</script>

<style scoped>
.about-page {
  width: 100%;
  min-height: 100vh;
  padding: 24px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  background: #f4f8fb;
  color: #303746;
  font-family: "Arial", "Helvetica", sans-serif;
}

.page-container {
  width: 100%;
  max-width: 1600px;
}

.panel-card,
.info-card {
  position: relative;
  width: 100%;
  background: #ffffff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  box-sizing: border-box;
}

.panel-tag {
  position: absolute;
  top: 16px;
  left: -10px;
  background: #b2e6f5;
  color: #ffffff;
  font-size: 18px;
  line-height: 1;
  padding: 12px 22px;
  border-radius: 0 4px 4px 0;
  font-weight: 600;
  z-index: 2;
}

.panel-tag::before {
  content: "";
  position: absolute;
  left: 0;
  bottom: -10px;
  width: 0;
  height: 0;
  border-top: 10px solid #a1d0dd;
  border-left: 10px solid transparent;
}

.hero-card {
  padding: 52px 64px 48px;
  margin-bottom: 18px;
}

.hero-inner {
  display: grid;
  grid-template-columns: 43% 57%;
  align-items: center;
  gap: 36px;
}

.hero-illustration {
  min-height: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plant-scene {
  position: relative;
  width: 430px;
  height: 210px;
  overflow: hidden;
}

.dna {
  position: absolute;
  right: 90px;
  top: 34px;
  color: #7bb4da;
  font-size: 105px;
  transform: rotate(8deg);
  opacity: 0.45;
}

.plant {
  position: absolute;
  left: 165px;
  bottom: 35px;
  width: 100px;
  height: 150px;
}

.stem {
  position: absolute;
  left: 49px;
  bottom: 18px;
  width: 5px;
  height: 116px;
  background: linear-gradient(#6fbd4d, #3f8d35);
  border-radius: 4px;
}

.leaf {
  position: absolute;
  width: 64px;
  height: 34px;
  background: linear-gradient(135deg, #8fd465, #4f9c3b);
  border-radius: 70% 0 70% 0;
}

.leaf-left {
  left: -4px;
  top: 48px;
  transform: rotate(25deg);
}

.leaf-right {
  right: -10px;
  top: 28px;
  transform: rotate(-35deg) scaleX(-1);
}

.soil {
  position: absolute;
  left: 8px;
  bottom: 5px;
  width: 86px;
  height: 18px;
  background: #8b6a46;
  border-radius: 50%;
}

.circle {
  position: absolute;
  border: 2px dashed #c7dff0;
  border-radius: 50%;
}

.circle-one {
  width: 130px;
  height: 130px;
  left: 230px;
  top: 10px;
}

.circle-two {
  width: 95px;
  height: 95px;
  left: 15px;
  top: 60px;
}

.hero-content h1 {
  margin: 0 0 18px;
  color: #123f79;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: 0.2px;
}

.hero-content p {
  margin: 0 0 12px;
  color: #3f4856;
  font-size: 15px;
  line-height: 1.8;
}

.info-grid.three-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  margin-bottom: 18px;
}

.info-card {
  min-height: 126px;
  padding: 28px 34px;
  display: grid;
  grid-template-columns: 78px 1fr;
  align-items: center;
  gap: 20px;
}

.icon-circle {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.icon-circle.blue {
  color: #2475d1;
  background: #edf5ff;
}

.icon-circle.green {
  color: #3d9b43;
  background: #eef9ee;
}

.icon-circle.purple {
  color: #8d57d6;
  background: #f5efff;
}

.icon-circle.orange {
  color: #ef7d43;
  background: #fff3eb;
}

.info-card h3,
.overview-item h3 {
  margin: 0 0 8px;
  color: #164982;
  font-size: 16px;
  font-weight: 800;
}

.info-card p,
.overview-item p {
  margin: 0;
  color: #3f4856;
  font-size: 14px;
  line-height: 1.65;
}

.overview-card {
  padding: 58px 46px 34px;
  margin-bottom: 18px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
}

.overview-item {
  min-height: 100px;
  display: grid;
  grid-template-columns: 76px 1fr;
  gap: 18px;
  align-items: center;
  padding: 0 28px;
  border-right: 1px solid #e6edf5;
}

.overview-item:last-child {
  border-right: none;
}

.group-card {
  padding: 58px 54px 36px;
  margin-bottom: 18px;
}

.group-layout {
  display: grid;
  grid-template-columns: 1fr 1.35fr;
  gap: 44px;
  align-items: center;
  margin-top: 18px;
}

.group-intro {
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 22px;
  align-items: center;
  padding-right: 36px;
  border-right: 1px solid #e6edf5;
}

.large-icon {
  font-size: 48px;
  color: #347fd4;
  text-align: center;
}

.group-intro p {
  margin: 0;
  color: #3f4856;
  font-size: 15px;
  line-height: 1.75;
}

.group-info {
  display: grid;
  gap: 13px;
}

.info-line {
  display: grid;
  grid-template-columns: 28px 130px 1fr;
  align-items: center;
  color: #3f4856;
  font-size: 14px;
}

.info-line strong {
  color: #303746;
}

.info-line a {
  color: #2d7bd8;
  text-decoration: none;
}

.line-icon {
  color: #347fd4;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1.1fr;
  gap: 18px;
}

.bottom-card {
  min-height: 128px;
  padding: 52px 38px 28px;
}

.bottom-content {
  display: grid;
  grid-template-columns: 92px 1fr;
  gap: 22px;
  align-items: center;
  margin-top: 18px;
}

.bottom-content p {
  margin: 0;
  color: #3f4856;
  font-size: 14px;
  line-height: 1.7;
}

.blue-text {
  color: #357fd5;
}

.citation-layout {
  display: grid;
  grid-template-columns: 1fr 150px;
  gap: 24px;
  align-items: center;
  margin-top: 18px;
}

.quote-box {
  display: grid;
  grid-template-columns: 42px 1fr;
  align-items: center;
  padding: 20px 24px;
  background: #f4f8fd;
  border-radius: 5px;
}

.quote-mark {
  color: #7bb8e7;
  font-size: 44px;
  font-weight: 700;
}

.quote-box p {
  margin: 0;
  color: #3f4856;
  font-size: 14px;
  line-height: 1.65;
}

.outline-btn {
  height: 36px;
  padding: 0 18px;
  color: #2c7bd6;
  background: #ffffff;
  border: 1px solid #8dbdf0;
  border-radius: 4px;
  cursor: pointer;
}

.outline-btn:hover {
  background: #edf6ff;
}

@media (max-width: 1100px) {
  .hero-inner,
  .group-layout,
  .bottom-grid {
    grid-template-columns: 1fr;
  }

  .info-grid.three-columns,
  .overview-grid {
    grid-template-columns: 1fr 1fr;
  }

  .overview-item {
    border-right: none;
    border-bottom: 1px solid #e6edf5;
    padding: 20px;
  }

  .group-intro {
    border-right: none;
    padding-right: 0;
  }
}

@media (max-width: 720px) {
  .about-page {
    padding: 16px;
  }

  .info-grid.three-columns,
  .overview-grid,
  .citation-layout {
    grid-template-columns: 1fr;
  }

  .hero-card,
  .overview-card,
  .group-card,
  .bottom-card {
    padding-left: 24px;
    padding-right: 24px;
  }
}
</style>