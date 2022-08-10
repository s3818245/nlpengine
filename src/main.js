import "bootstrap/dist/css/bootstrap.css"
import { createApp } from 'vue'
import App from './App.vue'

import VChartkick from 'vue-chartkick'
// import VueSuggestion from 'vue-suggestion'

import 'chartkick/chart.js'

let app = createApp(App);
app.use(VChartkick);
app.mount('#app')

import "bootstrap/dist/js/bootstrap.js"

