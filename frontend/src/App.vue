<template>
  <div class="layout">
    <!-- 顶部蓝色标题区域 -->
    <header class="hero-header">
      <div class="hero-content">
        <div class="logo-circle">
          <img src="/logo.png" alt="logo" class="logo-image" />
        </div>

        <div class="title-group">
          <h1>Structure-based SNF Homolog Database</h1>
          <p>
            For exploring sequence and structural homologs of symbiotic nitrogen fixation proteins across diverse species
          </p>
        </div>
      </div>
    </header>

    <!-- 导航栏区域 -->
    <header class="site-header">
      <div class="header-inner">
        <el-menu
          class="nav-menu"
          mode="horizontal"
          :ellipsis="false"
          :default-active="activeMenu"
          router
        >
          <el-menu-item index="/">Home</el-menu-item>

          <!-- Search 二级菜单 -->
          <el-sub-menu index="/search-menu">
        
            <template #title>Search</template>

            <el-menu-item index="/gene-info">
            SNF Protein Retrieval
            </el-menu-item>
            <el-menu-item index="/search">
              SNF Homolog Search Across Species
            </el-menu-item>
            <el-menu-item index="/structure-candidate-search">
             Custom Protein Homolog Search
            </el-menu-item>
          </el-sub-menu>

          <!-- <el-menu-item index="/gene-info">Gene</el-menu-item> -->

          <!-- Tools 二级菜单 -->
          <el-sub-menu index="/tools">
            <template #title>Tools</template>

            <el-menu-item index="/jbrowse">
              JBrowse
            </el-menu-item>

            <el-menu-item index="/sequence-alignment">
              Sequence Alignment
            </el-menu-item>

            <el-menu-item index="/structure-alignment">
              Structure Alignment
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/download">Download</el-menu-item>

          <el-menu-item index="/about">About</el-menu-item>
        </el-menu>
      </div>
    </header>

    <!-- 页面主体内容 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- 底部 footer -->
    <footer class="site-footer">
      <div class="footer-content">
        <p>
          This website is intended for academic research and communication only.&nbsp;&nbsp;&nbsp;
          The data and content are provided for reference purposes only.
        </p>
        <p>
          If you have any questions or suggestions about this website, please contact us at&nbsp;&nbsp;
          <a href="mailto:wanghaifeng@yzwlab.cn">wanghaifeng@yzwlab.cn</a>.
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

/*
  让二级菜单在子页面时保持一级菜单高亮：
  /search 和 /structure-candidate-search 高亮 Search
  /jbrowse、/sequence-alignment、/structure-alignment 高亮 Tools
*/
const activeMenu = computed(() => {
  const path = route.path

  if (
    path === '/search' ||
    path === '/structure-candidate-search'
  ) {
    return '/search-menu'
  }

  if (
    path === '/jbrowse' ||
    path === '/sequence-alignment' ||
    path === '/structure-alignment'
  ) {
    return '/tools'
  }

  if (path === '/test') {
    return '/download'
  }

  return path
})
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* =========================
   顶部蓝色标题区域
========================= */

.hero-header {
  width: 100%;
  min-height: 130px;
  background: #7ab9ea;
}

.hero-content {
  width: 100%;
  min-height: 130px;
  padding: 0 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 28px;
  box-sizing: border-box;
}

.logo-circle {
  width: 100px;
  height: 100px;
  flex: 0 0 100px;
  border-radius: 50%;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.title-group {
  text-align: center;
  color: #ffffff;
}

.title-group h1 {
  margin: 0;
  font-size: 42px;
  font-weight: 800;
  line-height: 1.08;
}

.title-group p {
  margin: 14px 0 0;
  font-size: 22px;
  line-height: 1.4;
}

/* =========================
   导航栏区域
========================= */

.site-header {
  width: 100%;
  height: 54px;
  background: #f7fbff;
  border-bottom: none;
}

.header-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/*
  el-menu 本体。
  这里同时设置 Element Plus 菜单变量，
  保证 el-menu-item 和 el-sub-menu 的颜色一致。
*/
.nav-menu,
.nav-menu.el-menu--horizontal {
  height: 100%;
  background: transparent !important;
  border-bottom: none !important;

  --el-menu-bg-color: transparent;
  --el-menu-hover-bg-color: transparent;
  --el-menu-text-color: #055da5;
  --el-menu-active-color: #69a4db;
  --el-menu-hover-text-color: #69a4db;
  --el-menu-border-color: transparent;
}

/*
  一级普通菜单：.el-menu-item
  一级二级菜单标题：.el-sub-menu__title
*/
.nav-menu :deep(.el-menu-item),
.nav-menu :deep(.el-sub-menu__title) {
  position: relative;
  height: 54px !important;
  line-height: 54px !important;
  padding: 0 48px !important;
  color: #055da5 !important;
  font-size: 20px !important;
  font-weight: 800 !important;
  letter-spacing: 0.2px;
  background: transparent !important;
  border-bottom: none !important;
}

/* hover 状态 */
.nav-menu :deep(.el-menu-item:hover),
.nav-menu :deep(.el-sub-menu__title:hover) {
  color: #69a4db !important;
  background: transparent !important;
  border-bottom: none !important;
}

/* active 状态 */
.nav-menu :deep(.el-menu-item.is-active),
.nav-menu :deep(.el-sub-menu.is-active .el-sub-menu__title) {
  color: #69a4db !important;
  background: transparent !important;
  border-bottom: none !important;
}

/* 当前激活菜单下方短横线 */
.nav-menu :deep(.el-menu-item.is-active::after),
.nav-menu :deep(.el-sub-menu.is-active .el-sub-menu__title::after) {
  content: "";
  position: absolute;
  left: 34px;
  right: 34px;
  bottom: 0;
  height: 2px;
  background: #e1edf9;
  border-radius: 999px 999px 0 0;
}

/* 去掉点击、聚焦时 Element Plus 默认背景 */
.nav-menu :deep(.el-menu-item:focus),
.nav-menu :deep(.el-menu-item:active),
.nav-menu :deep(.el-sub-menu__title:focus),
.nav-menu :deep(.el-sub-menu__title:active) {
  background: transparent !important;
  border-bottom: none !important;
}

/* 修复 el-sub-menu 自身默认样式 */
.nav-menu :deep(.el-sub-menu) {
  height: 54px !important;
  line-height: 54px !important;
  background: transparent !important;
  border-bottom: none !important;
}

.nav-menu :deep(.el-sub-menu.is-active) {
  border-bottom: none !important;
}

/* 二级菜单右侧小箭头 */
.nav-menu :deep(.el-sub-menu__icon-arrow) {
  color: inherit !important;
  font-weight: 800 !important;
}

/* =========================
   下拉菜单样式
   el-sub-menu 弹出层通常挂载到 body，
   scoped 管不到，所以用 :global。
========================= */

:global(.el-menu--popup) {
  min-width: 230px;
  padding: 6px 0;
  background: #ffffff !important;
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(5, 93, 165, 0.12);
}

:global(.el-menu--popup .el-menu-item) {
  height: 42px !important;
  line-height: 42px !important;
  color: #055da5 !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  background: #ffffff !important;
}

:global(.el-menu--popup .el-menu-item:hover) {
  color: #69a4db !important;
  background: #f7fbff !important;
}

:global(.el-menu--popup .el-menu-item.is-active) {
  color: #69a4db !important;
  background: #f7fbff !important;
}

/* =========================
   主体内容区域
========================= */

.main-content {
  flex: 1;
  width: 100%;
  background: #f7fbff;
  box-sizing: border-box;
}

/* =========================
   footer 区域
========================= */

.site-footer {
  width: 100%;
  background: #7ab9ea;
  color: #ffffff;
  padding: 18px 20px;
  box-sizing: border-box;
  text-align: center;
  height: 75px;
}

.footer-content p {
  margin: 4px 0;
  font-size: 13px;
  line-height: 1.6;
}

.site-footer a {
  color: #ffffff;
  text-decoration: underline;
}

/* =========================
   移动端适配
========================= */

@media (max-width: 768px) {
  .hero-content {
    flex-direction: column;
    padding: 20px;
    gap: 14px;
  }

  .logo-circle {
    width: 84px;
    height: 84px;
    flex-basis: 84px;
  }

  .title-group h1 {
    font-size: 30px;
  }

  .title-group p {
    font-size: 16px;
  }

  .site-header {
    height: auto;
  }

  .header-inner {
    overflow-x: auto;
    justify-content: flex-start;
  }

  .nav-menu :deep(.el-menu-item),
  .nav-menu :deep(.el-sub-menu__title) {
    padding: 0 18px !important;
    font-size: 16px !important;
  }

  .nav-menu :deep(.el-menu-item.is-active::after),
  .nav-menu :deep(.el-sub-menu.is-active .el-sub-menu__title::after) {
    left: 18px;
    right: 18px;
  }

  .site-footer {
    height: auto;
    padding: 14px 16px;
  }

  .footer-content p {
    font-size: 13px;
  }
}
</style>

<style>
html,
body,
#app {
  margin: 0;
  padding: 0;
  width: 100%;
  min-height: 100%;
}
</style>
