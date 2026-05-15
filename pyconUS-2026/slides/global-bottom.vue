<script setup lang="ts">
import { ref } from 'vue'

const open = ref(false)

function toggle() {
  open.value = !open.value
  document.documentElement.classList.toggle('goto-open', open.value)
}
</script>

<template>
  <button
    class="goto-toggle"
    :class="{ active: open }"
    title="Toggle slide list"
    @click="toggle"
  >
    ☰
  </button>
</template>

<style scoped>
.goto-toggle {
  position: fixed;
  bottom: 1.25rem;
  right: 1.25rem;
  z-index: 9999;
  width: 2rem;
  height: 2rem;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(30, 33, 41, 0.45);
  backdrop-filter: blur(6px);
  color: rgba(255, 255, 255, 0.35);
  font-size: 0.85rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.goto-toggle:hover {
  background: rgba(30, 33, 41, 0.75);
  color: rgba(255, 255, 255, 0.7);
  border-color: rgba(255, 255, 255, 0.25);
}
.goto-toggle.active {
  background: rgba(105, 240, 174, 0.15);
  color: #69f0ae;
  border-color: rgba(105, 240, 174, 0.4);
}
</style>
