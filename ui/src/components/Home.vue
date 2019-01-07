<template>
  <div>

      <div class="home-background"></div>
      <div class="home-background-2"></div>

      <div class="circle-right"></div>
      <div class="blur-right"></div>
      <div class="circle-left"></div>
      <div class="blur-left"></div>
      <div class="footer-background"></div>



      <div class="time-line-mask">
          <img src="../assets/images/time-line.png" alt="">
      </div>
      <div class="navBar">
          <div class="menu">
              <a v-scroll-to="'#home'" class="menu-item active" >خانه </a>
              <a  v-scroll-to="'#info'" class="menu-item " >معرفی</a>
              <a  v-scroll-to="'#awards'" class="menu-item " >جوایز</a>
              <a  v-scroll-to="'#timing'" class="menu-item " >برنامه </a>
              <a  v-scroll-to="'#footer'" class="menu-item ">تماس باما</a>
          </div>

          <div class="left-menu">
              <div class="float-left h-100 p-1 mr-2 ">
                  <i class="fa fa-bars text-white h-100"></i>
              </div>
              <div class="float-left h-100 p-1 mr-2">
                  <i class="fa fa-question text-white h-100"></i>
              </div>

              <div class="float-left h-100 p-1 mr-2">
                  <i class="fa fa-globe-americas text-white h-100"></i>
              </div>
              <div class="float-left h-100 p-1 mr-2">
                  <i class="fa fa-user text-white h-100"></i>
              </div>

          </div>

      </div>

      <div class="content mx-auto">
          <!--<div id="title" class="col-12 p-0 mt-4 ">-->
              <!--<b-row class="m-0">-->
                  <!--<b-col cols="5" class="title   mt-4 p-0">-->
                      <!--<b-col cols="6" class="title-sharif ">-->
                          <!--SHARIF-->
                      <!--</b-col>-->
                      <!--<b-col class="data-days p-0" cols="12">-->

                      <!--</b-col>-->
                      <!--<b-col cols="12" class="title-info p-0">-->
                          <!--<b-col cols="6" class="float-left title-name  h-100 ">-->
                              <!--<h5 >نخستین مسابقـه</h5>-->
                              <!--<h4>عـلــوم داده</h4>-->
                              <!--<b-col cols="12">-->
                              <!--<span></span>-->
                              <!--<span></span>-->
                              <!--<span>شریف</span>-->
                                  <!--<h6>15 و 16 اسفندماه 1397</h6>-->
                                  <!--<h6>مرحله غیرحضور بهمن 1397</h6>-->
                              <!--</b-col>-->
                          <!--</b-col>-->
                          <!--<b-col cols="6" class="float-left title-date border h-100"></b-col>-->
                      <!--</b-col>-->
                  <!--</b-col>-->
                  <!--<b-col class="p-0 logo-dark   ">-->
                  <!--</b-col>-->
                  <!--<b-col class="p-0 logo-light   "></b-col>-->
              <!--</b-row>-->

          <!--</div>-->
          <b-col id="home" cols="12" class="home mb-4">
              <b-col class="home-info">
                  <h1>نخستین مسابقه علوم داده</h1>

              </b-col>
              <div class="timer ">
                  <b-row class="m-0 h-100 text-center">
                      <b-col cols="3" class="h-100 p-0">
                          <div class="timer-box mx-auto"><span> 19 </span> </div>
                          <span>روز</span>
                      </b-col>
                      <b-col cols="3" class="h-100 p-0">
                          <div class="timer-box mx-auto"><span> 20 </span> </div>
                          <span>ساعت</span>
                      </b-col>
                      <b-col cols="3" class="h-100 p-0">
                          <div class="timer-box mx-auto"><span> 36 </span> </div>
                          <span>دقیقه</span>
                      </b-col>
                      <b-col cols="3" class="h-100 p-0">
                          <div class="timer-box mx-auto"><span> 45 </span> </div>
                          <span>ثانیه</span>
                      </b-col>

                  </b-row>
              </div>
          </b-col>
          <b-col id="info" cols="11" class="mx-auto info p-0">
              <h4 class="text-right m-0"> معرفی </h4>
              <p class="p-4">
                  اولین رویداد علوم داده دانشگاه شریف، data days، یک مسابقه چند مرحله‌ای آموزشی است. مهمترین هدف از برگزاری این مسابقه گسترش آموزش و علاقه در این حوزه به همراه محک زدن سطح دانش علوم داده در جامعه علمی ایران است. این رویداد با همکاری جمعی از دانشجویان دانشکده مهندسی کامپیوتر و با پشتیبانی اساتید پیشگام در این حوزه طراحی شده‌است. اگر چه تنها شرط شرکت در مسابقه دانشجو بودن است مسائل این مسابقه به گونه ای است که شرکت کنندگان با هر سطحی از دانش از مبتدی تا متخصص بتوانند آورده‌ای از مسابقات داشته باشند.
              </p>
              <b-col cols="12" class="p-2 text-center">
                  <b-button class="info-btn border-0"> شرکت در مسابقه </b-button>
              </b-col>
          </b-col>
          <b-col id="awards" cols="11" class="mx-auto awards mt-3">
              <h4 class="m-0 text-right"> جوایز</h4>
              <b-col cols="10" class="awards-info-1 mx-auto">
                  <b-col cols="4" class="awards-info-two float-right h-75 mt-5 pt-3">
                      <h5 class="text-center p-2"> تیم دوم </h5>
                      <h4 class="text-center"> 5میلیون تومان </h4>
                  </b-col>
                  <b-col cols="4" class="awards-info-one float-right h-100">
                      <h5 class="text-center p-3"> تیم قهرمان </h5>
                      <h4 class="text-center"> 7میلیون تومان </h4>
                  </b-col>
                  <b-col cols="4" class="awards-info-three float-right h-75 mt-5 pt-3">
                      <h5 class="text-center p-2"> تیم سوم </h5>
                      <h4 class="text-center"> 3میلیون تومان </h4>
                  </b-col>
              </b-col>
              <b-col cols="8" class="awards-info-2 mx-auto mt-5 mb-3">
                  <b-col cols="6" class="awards-info-four float-right h-100">
                      <h5 class="text-center p-2"> دو تیم از بین تیم های 4 تا 10: </h5>
                      <h4 class="text-center"> 2میلیون تومان </h4>
                  </b-col>
                  <b-col cols="6" class="awards-info-five float-right h-100">
                      <h5 class="text-center p-2"> دو تیم از بین تیم های 10 تا 20: </h5>
                      <h4 class="text-center"> 1میلیون تومان </h4>
                  </b-col>

              </b-col>
          </b-col>

          <b-col id="timing" cols="12" class="mx-auto timing">
              <h4 class="text-right m-0"> برنامه زمان بندی  </h4>

              <div class="timing-item text-center item-1">
                  <h5 class="">25دی ماه</h5>
                  <h4 class="">
                      شروع ثبت نام
                  </h4>
              </div>
              <div class="timing-item text-center item-2">
                  <h5 class=""> 10تا16بهمن ماه</h5>
                  <h4 class="">مسابقه اول غیرحضوری</h4>
              </div>
              <div class="timing-item text-center item-3">
                  <h5 class="">16بهمن ماه تا2اسفندماه  </h5>
                  <h4 class="">مسابقه دوم غیرحضوری</h4>
              </div>
              <div class="timing-item text-center item-4">
                  <h5 class="">15و16اسفندماه</h5>
                  <h4 class="">مسابقه حضوری </h4>
              </div>

          </b-col>

          <b-col id="footer" cols="12" class="footer"></b-col>

      </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
    date(){
      return{
         active:'home',

        }
    },
    computed:{

    },
    mounted() {



    },
    methods: {

    },

};
</script>

<style scoped lang="scss">
    .home-background{
        position: absolute;
        width: 100%;
        height: 860px;
        top: 0;
        left:0;
        z-index: -1;
        background: url("../assets/images/Main-Section.jpg") no-repeat center center;
        background-size:100% ;
    }
    .home-background-2{
        position: absolute;
        width: 100%;
        height: 200px;
        top: 700px;
        left:0;
        z-index: -1;
        background: url("../assets/images/wave.png") no-repeat center center;
        background-size:100% ;
    }

    .circle-right{
        position: absolute;
        width: 400px;
        height: 400px;
        top: 740px;
        left: 0px;
        background: url("../assets/images/CircleCircle.png") no-repeat center center;
        background-size: cover;
    }
    .blur-right{
        position: absolute;
        width: 600px;
        height: 600px;
        top: 610px;
        left: -300px;
        background: #0497ec;
        border-radius: 50%;
        opacity: .08;
        filter: blur(40px);
    }



    .circle-left{
        position: absolute;
        width: 400px;
        height: 400px;
        top: 2200px;
        right: 0px;
        background: url("../assets/images/CircleCircle.png") no-repeat center center;
        background-size: cover;
        transform: rotate(180deg);
    }
    .blur-left{
        position: absolute;
        width: 600px;
        height: 600px;
        top: 2100px;
        right: -300px;
        background: #0497ec;
        border-radius: 50% ;
        opacity: .08;
        filter: blur(40px);
    }


    .footer-background{
        background: url("../assets/images/footerWave.svg") no-repeat center center;
        background-size:100% ;
        position: absolute;
        width: 100%;
        height: 340px;
        top: 2800px;
        left: 0;
        z-index: -1;
    }


    .time-line-mask{
        position: absolute;
        width: 100%;
        height: 300px;
        top: 1820px;
        left: 0;
        right: 0;
        img{
            width: 100%;
        }
    }



    .navBar{
        width: 100%;
        height: 22px;
        line-height: 20px;
        .menu{
            float: right;
            height: 100%;
            a{
                cursor: pointer;
                text-decoration: none;

            }
            .menu-item{
                color: #036398;
                font-size:12px ;
                float: right;
                /*border: 1px solid red;*/
                height: 100%;
                padding: 0px 12px;
            }
            .menu-item.active{
                border:1px solid #036398;
                border-radius: 4px;
                color: #eeeeee;

            }
        }
        .left-menu{
            height: 100%;
            float: left;
            width: 40%;
            i{
                font-size:12px;
                line-height: initial;
                vertical-align: top;
            }
        }
    }

    .content{
        margin: 0 auto 5vh;
        position: relative;
        width: 82vw;

        .home{
            height: 800px;
            .home-info{
                opacity: 0;

            }
            .timer{
                width: 290px;
                margin: 650px auto 0;
                height: 72px;
                .timer-box{
                    width: 54px;
                    height: 50px;
                    border:1.4px solid #0081cb;
                    border-radius: 2.5px;
                    line-height: 48px;
                    span{
                        color: #eeeeee;
                        font-size: 27.8px;
                    }
                }
                span{
                    color:#0081cb;
                    font-size: 15.6px;
                }

            }
        }

        .info{
            margin-bottom: 100px;
            direction: rtl;
            height: 300px;
            color: #f5f5f5;
            font-family: Shabnam;
            h4{
                font-size: 18.5px;
            }

            p{
                font-size: 14.8px;
                text-align: justify;

            }
            .info-btn{
                border-radius: 25px;
                font-size: 17px;

                background: linear-gradient(45deg,#0e5aec,#64d9f5);
            }
        }
        .awards{
            margin-bottom: 100px;
            direction: rtl;
            color: #f5f5f5;
            font-family: Shabnam;
            overflow: hidden;
            h4{
                font-size: 18.5px;
            }
            .awards-info-1{
                height: 230px;
                font-family: Shabnam;


                .awards-info-one{
                    background: url("../assets/images/avval.png") no-repeat center center ;
                    background-size: 90%;
                    h5{
                        color: #0497ec;
                        font-size: 15px;
                    }
                    h4{
                        color: #f5f5f5;
                        font-size: 21px;
                        margin-top: 130px;

                    }
                }
                .awards-info-two,
                .awards-info-three{
                    background: url("../assets/images/dovvom.png") no-repeat center 24% ;
                    background-size: 80%;
                    h5{
                        color: #0497ec;
                        font-size: 13.5px;
                    }
                    h4{
                        color: #f5f5f5;
                        font-size: 17.2px;
                        margin-top: 100px;
                    }
                }

                .awards-info-three{
                    background: url("../assets/images/sevvom.png") no-repeat center 24% ;
                    background-size: 80%;
                }
            }
            .awards-info-2{
                height: 170px;
                .awards-info-four,
                .awards-info-five{

                    background: url("../assets/images/chaharrom.png") no-repeat center 30% ;
                    background-size: 80%;
                    h5{
                        font-size: 13.5px;
                        color: #0497ec;
                    }
                    h4{
                        font-size: 17.2px;
                        color: #f5f5f5;
                        margin-top: 120px;
                    }
                }

                .awards-info-five{

                    background: url("../assets/images/panjom.png") no-repeat center 36% ;
                    background-size: 80%;
                }
            }

        }
        .timing{
            margin-bottom: 100px;
            height: 300px;
            direction: rtl;
            color: #f5f5f5;
            font-family: Shabnam;

            h4{
                font-size: 18.5px;
            }
            .timing-item{
                float: right;
                position: relative;
                height: 100px;
                h4{
                    color: #f5f5f5;
                    font-size: 15.32px;
                    margin-top: 50px;

                }
                h5{
                    color: #0081cb;
                    font-size: 12.2px;
                }

                &.item-1{
                    top: 120px;
                    right: 138px;
                }
                &.item-2{
                    top: 98px;
                    right: 250px;
                }
                &.item-3{
                    top: 120px;
                    right: 376px;
                }
                &.item-4{
                    top: 28px;
                    right: 478px;
                }

            }
        }
        .footer{
            height: 400px;
        }

    }

    @media screen and (min-width: 1370px) {
        .home-background{
            background-size:80% ;
        }
        .home-background-2{
            height: 300px;
            top: 800px;
        }

        .circle-right{

            top: 840px;
        }
        .blur-right{
            top: 710px;
        }



        .circle-left{
            position: absolute;
            width: 400px;
            height: 400px;
            top: 2200px;
            right: 0px;
            background: url("../assets/images/CircleCircle.png") no-repeat center center;
            background-size: cover;
            transform: rotate(180deg);
        }
        .blur-left{
            position: absolute;
            width: 600px;
            height: 600px;
            top: 2100px;
            right: -300px;
            background: #0497ec;
            border-radius: 50% ;
            opacity: .08;
            filter: blur(40px);
        }


        .footer-background{
            height: 460px;
            top: 2700px;
        }


        .time-line-mask{

            top: 1886px;
        }



        .navBar{
            width: 100%;
            height: 22px;
            line-height: 20px;
            .menu{
                float: right;
                height: 100%;
                a{
                    text-decoration: none;

                }
                .menu-item{
                    color: #036398;
                    font-size:12px ;
                    float: right;
                    /*border: 1px solid red;*/
                    height: 100%;
                    padding: 0px 12px;
                }
                .menu-item.active{
                    border:1px solid #036398;
                    border-radius: 4px;
                    color: #eeeeee;

                }
            }
            .left-menu{
                height: 100%;
                float: left;
                width: 40%;
                i{
                    font-size:12px;
                    line-height: initial;
                    vertical-align: top;
                }
            }
        }

        .content {
            margin: 0 auto 5vh;
            position: relative;
            width: 82vw;

            .home {

                .timer {
                    margin: 680px auto 0;
                }
            }

            .info {
                margin-top: 100px;

            }

            .awards {
                .awards-info-1 {
                    .awards-info-one {
                        background-size: 70%;

                    }

                    .awards-info-two,
                    .awards-info-three {
                        background-size: 58%;

                    }

                    .awards-info-three {
                        background-size: 58%;
                    }
                }

                .awards-info-2 {

                    .awards-info-four,
                    .awards-info-five {
                        background-size: 60%;
                    }

                    .awards-info-five {

                        background-size: 60%;
                    }
                }

            }

            .timing {
                margin-top: 180px;

                .timing-item {
                    &.item-1 {
                        top: 120px;
                        right: 10.5vw;
                    }

                    &.item-2 {
                        top: 90px;
                        right: 21.5vw;
                    }

                    &.item-3 {
                        top: 120px;
                        right: 34vw;
                    }

                    &.item-4 {
                        top: -10px;
                        right: 44.5vw;
                    }

                }
            }

            .footer {
                height: 400px;
            }
        }
        }

</style>
