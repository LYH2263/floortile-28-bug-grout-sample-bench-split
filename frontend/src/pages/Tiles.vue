<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const meta = ref({})
onMounted(async () => {
  const data = await getJSON('/api/tiles')
  items.value = data.items
  meta.value = { room: data.sample_room, grout: data.catalog_grout_mm }
})
</script>
<template>
  <div class="page">
    <h1>砖型库</h1>
    <p class="hint" v-if="meta.room">
      示例房间 {{ meta.room.name }}（{{ meta.room.length }}×{{ meta.room.width }} m），
      当前默认缝宽 {{ meta.grout ?? 0 }} mm
    </p>
    <div class="tile-cards">
      <div v-for="t in items" :key="t.id" class="tile-card" :class="{ dirty: t.data_quality === 'dirty' }">
        <strong>{{ t.name }}</strong>
        <span>{{ t.tile_l }} × {{ t.tile_w }} m</span>
        <span>示例单片 {{ t.sample_piece_m2 ?? t.sample_eff_piece_m2 }} m²</span>
        <span v-if="t.sample_raw_count != null">示例 raw {{ t.sample_raw_count }} 片</span>
        <em v-if="t.data_quality === 'dirty'">无效规格</em>
      </div>
    </div>
  </div>
</template>
