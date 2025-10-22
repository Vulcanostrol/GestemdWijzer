<script setup lang="ts">
const { partyA, partyB, percentage } = defineProps<{
  partyA: string,
  partyB: string,
  percentage: number
}>()

const subjects = ref<{
  subject: string,
  explanation: string,
}[]>([]);
const showDifference = ref(false);

const config = useRuntimeConfig();
const apiBase = config.public.apiBase;
console.log(apiBase);

const openDifference = async () => {
  console.log("open difference", partyA, partyB);
  const result = await fetch(`${apiBase}/api/v1/votes/disagreements?party_a=${partyA}&party_b=${partyB}`);
  if (result.status !== 200) throw new Error(`Failed to fetch disagreements. Status ${result.status}`);
  const disagreements = await result.json();
  subjects.value = disagreements.subjects;
  showDifference.value = !showDifference.value;
}
</script>

<template>
  <td
    class="data-cell" :class="{ inverted: percentage < 70 }"
    :style="{ backgroundColor: `rgb(${255 - percentage * 3}, ${percentage * 1.5}, 75)` }"
  >
    <div class="data-cell-clicker" @click="openDifference">{{ percentage }}%</div>
    <MotionDisagreements v-if="showDifference" :party-a="partyA" :party-b="partyB" :subjects="subjects" @close="showDifference = false" />
  </td>
</template>

<style scoped>
td {
  position: relative;
  min-width: var(--cell-size);
  height: var(--cell-size);
  .data-cell-clicker {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    &:hover {
      background-color: #3355ff !important;
      color: #ffffff;
    }
  }
}
</style>