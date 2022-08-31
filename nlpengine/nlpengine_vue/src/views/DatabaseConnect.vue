<template>
  <div class="hello connect_db" style="height: 100%">
    <div
      id="myCarousel"
      class="carousel slide"
      data-bs-ride="carousel"
      style="width: 100%; height: 100vh; background-color: rbga(0, 0, 0, 1)"
    >
      <div
        class="carousel-inner"
        role="listbox"
      >
        <div
          class="carousel-item item active"
        >
          <img
            src="../assets/image1.jpg"
            style="width: 100%; height: 100%; object-fit: cover"
            alt=""
          />
        </div>
        <div class="carousel-item item">
          <img
            src="../assets/image2.png"
            style="width: 100%; height: 100%; object-fit: cover"
            alt=""
          />
        </div>
        <div class="carousel-item item">
          <img
            src="../assets/image3.jpg"
            style="width: 100%; height: 100%; object-fit: cover"
            alt=""
          />
        </div>
      </div>
    </div>
    <div class="align-middle">
      <div class="d-flex justify-content-center my-5 py-5">
        <img
          src="../assets/holistics.png"
          alt=""
          style="background-color: white; width: 30%; padding: 1%;"
        />
      </div>
      <h1 class="text-center my-3 py-3 text-color">
        Welcome to Holistics' NLP Engine
      </h1>
      <h4 class="text-center my-3 py-3 text-color">
        Explore your own database through data visualization
      </h4>
      <div class="d-flex justify-content-center">
        <!-- Button trigger modal -->
        <button
          type="button"
          class="btn btn-holistics text-center"
          data-bs-toggle="modal"
          data-bs-target="#exampleModal"
        >
          Connect to Database
        </button>

        <!-- Modal -->
        <div
          class="modal fade"
          id="exampleModal"
          tabindex="-1"
          aria-labelledby="exampleModalLabel"
          aria-hidden="true"
        >
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="exampleModalLabel">
                  New Data Source
                </h5>
                <button
                  type="button"
                  class="btn-close"
                  data-bs-dismiss="modal"
                  aria-label="Close"
                ></button>
              </div>
              <div class="modal-body">
                <div class="container">
                  <div class="row">
                    <div class="col-6">
                      <label for="basic-url" class="form-label">Host</label>
                      <div class="input-group mb-3">
                        <input
                          type="text"
                          class="form-control"
                          id="basic-url"
                          aria-describedby="basic-addon3"
                          v-model="host"
                        />
                      </div>
                    </div>
                    <div class="col-6">
                      <label for="basic-url" class="form-label">Port</label>
                      <div class="input-group mb-3">
                        <input
                          type="text"
                          class="form-control"
                          id="basic-url"
                          aria-describedby="basic-addon3"
                          v-model="port"
                        />
                      </div>
                    </div>
                  </div>

                  <div class="row">
                    <div class="col">
                      <label for="basic-url" class="form-label"
                        >Database Name</label
                      >
                      <div class="input-group mb-3">
                        <input
                          type="text"
                          class="form-control"
                          id="basic-url"
                          aria-describedby="basic-addon3"
                          v-model="name"
                        />
                      </div>
                    </div>
                  </div>
                  <div class="row">
                    <div class="col-6">
                      <label for="basic-url" class="form-label">Username</label>
                      <div class="input-group mb-3">
                        <input
                          type="text"
                          class="form-control"
                          id="basic-url"
                          aria-describedby="basic-addon3"
                          v-model="user"
                        />
                      </div>
                    </div>
                    <div class="col-6">
                      <label for="basic-url" class="form-label">Password</label>
                      <div class="input-group mb-3">
                        <input
                          type="text"
                          class="form-control"
                          id="basic-url"
                          aria-describedby="basic-addon3"
                          v-model="password"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <div v-if="failedConnect" style="color: red">Cannot connect to this database!</div>
                <button
                  type="button"
                  class="btn btn-success"
                  @click="connectDatabase()"
                >
                  CONNECT
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <h5 class="text-center my-3 py-3 text-color">
        Supported database: PostgreSQL
      </h5>
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
      password: "",
    };
  },
  methods: {
    connectDatabase() {
      axios
        .get("http://127.0.0.1:8000/nlp/database/connect/", {
          params: {
            name: this.name,
            type: "postgres",
            host: this.host,
            port: this.port,
            user: this.user,
            password: this.password,
          },
        })
        .then((res) => {
          if (res.data.message == "Success") {
            window.location.replace("http://localhost:8080/query");
          } else {
            this.failedConnect = true;
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
.item {
  position: fixed;
  width: 100%;
  height: 100%;
}
.item:after {
  content: "";
  display: block;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
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
  opacity: 0.75;
  background: rgba(0, 0, 0, 1);
}
.carousel {
  z-index: -99;
}
.carousel {
  position: fixed;
  top: 0;
  width: 100%;
  height: 100vh;
  opacity: 0.75;
}
.text-color {
  text-align: center;
  margin-top: 20px;
  padding: 10px;
  text-shadow: 2px 2px #000;
  color: #fff;
}
</style>