<template>
  <div class="hello" style="height: 100%;">
    <nav class="navbar navbar-expand-lg bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Holistics NLP</a>
      </div>
    </nav>
    <div class="align-middle">
      <h1 class="text-center my-5 py-5">Welcome to Holistics' NLP Engine</h1>
      <h4 class="text-center my-5 py-5">
        Explore your own database through data visualization
      </h4>
      <div class="d-flex justify-content-center">
        <!-- Button trigger modal -->
        <button type="button" class="btn btn-primary text-center" data-bs-toggle="modal" data-bs-target="#exampleModal">
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
      <h5 class="text-center my-3 py-3">Supported database: PostgreSQL</h5>
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
</style>