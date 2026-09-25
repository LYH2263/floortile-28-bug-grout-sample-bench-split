<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const detail = ref(null)
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
async function open(id) { detail.value = await getJSON(`/api/runs/${id}`) }
</script>
<template>
  <div class="page">
    <h1>测算记录</h1>
    <table class="tbl">
      <thead><tr><th>编号</th><th>时间</th><th>房间</th><th>砖型</th><th>缝宽(mm)</th><th>片数</th></tr></thead>
      <tbody>
        <tr v-for="r in items" :key="r.id" class="clickable" @click="open(r.id)">
          <td>{{ r.id }}</td>
          <td>{{ r.created_at?.slice(0, 19) }}</td>
          <td>{{ r.room_name }}</td>
          <td>{{ r.tile_name }}</td>
          <td>{{ r.result?.grout_mm ?? 0 }}</td>
          <td>{{ r.result?.order_count }}</td>
        </tr>
      </tbody>
    </table>
    <div v-if="detail" class="detail">
      <h2>测算 #{{ detail.id }}</h2>
      <ul>
        <li>缝宽 {{ detail.result?.grout_mm ?? 0 }} mm，有效单片 {{ detail.result?.eff_piece_m2 ?? detail.result?.piece_m2 }} m²</li>
        <li>净用量 {{ detail.result?.raw_count }} 片，损耗 {{ detail.result?.waste_pct }}%，订货 {{ detail.result?.order_count }} 片</li>
        <li>网格 {{ detail.result?.layout?.cols }} 列 × {{ detail.result?.layout?.rows }} 行，共 {{ detail.result?.layout?.grid_count }} 块</li>
        <li v-if="detail.note">备注：{{ detail.note }}</li>
      </ul>
    </div>
  </div>
</template>
