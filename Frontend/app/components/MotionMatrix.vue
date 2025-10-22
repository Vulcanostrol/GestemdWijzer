<script setup lang="ts">
import {ref} from 'vue'

type PartyVoteMapping = {
  DENK: number,
  PvdD: number,
  SP: number,
  ['GroenLinks-PvdA']: number,
  Volt: number,
  D66: number,
  ChristenUnie: number,
  NSC: number,
  CDA: number,
  SGP: number,
  VVD: number,
  BBB: number,
  JA21: number,
  PVV: number,
  FVD: number,
}


type VoteMatrix = {
  DENK: PartyVoteMapping,
  PvdD: PartyVoteMapping,
  SP: PartyVoteMapping,
  ['GroenLinks-PvdA']: PartyVoteMapping,
  Volt: PartyVoteMapping,
  D66: PartyVoteMapping,
  ChristenUnie: PartyVoteMapping,
  NSC: PartyVoteMapping,
  CDA: PartyVoteMapping,
  SGP: PartyVoteMapping,
  VVD: PartyVoteMapping,
  BBB: PartyVoteMapping,
  JA21: PartyVoteMapping,
  PVV: PartyVoteMapping,
  FVD: PartyVoteMapping,
}

const matrix = ref<VoteMatrix | undefined>(undefined);
const parties = ref<string[] | undefined>(undefined);

const config = useRuntimeConfig();
const apiBase = config.public.apiBase;
console.log(apiBase);

onMounted(async () => {
  const result = await fetch(`${apiBase}/api/v1/votes/matrix`);
  if (result.status !== 200) throw new Error(`Failed to fetch votes. Status ${result.status}`);
  const matrixData = await result.json();
  matrix.value = matrixData;
  parties.value = Object.keys(matrixData);
});
</script>

<template>
  <table>
    <thead>
      <tr>
        <th />
        <th
          v-for="party in parties"
          :key="party"
          class="party-name"
        >
          {{ party }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="party in parties" :key="party">
        <td class="party-name">{{ party }}</td>
        <MotionMatrixCell
          v-for="(percentage, party2) in matrix[party]"
          :key="party2"
          :party-a="party"
          :party-b="party2 as string"
          :percentage="percentage"
        />
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
table {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'Roboto', sans-serif;
  --cell-size: 50px;
  th, td {
    padding: 0.5rem;
    text-align: right;
    &.party-name {
      font-weight: bold;
    }
  }
  th {
    writing-mode: vertical-rl;
    height: auto;
    transform: rotate(-30deg) translate(-25px, -15px);
  }
}

@media (max-width: 768px) {
  table {
    inset: 0;
    transform: none;
    tbody {
      overflow-x: auto;
      overflow-y: auto;
    }
  }
}
</style>