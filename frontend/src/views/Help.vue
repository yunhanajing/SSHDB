<template>
  <div class="page help-page">
    <div class="page-container">
    <!-- Help Hero -->
    <section class="section-card hero-card">
      <div class="section-label">Help</div>

      <div class="hero-layout">
        <div class="hero-illustration">
          <div class="help-scene">
            <div class="plant">
              <div class="stem"></div>
              <div class="leaf leaf-left"></div>
              <div class="leaf leaf-right"></div>
              <div class="soil"></div>
            </div>
            <div class="question">?</div>
            <div class="screen"></div>
          </div>
        </div>

        <div class="hero-content">
          <h1>How can we help you?</h1>
          <p>
            Find user guides, workflow tips, and answers for using the platform effectively.
          </p>

          <div class="search-row">
            <div class="search-input">
              <span>🔍</span>
              <input
                v-model="keyword"
                type="text"
                placeholder="Search help topics (e.g., gene search, BLASTP, MAFFT, structure comparison)"
              />
            </div>
            <button class="primary-btn" @click="handleSearch">Search</button>
          </div>

          <div class="topic-chips">
            <button
              v-for="topic in topics"
              :key="topic"
              class="topic-chip"
              @click="keyword = topic"
            >
              {{ topic }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Start -->
    <section class="section-card quick-card">
      <div class="section-label">Quick Start</div>

      <div class="steps">
        <div
          v-for="(step, index) in quickSteps"
          :key="step.title"
          class="step-item"
        >
          <div class="step-number">{{ index + 1 }}</div>
          <div :class="['icon-circle', step.color]">
            <span>{{ step.icon }}</span>
          </div>
          <h3>{{ step.title }}</h3>
          <p>{{ step.desc }}</p>

          <div
            v-if="index !== quickSteps.length - 1"
            class="step-arrow"
          >
            →
          </div>
        </div>
      </div>
    </section>

    <!-- User Guides -->
    <section class="section-card guide-card">
      <div class="section-label">User Guides</div>

      <div class="guide-grid">
        <div
          v-for="guide in guides"
          :key="guide.title"
          class="guide-item"
        >
          <div :class="['icon-circle', guide.color]">
            <span>{{ guide.icon }}</span>
          </div>
          <div>
            <h3>{{ guide.title }}</h3>
            <p>{{ guide.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="section-card faq-card">
      <div class="section-label">Frequently Asked Questions</div>

      <div class="faq-layout">
        <div class="faq-column">
          <div
            v-for="item in leftFaqs"
            :key="item.question"
            class="faq-item"
          >
            <button class="faq-question" @click="toggleFaq(item)">
              <span class="question-icon">?</span>
              <span>{{ item.question }}</span>
              <span class="chevron">{{ item.open ? '⌃' : '⌄' }}</span>
            </button>

            <div v-if="item.open" class="faq-answer">
              {{ item.answer }}
            </div>
          </div>
        </div>

        <div class="faq-column">
          <div
            v-for="item in rightFaqs"
            :key="item.question"
            class="faq-item"
          >
            <button class="faq-question" @click="toggleFaq(item)">
              <span class="question-icon">?</span>
              <span>{{ item.question }}</span>
              <span class="chevron">{{ item.open ? '⌃' : '⌄' }}</span>
            </button>

            <div v-if="item.open" class="faq-answer">
              {{ item.answer }}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Bottom -->
    <section class="bottom-grid">
      <div class="section-card bottom-card">
        <div class="section-label">Contact Support</div>

        <div class="support-content">
          <div class="icon-circle green large">
            <span>🎧</span>
          </div>

          <div>
            <h3>Need additional help?</h3>
            <p>
              Contact our team for technical issues or usage questions.
            </p>
          </div>

          <button class="outline-btn">Contact Us</button>
        </div>
      </div>

      <div class="section-card bottom-card">
        <div class="section-label">Documentation</div>

        <div class="support-content">
          <div class="icon-circle purple large">
            <span>📖</span>
          </div>

          <div>
            <h3>Browse detailed tutorials and workflow documentation for all major modules.</h3>
          </div>

          <button class="outline-btn">View Documentation</button>
        </div>
      </div>
    </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Help',

  data() {
    return {
      keyword: '',

      topics: [
        'Gene Search',
        'Gene Page',
        'Sequence Alignment',
        'Structure Comparison',
        'Download'
      ],

      quickSteps: [
        {
          title: 'Choose Species',
          desc: 'Select species and genome version.',
          icon: '🌱',
          color: 'green'
        },
        {
          title: 'Enter Query',
          desc: 'Input gene ID, protein ID, sequence, or keyword.',
          icon: '🔍',
          color: 'blue'
        },
        {
          title: 'View Results',
          desc: 'Browse search or analysis results.',
          icon: '▣',
          color: 'green'
        },
        {
          title: 'Analyze Data',
          desc: 'Use sequence alignment or structure comparison tools.',
          icon: '☰',
          color: 'purple'
        },
        {
          title: 'Download',
          desc: 'Export sequences, annotations, or result files.',
          icon: '↓',
          color: 'blue'
        }
      ],

      guides: [
        {
          title: 'Search Guide',
          desc: 'How to search by gene ID, symbol, keyword, and species.',
          icon: '🔍',
          color: 'blue'
        },
        {
          title: 'Gene Page Guide',
          desc: 'How to read gene details, sequences, and annotations.',
          icon: '📄',
          color: 'green'
        },
        {
          title: 'Sequence Alignment Guide',
          desc: 'How to run BLASTP local alignment and MAFFT global alignment, and how to interpret the results.',
          icon: '☰',
          color: 'orange'
        },
        {
          title: 'Structure Comparison Guide',
          desc: 'How to upload structures and interpret structural similarity metrics.',
          icon: '🔗',
          color: 'purple'
        },
        {
          title: 'Download Guide',
          desc: 'How to export gene, protein, annotation, and analysis files.',
          icon: '↓',
          color: 'blue'
        }
      ],

      leftFaqs: [
        {
          question: 'What identifiers can I search?',
          open: true,
          answer:
            'You can search using gene IDs, protein IDs, gene symbols, or keywords. Please select the correct species and genome version for accurate results.'
        },
        {
          question: 'Why does BLASTP show no hit?',
          open: true,
          answer:
            'BLASTP performs local alignment and may return no statistically reportable local hit for your query. In such cases, the interface will show “No local alignment found”. However, MAFFT global alignment may still be available to assess overall similarity.'
        },
        {
          question: 'Can I search across different species?',
          open: false,
          answer:
            'Yes. You can select different species and genome versions before searching. Search results depend on the selected data source.'
        }
      ],

      rightFaqs: [
        {
          question: 'What is the difference between BLASTP and MAFFT?',
          open: true,
          answer:
            'BLASTP performs local alignment to find high-scoring regions between sequences, while MAFFT performs global alignment to align full-length sequences for comprehensive comparison.'
        },
        {
          question: 'How do I interpret TM-score in structure comparison?',
          open: false,
          answer:
            'TM-score is commonly used to evaluate structural similarity. A higher TM-score usually indicates stronger structural similarity between two protein structures.'
        },
        {
          question: 'Can I download sequences and annotations?',
          open: false,
          answer:
            'Yes. You can download gene sequences, protein sequences, annotation files, and analysis results from the Download page or result panels.'
        }
      ]
    }
  },

  methods: {
    toggleFaq(item) {
      item.open = !item.open
    },

    handleSearch() {
      if (!this.keyword.trim()) {
        this.$message?.warning?.('Please enter a help keyword.')
        return
      }

      this.$message?.success?.(`Searching help topic: ${this.keyword}`)
    }
  }
}
</script>

<style scoped>
.page {
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

.section-card {
  position: relative;
  width: 100%;
  background: #ffffff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  box-sizing: border-box;
}

.section-label {
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

.section-label::after {
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
  padding: 52px 64px 36px;
  margin-bottom: 18px;
}

.hero-layout {
  display: grid;
  grid-template-columns: 38% 62%;
  align-items: center;
  gap: 34px;
}

.hero-illustration {
  min-height: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.help-scene {
  position: relative;
  width: 410px;
  height: 210px;
}

.plant {
  position: absolute;
  left: 120px;
  bottom: 40px;
  width: 100px;
  height: 145px;
}

.stem {
  position: absolute;
  left: 48px;
  bottom: 18px;
  width: 5px;
  height: 105px;
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
  left: -5px;
  top: 52px;
  transform: rotate(25deg);
}

.leaf-right {
  right: -8px;
  top: 32px;
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

.question {
  position: absolute;
  left: 215px;
  top: 55px;
  width: 88px;
  height: 88px;
  border: 8px solid #97c8ec;
  border-radius: 50%;
  color: #6aaee3;
  font-size: 58px;
  font-weight: 800;
  text-align: center;
  line-height: 80px;
  opacity: 0.85;
}

.screen {
  position: absolute;
  right: 28px;
  bottom: 52px;
  width: 110px;
  height: 70px;
  border: 6px solid #d5e7f4;
  border-radius: 6px;
  opacity: 0.85;
}

.screen::after {
  content: "";
  position: absolute;
  left: 42px;
  bottom: -30px;
  width: 28px;
  height: 25px;
  background: #d5e7f4;
}

.hero-content h1 {
  margin: 0 0 8px;
  color: #123f79;
  font-size: 30px;
  font-weight: 800;
}

.hero-content p {
  margin: 0 0 18px;
  color: #3f4856;
  font-size: 15px;
}

.search-row {
  display: grid;
  grid-template-columns: 1fr 100px;
  gap: 14px;
  margin-bottom: 16px;
}

.search-input {
  height: 44px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 15px;
  border: 1px solid #dce5ef;
  border-radius: 4px;
  background: #ffffff;
}

.search-input span {
  color: #8ca0b4;
}

.search-input input {
  flex: 1;
  height: 100%;
  border: none;
  outline: none;
  color: #344053;
  font-size: 14px;
}

.primary-btn {
  height: 44px;
  color: #2c7bd6;
  background: #f6fbff;
  border: 1px solid #9dc7f2;
  border-radius: 4px;
  cursor: pointer;
}

.primary-btn:hover {
  background: #edf6ff;
}

.topic-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.topic-chip {
  height: 34px;
  padding: 0 20px;
  color: #2c7bd6;
  background: #ffffff;
  border: 1px solid #b9d5f3;
  border-radius: 4px;
  cursor: pointer;
}

.topic-chip:hover {
  background: #edf6ff;
}

.quick-card {
  padding: 58px 46px 30px;
  margin-bottom: 18px;
}

.steps {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
}

.step-item {
  position: relative;
  min-height: 132px;
  padding: 0 26px;
  text-align: center;
  border-right: 1px solid #e6edf5;
}

.step-item:last-child {
  border-right: none;
}

.step-number {
  position: absolute;
  top: -24px;
  left: 28px;
  width: 28px;
  height: 28px;
  color: #ffffff;
  background: #3d83d8;
  border-radius: 50%;
  line-height: 28px;
  font-size: 13px;
  font-weight: 700;
}

.step-arrow {
  position: absolute;
  right: -12px;
  top: 42px;
  color: #9aa9b8;
  font-size: 24px;
  z-index: 2;
}

.icon-circle {
  width: 64px;
  height: 64px;
  margin: 0 auto 12px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
}

.icon-circle.large {
  width: 70px;
  height: 70px;
  margin: 0;
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

.step-item h3,
.guide-item h3,
.support-content h3 {
  margin: 0 0 7px;
  color: #164982;
  font-size: 15px;
  font-weight: 800;
}

.step-item p,
.guide-item p,
.support-content p {
  margin: 0;
  color: #3f4856;
  font-size: 13px;
  line-height: 1.55;
}

.guide-card {
  padding: 48px 26px 24px;
  margin-bottom: 18px;
}

.guide-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.guide-item {
  min-height: 112px;
  padding: 20px 18px;
  display: grid;
  grid-template-columns: 62px 1fr;
  gap: 14px;
  align-items: center;
  border: 1px solid #e6edf5;
  border-radius: 6px;
  background: #ffffff;
}

.guide-item .icon-circle {
  width: 58px;
  height: 58px;
  margin: 0;
  font-size: 24px;
}

.faq-card {
  padding: 52px 28px 28px;
  margin-bottom: 18px;
}

.faq-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.faq-column {
  display: grid;
  gap: 10px;
}

.faq-item {
  border: 1px solid #e2ebf4;
  border-radius: 5px;
  overflow: hidden;
  background: #ffffff;
}

.faq-question {
  width: 100%;
  min-height: 46px;
  display: grid;
  grid-template-columns: 28px 1fr 28px;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  color: #1e63ad;
  background: #ffffff;
  border: none;
  font-size: 14px;
  font-weight: 800;
  text-align: left;
  cursor: pointer;
}

.question-icon {
  width: 18px;
  height: 18px;
  color: #ffffff;
  background: #2e7fd4;
  border-radius: 50%;
  font-size: 12px;
  line-height: 18px;
  text-align: center;
}

.chevron {
  color: #6b7d90;
  text-align: right;
}

.faq-answer {
  padding: 12px 46px 18px 54px;
  color: #3f4856;
  background: #f7fbff;
  font-size: 14px;
  line-height: 1.65;
  border-top: 1px solid #e6edf5;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.bottom-card {
  min-height: 110px;
  padding: 48px 34px 24px;
}

.support-content {
  display: grid;
  grid-template-columns: 84px 1fr 150px;
  gap: 20px;
  align-items: center;
}

.support-content h3 {
  color: #26364b;
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

@media (max-width: 1200px) {
  .hero-layout,
  .faq-layout,
  .bottom-grid {
    grid-template-columns: 1fr;
  }

  .steps,
  .guide-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 18px;
  }

  .step-item {
    border-right: none;
    border-bottom: 1px solid #e6edf5;
    padding-bottom: 20px;
  }

  .step-arrow {
    display: none;
  }

  .support-content {
    grid-template-columns: 80px 1fr;
  }

  .support-content .outline-btn {
    grid-column: 2;
    width: 150px;
  }
}

@media (max-width: 720px) {
  .page {
    padding: 20px 16px;
  }

  .hero-card,
  .quick-card,
  .guide-card,
  .faq-card,
  .bottom-card {
    padding-left: 22px;
    padding-right: 22px;
  }

  .search-row,
  .steps,
  .guide-grid,
  .support-content {
    grid-template-columns: 1fr;
  }

  .support-content .outline-btn {
    grid-column: auto;
  }
}
</style>