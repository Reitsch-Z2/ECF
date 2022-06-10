
let today = new Date()

function Calender(year, month=(new Date(today).getMonth()), day=(new Date(today).getDay())){

    const days = [ "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

    function daysMapper(year, month){                              //TODO move to exterior?
      var daysTotal = new Date(year, month+1, 0).getDate()
      var days = []
      for (i=1; i < (daysTotal+1); i++){
        var x = [i,(new Date(year, month, i).getDay())]
        days.push(x)
      }
      return days
    }

    function weeksMapper(day_mapper){                              //TODO move to exterior?

      var weeks = []
      var week = []

      for (i=0; i < day_mapper.length; i++){
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

//      weeks.forEach(week => alert(week))

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

//    this.test = function(x){alert(x)}

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
      var next = this.daysMapper(this.year, this.nextMonth)
      var postLength = 7 - this.lastWeek.length
      if (postLength !=0){
        return this.arraySlicer(next, 0, postLength)
      }
    }.bind(this))()

    this.no_days = (function (){
      return new Date(month, year, 0).getDate();
    }())

}



function generateCalender(year, month=(new Date(today).getMonth()), day=(new Date(today).getDay())){

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

  function dayLooper(theWeek, boolean=0){
      theWeek.forEach(day => {
      var td = document.createElement("td")
      var div = document.createElement("div")
      var text = document.createTextNode(day[0])
      if (boolean) {
        td.classList.add("outer-day")
      }
      div.append(text); td.append(div); row.append(td); body.append(row)
    })

  }




  var table = document.createElement("table")
  var header = document.createElement("thead")
  var body = document.createElement("tbody")
  var header_row = document.createElement("tr")
  table.append(header)
  table.append(body)
  header.append(header_row)
  table.id = "calender"

  for (i=0; i < 7; i++){                //creating the calender TH/header cells
    var cell = document.createElement("th")
    var div = document.createElement("div")
    cell.append(div)
    div.append(days[i].slice(0, 3))
    header.append(cell)
  }

  var calenderHolder = document.getElementById("calender-holder")
  calenderHolder.append(table)





  var content = new Calender(year, month, day)

  for (i=0; i < content.weeks.length; i++){           //TODO let?
    var row = document.createElement("tr")
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


  var month = document.createElement("div")
  month.id="month"
  var e1 = document.createTextNode('<')
  var e2 = document.createTextNode('June')
  var e3 = document.createTextNode('>')
  month.append(e1, e2, e3)
  calenderHolder.prepend(month)



}

generateCalender(2022, 5)

//var content = new Calender(2022, 8)
//content.daysMapper(2022, 2)
//alert(content.month)
//alert(content.previousMonth)
//alert(content.nextMonth)
//alert(content.firstWeek)
//alert(content.lastWeek)
//var content2 = new Calender(2022, content.previousMonth)
//alert("yo")
//alert(content.day)
//alert(content.day_named)
//alert(content.month)
//alert(content.month_named)
//alert(content.daysMapper(content.year, content.month))
//var previousMonth = content.daysMapper(content.year, content.previousMonth)
//alert(content.daysMapper(2022, 2))
//alert(content.month_named)
//alert(previousMonth)

//alert(content.preWeek)
//alert(content.postWeek)



