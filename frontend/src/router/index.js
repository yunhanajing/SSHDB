import { createRouter, createWebHistory } from 'vue-router'
import { trackPageView } from '@/utils/visitorTracking'

const HomeView = () => import('../views/Home.vue')
const IndexView = () => import('../views/Index.vue')
const GeneInfoPage = () => import('../views/GeneInfoPage.vue')
const ProteinDetail = () => import('../views/components/ProteinDetail.vue')

const SequenceAlignment = () => import('../views/SequenceAlignment.vue')
const StructureAlignment = () => import('../views/StructureAlignment.vue')
const StructureCandidateSearch = () => import('../views/StructureCandidateSearch.vue')
const JBrowse = () => import('../views/JBrowse.vue')
const Download = () => import('../views/Download.vue')

const About = () => import('../views/About.vue')

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/search',
    name: 'search',
    component: IndexView
  },
  {
    path: '/gene-info',
    name: 'geneInfo',
    component: GeneInfoPage
  },
  {
    path: '/protein/detail',
    name: 'proteinDetail',
    component: ProteinDetail
  },

  // Tools 下的页面
  {
    path: '/jbrowse',
    name: 'jbrowse',
    component: JBrowse
  },
  {
    path: '/sequence-alignment',
    name: 'sequenceAlignment',
    component: SequenceAlignment
  },
  {
    path: '/structure-alignment',
    name: 'structureAlignment',
    component: StructureAlignment
  },
  {
    path: '/structure-candidate-search',
    name: 'structureCandidateSearch',
    component: StructureCandidateSearch
  },
  {
    path: '/download',
    name: 'download',
    component: Download
  },
  {
    path: '/test',
    redirect: '/download'
  },
  {
    path: '/about',
    name: 'about',
    component: About
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach((to, from, failure) => {
  if (!failure) {
    trackPageView(to.path)
  }
})

export default router
