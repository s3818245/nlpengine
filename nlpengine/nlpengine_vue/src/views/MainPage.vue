<template>
  <div class="hello">
    <!-- <nav class="navbar navbar-expand-lg bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Holistics NLP</a>

        <div class="d-flex">
          <button type="button" class="btn mb-2 mb-md-0 py-2 px-2 btn-quarternary">End Session</button>
        </div>
      </div>
    </nav> -->

    <div class="sidebar" :style="{ width: sidebarWidth }">
      <h1>
        <span v-if="collapsed">
          <div>N</div>
          <div>E</div>
        </span>
        <span v-else>
          NLP Engine
        </span>
      </h1>

      <div>
        <div v-if="!collapsed">
          <div class="" v-for="num in 5" :key="num">
            <div class="d-flex align-items-center">

              <div class="d-flex ms-0">
                <button class="btn mx-2 my-2" type="button" data-bs-toggle="collapse" :data-bs-target="'#table' + num"
                  aria-expanded="false" :aria-controls="'table' + num">
                  v
                </button>
                <h5 class="align-self-center">Table name</h5>
              </div>

              <button class="btn me-0 mx-2 my-2 w-25" type="button">
                <img src="https://cdn-icons-png.flaticon.com/512/875/875623.png" />
              </button>

            </div>
            <div class="collapse" :id="'table' + num">
              <div class="d-flex flex-column mb-3">

                <button type="button" class="btn field py-1 mx-2 my-2"
                  @click="addToInput('Column name 1')">Column name 1</button>
                <button type="button" class="btn field py-1 mx-2 my-2"
                  @click="addToInput('Column name 2')">Column name 2</button>
                <button type="button" class="btn field py-1 mx-2 my-2"
                  @click="addToInput('Column name 3')">Column name 3</button>
              </div>
            </div>
          </div>
        </div>
        <div v-else></div>
      </div>


      <div v-if="!collapsed">
        <button type="button" class="btn mb-2 mb-md-0 py-2 px-2 btn-quarternary">End Session</button>
      </div>
      <div v-else>
        <button type="button" class="btn mb-2 mb-md-0 py-2 px-2 btn-quarternary">
          <i class="fa-solid fa-circle-stop"></i>
        </button>
      </div>
      <span class="collapse-icon" :class="{ 'rotate-180': collapsed }" @click="toggleSidebar">
        <i class="fas fa-angle-double-left" />
      </span>
    </div>

    <br />
    <br />
    <div class="container-fluid">
      <div class="row">

        <div class="col-1 col-sm-2">

        </div>
        <div class="col-10 col-sm-8">
          <div class="row">
            <label for="basic-url" class="form-label">Business Question</label>
            <AutoCompleteVue @updateData="updateDataFromChild($event)" :newValue="input" :watchState="bool" :items="[
              'Apple',
              'Banana',
              'Orange',
              'Mango',
              'Pear',
              'Peach',
              'Grape',
              'Tangerine',
              'Pineapple',
            ]" />
            <br />
          </div>

          <div class="card">
            <div class="card-body">
              <div class="card h-100 my-2">
                <div class="card-body">
                  <bar-chart v-if="barChartData != undefined" :data="barChartData">
                  </bar-chart>
                  <div v-if="queryData != undefined && queryData.result != undefined">
                    <table class="table table-dark table-striped-columns">
                      <thead>
                        <tr>
                          <th scope="col">#</th>

                          <th v-for="(item, key) in queryData.result" :key="item.id">
                            {{  key  }}
                          </th>
                        </tr>
                      </thead>

                      <tbody>
                        <tr v-for="num in queryData.rowCount" :key="num">
                          <td scrop="col">{{  num  }}</td>

                          <td v-for="item in queryData.result" :key="item.id">
                            {{  item[num - 1]  }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              <br />
              <ul class="
                  nav nav-tabs nav-pills
                  with-arrow
                  lined
                  flex-sm-row
                  text-center
                  mb-3
                " id="pills-tab" role="tablist">
                <li class="nav-item" role="presentation">
                  <a class="
                      nav-link
                      active
                      text-uppercase
                      font-weight-bold
                      rounded-0
                      border
                    " id="pills-profile-tab" data-bs-toggle="pill" data-bs-target="#pills-sql" type="button" role="tab"
                    aria-controls="pills-sql" aria-selected="false">SQL Query</a>
                </li>
                <li class="nav-item" role="presentation">
                  <a class="
                      nav-link
                      text-uppercase
                      font-weight-bold
                      rounded-0
                      border
                    " id="pills-profile-tab" data-bs-toggle="pill" data-bs-target="#pills-json" type="button"
                    role="tab" aria-controls="pills-json" aria-selected="false">JSON Data</a>
                </li>
              </ul>

              <div class="tab-content h-100" id="pills-tabContent">
                <div class="tab-pane fade show active" id="pills-sql" role="tabpanel"
                  aria-labelledby="pills-profile-tab">
                  <div class="card bg-light" style="height: 100%">
                    <div class="card-body">
                      <pre>{{
                           queryData != undefined
                           ? formatSQL(queryData?.sqlQuery)
                           : "No Data"

                      }}</pre>
                    </div>
                  </div>
                </div>
                <div class="tab-pane fade" id="pills-json" role="tabpanel" aria-labelledby="pills-profile-tab">
                  <div class="card bg-light" style="height: 100%">
                    <div class="card-body">
                      <vue-json-pretty :path="'res'" :data="
                        queryData != undefined ? queryData.expStruct : []
                      " @click="handleClick">
                      </vue-json-pretty>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-1 col-sm-2">

        </div>
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
import { collapsed, toggleSidebar, sidebarWidth } from "@/components/sidebarState.js";

export default {
  name: "MainPage",
  components: {
    VueJsonPretty,
    AutoCompleteVue,
  },
  props: {
    msg: String,
  },
  setup() {
    return { collapsed, toggleSidebar, sidebarWidth }
  },
  data() {
    return {
      chosen: "",
      queryData: undefined,
      barChartData: undefined,
      input: "",
      bool: false,
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
          for (var y = 0; y < data.rowCount; y++) {
            var key = data.result[keyArray[0]][y]
            result[key] = data.result[keyArray[i]][y]
          }
        }
        this.barChartData = result;
        this.queryData = { 'expStruct': data.expStruct, 'sqlQuery': data.sqlQuery }
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
    addToInput(text) {
      this.bool = !this.bool
      this.input = text
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

<style>
:root {
  --sidebar-bg-color: #2f855a;
  --sidebar-item-hover: #38a169;
  --sidebar-item-active: #276749;
}
</style>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}

img {
  width: 75%;
  height: 75%;
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


.btn .btn.btn-quarternary {
  color: #fff;
  border-color: #a1dd70;
  background: #4FB47F;
}

.sidebar {
  color: white;
  background-color: var(--sidebar-bg-color);
  float: left;
  position: fixed;
  z-index: 1;
  top: 0;
  left: 0;
  bottom: 0;
  padding: 0.5em;
  transition: 0.3s ease;
  display: flex;
  flex-direction: column;
}

.sidebar h1 {
  height: 2.5em;
}

.collapse-icon {
  position: absolute;
  bottom: 0;
  padding: 0.75em;
  color: rgba(255, 255, 255, 0.7);
  transition: 0.2s linear;
}

.rotate-180 {
  transform: rotate(180deg);
  transition: 0.2s linear;
}

.field {
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  font-weight: 400;
  user-select: none;
  margin: 0.1em 0;
  padding: 0.4em;
  border-radius: 0.25em;
  height: 1.5em;
  color: white;
  text-decoration: none;
}
.field:hover {
  background-color: var(--sidebar-item-hover);
}
</style>
