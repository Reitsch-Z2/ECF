(function () {
	window.onpageshow = function(event) {
		if (event.persisted) {
			window.location.reload();
		}
	};
})()


let today = new Date()
var datePacker = {}
var paginationPacker = {}
var queryTypePacker = {}
var currencyTypePacker = {}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

reqPack = function(){
  let package = {}
  package["data"] = {}
  package.data["time"] = datePacker
  package.data["pagination"] = paginationPacker
  package.data["query_type"] = queryTypePacker
  package.data["query_currency"] = currencyTypePacker
  return package
}

function xhrSend(package, responseFunction, ...args){
  let xhr = new XMLHttpRequest()                                              //TODO global or local
  xhr.open("POST", "/api/tables", true)
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")      //TODO recheck if mandatory
  xhr.setRequestHeader("Accept", "application/json;charset=UTF-8")            //TODO recheck if mandatory
  xhr.send(JSON.stringify(package))
  xhr.onload = function() {
    if (xhr.status == 200){
      responseFunction(...args, xhr.response)
    }
  }
}


var selta = function(){
  alert(JSON.stringify(reqPack()))
  let test = typeof(reqPack()["data"]["time"]["dates"])
  if (test != "undefined"){
    xhrSend(reqPack(), queryTableMaker, "queried-results")
  } else {
    let holder = document.getElementById("queried-results")
    if (holder != null){
      holder.innerHTML = " "
      let info = document.createElement("div")
      info.textContent = "no dates selected"
      info.id = "no-results"
      holder.append(info)
    }
  }
}

function Calender(year=(new Date(today).getFullYear()), month=(new Date(today).getMonth()), day=(new Date(today).getDay())){

  const days = [ "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

  function daysMapper(year, month){                              //TODO move to exterior?
    let daysTotal = new Date(year, month+1, 0).getDate()
    let days = []
    for (let i=1; i < (daysTotal+1); i++){
      let x = [i,(new Date(year, month, i).getDay())]
      days.push(x)
    }
    return days
  }

  function weeksMapper(day_mapper){                              //TODO move to exterior?

    var weeks = []
    var week = []

    for (let i=0; i < day_mapper.length; i++){
      if ((day_mapper[i][1] != 0) && (day_mapper[i][0] != day_mapper.slice(-1)[0][0])){
        week.push(day_mapper[i])
      } else if ((day_mapper[i][1] != 0) && (day_mapper[i][0] == day_mapper.slice(-1)[0][0])){
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

  function arraySlicer (array, start, end){                              //TODO move to exterior?
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

  this.preWeek = (function(){
    var previous = this.daysMapper(this.year, this.previousMonth)
    var preLength = 7 - this.firstWeek.length
    if (preLength !=0){
      return this.arraySlicer(previous, -preLength)
    }
  }.bind(this))()

  this.postWeek = (function(){
    let next = this.daysMapper(this.year, this.nextMonth)
    let postLength = 7 - this.lastWeek.length
    if (postLength !=0){
      return this.arraySlicer(next, 0, postLength)
    }
  }.bind(this))()

  this.no_days = (function (){
    return new Date(month, year, 0).getDate();
  }())

}

function generateCalender(year=(new Date(today).getFullYear()), month=(new Date(today).getMonth()), day=(new Date(today).getDay())){
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  window["monthGlobal"]=month+1                   //TODO Careful around this one! Real enum vs. JS month enum
  window["yearGlobal"]=year
  function dayLooper(theWeek, boolean=0){         //TODO only add the function to this.function instead of pre-naming?
      theWeek.forEach(day => {
      let td = document.createElement("td")
      let div = document.createElement("div")
      let text = document.createTextNode(day[0])
      if (boolean) {
        td.classList.add("outer-day")
      } else {
        td.classList.add("day")
      }
      div.append(text); td.append(div); row.append(td); body.append(row)
    })
  }

  let table = document.createElement("table")
  let header = document.createElement("thead")
  let body = document.createElement("tbody")
  let header_row = document.createElement("tr")
  table.append(header)
  table.append(body)
  header.append(header_row)
  table.id = "calender"

  for (let i=0; i < 7; i++){                //creating the calender TH/header cells
    let cell = document.createElement("th")
    let div = document.createElement("div")
    cell.append(div)
    div.append(days[i].slice(0, 3))
    header.append(cell)
  }

  let calenderHolder = document.getElementById("calender-holder")
  monthNav()
  calenderHolder.append(table)
  let content = new Calender(year, month, day)

  for (let i=0; i < content.weeks.length; i++){
    var row = document.createElement("tr")
    row.classList.add("week")
    body.append(row)

    var week = content.weeks[i]
    if ((i==0 ) && content.preWeek){
      dayLooper(content.preWeek, true)
    }
    dayLooper(week)
    if ((i==(content.weeks.length-1) ) && content.postWeek){
      dayLooper(content.postWeek, true)
    }
  }
  if (content.weeks.length==5){
    var row = document.createElement("tr")
    body.append(row)
    for (let i=0; i<7; i++){
      var td = document.createElement("td")
      var div = document.createElement("div")
      td.append(div); row.append(td);
      td.setAttribute("style", "border: 1px solid transparent")     //TODO ADD AS A CLASS TO PARENT!!!
    }
    body.append(row)
  }
  timeMarker()
}

function timeMarker(){
  let cal = document.getElementById("calender")
  cal.addEventListener("click", function(e){
    if (mode == "day"){
      let target = e.target.closest("td.day")
      let targetChild = target.children[0]
      let remover = this.querySelectorAll("td div")
      remover.forEach(day => {day.classList.remove("clicked")})
      targetChild.classList.add("clicked")
      let day = targetChild.textContent
      let date = datePipeline(yearGlobal, monthGlobal, day, mode)
      datePacker["dates"] = date
      datePacker["day"] = day
    } else if (mode == "week"){
      let target = e.target.closest("tr.week")
      let weeks = document.body.getElementsByClassName('week')
      let weekNo = [...weeks].indexOf(target) + 1
      let days = target.querySelectorAll("div")
      days = Array.from(days)
      let remover = this.querySelectorAll("td div")
      remover.forEach(day => {day.classList.remove("clicked")})
      days.forEach(day => {day.classList.add("clicked")})
      let additional
      if (days[0].parentNode.className == "outer-day"){
        additional = "pre"
      } else if (days[6].parentNode.className == "outer-day"){
        additional = "post"
      } else {
        additional = "mid"
      }
      days = days.map(x => x.textContent)
      let dates = datePipeline(yearGlobal, monthGlobal, days, mode, additional)
      datePacker["dates"] = dates
      datePacker["week"] = weekNo
    } else if (mode == "month"){
      let target = e.target.closest("tbody")
      let days = target.querySelectorAll(".day div")
      days = Array.from(days)
      var remover = this.querySelectorAll("td div")
      remover.forEach(day => {day.classList.remove("clicked")})
      days.forEach(day => {day.classList.add("clicked")})
      days = days.map(x => x.textContent)
      let dates = datePipeline(yearGlobal, monthGlobal, days, mode)
      datePacker["dates"] = dates
    } else {
      //pass
    }
    datePacker["year"] = yearGlobal         //TODO should be revised (moved up) if "period" mode is introduced
    datePacker["month"] = monthGlobal
    datePacker["mode"] = mode
    selta()
  })
}

function dateFormat(Y, M, D){               //TODO let instead of var
  var D = D, M = String(M)
  D.length < 2 ? (D = ("0"+ D)) : (D = D);
  M.length < 2 ? (M = ("0"+ M)) : (M = M);

  return (Y+"-"+ M + "-" + D)                           //TODO add sub-object with key=func for additional date formats
}

function weekDatesParser(Y, M, D, additional){
  let innerDays, outerDays, dates
  switch(additional){
    case("mid"):
      dates = D.map(day => dateFormat(Y, M, day))
      return dates
      break
    case("pre"):
    case("post"):
      let firstPart = []              //denoting the first part of the week
      let secondPart = []             //denoting the second part of the week
      for (let i = 0; i <D.length; i++){
        (parseInt(D[i])>parseInt(D[6])) ? firstPart.push(D[i]) : secondPart.push(D[i])
      }
    switch(additional){
      case("pre"):
        innerDays = secondPart.map(day => dateFormat(Y, M, day))
        M == 1 ? (M = 12, Y = parseInt(Y)-1) : (M = parseInt(M)-1)
        outerDays = firstPart.map(day => dateFormat(Y, M, day))
        dates = outerDays.concat(innerDays)
        return dates
        break
      case("post"):
        innerDays = firstPart.map(day => dateFormat(Y, M, day))
        alert(window.innerDays)
        M == 12 ? (M = 11, Y = parseInt(Y)+1) : (M = parseInt(M)+1)
        outerDays = secondPart.map(day => dateFormat(Y, M, day))
        dates = innerDays.concat(outerDays)
        return dates
        break
    }
  }
}

function monthDatesParser(Y, M, D){
  let firstDay = D[0]
  let lastDay = D[D.length-1]
  let monthScope = [dateFormat(Y, M, firstDay), dateFormat(Y, M, lastDay)]
  return monthScope

}

function datePipeline(Y, M, D, mode, additional=0){                       //TODO switsch statement with "mode" as an arg instead of type-parsing
  switch(mode){
    case "day":
      return dateFormat(Y, M, D)
      break
    case "week":
      return weekDatesParser(Y, M, D, additional)
      break
    case "month":
      return monthDatesParser(Y, M, D)
      break
    case "period":      //TODO to be added later on
      //pass
      break
  }
}

function monthModes(){
  let month = document.createElement("div")
  month.id="modes-group"
  let buttonDay = document.createElement("button")
  let buttonWeek = document.createElement("button")
  let buttonMonth = document.createElement("button")
  buttonDay.id = "day-mode"; buttonDay.textContent = "day"
  buttonWeek.id = "week-mode"; buttonWeek.textContent = "week"
  buttonMonth.id = "month-mode"; buttonMonth.textContent = "month"
  month.append(buttonDay, buttonWeek, buttonMonth)

  month.addEventListener("click", function(e){
    var target = e.target
    if (month.querySelectorAll(".clicked")[0]){                             //TODO experimental... FIRST CLICK on a mode not working proper
      current = month.querySelectorAll(".clicked")[0]
      if (target.id != current.id){
        let cleaner = document.querySelectorAll(".clicked")
        cleaner.forEach(day => {day.classList.remove("clicked")})
        datePacker={}
        selta()
      }
    }

    let outers = document.body.querySelectorAll(".outer-day div")

    if (target.id == "week-mode"){
      outers.forEach(day => {day.classList.remove("hidden")})
    } else {
      outers.forEach(day => {day.classList.add("hidden")})
    }

    if (target.tagName=="BUTTON"){
      let holder = target.closest("#modes-group")
      holder = Array.from(holder.children)
      holder.forEach(button => {button.classList.remove("clicked")})
      target.classList.add("clicked")
      mode = target.textContent
    }
  })
  document.getElementById('calender-holder').prepend(month)
}

function monthNav(){

  let calenderHolder = document.getElementById('calender-holder')
  let content = new Calender(yearGlobal, monthGlobal - 1)
  let month = document.createElement("nav")
  month.id="month-nav-container"
  let navList = document.createElement("ul")
  navList.id = "month-nav"
  let larr = document.createElement("li")
  larr.id = "prev-month"; larr.textContent = "<"
  let monthName = document.createElement("li")
  monthName.id = "month-name"; monthName.textContent = (content.month_named + " " + content.year)
  let rarr = document.createElement("li")
  rarr.id = "next-month"; rarr.textContent = ">"

  navList.append(larr, monthName, rarr)
  month.append(navList)
  calenderHolder.append(month)

  larr.addEventListener("click", function(){
    let x = document.getElementById("month-nav-container")
    datePacker = {}
    selta()
    x.remove()
    calender.remove()
    let year = content.year
    let month = content.month - 1
    if (content.month == 0){
      month = 11
      year = year -1
    }
    generateCalender(year, month)         //TODO this maybe should get passed into monthNav
  })
  rarr.addEventListener("click", function(){
    let x = document.getElementById("month-nav-container")
    datePacker = {}
    selta()
    x.remove()
    calender.remove()
    let year = content.year
    let month = content.month +1
    if (content.month == 11){
      month = 0
      year = year + 2
    }
    generateCalender(year, month)
  })
}


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


function queryUnpacker(query){
  query = JSON.parse(query)["data"]
  generateCalender(query.time.year, query.time.month-1)
  var noResults = document.getElementById('pagination')
  noResults.value = query.pagination.limit
  noResults.dispatchEvent(new Event("change"))

  if (Object.keys(query.query_type).length != 0){
    var qtype = query.query_type
    var noResults = document.getElementById('type-query-buttons').children
    var key = Object.keys(qtype)[0]
    var value = qtype[key]
    var button = [...noResults].filter(element => (element.textContent == key))[0]
    button.click()
    var input = document.getElementById('type-query')
    input.value = value
    input.dispatchEvent(new Event('change'))
  }
  document.getElementById(query.time.mode + '-mode').click()
  switch(query.time.mode){
    case('day'):
      var days = document.querySelectorAll('.day')
      var day = [...days].filter(day => (day.textContent == '28'))[0]
      day.click()
      break

    case('week'):
      var weeks = document.querySelectorAll('.week')
      var week = [...weeks][query.time.week - 1]
      week.click()
      break

    case('month'):
      document.querySelectorAll('.day')[0].click()
      break
  }
  let observer = new MutationObserver(callFunc)
  function callFunc(mutationList, observer){
    for (let i=0; i<mutationList.length; i++){
      var target = document.getElementById('#query-table-paginator')
      if (target != null){
        if (target.hasChildNodes){
          target = target.children
          var element = [...target].filter(page => (page.textContent == query.pagination.page))[0]
          element.click()
          observer.disconnect()
        return
        }
      } else{
        observer.disconnect()
      }
    }
  }
  var target = document.querySelector('#queried-results')
  observer.observe(target, {childList: true, subtree: true})
}

monthModes()
createQueryOptions('queried-holder')
if (Object.keys(lastQuery).length != 0 ){
  queryUnpacker(lastQuery)
} else {
  generateCalender()
}







