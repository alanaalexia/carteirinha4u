<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* Zera as margens para ocupar a tela toda */
header {
  line-height: 1.5;
  max-height: 100vh;
}

body {
  margin: 0;
  padding: 0;
}
</style>