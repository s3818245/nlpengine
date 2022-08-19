import "bootstrap/dist/css/bootstrap.css"
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import VChartkick from 'vue-chartkick'
import 'chartkick/chart.js'

let app = createApp(App);
app.use(VChartkick);
app.use(router);
app.use(store);
app.mount('#app')

import "bootstrap/dist/js/bootstrap.js"


