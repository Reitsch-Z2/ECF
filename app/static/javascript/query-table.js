

function queryTableMaker(id, responseObject){
  var holder = document.getElementById(id)

  responseObject = JSON.parse(responseObject)
  var rows = responseObject["data"]["rows"]
  var columns = responseObject["data"]["columns"]

  var table = document.createElement("table")
  var headers = document.createElement("thead")
  var body = document.createElement("tbody")
  table.id = "table-costs"

  var headerRow = document.createElement("tr")
  for (let i = 0; i < columns.length; i++){
    var th = document.createElement("th")
    var container = document.createElement("div")
    container.textContent = columns[i]
    th.append(container)
    headerRow.append(th)
  }
  headers.append(headerRow)

  for (let i = 0; i < rows.length; i++){
    var tableRow = document.createElement("tr")
    for (let x = 0; x < columns.length; x++){
      var td = document.createElement("td")
      var container = document.createElement("div")
      container.textContent = rows[i][columns[x]]
      td.append(container)
      tableRow.append(td)
    }
    body.append(tableRow)
  }
  table.append(headers)
  table.append(body)

  previous = document.getElementById("table-costs")
  if (previous){
    previous.remove()
  }

  holder.append(table)
}