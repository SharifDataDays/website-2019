<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>

<style lang="scss">
    @import '../node_modules/bootstrap/scss/bootstrap.scss';
    @font-face {
        src: url("../dist/static/css/fonts/IRANYekanRegular.ttf");
        font-family: yekan;
    }
@font-face {
        src: url("../dist/static/css/fonts/IRANYekanBold.ttf");
        font-family:Byekan;
    }
@font-face {
        src: url("../dist/static/css/fonts/Shabnam.ttf");
        font-family:Shabnam;
    }

    @font-face {
        src: url("../dist/static/css/fonts/NexaBold.otf");
        font-family: Nexa;
    }
    *{
        font-family:yekan ;
        box-sizing: border-box;
    }
    body{
      overflow-x: hidden;
    background: #02213d;
    padding: 28px 50px;
    margin: 0;
  }
</style>
