<template>
  <div class="autocomplete">
    <div class="input-group mb-2">

      <!-- <highlightable-input highlight-style="background-color:yellow" :highlight-enabled="highlightEnabled"
        :highlight="highlight" v-model="msg" /> -->

      <input type="text" class="form-control my-highlight" id="basic-url" placeholder="Ask a question..."
        aria-describedby="basic-addon3" @input="onChange" v-model="search" @keydown.down="onArrowDown"
        @keydown.up="onArrowUp" @keydown.enter="onEnter" />

      <button type="button" class="btn mb-2 mb-md-0 py-3 px-3 btn-quarternary"
        @click="getQueryResult(search)">SEND</button>
    </div>

    <ul id="autocomplete-results" v-show="isOpen" class="autocomplete-results">
      <li class="loading" v-if="isLoading">Loading results...</li>
      <li v-else v-for="(result, i) in results" :key="i" @click="setResult(result)" class="autocomplete-result"
        :class="{ 'is-active': i === arrowCounter }">
        {{  result  }}
      </li>
    </ul>

    <br />
    Entered Query:
    <span v-for="item in inputArray" :key="item">
      <Highlighter class="my-highlight" :style="{ color: 'black' }" highlightClassName="highlight" :searchWords="keywordArray"
      :autoEscape="true" :textToHighlight="item+' '" :highlightStyle="{ backgroundColor: dataKeyword[item] }" />
    </span>
   
      <!-- <Highlighter class="my-highlight" :style="{ color: 'black' }" highlightClassName="highlight" :searchWords="keywords"
      :autoEscape="true" :textToHighlight="search" :highlightStyle="{ backgroundColor: '#4FB47F' }" /> -->

    <br />
  </div>
</template>

<script>
import axios from 'axios';
import Highlighter from 'vue-highlight-words'
import HighlightableInput from 'vue-highlightable-input'

export default {
  name: "AutoComplete",
  components: {
    HighlightableInput,
    Highlighter
  },
  props: {
    watchState: {
      type: Boolean,
      required: false,
      default: false
    },
    newValue: {
      type: String,
      required: false,
      default: ""
    },
    items: {
      type: Array,
      required: false,
      default: () => [],
    },
    isAsync: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      isOpen: false,
      results: [],
      search: "",
      isLoading: false,
      arrowCounter: -1,
      msg: '',

      keywordArray: [
        "chicken",
        "noodle",
        "soup",
        "so"
      ]
      ,
      dataKeyword: 
        {
        'chicken': "#f37373" ,
        'noodle': "#fca88f" ,
         'soup': "#bbe4cb" ,
         'so': "#fff05e" 
        },
      inputArray: []

    };
  },
  computed: {
    keywords() {
      inputArray = this.search.split(' ')
    }
  },
  watch: {
    items: function (value, oldValue) {
      if (value.length !== oldValue.length) {
        this.results = value;
        this.isLoading = false;
      }
    },
    watchState: function () {

      this.search += " " + this.newValue

    }
  },
  mounted() {
    document.addEventListener("click", this.handleClickOutside);
  },
  unmounted() {
    document.removeEventListener("click", this.handleClickOutside);
  },
  methods: {
    getQueryResult(queryQuestion) {
      axios
        .get("http://127.0.0.1:8000/nlp/query/", {
          params: {
            query: queryQuestion,
          },
        })
        .then((res) => this.$emit("updateData", res.data))
        .catch((error) => console.log(error));
    },
    setResult(result) {

      this.inputArray[this.inputArray.length-1] = result;
      this.search = this.inputArray.join(" ")
      this.isOpen = false;
    },
    filterResults() {
      this.results = this.items.filter((item) => {
        return item.toLowerCase().indexOf(this.inputArray[this.inputArray.length-1].toLowerCase()) > -1;
      });
    },
    onChange() {
      this.inputArray = this.search.split(' ')
      this.filterResults();
      // console.log(this.inputArray)
      this.$emit("input", this.search);

      if (this.inputArray[this.inputArray.length-1] != "") {
        
        this.isOpen = true;
      }

      if (this.results.length == 0) {
          this.isOpen = false;
      }

    },
    handleClickOutside(event) {
      if (!this.$el.contains(event.target)) {
        this.isOpen = false;
        this.arrowCounter = -1;
      }
    },
    onArrowDown() {
      if (this.arrowCounter < this.results.length) {
        this.arrowCounter = this.arrowCounter + 1;
      }
    },
    onArrowUp() {
      if (this.arrowCounter > 0) {
        this.arrowCounter = this.arrowCounter - 1;
      }
    },
    onEnter() {
      this.search += this.results[this.arrowCounter];
      this.isOpen = false;
      this.arrowCounter = -1;
    },
  },
};
</script>

<style>
.autocomplete {
  position: relative;
}

.autocomplete-results {
  padding: 0;
  margin: 0;
  border: 1px solid #eeeeee;
  height: 120px;
  overflow: auto;
}

.autocomplete-result {
  list-style: none;
  text-align: left;
  padding: 4px 2px;
  cursor: pointer;
}

.autocomplete-result.is-active,
.autocomplete-result:hover {
  background-color: #4aae9b;
  color: white;
}

.btn.btn-quarternary {
  color: #fff;
  border-color: #a1dd70;
  background: #4FB47F;
}
</style>
