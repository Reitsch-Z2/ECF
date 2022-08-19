var presets = presets
var presets_pagination = presets['pagination']
var presets_currency_query = presets['currency_query']
var presets_currency_query_choice = presets['currency_query_choice']

function createQueryOptions(id){
  let holder = document.getElementById(id)
  let navContainer = document.createElement('div')
  navContainer.id = 'query-options'
  navContainer.classList.add('form-alt2')
  let queryOptions = document.createElement('div')
  queryOptions.classList.add('item-form')
  let resultsContainer = document.createElement('div')
  resultsContainer.id = 'queried-results'

  queryOptions.append(paginationQuery())
  queryOptions.append(currencyQuery())
  queryOptions.append(typeQuery())
  navContainer.append(queryOptions)
  holder.prepend(navContainer)
  holder.append(resultsContainer)
}

function br(){
  return document.createElement("br")
}

function paginationQuery(){
  let paginationContainer = document.createElement('span')
  paginationContainer.id = 'pagination-container'
  paginationContainer.classList.add('form-element')
  let pagination = document.createElement('select')
  pagination.name = 'pagination'
  pagination.id = 'pagination'
  let label = document.createElement('label')
  label.htmlFor = pagination.id
  label.textContent = 'No. of results'
  let options = presets_pagination
  for (let i=0; i < options.length; i++){
    let option = document.createElement('option')
    let value = options[i]
    option.value = value
    option.textContent = value
    pagination.append(option)
  }
  paginationContainer.append(label, br(), pagination)
  paginationPacker['limit'] = pagination.value
  paginationPacker['page'] = 1
  pagination.addEventListener('change', function(){
    paginationPacker['limit'] = pagination.value
    paginationPacker['page'] = "1"
    selta()
  })
  return paginationContainer
}

function currencyQuery(){
  let currencyQueryContainer = document.createElement('span')
  currencyQueryContainer.id = 'currency-query-container'
  currencyQueryContainer.classList.add('form-element')
  let currencyQuery = document.createElement('select')
  currencyQuery.name = 'currency-query'
  currencyQuery.id = 'currency-query'
  let label = document.createElement('label')
  label.htmlFor = currencyQuery.id
  label.textContent = 'Query by currency'
  let options = presets_currency_query
  for (let i=0; i < options.length; i++){
    let option = document.createElement('option')
    let value = options[i]
    option.value = value
    option.textContent = value
    currencyQuery.append(option)
  }
  currencyQuery.value = presets_currency_query_choice
  currencyQueryContainer.append(label, br(), currencyQuery)
  currencyTypePacker['currency'] = currencyQuery.value
  currencyQuery.addEventListener('change', function(){
    let xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/user-settings', true)
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
    xhr.setRequestHeader("Accept", "application/json;charset=UTF-8")
    xhr.send(JSON.stringify({'setting_name': 'query_currency', 'setting': currencyQuery.value}))
    xhr.onload = function() {
    if (xhr.status == 200){
      currencyTypePacker['currency'] = xhr.response
      alert('almost')
      alert(JSON.stringify(paginationPacker))
      paginationPacker['page'] = "1"
      alert(JSON.stringify(paginationPacker))
    }
    selta()
  }

  })
  return currencyQueryContainer
}


function typeQuery(){
  let typeQueryContainer = document.createElement('span')
  typeQueryContainer.id = 'type-query-container'
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
  buttonGroup.addEventListener('click', function(e){
    queryTypePacker={}
    selta()
    let temp = document.getElementById('type-query')
    let target = e.target
    if (target.matches('.chosen')){
      target.classList.remove('chosen')
      typeLabel.classList.remove('disappeared')
      if (temp){temp.remove()}
      queryTypePacker={}
    } else {
      if (temp){temp.remove()}
      let inputField = document.createElement('input')
      inputField.id = 'type-query'
      inputField.type = 'text'
      let buttons = buttonGroup.querySelectorAll('button')
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
        paginationPacker['page'] = 1
        selta()
      })
    }
  }
  )
  return typeQueryContainer
}









































