(function () {                                //prevent the page from loading from cache - so that the user either
	window.onpageshow = function(event) {       // gets the last saved query results, or a blank context for a new query
		if (event.persisted) {
			window.location.reload();
		}
	};
})()

/*Generating global variables - "today" for the calender widget creation, and sub-objects which when compiled together
form the body of an ajax request for querying the results. They are kept in the global scope so that the individual
functions and choices that the user makes can update them instantly*/
let today = new Date()
let datePacker = {}
let paginationPacker = {}
let queryTypePacker = {}
let currencyTypePacker = {}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

reqPack = function() {
  /**
   * A function that gets the global variables with the query options in their current state and forms the main
   *  object with all the attributes via which an ajax request with the query parameters is made
   */
  let package = {}
  package['data'] = {}
  package.data['time'] = datePacker
  package.data['pagination'] = paginationPacker
  package.data['query_type'] = queryTypePacker
  package.data['query_currency'] = currencyTypePacker
  return package
}

function xhrSend(package, responseFunction, ...args) {        //function that defines the parameters of a standard ajax
  let xhr = new XMLHttpRequest()                              // request for query results
  xhr.open('POST', '/api/tables', true)
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
  xhr.setRequestHeader('Accept', 'application/json;charset=UTF-8')
  xhr.send(JSON.stringify(package))
  xhr.onload = function() {
    if (xhr.status == 200) {
      responseFunction(...args, xhr.response)
    }
  }
}

var postQuery = function() {
  /**
   * A wrapper for the xhrSend function, defining the callback function for the response, and also preventing the
   *  request from being sent if it has incomplete data (dates missing, as the main element). It also clears the
   *  results of a previous query and appends the new ones
   */
  let test = typeof(reqPack()['data']['time']['dates'])
  if (test != 'undefined') {
    xhrSend(reqPack(), queryTableMaker, 'queried-results')
  } else {
    let holder = document.getElementById('queried-results')
    if (holder != null) {
      holder.innerHTML = ' '
      let info = document.createElement('div')
      info.textContent = 'no dates selected'
      info.id = 'no-results'
      holder.append(info)
    }
  }
}

function Calender(                                                //TODO proper line breaks?
  year=(new Date(today).getFullYear()),
  month=(new Date(today).getMonth()),
  day=(new Date(today).getDay())
  ) {
  /**
   * A function that creates the calender object from the JS Date object. It takes three arguments, if a specific
   * time is necessary, or creates the calender for the current time by default. Two constants with name mappings
   * for days and months are created, so that one could render the days/months either as a number or a name.
   * Multiple attributes and methods are defined for the object, so that the relevant data can be displayed/processes
   *  in whichever format necessary.
   *
   */
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  function daysMapper(year, month) {                             //get all the days from the month in number format
    let daysTotal = new Date(year, month+1, 0).getDate()        //get the last day of the month to determine the number
    let days = []                                               // of days in that month
    for (let i = 1; i < (daysTotal + 1); i++) {
      let x = [i, (new Date(year, month, i).getDay())]
      days.push(x)
    }
    return days
  }

  function weeksMapper(day_mapper) {
   /**
    * A function to organize all the days in a month into an array of weeks - takes the array with all the enumerated
    *  days in that month as an argument.
    * Three conditions defined for the loop:
    *  -if the day is not Sunday (0) and the day is not the last day of the month - push to current week array
    *  -else if the last day of the month (Sunday or not) - add it to current week array and push the week to weeks
    *  -else the day is Sunday - add it to the current week array and push the week array to weeks
    */
    var weeks = []                        //weeks array that gets populated with individual week arrays defined below
    var week = []                                     //week array that, when populated, is added to weeks and emptied
    for (let i = 0; i < day_mapper.length; i++) {
      if ((day_mapper[i][1] != 0) && (day_mapper[i][0] != day_mapper.slice(-1)[0][0])) {
        week.push(day_mapper[i])
      } else if (day_mapper[i][0] == day_mapper.slice(-1)[0][0]) {
        week.push(day_mapper[i])
        weeks.push(week)
        week = []
      } else {
        week.push(day_mapper[i])
        weeks.push(week)
        week = []
      }
    }
    return weeks
  }

  function arraySlicer (array, start, end) {           //local helper function for custom slicing of arrays
    return array.slice(start, end)
  }

  this.day = day
  this.day_named = days[this.day]
  this.month = month
  this.month_named = months[this.month]
  this.previousMonth = month-1
  this.nextMonth = month+1
  this.month_named = months[this.month]
  this.year = year

  this.daysMapper = daysMapper
  this.arraySlicer = arraySlicer
  this.days = (daysMapper(this.year, this.month))
  this.weeks = (weeksMapper(this.days))

  this.firstWeek = this.weeks[0]
  this.lastWeek = this.weeks[this.weeks.length-1]

  //gets the missing days of the first week of the month from the previous month, if that week does not start on Monday
  this.preWeek = (function() {
    let previous = this.daysMapper(this.year, this.previousMonth)
    let preLength = 7 - this.firstWeek.length
    if (preLength !=0) {
      return this.arraySlicer(previous, -preLength)
    }
  }.bind(this))()

  //gets the missing days of the last week of the month from the next month, if that week does not end on Sunday
  this.postWeek = (function() {
    let next = this.daysMapper(this.year, this.nextMonth)
    let postLength = 7 - this.lastWeek.length
    if (postLength !=0) {
      return this.arraySlicer(next, 0, postLength)
    }
  }.bind(this))()

  this.no_days = (function () {
    return new Date(month, year, 0).getDate();
  }())
}

function generateCalender(
  year=(new Date(today).getFullYear()),
  month=(new Date(today).getMonth()),
  day=(new Date(today).getDay())) {
 /**
  * A function to organize all the days in a month into an month table/calendar. It uses the Calender object defined
  *  above to access various attributes necessary to define the appearance and functionality of the calender widget,
  *  which is used to make queries.
  * Month and year defined as global variables, so that other functions can access them to - "monthGlobal" is mostly
  *  used for creating date strings, so the number has to be incremented by 1 in order to display it properly (i.e.
  *  month enumeration going from 1-12, instead of JS date object 0-11 enumeration)
  */
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  window['monthGlobal']=month+1                   //defines month and year as global too, so that other functions can
  window['yearGlobal']=year                       // access them too.
  function dayLooper(theWeek, row, boolean=0) {
   /**
    * A function that populates table rows which represent weeks with html nodes for days in that week.
    * It does not generate the row/week, but takes a pre-created week/row node as an argument, because the last
    *  and first weeks of the month often contain days from the next/previous months. Due to that, this function gets
    *  called conditionally once or twice based on the existence of the pre/post days (twice for the first week and last
    *  week potentially) within a block of code for a single week within the for loop for weeks below.
    */
    theWeek.forEach(day => {
      let td = document.createElement('td')
      let div = document.createElement('div')
      let text = document.createTextNode(day[0])
      if (boolean) {
        td.classList.add('outer-day')
      } else {
        td.classList.add('day')
      }
      div.append(text); td.append(div); row.append(td)
    })
  }

  let table = document.createElement('table')
  let header = document.createElement('thead')
  let body = document.createElement('tbody')
  let header_row = document.createElement('tr')
  table.append(header)
  table.append(body)
  header.append(header_row)
  table.id = 'calender'

  for (let i = 0; i < 7; i++) {                      //creating the calender TH/header cells
    let cell = document.createElement('th')
    let div = document.createElement('div')
    cell.append(div)
    div.append(days[i].slice(0, 3))               //first three letters of the name of the day for table headers
    header.append(cell)
  }

  let calenderHolder = document.getElementById('calender-holder')       //get the existing html node
  calenderHolder.append(monthNav())                   //appends the small month-navigation element
  calenderHolder.append(table)
  let content = new Calender(year, month, day)

  for (let i = 0; i < content.weeks.length; i++) {   //for each week create a table row, and populate it via the
    let row = document.createElement('tr')        // dayLooper function. The row gets populated via a combination
    row.classList.add('week')                     // of calls to the dayLooper function - it gets called once or twice
    body.append(row)
    let week = content.weeks[i]

    if ((i==0 ) && content.preWeek) {             //if it is the first week and it contains days from the previous month
      dayLooper(content.preWeek, row, true)
    }

    dayLooper(week, row)                          //always called - for the days of the week belonging to current month

    if ((i==(content.weeks.length-1) ) && content.postWeek) {        //if it is the last week and it contains days
      dayLooper(content.postWeek, row, true)                        // from the following month
    }
  }

  if (content.weeks.length==5) {                   //since a month can have 4 or 6 weeks (incomplete 6), this conditional
    var row = document.createElement('tr')        // creates 1 or 2 "phantom" placeholder rows, so that the position
    body.append(row)                              // of the elements on the page does not shift when the user browses
    for (let i = 0; i<7; i++) {                      // through the calender
      var td = document.createElement('td')
      var div = document.createElement('div')
      td.append(div); row.append(td);
      td.setAttribute('style', 'border: 1px solid transparent')     //TODO ADD AS A CLASS TO PARENT!!!
    }
    body.append(row)
  }
  timeMarker()                                    //adds an event listener to the calender
}

function timeMarker() {
   /**
    * A function that creates an event listener on the calender widget.
    * It uses the value of the global variable "mode" (variable editable via the element created by "monthModes"
    *  function) to define which element of the month gets selected and queried - a day, a week, or a month.
    * It adds visual confirmation for the selection into the calender, updates the global querying object, and on click
    *  event instantly creates a new ajax request with the to-query data, serving the results back into the table.
    */
  let cal = document.getElementById('calender')
  cal.addEventListener('click', function(e) {
    if (mode == 'day') {                                           //TODO restructure it as a switch in the future?
      let target = e.target.closest('td.day')
      let targetChild = target.children[0]
      let remover = this.querySelectorAll('td div')
      remover.forEach(day => {day.classList.remove('clicked')})   //remove the class for marking the dates from
      targetChild.classList.add('clicked')                        // previously selected and add it to newly selected
      let day = targetChild.textContent
      let date = datePipeline(yearGlobal, monthGlobal, day, mode) //helper function for creating the date strings
      datePacker['dates'] = date                                  //updates the global variable used for query requests
      datePacker['day'] = day                                     //updates the global variable used for query requests
    } else if (mode == 'week') {
      let target = e.target.closest('tr.week')
      let weeks = document.body.getElementsByClassName('week')
      let weekNo = [...weeks].indexOf(target) + 1
      let days = target.querySelectorAll('div')
      days = Array.from(days)
      let remover = this.querySelectorAll('td div')
      remover.forEach(day => {day.classList.remove('clicked')})
      days.forEach(day => {day.classList.add('clicked')})
      /*
      "additional" argument used in datePipeline function (only for the weeks) - if the "outer days" (from past or
      following month) are contained in the selected week, this info is used in the weekParser function to return
      the correct month for those days.
      */
      let additional
      if (days[0].parentNode.className == 'outer-day') {
        additional = 'pre'                                          //pre = contains days from the past month
      } else if (days[6].parentNode.className == 'outer-day') {
        additional = 'post'                                         //post = contains days from the following month
      } else {
        additional = 'mid'                              //mid = all the days of the week are from the current month
      }
      days = days.map(x => x.textContent)
      let dates = datePipeline(yearGlobal, monthGlobal, days, mode, additional)
      datePacker['dates'] = dates
      datePacker['week'] = weekNo
    } else if (mode == 'month') {
      let target = e.target.closest('tbody')
      let days = target.querySelectorAll('.day div')
      days = Array.from(days)
      var remover = this.querySelectorAll('td div')
      remover.forEach(day => {day.classList.remove('clicked')})
      days.forEach(day => {day.classList.add('clicked')})
      days = days.map(x => x.textContent)
      let dates = datePipeline(yearGlobal, monthGlobal, days, mode)
      datePacker['dates'] = dates
    } else {
      //pass
    }
    datePacker['year'] = yearGlobal                     //updates the global variable used for query requests with
    datePacker['month'] = monthGlobal                   // data shared between the mode options, and add the chosen
    datePacker['mode'] = mode                           // mode to it + make an ajax request with the new query
    postQuery()
  })
}

function dateFormat(Y, M, D) {                           //function returning dates as a string in a necessary format
 /**
  * A function that returns a date as a string in the necessary format for making queries.
  * Used as stand-alone when user makes queries in "day" mode, or as a nested function in datePipeline functions
  *  which return dates for "month" and "week" query modes.
  */
  var D = D, M = String(M)
  D.length < 2 ? (D = ('0'+ D)) : (D = D);
  M.length < 2 ? (M = ('0'+ M)) : (M = M);

  return (Y+'-'+ M + '-' + D)
}

function weekDatesParser(Y, M, D, additional) {
 /**
  * A function used in a datePipeline function in the case when user queries the result by weeks.
  * It takes all the days of a week, and in case that the week contains days from the past or following month,
  *  it returns those days as dates with a proper non-current month.
  */
  let innerDays, outerDays, dates
  switch(additional) {
    case('mid'):
      dates = D.map(day => dateFormat(Y, M, day))
      return dates
      break
    case('pre'):
    case('post'):
      let firstPart = []                      //denoting the first part of the week
      let secondPart = []                     //denoting the second part of the week
      /*
      For loop with a ternary operator, used to split the week into two parts if the week days belong to two different
      months (first and last week scenarios). The logic in both cases is the same - the beginning days of the week
      have a higher number than the ones at the end of the week, and as long as the day number is greater than the
      number of the last day of of the week, they get pushed into the "first part". As soon as the condition changes,
      the remaining days get pushed to the "second part" of the week. There is a fall through sub-switch statement
      for these scenarios, based on which the "outer days"/non-current month days get their month changed.
      */
      for (let i = 0; i <D.length; i++) {
        (parseInt(D[i])>parseInt(D[6])) ? firstPart.push(D[i]) : secondPart.push(D[i])
      }
    switch(additional) {
      case('pre'):
        innerDays = secondPart.map(day => dateFormat(Y, M, day))
        M == 1 ? (M = 12, Y = parseInt(Y)-1) : (M = parseInt(M)-1)    //year change if the current month is January
        outerDays = firstPart.map(day => dateFormat(Y, M, day))
        dates = outerDays.concat(innerDays)
        return dates
        break
      case('post'):
        innerDays = firstPart.map(day => dateFormat(Y, M, day))
        M == 12 ? (M = 11, Y = parseInt(Y)+1) : (M = parseInt(M)+1)   ////year change if the current month is December
        outerDays = secondPart.map(day => dateFormat(Y, M, day))
        dates = innerDays.concat(outerDays)
        return dates
        break
    }
  }
}

  function monthDatesParser(Y, M, D) {                     //returns dates for the first and the last day of the month
  let firstDay = D[0]
  let lastDay = D[D.length-1]
  let monthScope = [dateFormat(Y, M, firstDay), dateFormat(Y, M, lastDay)]
  return monthScope
}

function datePipeline(Y, M, D, mode, additional=0) {      //function handling the return of proper date formats for
  switch(mode) {                                          // all three query modes.
    case 'day':
      return dateFormat(Y, M, D)
      break
    case 'week':
      return weekDatesParser(Y, M, D, additional)
      break
    case 'month':
      return monthDatesParser(Y, M, D)
      break
    case 'period':      //TODO to be added later on
      //pass
      break
  }
}

function monthModes() {
 /**
  * A function used to create a button group for selecting the query mode - day, week, or month.
  */
  let month = document.createElement('div')
  month.id='modes-group'
  let buttonDay = document.createElement('button')
  let buttonWeek = document.createElement('button')
  let buttonMonth = document.createElement('button')
  buttonDay.id = 'day-mode'; buttonDay.textContent = 'day'
  buttonWeek.id = 'week-mode'; buttonWeek.textContent = 'week'
  buttonMonth.id = 'month-mode'; buttonMonth.textContent = 'month'
  month.append(buttonDay, buttonWeek, buttonMonth)

  month.addEventListener('click', function(e) {
    var target = e.target
    if (month.querySelectorAll('.clicked')[0]) {
      current = month.querySelectorAll('.clicked')[0]       //when a new mode is selected, calender days get deselected
      if (target.id != current.id) {
        let cleaner = document.querySelectorAll('div .clicked')
        cleaner.forEach(day => {day.classList.remove('clicked')})
        datePacker={}
        postQuery()
      }
    }

    let outers = document.body.querySelectorAll('.outer-day div')     //days not belonging to the current month to
    if (target.id == 'week-mode') {                                   // be displayed only for the "week" query mode
      outers.forEach(day => {day.classList.remove('hidden')})
    } else {
      outers.forEach(day => {day.classList.add('hidden')})
    }

    if (target.tagName=='BUTTON') {                         //when a new mode is selected, other modes get deselected
      let holder = target.closest('#modes-group')
      holder = Array.from(holder.children)
      holder.forEach(button => {button.classList.remove('clicked')})
      target.classList.add('clicked')
      mode = target.textContent
    }
  })
  document.getElementById('calender-holder').prepend(month)   //not returned but prepended, because it should stay
}                                                             // separate from the calender which changes dynamically,
                                                              // keeping the chosen option when the calender changes
function monthNav() {
 /**
  * A function used to create a navigation element above the calender, showing the current month and year, and allowing
  *  the user to move one month forward or backward in time.
  */
  let calenderHolder = document.getElementById('calender-holder')
  let content = new Calender(yearGlobal, monthGlobal -1)      //generates the Calender object only to access its
  let month = document.createElement('nav')                   // attributes in order to properly display month and year
  month.id='month-nav-container'
  let navList = document.createElement('ul')
  navList.id = 'month-nav'
  let larr = document.createElement('li')
  larr.id = 'prev-month'; larr.textContent = '<'
  let monthName = document.createElement('li')
  monthName.id = 'month-name'; monthName.textContent = (content.month_named + ' ' + content.year)
  let rarr = document.createElement('li')
  rarr.id = 'next-month'; rarr.textContent = '>'

  navList.append(larr, monthName, rarr)
  month.append(navList)

  larr.addEventListener('click', function() {                 //add event listener for the left arrow, to generate a
    let x = document.getElementById('month-nav-container')    // calender widget for the previous month
    datePacker = {}
    postQuery()                                           //used here to inform the user to select dates, which happens
    x.remove()                                            // without sending the request if no dates are selected
    calender.remove()
    let year = content.year
    let month = content.month - 1
    if (content.month == 0) {                             //if current month is January, change also the year when
      month = 11                                          // moving backward in time
      year = year - 1
    }
    generateCalender(year, month)
  })
  rarr.addEventListener('click', function() {
    let x = document.getElementById('month-nav-container')    //add event listener for the right arrow, to generate a
    datePacker = {}                                           // calender widget for the following month
    postQuery()
    x.remove()
    calender.remove()
    let year = content.year
    let month = content.month +1
    if (content.month == 11) {                            //if current month is December, change also the year when
      month = 0                                           // moving forward in time
      year = year + 1
    }
    generateCalender(year, month)
  })
  return month
}

function queryUnpacker(query) {
 /**
  * A function used to reconstruct the last query when the user comes to the overview page. This happens either
  *  after editing/deleting data of an item, or if the user decided to save and redisplay the last query
  *  (profile settings).
  * It uses the same object which was sent as an ajax query request - this object gets returned as a response and
  *  optionally saved to the database
  * Sub functions and blocks below parse the data from that object and re-create/check/click all the options, thus
  *  also resending the last query and displaying the page as it was when the query was made.
  *
  *
  */
  query = JSON.parse(query)['data']                             //parse the original object with the query data
  generateCalender(query.time.year, query.time.month-1)
  let activatePagination = document.getElementById('pagination')
  activatePagination.value = query.pagination.limit
  activatePagination.dispatchEvent(new Event('change'))

  if (Object.keys(query.query_type).length != 0) {    //if user used Item/Category filter, they get reconstructed here
    let qtype = query.query_type
    let noResults = document.getElementById('type-query-buttons').children
    let key = Object.keys(qtype)[0]
    let value = qtype[key]
    let button = [...noResults].filter(element => (element.textContent == key))[0]
    button.click()
    let input = document.getElementById('type-query')
    input.value = value
    input.dispatchEvent(new Event('change'))          //change event triggers the updating of the global query object
  }                                                   // which has to be sent in order to get the same results

  document.getElementById(query.time.mode + '-mode').click()  //click/select the saved time query mode - day/week/month

  switch(query.time.mode) {                                   //select relevant day/days in the calender
    case('day'):
      let days = document.querySelectorAll('.day')
      let day = [...days].filter(day => (day.textContent == query.time.day))[0]
      day.click()
      break

    case('week'):
      let weeks = document.querySelectorAll('.week')
      let week = [...weeks][query.time.week - 1]
      week.click()
      break

    case('month'):
      document.querySelectorAll('.day')[0].click()
      break
  }

  let observer = new MutationObserver(callFunc)

  function callFunc(mutationList, observer) {
 /**
  * Since the node showing the current/total pages gets dynamically created after the main function is called, i.e.
  *  depends on the results which get returned when the repeated query above is made, it is necessary to wait for
  *  the element to be inserted into the DOM in order to select the page from the original query.
  * In case there is only one page with results, nothing happens - otherwise, the last visited page gets clicked,
  *  triggering the query for that batch of results, with other query options staying the same.
  * Currency type query is considered a user setting (editable in profile settings), so it always gets loaded
  *  from user settings (separately), and not from the returned object with the data for the last query.
  */
    for (let i = 0; i < mutationList.length; i++) {
      var target = document.getElementById('#query-table-paginator')
      if (target != null) {
        if (target.hasChildNodes) {
          target = target.children
          let element = [...target].filter(page => (page.textContent == query.pagination.page))[0]
          element.click()
          observer.disconnect()
        return
        }
      } else{
        observer.disconnect()
      }
    }
  }
  let target = document.querySelector('#queried-results')
  observer.observe(target, {childList: true, subtree: true})
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

monthModes()                //create buttons for selecting the query mode - day/week/month get all the settings from the
var presets = presets       // flask route as a JSON object which gets converted into proper format in the html template

/*
"lastQuery" is only defined in the html template if the overview page should be reconstructed with the settings for the
 last query - either after editing an item, in order to let user get back to the same page, or if the user opted to
  save the last queries and redisplay them when landing on the overview page.
*/

createQueryOptions('queried-holder', presets)
if (Object.keys(lastQuery).length != 0 ) {            //if lastQuery is defined - reconstruct the page and the query
  queryUnpacker(lastQuery)
} else {                                              //else - generate an empty Calender with default settings/options
  generateCalender()
}







