

function queryTableMaker(id, responseObject){
  var holder = document.getElementById(id)

  holder.innerHTML=""




  responseObject = JSON.parse(responseObject)
  alert(responseObject["data"]["total"])
  alert(total)
  var rows = responseObject["data"]["rows"]
  var columns = responseObject["data"]["columns"]
  if (rows.length ==0){
    var info = document.createElement("div")
    info.textContent = "no matching results found"
    info.id = "no-results"
    holder.append(info)
    return
  }
  var limit = responseObject["data"]["limit"]
  var page = responseObject["data"]["page"]
  var count = responseObject["data"]["count"]
  var total = responseObject["data"]["total"]


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
      container.innerHTML = rows[i][columns[x]]         //TODO maybe only do this for the ones with a link
      td.append(container)
      tableRow.append(td)
    }
    body.append(tableRow)
  }

  var footer = document.createElement('div')
  footer.id = "pagination-sum"
  footer.append(showPages(limit, page, count))
  footer.append(showSumTotal(total))

  table.append(headers)
  table.append(body)

  holder.append(showPosition(limit, page, count))
  holder.append(table)
  holder.append(footer)


}


function showPosition(limit, page, count){

  var pointer = document.createElement("div")
  pointer.id = "query-table-pointer"
  var offset = (page-1)*limit
  var startingPoint = 1 + offset
  var endPoint = startingPoint+limit-1

  count <= (startingPoint+limit-1) ? (endPoint = count) : (endPont = startingPoint + limit)
  endPoint = (endPoint == 1) ? " " : " - " + String(endPoint)

  var message = "Page " + String(page)
  message += " - Showing results "+ String(startingPoint) + endPoint
  message += " out of " + String(count) +" total"

  pointer.textContent = message

  return pointer
}



function showPages(limit, page, count){
  var paginator = document.createElement("span")
  paginator.id = "query-table-paginator"
  var numberOfPages = Math.ceil(count/limit)
  if (numberOfPages <= 1){
    return ' '
  }
  var pages = [...Array(numberOfPages+1).keys()].slice(1)
  var currentPage = parseInt(page)
  var paginated = []
    if ((currentPage <= 4) && (numberOfPages >= 10)){
      paginated.push(...pages.slice(0,5))
      paginated.push('...')
      paginated.push(pages[pages.length-1])
    } else if ((numberOfPages - currentPage <= 3) && (numberOfPages >= 10)){
      paginated.push(1)
      paginated.push('...')
      paginated.push(...pages.slice(-5))
    } else if (numberOfPages >= 10){
      paginated.push(1)
      paginated.push('...')
      paginated.push(currentPage - 1)
      paginated.push(currentPage)
      paginated.push(currentPage + 1)
      paginated.push('...')
      paginated.push(pages[pages.length-1])
    } else {
      paginated.push(...pages)
    }

  for (let i = 0; i < paginated.length; i++){
    var pageHolder = document.createElement('span')
    pageHolder.textContent = paginated[i]

    if ((paginated[i] != '...') && (paginated[i] != currentPage)){
      pageHolder.classList.add('page')
    } else if (paginated[i] == currentPage){
      pageHolder.classList.add('current-page')
    } else {
      pageHolder.classList.add('hidden-pages')
    }

    paginator.append(pageHolder)
  }

  paginator.addEventListener('click', function(e){
    var target = e.target
    if (target.matches('.page')){
      paginationPacker['page'] = target.textContent
      selta()
    }
  })

  return paginator

}



function showSumTotal(total){
  var sumTotal = document.createElement("span")
  sumTotal.id = "query-table-sum"
  sumTotal.textContent = total


  return sumTotal

}


















