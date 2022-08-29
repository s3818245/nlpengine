<template>
  <div class="hello connect_db" style="height: 100%;">
    <nav class="navbar navbar-expand-lg bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Holistics NLP</a>
      </div>
    </nav>
    <div id="myCarousel" class="carousel slide" data-bs-ride="carousel">
      <div class="carousel-inner" role="listbox" style=" position: absolute; top: 0; right: 0; left: 0; bottom: 0;">
        <div class="carousel-item item active">
          <img src="../assets/image1.jpg" style="width: 100%; height: 100%; object-fit: cover;" alt="">
        </div>
        <div class="carousel-item item">
          <img src="../assets/image2.png" style="width: 100%; height: 100%; object-fit: cover;" alt="">
        </div>
        <div class="carousel-item item">
          <img src="../assets/image3.jpg" style="width: 100%; height: 100%; object-fit: cover;" alt="">
        </div>
      </div>
    </div>
    <div class="align-middle">
      <div class="d-flex justify-content-center">
        <img class="my-5 py-5" src="../assets/holistics.png" alt="" style="background-color: white; width: 30%;">
      </div>
      <h1 class="text-center my-5 py-5 text-color">Welcome to Holistics' NLP Engine</h1>
      <h4 class="text-center my-5 py-5 text-color">
        Explore your own database through data visualization
      </h4>
      <div class="d-flex justify-content-center">
        <!-- Button trigger modal -->
        <button type="button" class="btn btn-holistics text-center text-color" data-bs-toggle="modal"
          data-bs-target="#exampleModal">
          Connect to Database
        </button>

        <!-- Modal -->
        <div class="modal fade" id="exampleModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="exampleModalLabel">
                  New Data Source
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <div class="container">
                  <div class="row">
                    <div class="col-6">
                      <label for="basic-url" class="form-label">Host</label>
                      <div class="input-group mb-3">
                        <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3"
                          v-model="host" />
                      </div>
                    </div>
                    <div class="col-6">
                      <label for="basic-url" class="form-label">Port</label>
                      <div class="input-group mb-3">
                        <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3"
                          v-model="port" />
                      </div>
                    </div>
                  </div>

                  <div class="row">
                    <div class="col">
                      <label for="basic-url" class="form-label">Database Name</label>
                      <div class="input-group mb-3">
                        <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3"
                          v-model="name" />
                      </div>
                    </div>
                  </div>
                  <div class="row">
                    <div class="col-6">
                      <label for="basic-url" class="form-label">Username</label>
                      <div class="input-group mb-3">
                        <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3"
                          v-model="user" />
                      </div>
                    </div>
                    <div class="col-6">
                      <label for="basic-url" class="form-label">Password</label>
                      <div class="input-group mb-3">
                        <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3"
                          v-model="password" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-primary" @click="connectDatabase()">CONNECT</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <h5 class="text-center my-3 py-3 text-color">Supported database: PostgreSQL</h5>
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "DatabaseConnect",
  data() {
    return {
      name: "",
      host: "",
      port: "",
      user: "",
      failedConnect: false,
      password: NaN
    }
  },
  methods: {
    connectDatabase() {
      axios
        .get("http://127.0.0.1:8000/nlp/database/", {
          params: {
            name: "nlp_demo",
            type: "postgres",
            host: "localhost",
            port: 5432,
            user: "postgres",
            password: this.password
          },
        })
        .then((res) => {
          if (res.data.message == "Success") {
            window.location.replace("http://localhost:8080/query")
          } else {
            this.failedConnect = true
          }
        })
        .catch((error) => console.log(error));
    },
  },

};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}

.text-color {
  color: black;
  
  -webkit-text-fill-color: transparent;
  -webkit-text-stroke: 1px;
}

.btn-holistics {
  background-color: #4fb47f;
}

.carousel-fade .carousel-inner .item {
  opacity: 0;
  transition-property: opacity;
  background: rgba(0, 0, 0, 1);
}

.carousel-fade .carousel-inner .active {
  opacity: 0.5;
  background: rgba(0, 0, 0, 1);
}

/* .carousel-fade .carousel-inner .active.left,
.carousel-fade .carousel-inner .active.right {
  left: 0;
  opacity: 0;
  z-index: 1;
}

.carousel-fade .carousel-inner .next.left,
.carousel-fade .carousel-inner .prev.right {
  opacity: 1;
}

.carousel-fade .carousel-control {
  z-index: 2;
} */

/* @media all and (transform-3d),
(-webkit-transform-3d) {

  .carousel-fade .carousel-inner>.item.next,
  .carousel-fade .carousel-inner>.item.active.right {
    opacity: 0;
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
  }

  .carousel-fade .carousel-inner>.item.prev,
  .carousel-fade .carousel-inner>.item.active.left {
    opacity: 0;
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
  }

  .carousel-fade .carousel-inner>.item.next.left,
  .carousel-fade .carousel-inner>.item.prev.right,
  .carousel-fade .carousel-inner>.item.active {
    opacity: 1;
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
  }
} */

/* .item:nth-child(1) {
  background: no-repeat center center fixed;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  background-color: rgba(0, 0, 0, 1);
}

.item:nth-child(2) {
  background: no-repeat center center fixed;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  background-color: rgba(0, 0, 0, 1);
}

.item:nth-child(3) {
  background: no-repeat center center fixed;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  background-color: rgba(0, 0, 0, 1);
} */

.carousel {
  z-index: -99;
}

.carousel .item {
  position: fixed;
  width: 100%;
  height: 100%;
  opacity: 0.75;
}


.carousel-item::after {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.6);
}

.title {
  text-align: center;
  margin-top: 20px;
  padding: 10px;
  text-shadow: 2px 2px #000;
  color: #FFF;
}
</style>