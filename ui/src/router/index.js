import Vue from 'vue';
import Router from 'vue-router';
import Home from '@/components/Home';
import BootstrapVue from 'bootstrap-vue';
import fa from 'fontawesome-vue';
import vueScrollto from 'vue-scrollto'

Vue.use(vueScrollto)
Vue.use(fa);
Vue.use(Router);
Vue.use(BootstrapVue);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
    },
  ],
});
