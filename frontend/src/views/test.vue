<template>
  <iframe
    :src="icn3dUrl"
    style="width: 100%; height: 700px; border: none;"
    allow="xr-spatial-tracking *"
    allowfullscreen
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  cifUrl: {
    type: String,
    default: 'https://dayton-duo-spanking-pleased.trycloudflare.com/cif/mtnsp1__phvul_010g129400_model.cif',
  },
})

const icn3dUrl = computed(() => {
  const params = new URLSearchParams({
    type: 'mmcif',
    url: props.cifUrl,
    showcommand: '0',
    mobilemenu: '1',
    showtitle: '0',
    closepopup: '1',
    // 👇 关键：强制显示 ribbon + 自动计算二级结构
    command: 'set default; color chain; ribbon; ribbon thickness 0.7'
  })
  // 👇 必须用 full 功能完整版
  return `https://www.ncbi.nlm.nih.gov/Structure/icn3d/full.html?${params.toString()}`
})
</script>