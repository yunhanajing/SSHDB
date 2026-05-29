<template>
  <div class="page about-page">
    <!-- About Hero -->
    <section class="section-card hero-card">
      <div class="section-label">About</div>

      <div class="hero-inner">
        <div class="hero-illustration">
          <div class="plant-scene">
            <div class="dna">⌁</div>
            <div class="plant">
              <div class="stem"></div>
              <div class="leaf leaf-left"></div>
              <div class="leaf leaf-right"></div>
              <div class="soil"></div>
            </div>
            <div class="circle circle-one"></div>
            <div class="circle circle-two"></div>
          </div>
        </div>

        <div class="hero-content">
          <h1>PlantGenomics Research Group</h1>
          <p>
            Our group develops a comprehensive plant gene and protein information platform and is
            dedicated to plant genomics, comparative genomics, gene family analysis, protein function
            prediction, and bioinformatics tool development.
          </p>
          <p>
            The platform supports gene discovery, annotation, sequence analysis, structure comparison,
            and data sharing to empower plant biology research.
          </p>
        </div>
      </div>
    </section>

    <!-- Research Highlights -->
    <section class="info-grid three-columns">
      <div class="info-card">
        <div class="icon-circle green">
          <i class="iconfont">🌱</i>
        </div>
        <div>
          <h3>Our Research</h3>
          <p>
            We focus on plant genomics, comparative genomics, gene family evolution,
            transcriptomics, and functional bioinformatics.
          </p>
        </div>
      </div>

      <div class="info-card">
        <div class="icon-circle blue">
          <i class="iconfont">◎</i>
        </div>
        <div>
          <h3>Platform Mission</h3>
          <p>
            Our mission is to build an accessible, reliable and user-friendly database and analysis
            platform for plant research.
          </p>
        </div>
      </div>

      <div class="info-card">
        <div class="icon-circle purple">
          <i class="iconfont">👥</i>
        </div>
        <div>
          <h3>Who We Serve</h3>
          <p>
            We support students, bioinformaticians, molecular biologists, and plant science
            researchers worldwide.
          </p>
        </div>
      </div>
    </section>

    <!-- Platform Overview -->
    <section class="section-card overview-card">
      <div class="section-label">Platform Overview</div>

      <div class="overview-grid">
        <div class="overview-item">
          <div class="icon-circle blue">
            <i>🔍</i>
          </div>
          <div>
            <h3>Gene Search</h3>
            <p>
              Search genes by ID, keyword, or symbol across species and genome versions.
            </p>
          </div>
        </div>

        <div class="overview-item">
          <div class="icon-circle green">
            <i>🧬</i>
          </div>
          <div>
            <h3>Protein Information</h3>
            <p>
              Browse protein sequences, domains, motifs, features, and annotations.
            </p>
          </div>
        </div>

        <div class="overview-item">
          <div class="icon-circle orange">
            <i>☰</i>
          </div>
          <div>
            <h3>Sequence Alignment</h3>
            <p>
              Perform BLASTP local alignment and MAFFT global alignment.
            </p>
          </div>
        </div>

        <div class="overview-item">
          <div class="icon-circle purple">
            <i>🔗</i>
          </div>
          <div>
            <h3>Structure Comparison</h3>
            <p>
              Compare protein structures and inspect structural similarity.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Research Group -->
    <section class="section-card group-card">
      <div class="section-label">Research Group</div>

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
      <div class="section-card bottom-card">
        <div class="section-label">Data Resources</div>

        <div class="bottom-content">
          <div class="large-icon blue-text">▱</div>
          <p>
            Our platform integrates multiple data resources including genome assemblies, gene
            annotations, protein sequences, functional annotation, expression-related resources,
            and structure analysis data, providing comprehensive support for plant genomics research.
          </p>
        </div>
      </div>

      <div class="section-card bottom-card">
        <div class="section-label">Citation</div>

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
.page {
  min-height: 100vh;
  padding: 32px 54px 56px;
  background: #f4f8fb;
  color: #303746;
  font-family: "Arial", "Helvetica", sans-serif;
}

.section-card,
.info-card {
  position: relative;
  background: #ffffff;
  border: 1px solid #e4ebf2;
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(39, 70, 115, 0.08);
}

.section-label {
  position: absolute;
  top: 14px;
  left: -8px;
  min-width: 118px;
  height: 36px;
  padding: 0 18px;
  line-height: 36px;
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
  background: #a7dceb;
  border-radius: 3px 3px 3px 0;
  text-align: center;
}

.section-label::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -8px;
  border-top: 8px solid #78c0d5;
  border-left: 8px solid transparent;
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
  .page {
    padding: 20px 16px;
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