<template>
  <div class="hello">
    <h1 class="text-center">Welcome to Holistics' NLP Engine</h1>
    <br/>
    <br/>
    <br/>
    <h4 class="text-center">Explore your own database through data visualization</h4>
    <br/>

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
                    <h5 class="modal-title" id="exampleModalLabel">New Data Source</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="container">
                        <div class="row">
                            <div class="col">
                                <label for="basic-url" class="form-label">Display Name</label>
                                <div class="input-group mb-3">
                                    <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-6">
                                <label for="basic-url" class="form-label">Host</label>
                                <div class="input-group mb-3">
                                    <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3">
                                </div>
                            </div>
                            <div class="col-6">
                                <label for="basic-url" class="form-label">Post</label>
                                <div class="input-group mb-3">
                                    <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3">
                                </div>
                            </div>
                        </div>

                        <div class="row">
                            <div class="col">
                                <label for="basic-url" class="form-label">Database Name</label>
                                <div class="input-group mb-3">
                                    <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-6">
                                <label for="basic-url" class="form-label">Username</label>
                                <div class="input-group mb-3">
                                    <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3">
                                </div>
                            </div>
                            <div class="col-6">
                                <label for="basic-url" class="form-label">Password</label>
                                <div class="input-group mb-3">
                                    <input type="text" class="form-control" id="basic-url" aria-describedby="basic-addon3">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary">Test Connection</button>
                </div>
                </div>
            </div>
        </div>
    </div>
    

    <br/>
    <br/>
    <h5 class="text-center">Supported database: PostgreSQL</h5>
    
  </div>
</template>

<script>
export default {
  name: 'DbConnect',
  props: {
    msg: String
  }
}
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
