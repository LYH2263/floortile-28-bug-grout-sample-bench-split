<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const settings = ref({})
const groutMm = ref(0)
const msg = ref('')
const err = ref('')
onMounted(async () => {
  settings.value = await getJSON('/api/settings')
  groutMm.value = Number(settings.value.grout_mm ?? 0)
})
async function save() {
  err.value = ''
  msg.value = ''
  try {
    settings.value = await postJSON('/api/settings', { grout_mm: groutMm.value })
    msg.value = '已保存，默认缝宽只影响新测算'
  } catch (e) {
    err.value = e.message
  }
}
</script>
<template>
  <div class="page">
    <h1>损耗规则</h1>
    <p>默认损耗率按面积法向上取整后再乘 (1+损耗%)。</p>
    <p>当前默认损耗：<strong>{{ settings.waste_pct }}%</strong></p>
    <label>默认缝宽(mm) <input type="number" v-model.number="groutMm" min="0" step="0.5" /></label>
    <button @click="save">保存默认缝宽</button>
    <p v-if="msg" class="ok">{{ msg }}</p>
    <p v-if="err" class="alert">{{ err }}</p>
    <p>有效边长 = 砖边 − 缝宽，有效单片面积进入面积法 raw，网格预览按有效边长排布。</p>
    <p>网格预览块数可能大于面积法片数，下单以面积法 order_count 为准。</p>
  </div>
</template>
