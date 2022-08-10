<template>  
  <div id="app">
      <MainPageVue/>
  </div>
</template>

<script>

import MainPageVue from './components/MainPage.vue'

export default {
  name: 'App',
  components: {
    MainPageVue
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-bottom: 30px;
}
</style>
