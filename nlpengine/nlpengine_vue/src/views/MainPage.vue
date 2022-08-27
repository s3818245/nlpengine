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
        <div class="col-2"></div>
        <div class="col-8">
          <div class="row">
            <label for="basic-url" class="form-label">Business Question</label>
            <AutoCompleteVue
              @updateData="updateDataFromChild($event)"
              :items="[
                'Apple',
                'Banana',
                'Orange',
                'Mango',
                'Pear',
                'Peach',
                'Grape',
                'Tangerine',
                'Pineapple',
              ]"
            />
            <br />
          </div>

          <div class="card">
            <div class="card-body">
              <div class="card h-100 my-2">
                <div class="card-body">
                  <bar-chart
                    v-if="barChartData != undefined"
                    :data="barChartData">
                  </bar-chart>
                  <div v-if="queryData != undefined && queryData.result != undefined">
                    <table class="table table-dark table-striped-columns">
                      <thead>
                        <tr>
                          <th scope="col">#</th>

                          <th
                            v-for="(item, key) in queryData.result"
                            :key="item.id"
                          >
                            {{ key }}
                          </th>
                        </tr>
                      </thead>

                      <tbody>
                        <tr v-for="num in queryData.rowCount" :key="num">
                          <td scrop="col">{{ num }}</td>

                          <td v-for="item in queryData.result" :key="item.id">
                            {{ item[num - 1] }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              <br />
              <ul
                class="
                  nav nav-tabs nav-pills
                  with-arrow
                  lined
                  flex-sm-row
                  text-center
                  mb-3
                "
                id="pills-tab"
                role="tablist"
              >
                <li class="nav-item" role="presentation">
                  <a
                    class="
                      nav-link
                      active
                      text-uppercase
                      font-weight-bold
                      rounded-0
                      border
                    "
                    id="pills-profile-tab"
                    data-bs-toggle="pill"
                    data-bs-target="#pills-sql"
                    type="button"
                    role="tab"
                    aria-controls="pills-sql"
                    aria-selected="false"
                    >SQL Query</a
                  >
                </li>
                <li class="nav-item" role="presentation">
                  <a
                    class="
                      nav-link
                      text-uppercase
                      font-weight-bold
                      rounded-0
                      border
                    "
                    id="pills-profile-tab"
                    data-bs-toggle="pill"
                    data-bs-target="#pills-json"
                    type="button"
                    role="tab"
                    aria-controls="pills-json"
                    aria-selected="false"
                    >JSON Data</a
                  >
                </li>
              </ul>

              <div class="tab-content h-100" id="pills-tabContent">
                <div
                  class="tab-pane fade show active"
                  id="pills-sql"
                  role="tabpanel"
                  aria-labelledby="pills-profile-tab"
                >
                  <div class="card bg-light" style="height: 100%">
                    <div class="card-body">
                      <pre>{{
                        queryData != undefined
                          ? formatSQL(queryData?.sqlQuery)
                          : ""
                      }}</pre>
                    </div>
                  </div>
                </div>
                <div
                  class="tab-pane fade"
                  id="pills-json"
                  role="tabpanel"
                  aria-labelledby="pills-profile-tab"
                >
                  <div class="card bg-light" style="height: 100%">
                    <div class="card-body">
                      <vue-json-pretty
                        :path="'res'"
                        :data="
                          queryData != undefined ? queryData.expStruct : []
                        "
                        @click="handleClick"
                      >
                      </vue-json-pretty>
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
import VueJsonPretty from "vue-json-pretty";
import "vue-json-pretty/lib/styles.css";
import { format } from "sql-formatter";
import AutoCompleteVue from "../components/AutoComplete.vue";
import { assertExpressionStatement } from "@babel/types";

export default {
  name: "MainPage",
  components: {
    VueJsonPretty,
    AutoCompleteVue,
  },
  props: {
    msg: String,
  },
  data() {
    return {
      chosen: "",
      queryData: undefined,
      barChartData: undefined,
      input: "",
      item: {},
      items: [
        { id: 1, name: "Golden Retriever" },
        { id: 2, name: "Cat" },
        { id: 3, name: "Squirrel" },
      ],
    };
  },
  methods: {
    updateDataFromChild(data) {
      if (
        data.expStruct.visualization &&
        data.expStruct.visualization == "Bar_Chart"
      ) {
        console.log("aloha")
        var result = {}
        var keyArray = Object.keys(data.result)
        console.log(keyArray.length)
        for (var i = 1; i < keyArray.length; i++) {
           for ( var y = 0; y < data.rowCount; y++) {
              var key = data.result[keyArray[0]][y]
              result[key] = data.result[keyArray[i]][y]
           }
        }
        this.barChartData = result;
        this.queryData = {'expStruct': data.expStruct, 'sqlQuery': data.sqlQuery}
      } else {
        this.barChartData = undefined
        this.queryData = data;
      }
    },
    formatSQL(value) {
      return format(value, {
        language: "postgresql",
        tabWidth: 2,
        keywordCase: "upper",
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
  },
};

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
  background-color: #4fb47f;
  color: white;
}
</style>