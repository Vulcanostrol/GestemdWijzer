<script setup lang="ts">
const { subjects } = defineProps<{
  partyA: string,
  partyB: string,
  subjects: {
    subject: string,
    explanation: string,
  }[],
}>()

defineEmits([ 'close' ])
</script>

<template>
  <div class="motion-disagreements">
    <h1>Verschillen {{ partyA }} en {{ partyB }}</h1>
    <details v-for="subject in subjects" :key="subject.subject">
      <summary>{{ subject.subject }}</summary>
      {{ subject.explanation }}
    </details>
    <button @click="$emit('close')">
      <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px">
        <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
      </svg>
    </button>
  </div>
</template>

<style scoped>
div.motion-disagreements {
  position: fixed;
  box-sizing: border-box;
  padding: 32px 12px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  max-width: calc(100vw - 24px);
  height: 800px;
  max-height: calc(100vh - 24px);
  text-align: left;
  background: white;
  color: black;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  z-index: 9999;
  cursor: auto;
  details {
    margin-bottom: 12px;
    summary {
      font-weight: bold;
      cursor: pointer;
    }
  }
  button {
    position: absolute;
    top: 8px;
    right: 8px;
    border-radius: 9999px;
    width: 48px;
    height: 48px;
    background-color: rgba(0, 0, 0, 0);
    border: none;
    outline: none;
    transition: background-color 0.2s ease-in-out;
    &:hover {
      background-color: rgba(0, 0, 0, 0.1);
      cursor: pointer;
    }
    svg {
      fill: black;
    }
  }
}
</style>