function createQueryOptions(id, presets) {
  /**
   * Function used to create the custom query form
   * It contains three sub-functions, each responding to a query option:
   *   - pagination element, i.e. number of results per page
   *   - currency type query (main currency total - expenses converted to the main currency, all currencies combined
   *     total, or individual currencies partial, i.e.only the results for the relevant currency where the
   *     original/first entry was in that currency)
   *   - item/category query - a filtering sub-option, if the user wants to see only specific items or item categories
   * Function takes two arguments - the id of the existing DOM node to which the dynamically generated content should
   *  be appended to, and the presets, which are values returned from the flask route - JSON constants for pagination
   *  options and types of currency queries the user can choose, as well as the main/default currency query type chosen
   *  by the user (so that the currency query options are loaded with the chosen options as the first option)
   */

  let presets_pagination = presets['pagination']
  let presets_currency_query = presets['currency_query']
  let presets_currency_query_choice = presets['currency_query_choice']

  let holder = document.getElementById(id)        //existing node, which will hold both the query options and the table
  let navContainer = document.createElement('div')    //dynamically created node holding all query options
  navContainer.id = 'query-options'
  navContainer.classList.add('form-alt2')
  let queryOptions = document.createElement('div')
  queryOptions.classList.add('item-form')
  let resultsContainer = document.createElement('div')
  resultsContainer.id = 'queried-results'

  queryOptions.append(paginationQuery(presets_pagination))
  queryOptions.append(currencyQuery(presets_currency_query, presets_currency_query_choice))
  queryOptions.append(typeQuery())
  navContainer.append(queryOptions)

  holder.append(navContainer)
  holder.append(resultsContainer)                     //empty node element as a placeholder for the table with results
}

function br() {                                        //dynamically created break element, for visually structuring the
  return document.createElement('br')                 // query options/fields
}

function paginationQuery(presets_pagination) {              //create a html select element from which to choose the
  let paginationContainer = document.createElement('span')  // number of queried results per page
  paginationContainer.id = 'pagination-container'
  paginationContainer.classList.add('form-element')
  let pagination = document.createElement('select')
  pagination.name = 'pagination'
  pagination.id = 'pagination'
  let label = document.createElement('label')
  label.htmlFor = pagination.id
  label.textContent = 'No. of results'
  let options = presets_pagination
  for (let i = 0; i < options.length; i++) {
    let option = document.createElement('option')
    let value = options[i]
    option.value = value
    option.textContent = value
    pagination.append(option)
  }
  paginationContainer.append(label, br(), pagination)
  paginationPacker['limit'] = pagination.value
  paginationPacker['page'] = '1'
  pagination.addEventListener('change', function() {
    paginationPacker['limit'] = pagination.value
    paginationPacker['page'] = '1'                          //if the number of results per page is changed the page
    postQuery()                                             // number is reset to the first page, as to avoid staying
  })                                                        // on the page which maybe does not exist anymore
  return paginationContainer
}

function currencyQuery(presets_currency_query, presets_currency_query_choice) { //create an html select element to
  let currencyQueryContainer = document.createElement('span')                   // choose the type of currency query
  currencyQueryContainer.id = 'currency-query-container'
  currencyQueryContainer.classList.add('form-element')
  let currencyQuery = document.createElement('select')
  currencyQuery.name = 'currency-query'
  currencyQuery.id = 'currency-query'
  let label = document.createElement('label')
  label.htmlFor = currencyQuery.id
  label.textContent = 'Query by currency'
  let options = presets_currency_query
  for (let i=0; i < options.length; i++) {
    let option = document.createElement('option')
    let value = options[i]
    option.value = value
    option.textContent = value
    currencyQuery.append(option)
  }
  currencyQuery.value = presets_currency_query_choice
  currencyQueryContainer.append(label, br(), currencyQuery)
  currencyTypePacker['currency'] = currencyQuery.value

  /* Currency query type is here considered a user setting, which makes it necessary to write it into the db in
   * order to always load it by default when the page loads. For this reason, an api route is created, to which
   * an ajax request is sent on change event in this select field. The response from the ajax query updates the page
   * number to 1, and repeats the current query with the changed currency type query option, so that the refreshed
   * results are instantly displayed on change event.
   */
  currencyQuery.addEventListener('change', function() {
    let xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/user-settings', true)
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
    xhr.setRequestHeader('Accept', 'application/json;charset=UTF-8')
    xhr.send(JSON.stringify({'setting_name': 'query_currency', 'setting': currencyQuery.value}))

    xhr.onload = function() {
      if (xhr.status == 200) {
        currencyTypePacker['currency'] = xhr.response
        paginationPacker['page'] = '1'
      }
      postQuery()
    }
  })
  return currencyQueryContainer
}

function typeQuery() {                                            //create an html select element for the query option
  let typeQueryContainer = document.createElement('span')         // via which the user can filter the results based
  typeQueryContainer.id = 'type-query-container'                  // on item or category name
  typeQueryContainer.classList.add('form-element')
  let typeLabel = document.createElement('div')
  typeLabel.textContent = 'Query by:'
  let itemButton = document.createElement('button')
  itemButton.id = 'query-item'
  itemButton.type = 'button'
  itemButton.textContent = 'Item'
  let categoryButton = document.createElement('button')
  categoryButton.id = 'query-category'
  categoryButton.type = 'button'
  categoryButton.textContent = 'Category'
  let buttonGroup = document.createElement('span')
  buttonGroup.id = 'type-query-buttons'

  buttonGroup.append(itemButton, categoryButton)
  typeQueryContainer.append(typeLabel, buttonGroup, br())

  /* Click event on the button group - if no button is selected, the clicked button gets a new class marking it as
   *  selected, and the input field appears in which the user can type the name to search by. The input field has
   *  autoSuggest function called on it, which sends an ajax request to an api route on input event, which queries the
   *  existing items or categories for the current user, and returns results that match the typed characters in a
   *  dropdown list from which the user can choose from.
   *
   */
  buttonGroup.addEventListener('click', function(e) {
    queryTypePacker={}
    postQuery()
    let temp = document.getElementById('type-query')
    let target = e.target
    if (target.matches('.chosen')) {                        //if the user clicks on the already selected button,
      target.classList.remove('chosen')                     // the input field disappears and the query by type option
      typeLabel.classList.remove('disappeared')             // does not get processed in the query
      if (temp) {temp.remove()}
      queryTypePacker={}
    } else {
      if (temp) {temp.remove()}
      let inputField = document.createElement('input')
      inputField.id = 'type-query'
      inputField.type = 'text'
      let buttons = buttonGroup.querySelectorAll('button')
      buttons.forEach(button => {button.classList.remove('chosen')})
      target.classList.add('chosen')
      typeLabel.classList.add('disappeared')
      query_type = target.textContent
      if (query_type == 'Item') {                           //the input field that appears is always the same, it only
        typeQueryContainer.append(inputField)               // gets 'decorated' with a different autoSuggest function
        autoSuggest('type-query', 'items')                  // based on the button clicked, which changes the property
      } else {                                              // that is queried in the api route and returned as a
        typeQueryContainer.append(inputField)               // response (either existing items or categories)
        autoSuggest('type-query', 'categories')
      }
      inputField.addEventListener('change', function() {    //if the option is chosen, either by clicking on one of
        if (!buttonGroup.matches(':hover')) {               // the suggestions or typing the existing name, the
        queryTypePacker={}                                  // query data is updated and a new query is made; on top
        queryTypePacker[query_type]=inputField.value        // of that, the page number for the query is updated to 1
        postQuery()
        } else {
          queryTypePacker={}
          queryTypePacker[query_type]=inputField.value
          postQuery()
        }
        paginationPacker['page'] = '1'
        postQuery()
      })
    }
  }
  )
  return typeQueryContainer
}









































