import { createRouter, createWebHistory } from 'vue-router'

const IndexView = () => import('../views/Index.vue')
const HomeView = () => import('../views/Home.vue')
const TestView = () => import('../views/test.vue')
const GeneInfoPage = () => import('../views/GeneInfoPage.vue')
const ProteinDetail = () => import('../views/components/ProteinDetail.vue')
const SequenceAlignment = () => import('../views/SequenceAlignment.vue')
const StructureCandidateSearch = () => import('../views/StructureCandidateSearch.vue')

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/search',
    name: 'index',
    component: IndexView
  },
  {
    path: '/structure-candidate-search',
    name: 'StructureCandidateSearch',
    component: StructureCandidateSearch
  },
  {
    path: '/test',
    name: 'test',
    component: TestView
  },
  {
    path: '/gene-info',
    name: 'gene-info',
    component: GeneInfoPage
  },
  {
    path: '/protein/detail',
    name: 'ProteinDetail',
    component: ProteinDetail
  },
  {
    path: '/sequence-alignment',
    name: 'SequenceAlignment',
    component: SequenceAlignment
  },
  {
  path: '/jbrowse',
  name: 'JBrowse',
  component: () => import('@/views/JBrowse.vue'),
  },
  {
    path: '/structure-alignment',
    name: 'StructureAlignment',
    component: () => import('@/views/StructureAlignment.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router