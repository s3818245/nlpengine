<template>
  <div class="hello">
    <nav class="navbar navbar-expand-lg bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Holistics NLP</a>
      </div>
    </nav>
    <br />
    <br />
    <div class="container-fluid">
      <div class="row">
        <div class="col-2">

        </div>
        <div class="col-8">
          <div class="row">
            <label for="basic-url" class="form-label">Business Question</label>
            <div class="input-group mb-3">
              <input type="text" class="form-control" id="basic-url" placeholder="Ask a question..."
                aria-describedby="basic-addon3" required v-model="input">
              <button type="button" class="btn mb-2 mb-md-0 py-3 px-4 btn-quarternary">SEND</button>
            </div>
            <vue-suggestion :items="items" v-model="item" :setLabel="setLabel" :itemTemplate="itemTemplate"
              @changed="inputChange" @selected="itemSelected">
            </vue-suggestion>
          </div>


          <div class="card">
            <div class="card-body">
              <div class="card h-100 my-2">
                <div class="card-body">
                  <bar-chart
                    :data="{ '2021-01-01': 11, '2021-01-02': 6, '2021-01-03': 20, '2021-01-04': 15, '2021-01-05': 4, '2021-01-06': 40 }">
                  </bar-chart>

                </div>
              </div>
              <br />
              <ul class="nav nav-tabs nav-pills with-arrow lined flex-sm-row text-center mb-3" id="pills-tab"
                role="tablist">

                <li class="nav-item" role="presentation">
                  <a class="nav-link active text-uppercase font-weight-bold rounded-0 border" id="pills-profile-tab"
                    data-bs-toggle="pill" data-bs-target="#pills-sql" type="button" role="tab" aria-controls="pills-sql"
                    aria-selected="false">SQL Query</a>
                </li>
                <li class="nav-item" role="presentation">
                  <a class="nav-link text-uppercase font-weight-bold rounded-0 border" id="pills-profile-tab"
                    data-bs-toggle="pill" data-bs-target="#pills-json" type="button" role="tab"
                    aria-controls="pills-json" aria-selected="false">JSON Data</a>
                </li>
              </ul>

              <div class="tab-content h-100" id="pills-tabContent">

                <div class="tab-pane fade show active" id="pills-sql" role="tabpanel"
                  aria-labelledby="pills-profile-tab">
                  <div class="card bg-light" style="height: 100%;">
                    <div class="card-body">
                      <pre>{{ formatSQL(sqlData) }}</pre>
                    </div>
                  </div>

                </div>
                <div class="tab-pane fade" id="pills-json" role="tabpanel" aria-labelledby="pills-profile-tab">
                  <div class="card bg-light" style="height: 100%;">
                    <div class="card-body">
                      <vue-json-pretty :path="'res'" :data="jsonData" @click="handleClick"> </vue-json-pretty>
                    </div>
                  </div>

                </div>
              </div>

            </div>
          </div>



        </div>
        <div class="col-2"></div>
      </div>
    </div>
  </div>
</template>

<script>
import itemTemplate from './item-template.vue';
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import { format } from 'sql-formatter';

export default {

  name: 'MainPage',
  components: {
    VueJsonPretty,
  },
  props: {
    msg: String
  },
  data() {
    return {
      input: '',
      jsonData: [
        {
          "dimensions": [
            {
              "table_name": "name",
              "field_name": "column_name"
            }
          ],
          "measures": [
            {
              "table_name": "name",
              "field_name": "column_name",
              "aggregation_type": "count"
            }
          ],
          "filters": [
            {
              "field": {
                "table_name": "name",
                "field_name": "column_name"
              },
              "operator": "equal",
              "values": "123"
            }
          ]
        }
      ],
      sqlData:
        "select * from Employee a where  rowid = (select max(rowid) from Employee b where  a.Employee_no=b.Employee_no);",
      item: {},
      items: [
        { id: 1, name: 'Golden Retriever' },
        { id: 2, name: 'Cat' },
        { id: 3, name: 'Squirrel' },
      ],
      itemTemplate,
    }
  },
  methods: {
    formatSQL(value) {
      return format(value, {
        language: 'postgresql',
        tabWidth: 2,
        keywordCase: 'upper',
        indentStyle: "tabularLeft",
        linesBetweenQueries: 2,
      });
    },
    itemSelected(item) {
      this.item = item;
    },
    setLabel(item) {
      return item.name;
    },
    inputChange(text) {
      // your search method
      this.items = this.items.filter((item) => item.name.indexOf(text) > -1);
      // now `items` will be showed in the suggestion list
    },

  }
}

// document.getElementById("json").innerHTML = JSON.stringify(jsonData, undefined, 2);


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

.lined .nav-link {
  border: none;
  border-bottom: 3px solid transparent;
}

.lined .nav-link.active {
  background: none;
  color: #555;
  border-color: #282c34;
}

.nav-pills .nav-link {
  color: #555;
}

.text-uppercase {
  letter-spacing: 0.1em;
}

.nav-tabs .nav-item .nav-link.active {
  background-color: #4FB47F;
  color: white;
}

.btn.btn-quarternary {
  color: #fff;
  border-color: #a1dd70;
  background: #4FB47F;
}

</style>
