var presets = presets
var presets_pagination = presets['pagination']
var presets_currency_query = presets['currency_query']
var presets_currency_query_choice = presets['currency_query_choice']

function createQueryOptions(id){
  var holder = document.getElementById(id)
  var navContainer = document.createElement('div')
  navContainer.id = 'query-options'
  navContainer.classList.add('form-alt2')
  var queryOptions = document.createElement('div')
  queryOptions.classList.add('experiment')
  var resultsContainer = document.createElement('div')
  resultsContainer.id = 'queried-results'
  function br(){
    return document.createElement("br")
  }
  var paginationContainer = document.createElement('span')
  paginationContainer.id = 'pagination-container'
  paginationContainer.classList.add('poly')                         //TODO new one
  var pagination = document.createElement('select')
  pagination.name = 'pagination'
  pagination.id = 'pagination'
  var label = document.createElement('label')
  label.htmlFor = pagination.id
  label.textContent = 'No. of results'
  var options = presets_pagination
  for (let i=0; i < options.length; i++){
    var option = document.createElement('option')
    var value = options[i]
    option.value = value
    option.textContent = value
    pagination.append(option)
  }
  paginationContainer.append(label, br(), pagination)
  paginationPacker['limit'] = pagination.value
  paginationPacker['page'] = 1

  var typeQueryContainer = document.createElement('span')            //TODO span or div? tbd
  typeQueryContainer.id = 'type-query-container'
  typeQueryContainer.classList.add('poly')
  var typeLabel = document.createElement('div')
  typeLabel.textContent = 'Query by:'
  var itemButton = document.createElement('button')
  itemButton.id = 'query-item'
  itemButton.type = 'button'
  itemButton.textContent = 'Item'
  var categoryButton = document.createElement('button')
  categoryButton.id = 'query-category'
  categoryButton.type = 'button'
  categoryButton.textContent = 'Category'
  var buttonGroup = document.createElement('span')
  buttonGroup.id = 'type-query-buttons'
  buttonGroup.append(itemButton, categoryButton)
  typeQueryContainer.append(typeLabel, buttonGroup, br())
  buttonGroup.addEventListener('click', function(e){
    queryTypePacker={}
    selta()
    var temp = document.getElementById('type-query')
    var target = e.target

    if (target.matches('.chosen')){
      target.classList.remove('chosen')
      typeLabel.classList.remove('disappeared')
      if (temp){temp.remove()}
      queryTypePacker={}
    } else {
      if (temp){temp.remove()}
      var inputField = document.createElement('input')
      inputField.id = 'type-query'
      inputField.type = 'text'
      var buttons = buttonGroup.querySelectorAll('button')
      buttons.forEach(button => {button.classList.remove('chosen')})
      target.classList.add('chosen')
      typeLabel.classList.add('disappeared')
      query_type = target.textContent
      if (query_type == 'Item'){
        typeQueryContainer.append(inputField)
        autoSuggest('type-query', '#type-query-container', 'items')
      } else {
        typeQueryContainer.append(inputField)
        autoSuggest('type-query', '#type-query-container', 'categories')
      }

      inputField.addEventListener('change', function(){
        if (!buttonGroup.matches(':hover')){
        alert(inputField.value)
        queryTypePacker={}
        queryTypePacker[query_type]=inputField.value
        selta()
        } else {
          queryTypePacker={}
          queryTypePacker[query_type]=inputField.value
          selta()
        }
      })
    }
  }
  )

  var currencyQueryContainer = document.createElement('span')
  currencyQueryContainer.id = 'currency-query-container'
  currencyQueryContainer.classList.add('poly')                         //TODO new one
  var currencyQuery = document.createElement('select')
  currencyQuery.name = 'currency-query'
  currencyQuery.id = 'currency-query'
  var label = document.createElement('label')
  label.htmlFor = currencyQuery.id
  label.textContent = 'Query by currency'
  var options = presets_currency_query
  for (let i=0; i < options.length; i++){
    var option = document.createElement('option')
    var value = options[i]
    option.value = value
    option.textContent = value
    currencyQuery.append(option)
  }
  currencyQuery.value = presets_currency_query_choice
  currencyQueryContainer.append(label, br(), currencyQuery)
  currencyTypePacker['currency'] = currencyQuery.value

  queryOptions.append(paginationContainer)
  queryOptions.append(currencyQueryContainer)
  queryOptions.append(typeQueryContainer)
  navContainer.append(queryOptions)
  holder.prepend(navContainer)
  holder.append(resultsContainer)

  pagination.addEventListener('change', function(){
    paginationPacker['limit'] = pagination.value
    paginationPacker['page'] = 1
    selta()
  })

  currencyQuery.addEventListener('change', function(){
    var xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/user-settings', true)
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
    xhr.setRequestHeader("Accept", "application/json;charset=UTF-8")
    xhr.send(JSON.stringify({'setting_name': 'query_currency', 'setting': currencyQuery.value}))
    xhr.onload = function() {
    if (xhr.status == 200){
      currencyTypePacker['currency'] = xhr.response
    }
  }
    selta()
  })
}



