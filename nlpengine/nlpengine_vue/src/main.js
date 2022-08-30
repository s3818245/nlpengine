import "bootstrap/dist/css/bootstrap.css"
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import VChartkick from 'vue-chartkick'
import 'chartkick/chart.js'
import '@fortawesome/fontawesome-free/js/all'
import HighlightableInput from "vue-highlightable-input"

let app = createApp(App);
app.use(VChartkick);
app.use(router);
app.use(HighlightableInput)
app.use(store);
app.mount('#app')

import "bootstrap/dist/js/bootstrap.js"


