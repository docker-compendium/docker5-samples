<template>
  <div class="cal">
    <calendar-view
      class="theme-default holiday-de-traditional holiday-de-official"
      :startingDayOfWeek="1"
      :items="events"
      :locale="'de'"
      v-on:click-item="eventClicked"
      v-on:show-date-change="dateChanged"
      :show-date="showDate"
    >
      <template #header="{ headerProps }">
        <calendar-view-header :header-props="headerProps" @input="dateChanged" />
      </template>
    </calendar-view>
  </div>
</template>
<script>
import { CalendarView, CalendarViewHeader } from 'vue-simple-calendar'

import request from '../util/request'
import 'vue-simple-calendar/dist/vue-simple-calendar.css'
// import 'vue-simple-calendar/dist/css/default.css'
// import 'vue-simple-calendar/dist/css/holidays-us.css'
export default {
  name: 'calendar',
  props: ['entries'],
  watch: {
    entries() {
      if (this.entries && this.entries.length) {
        this.showDate = new Date(this.entries[0].date)
      }
    },
  },
  computed: {
    events() {
      return this.entries.map((val) => {
        return {
          startDate: val.date,
          title: val.title,
          thumbnail: 'url(data:' + val.mime + ';base64,' + val.thumbnail + ')',
          id: val._id,
          url: '#_' + val._id,
        }
      })
    },
  },
  data() {
    return {
      showDate: new Date(),
    }
  },
  methods: {
    eventClicked(e) {
      console.log('EVENT clicked ', e)
      window.location.hash = '#_' + e.id
    },
    dateChanged(d) {
      console.log('Date event ', d)
      this.showDate = d
      request
        .get(
          '/entries/' +
            d.getFullYear() +
            '-' +
            (d.getMonth() + 1).toLocaleString('de', { minimumIntegerDigits: 2 })
        )
        .then((json) => {
          if (json.length) {
            this.$store.commit('setEntries', json)
            // this.entries = json
          }
        })
    },
  },
  components: {
    CalendarView,
    CalendarViewHeader,
  },
}
</script>
<style>
.cal {
  min-height: 550px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.theme-default .cv-event {
  height: auto;
  min-height: 50%;
  border-radius: 0;
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
}

.theme-default > a,
.theme-default > a:visited {
  color: black;
  background: white;
  text-decoration: none;
  opacity: 0.7;
  padding: 0.2em;
}
</style>
