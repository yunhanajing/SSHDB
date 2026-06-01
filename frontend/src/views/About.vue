<template>
  <div class="about-page">
    <div class="about-shell">
      <div class="doc-layout">
        <aside class="doc-sidebar" aria-label="About navigation">
          <a
            class="sidebar-link"
            :class="{ 'is-active': activeSection === 'framework' }"
            href="#framework"
            @click="setActiveSection('framework')"
          >
            1. Framework
          </a>
          <a
            class="sidebar-link"
            :class="{ 'is-active': activeSection === 'search' }"
            href="#search"
            @click="setActiveSection('search')"
          >
            2. Search
          </a>
          <a
            class="sidebar-link"
            :class="{ 'is-active': activeSection === 'resources' }"
            href="#resources"
            @click="setActiveSection('resources')"
          >
            3. Tools
          </a>
          <a
            class="sidebar-link"
            :class="{ 'is-active': activeSection === 'download' }"
            href="#download"
            @click="setActiveSection('download')"
          >
            4. Download
          </a>
          <a
            class="sidebar-link"
            :class="{ 'is-active': activeSection === 'contact' }"
            href="#contact"
            @click="setActiveSection('contact')"
          >
            5. Contact
          </a>
          <a
            class="sidebar-link"
            :class="{ 'is-active': activeSection === 'reference' }"
            href="#reference"
            @click="setActiveSection('reference')"
          >
            6. Reference
          </a>
        </aside>

        <main class="doc-panel">
          <section id="framework" class="doc-section framework-section">
            <div class="section-title">
              <span>1.</span>
              <h1>Framework</h1>
            </div>

            <div class="framework-copy">
              <p>
                <strong class="keyword keyword-blue">SSHDB</strong> is a specialized database
                dedicated to homologous proteins involved in
                <strong class="keyword keyword-green">symbiotic nitrogen fixation (SNF)</strong>
                across diverse species. It integrates
                <strong class="keyword keyword-blue">sequence-</strong> and
                <strong class="keyword keyword-blue">structure-based homology search data</strong>
                from <strong class="keyword keyword-amber">over 250 organisms</strong>,
                encompassing comprehensive information on sequence similarity, structural similarity,
                as well as paired sequence and structure alignments (Fig. 1). Designed to advance
                SNF research, the database provides robust support for the evolutionary analysis and
                targeted engineering of SNF systems in non-leguminous crops.
              </p>

              <p>
                Uniquely, <strong class="keyword keyword-blue">SSHDB</strong> systematically
                consolidates homologous relationships predicted by both sequence and structural
                similarity metrics, with standardized
                <strong class="keyword keyword-green">pairwise sequence and structural alignments</strong>
                provided for all candidate homologous protein pairs. This  <strong class="keyword keyword-green">multi-dimensional analytical
                framework</strong> enables multi-level comparative evaluation of SNF-related homologs,
                effectively facilitating the identification of <strong class="keyword keyword-green">distant SNF-associated protein homologs</strong>
                that are frequently overlooked by conventional sequence-only homology search methods.
                By curating and unifying these multi-dimensional homology data into an open, freely accessible
                platform, SSHDB serves as a reliable and practical resource for comparative
                evolutionary studies, <strong class="keyword keyword-green">novel candidate gene mining</strong>, and cross-species characterization
                of conserved symbiosis-related components across a wide range of plant lineages.
              </p>
            </div>

            <figure class="framework-figure">
              <img src="/1.png" alt="SSHDB framework overview" />
            </figure>
          </section>

          <section id="search" class="doc-section">
            <div class="section-title compact-title">
              <span>2.</span>
              <h2>Search</h2>
            </div>

            <p class="section-text">
              The search framework of SSHDB is
              implemented based on the structural search capability of
              <strong class="keyword keyword-blue">TM-Vec</strong>. This tool enables the prediction
              of <strong class="keyword keyword-blue">protein structural similarity</strong> using
              only <strong class="keyword keyword-blue">amino acid sequences</strong>, eliminating
              the requirement for experimentally resolved structural files
              for query proteins. Notably, the
              <strong class="keyword keyword-blue">predicted TM-score</strong> generated by TM-Vec
              may exhibit slight deviations from the
              <strong class="keyword keyword-blue">actual structural TM-score</strong> calculated
              from resolved protein structures. The overall search module consists of
              <strong class="keyword keyword-blue">three refined sub-functions</strong> with
              independent and complementary capabilities, as detailed below.
            </p>

            <div class="subsection-list">
              <article class="content-card">
                <h3><el-icon style="margin-right: 8px;"><Search /></el-icon>SNF Protein Retrieval</h3>
                <p>
                  This core query module enables users to directly retrieve comprehensive annotation
                  information of documented
                  <strong class="keyword keyword-blue">SNF-related proteins</strong> archived in
                  SSHDB. It supports fast and precise access to basic biological attributes of target
                  SNF proteins, including
                  <strong class="keyword keyword-blue">protein sequences</strong>,
                  <strong class="keyword keyword-blue">structural characteristics</strong>,
                  <strong class="keyword keyword-blue">species source</strong>, and
                  <strong class="keyword keyword-blue">functional annotations</strong>. This function
                  focuses on the intrinsic information of canonical SNF proteins, providing reliable
                  baseline data for users to understand the fundamental features of SNF-related
                  proteins without involving cross-species homologous prediction.
                </p>
              </article>

              <article class="content-card">
                <h3><el-icon style="margin-right: 8px;"><Search /></el-icon>SNF Homolog Search Across Species</h3>
                <p>
                  Dedicated for cross-species homology mining of SNF proteins, this function takes
                  experimentally validated SNF proteins as
                  seed sequences and performs
                  homologous screening across
                  <strong class="keyword keyword-blue">more than 250 collected organisms</strong>.
                  Different from conventional sequence-only searching strategies, it integrates both
                  <strong class="keyword keyword-blue">sequence similarity</strong> and
                  <strong class="keyword keyword-blue">structural similarity</strong> evaluation,
                  together with <strong class="keyword keyword-blue">paired sequence and structural alignment results</strong>. This
                  multi-dimensional comparison strategy effectively identifies evolutionarily distant
                  SNF homologous candidates that are easily neglected by traditional methods,
                  providing critical candidate resources for studying the evolutionary conservation
                  and functional differentiation of SNF systems across different species.
                </p>
              </article>

              <article class="content-card">
                <h3><el-icon style="margin-right: 8px;"><Search /></el-icon>Custom Protein Homolog Search</h3>
                <p>
                  As an open and flexible universal homology search module, this function allows
                  users to submit <strong class="keyword keyword-blue">custom protein ID</strong>
                  that are not limited to canonical SNF proteins. The system conducts full-scale
                  cross-species homologous prediction and candidate screening based on integrated
                  sequence and structural homology verification,
                  and outputs  <strong class="keyword keyword-blue">reliable homologous protein candidates with corresponding alignment
                  evidence</strong>. This function greatly expands the application scope of SSHDB, enabling
                  extended exploration of potential symbiosis-related homologous proteins and
                  providing a powerful tool for discovering novel SNF-associated components and
                  analyzing universal protein evolutionary relationships.
                </p>
              </article>
            <figure class="framework-figure2">
              <img src="/2.png" alt="SSHDB framework overview" />
            </figure>
            </div>
          </section>

          <section id="resources" class="doc-section">
            <div class="section-title compact-title">
              <span>3.</span>
              <h2>Tools</h2>
            </div>

            <div class="tool-grid">
              <article class="tool-card">
                <div class="tool-card-header">
                  🧬
                  <h3>JBrowse</h3>
                </div>
                <p>
                  JBrowse is an interactive, web-based <strong class="keyword keyword-blue">genome visualization tool</strong> embedded in SSHDB. 
                  It supports intuitive and dynamic browsing of genomic location information, gene structure features, and functional annotations of SNF-related genes across multiple species. 
                  Users can visually inspect exon-intron architectures, local genomic context, and annotation features of target SNF genes, facilitating visual assessment of gene structure organization and genomic context.
                </p>
              </article>

              <article class="tool-card">
                <div class="tool-card-header">
                  🧬
                  <h3>Sequence Alignment</h3>
                </div>
                <p>
                      The Sequence Alignment tool enables systematic
                      <strong class="keyword keyword-blue">pairwise sequence comparison</strong> of SNF
                      homologous proteins derived from cross-species screening. It generates
                      <strong class="keyword keyword-blue">standardized alignment results</strong> with
                      corresponding <strong class="keyword keyword-blue">sequence similarity metrics</strong>,
                      allowing users to visualize identical and similar amino acid residues,
                      variable regions, and alignment patterns across homologous candidates.
                </p>
              </article>

              <article class="tool-card">
                <div class="tool-card-header">
                  🧬
                  <h3>Structure Alignment</h3>
                </div>
                <p>
                  The Structure Alignment tool leverages
                  <strong class="keyword keyword-blue">US-align</strong> for protein structural
                  superposition and structural similarity calculation, combined with
                  <strong class="keyword keyword-blue">3Dmol</strong> for real-time interactive 3D
                  visualization. Unlike sequence-based alignment or TM-Vec-based structural
                  similarity prediction from amino acid sequences, this module supports
                  structure-file-based pairwise comparison by allowing users to upload two
                  protein structure files in <strong class="keyword keyword-blue">.pdb</strong>,
                  <strong class="keyword keyword-blue">.cif</strong>, or
                  <strong class="keyword keyword-blue">.mmCIF</strong> formats. US-align quantitatively
                  evaluates structural similarity and generates standardized structural alignment
                  results, while 3Dmol renders interactive superimposed 3D protein structures in
                  the browser without additional software installation.
                </p>
              </article>
            </div>
            <figure class="framework-figure2">
              <img src="/3.png" alt="SSHDB framework overview" />
            </figure>
          </section>

          <section id="download" class="doc-section">
            <div class="section-title compact-title">
              <span>4.</span>
              <h2>Download</h2>
            </div>

            <div class="download-card">
              <p>
                <strong class="keyword keyword-blue">SSHDB</strong> provides a comprehensive and
                user-friendly data download module
                that supports free access to
                <strong class="keyword keyword-blue">genome annotation</strong>,
                <strong class="keyword keyword-blue">sequence</strong>, and
                <strong class="keyword keyword-blue">structural resources</strong> integrated in the
                database. Users can download genome sequences in
                <strong class="keyword keyword-blue">FASTA</strong> format and genome annotations in
                <strong class="keyword keyword-blue">GFF</strong> format. 
                Furthermore, this module archives and provides access to
                <strong class="keyword keyword-blue">predicted structural models</strong> for
                <strong class="keyword keyword-amber">more than 200 reported SNF-related proteins</strong>.
              </p>
            </div>
          </section>

          <section id="contact" class="doc-section">
            <div class="section-title compact-title">
              <span>5.</span>
              <h2>Contact</h2>
            </div>

            <div class="contact-grid">
              <article class="content-card">
                <h3><el-icon style="margin-right: 8px;"><Star /></el-icon> Expect</h3>
                <p>
                  SSHDB will be continuously updated to expand its coverage of SNF homologous
                  proteins across more species and optimize the accuracy of structural homology
                  prediction. We will also integrate additional analytical tools and validated
                  functional data to further facilitate in-depth evolutionary research and targeted
                  engineering of SNF systems in non-leguminous crops.
                </p>
              </article>

              <article class="content-card">
                <h3><el-icon style="margin-right: 8px;"><Star /></el-icon>Funding</h3>
                <p>
                  This work was supported by grants from
                  <strong class="keyword keyword-blue">Biological Breeding-National Science and
                  Technology Major Project (2024ZD04079)</strong>, <strong class="keyword keyword-blue">National Key R&amp;D Program of
                  China (2025YFE0200400)</strong>, <strong class="keyword keyword-blue">National Natural Science Foundation of China (32160142)</strong>,
                  and <strong class="keyword keyword-blue">Yazhouwan National Laboratory project (2310WC01)</strong>.
                </p>
              </article>

              <article class="content-card contact-card">
                <h3><el-icon style="margin-right: 8px;"><Phone /></el-icon>Contact us</h3>
                <p>
                  We highly welcome all questions, comments, and valuable feedback regarding SSHDB,
                  and sincerely look forward to communications and academic exchanges.
                </p>
                <div class="contact-lines">
                  <div>
                    <strong>Address:</strong>
                    <span>Yazhouwan National Laboratory, Sanya, Hainan 572025, China.</span>
                  </div>
                  <div>
                    <strong>Telephone:</strong>
                    <span>To be updated</span>
                  </div>
                  <div>
                    <strong>Fax:</strong>
                    <span>To be updated</span>
                  </div>
                  <div>
                    <strong>E-mail:</strong>
                    <span>To be updated</span>
                  </div>
                </div>
              </article>
            </div>
          </section>

          <section id="reference" class="doc-section">
            <div class="section-title compact-title">
              <span>6.</span>
              <h2>Reference</h2>
            </div>

            <ol class="reference-list">
              <li>
                Hamamsy T, et al. Protein remote homology detection and structural alignment using
                deep learning. <em>Nat. Biotechnol.</em> 42, 975-985 (2024).
              </li>
              <li>
                Hamilton JP, Li C, Buell CR. The rice genome annotation project: an updated
                database for mining the rice genome. <em>Nucleic Acids Res.</em> 53, D1614-D1622
                (2025).
              </li>
              <li>
                Li Y, Pi M, Gao Q, Liu Z, Kang C. Updated annotation of the wild strawberry
                Fragaria vesca V4 genome. <em>Hortic. Res.</em> 6, 61 (2019).
              </li>
              <li>
                Amundson KR, et al. A deep-time landscape of plant cis-regulatory sequence
                evolution. <em>Science</em> 0, eadt8983.
              </li>
              <li>
                Altschul SF, Gish W, Miller W, Myers EW, Lipman DJ. Basic local alignment search
                tool. <em>J. Mol. Biol.</em> 215, 403-410 (1990).
              </li>
              <li>
                Zhang C, Shine M, Pyle AM, Zhang Y. US-align: universal structure alignments of
                proteins, nucleic acids, and macromolecular complexes.
                <em>Nat. Methods</em> 19, 1109-1115 (2022).
              </li>
            </ol>
          </section>
        </main>
      </div>
    </div>
  </div>
</template>

<script>
import { Box, Connection, DataLine, Search, Star, Phone } from '@element-plus/icons-vue'

export default {
  name: 'About',

  data() {
    return {
      activeSection: ''
    }
  },

  components: {
    Box,
    Connection,
    DataLine,
    Search,
    Star, Phone
  },

  mounted() {
    this.syncActiveSectionFromHash()
    window.addEventListener('hashchange', this.syncActiveSectionFromHash)
  },

  beforeUnmount() {
    window.removeEventListener('hashchange', this.syncActiveSectionFromHash)
  },

  methods: {
    setActiveSection(section) {
      this.activeSection = section
    },

    syncActiveSectionFromHash() {
      this.activeSection = window.location.hash.replace('#', '')
    }
  }
}
</script>

<style scoped>
.about-page {
  --accent-blue: #1261cb;
  --accent-blue-dark: #0d4f9e;
  --accent-blue-soft: #f4f7fc;
  --accent-blue-border: #d8e8fb;
  --accent-blue-muted: #6fa4e8;
  width: 100%;
  min-height: 100vh;
  padding: 16px 24px 28px;
  box-sizing: border-box;
  background:
    radial-gradient(circle at top left, rgba(122, 185, 234, 0.18), transparent 34%),
   #fff;
  color: #17284a;
  font-family: "Arial", "Helvetica", sans-serif;
}

.about-shell {
  width: 100%;
  max-width: 1540px;
  margin: 0 auto;
}

.breadcrumb-card {
  height: 44px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #bacfe7;
  background: linear-gradient(90deg, #f0f7ff, #e7f1fb);
  border: 1px solid #dbe9f6;
  border-radius: 6px;
  box-shadow: 0 6px 18px rgba(51, 112, 181, 0.08);
  box-sizing: border-box;
}

.breadcrumb-card a,
.breadcrumb-card strong {
  color: #e0e8f3;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
}

.breadcrumb-card span {
  color: #e3eefb;
  font-size: 14px;
}

.doc-layout {
  display: grid;
  grid-template-columns: 290px minmax(0, 1fr);
  gap: 2px;
  margin-top: 14px;
}

.doc-sidebar,
.doc-panel {
  background: #ffffff;
  border: 1px solid #dce8f6;
  border-radius: 8px;
  box-shadow: 0 8px 28px rgba(27, 83, 142, 0.08);
}

.doc-sidebar {
  align-self: start;
  position: sticky;
  top: 18px;
  padding: 14px 12px;
  font-weight: 700;
}

.sidebar-link {
  display: block;
  padding: 11px 16px;
  color: #2f456b;
  font-size: 15px;
  line-height: 1.2;
  text-decoration: none;
  border-radius: 4px;
  border-left: 3px solid transparent;
}

.sidebar-link + .sidebar-link {
  margin-top: 6px;
}

.sidebar-link:hover,
.sidebar-link.is-active {
  color: var(--accent-blue-dark);
  background: var(--accent-blue-soft);
  border-left-color: var(--accent-blue-muted);
}

.doc-panel {
  padding: 26px 28px 22px;
}

.doc-section {
  scroll-margin-top: 24px;
}

.doc-section + .doc-section {
  margin-top: 26px;
}

.section-title {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 12px;
  color: var(--accent-blue-dark);
}

.section-title span,
.section-title h1,
.section-title h2 {
  margin: 0;
  font-weight: 800;
  letter-spacing: 0;
}

.section-title span,
.section-title h1 {
  font-size: 25px;
}

.section-title h2,
.compact-title span {
  font-size: 23px;
}

.framework-copy {
  max-width: 1120px;
}

.framework-copy p,
.section-text {
  margin: 0;
  color: #203250;
  font-size: 15px;
  line-height: 1.85;
}

.framework-copy p + p {
  margin-top: 14px;
}

.subsection-list,
.contact-grid {
  display: grid;
  gap: 16px;
  margin-top: 18px;
}

.content-card,
.tool-card {
  border: 1px solid #dbe7f4;
  border-radius: 7px;
  box-shadow: 0 6px 18px rgba(33, 95, 163, 0.06);
  box-sizing: border-box;
}

.content-card {
  padding: 18px 20px;
}

.content-card h3 {
  margin: 0 0 14px;
  padding-bottom: 12px;
  display: flex;
  align-items: center;
  color: var(--accent-blue-dark);
  border-bottom: 1px solid var(--accent-blue-border);
  font-size: 16px;
  font-weight: 580;
}

.content-card p {
  margin: 0;
  color: #203250;
  font-size: 14px;
  line-height: 1.75;
}

.download-card {
  margin-top: 14px;
}

.download-card p {
  font-size: 15px;
  line-height: 1.85;
}

.keyword {
  font-weight: 580;
}

.keyword-blue {
  color: var(--accent-blue);
}

.keyword-green {
  color: var(--accent-blue);
}

.keyword-amber {
  color: var(--accent-blue);
}

.framework-figure {
  margin: 22px auto 2px;
  padding: 26px 18px 12px;
  max-width: 680px;
  text-align: center;
  border: 1px solid #dbe9f6;
  border-radius: 8px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85);
  box-sizing: border-box;
}
.framework-figure2 {
  margin: 24px auto 4px;
  padding: 20px 20px 18px;
  max-width: 1180px;
  width: 100%;
  text-align: center;
  border: 1px solid #dbe9f6;
  border-radius: 8px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85);
  box-sizing: border-box;

  display: flex;
  justify-content: center;
  align-items: center;
}

.framework-figure2 img {
  display: block;
  width: 100%;
  max-width: 1120px;
  height: auto;
  max-height: none;
  object-fit: contain;
  object-position: center center;
}
.framework-figure img {
  display: block;
  width: min(100%, 860px);
  max-height: 620px;
  margin: 0 auto;
  object-fit: contain;
  object-position: center center;
  transform: translateY(6px);
}

.framework-figure figcaption {
  margin-top: 12px;
  color: #60758f;
  font-size: 13px;
  line-height: 1.5;
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
  margin-top: 16px;
}

.tool-card {
  padding: 24px 26px 26px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.tool-card-header {
  display: flex;
  align-items: center;
  gap: 18px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--accent-blue-border);
}

.tool-card h3 {
  margin: 0;
  color: var(--accent-blue-dark);
  font-size: 16px;
  font-weight: 580;
}

.tool-card p {
  margin: 0;
  color: #203250;
  font-size: 15px;
  line-height: 1.9;
}

.tool-icon {
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  color: var(--accent-blue);
  background: var(--accent-blue-soft);
  border: 1px solid var(--accent-blue-border);
  border-radius: 50%;
  font-size: 28px;
}

.contact-grid {
  grid-template-columns: 1fr;
}

.contact-card {
  grid-column: auto;
}

.contact-lines {
  display: grid;
  gap: 8px;
  margin-top: 14px;
}

.contact-lines div {
  display: grid;
  grid-template-columns: 92px 1fr;
  gap: 12px;
  color: #203250;
  font-size: 14px;
  line-height: 1.55;
}

.contact-lines strong {
  color: var(--accent-blue-dark);
}

.reference-list {
  margin: 14px 0 0;
  padding: 18px 22px 18px 42px;
  color: #203250;
  background: #fbfdff;
  border: 1px solid #dbe7f4;
  border-radius: 7px;
}

.reference-list li {
  padding-left: 6px;
  font-size: 14px;
  line-height: 1.7;
}

.reference-list li + li {
  margin-top: 8px;
}

@media (max-width: 1100px) {
  .doc-layout {
    grid-template-columns: 1fr;
  }

  .doc-sidebar {
    position: static;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
  }

  .sidebar-link {
    margin-top: 0 !important;
    text-align: center;
  }

  .tool-grid,
  .contact-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .about-page {
    padding: 12px 14px 22px;
  }

  .breadcrumb-card {
    padding: 0 16px;
    overflow-x: auto;
    white-space: nowrap;
  }

  .doc-panel {
    padding: 22px 18px 18px;
  }

  .doc-sidebar {
    grid-template-columns: 1fr;
  }

  .contact-lines div {
    grid-template-columns: 1fr;
  }

  .framework-figure {
    padding: 10px;
  }

  .section-title span,
  .section-title h1 {
    font-size: 23px;
  }
}
</style>
