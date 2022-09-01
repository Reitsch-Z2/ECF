function queryTableMaker(id, responseObject) {
  /**
   * Function used to create the table with the queried results.
   * It contains four sub-functions, which are used to create different elements of the table and
   * the relevant additional data:
   *   - position/cursor, showing the enumeration of the displayed results as well as the number of total results
   *   - table with results
   *   - pagination data - current page and pages total
   *   - sum of the queried costs
   */
  let holder = document.getElementById(id)
  responseObject = JSON.parse(responseObject)
  holder.innerHTML=''
  if (Object.keys(responseObject['data']).length == 0) {  // If there are no matching results, inform the user
    let info = document.createElement('div')
    info.textContent = 'no matching results found'
    info.id = 'no-results'
    holder.append(info)
  } else {                                                // If there are results, unpack the values from the response,
  let limit = responseObject['data']['limit']             // which are then used in the sub-functions to organize and
  let page = responseObject['data']['page']               // display the queried data
  let count = responseObject['data']['count']
  let total = responseObject['data']['total']
  let rows = responseObject['data']['rows']
  let columns = responseObject['data']['columns']
  let saved = responseObject['data']['saved']

  let footer = document.createElement('div')
  footer.id = 'pagination-sum'
  footer.append(showPages(limit, page, count))
  footer.append(showSumTotal(total, count))
  holder.append(showPosition(limit, page, count))
  holder.append(createTable(rows, columns, responseObject))
  holder.append(footer)
  }
}


function showPosition(limit, page, count) {               // Create pointer/cursor, showing the current results out of
  let pointer = document.createElement('div')             // total results
  pointer.id = 'query-table-pointer'
  let offset = (page-1)*limit
  let startingPoint = 1 + offset
  let endPoint = startingPoint+limit-1

  count <= (startingPoint+limit-1) ? (endPoint = count) : (endPont = startingPoint + limit)
  endPoint = (endPoint == 1) ? ' ' : ' - ' + String(endPoint)

  let message = 'Page ' + String(page)
  message += ' - Showing results '+ String(startingPoint) + endPoint
  message += ' out of ' + String(count) +' total'
  pointer.textContent = message
  return pointer
}

function createTable(rows, columns, responseObject) {     // Create the table and fill it with the queried data
  let table = document.createElement('table')
  let headers = document.createElement('thead')
  let body = document.createElement('tbody')
  table.id = 'table-costs'

  let headerRow = document.createElement('tr')            // Create the table headers
  for (let i = 0; i < columns.length; i++) {
    let th = document.createElement('th')
    let container = document.createElement('div')
    container.textContent = columns[i]
    th.append(container)
    headerRow.append(th)
  }
  headers.append(headerRow)
  for (let i = 0; i < rows.length; i++) {                 // Create the body of the table and populate it
    let tableRow = document.createElement('tr')
    for (let x = 0; x < columns.length; x++) {
      let td = document.createElement('td')
      let container = document.createElement('div')
      if (columns[x]=='item') {
        container.innerHTML = rows[i][columns[x]]         // Used only for the <a>/link element
      } else {
        container.textContent = rows[i][columns[x]]       // Used for plain text
      }
      td.append(container)
      tableRow.append(td)
    }
    body.append(tableRow)
  }
  table.append(headers)
  table.append(body)
  return table
}

function showPages(limit, page, count) {                // Create the page-navigation, based on number of results
  let paginator = document.createElement('span')        // returned and the results displayed.
  paginator.id = 'query-table-paginator'
  let numberOfPages = Math.ceil(count/limit)
  if (numberOfPages <= 1) {
    return ''
  }

  let pages = [...Array(numberOfPages+1).keys()].slice(1)
  let currentPage = parseInt(page)
  let paginated = []                                    // Array that receives page navigation elements - Nos and "..."

  if ((currentPage <= 4) && (numberOfPages >= 10)) {    // Formatting the start/beginning of the scope, i.e. the
    paginated.push(...pages.slice(0,5))                 // scenario where the user is browsing the first few pages
    paginated.push('...')
    paginated.push(pages[pages.length-1])
  } else if ((numberOfPages - currentPage <= 3) && (numberOfPages >= 10)) {  // Formatting the end of the scope
    paginated.push(1)
    paginated.push('...')
    paginated.push(...pages.slice(-5))
  } else if (numberOfPages >= 10) {                     // Formatting the middle of the scope
    paginated.push(1)
    paginated.push('...')
    paginated.push(currentPage - 1)
    paginated.push(currentPage)
    paginated.push(currentPage + 1)
    paginated.push('...')
    paginated.push(pages[pages.length-1])
  } else {                                              // Displays all pages if the number thereof is less than 10
    paginated.push(...pages)
  }

  for (let i = 0; i < paginated.length; i++) {          // Creates DOM nodes from the pagination elements
    let pageHolder = document.createElement('span')
    pageHolder.textContent = paginated[i]
    if ((paginated[i] != '...') && (paginated[i] != currentPage)) {
      pageHolder.classList.add('page')                  // Style the numbers representing the pages with results
    } else if (paginated[i] == currentPage) {
      pageHolder.classList.add('current-page')          // Style the number representing the current page
    } else {
      pageHolder.classList.add('hidden-pages')          // Style hidden pages, represented as "..."
    }
    paginator.append(pageHolder)
  }

  paginator.addEventListener('click', function(e) {     // Event listener that triggers a new ajax request, where the
    let target = e.target                               // response shows the different batch of results for the current
    if (target.matches('.page')) {                      // query, based on the page chosen
      paginationPacker['page'] = target.textContent
      postQuery()
    }
  })
  return paginator
}

function showSumTotal(total, count) {               // Create a node/element showing the sum for the queried expenses
  let sumTotal = document.createElement('span')
  sumTotal.id = 'query-table-sum'
  sumTotal.textContent = total
  return sumTotal
}



















