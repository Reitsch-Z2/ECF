
var presets = presets
var presets_pagination = presets['pagination']
//var presets_query_currency = presets['query_currency']
var presets_currency_query = presets['currency_query']


//alert(presets_currency_query)


function createQueryOptions(id){
  var holder = document.getElementById(id)
  var navContainer = document.createElement('div')
  navContainer.id = 'query-options'
  navContainer.classList.add('form-alt')
  var queryOptions = document.createElement('div')
  queryOptions.classList.add('experiment')


  function br(){
    return document.createElement("br")
  }

  var paginationContainer = document.createElement('span')          //TODO span or div? tbd
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
  var inputField = document.createElement('input')
  inputField.id = 'type-query'
  inputField.type = 'text'
  inputField.classList.add('disappeared')
  buttonGroup.append(itemButton, categoryButton)
  typeQueryContainer.append(typeLabel, buttonGroup, br(), inputField)
  buttonGroup.addEventListener('click', function(e){
    var target = e.target
    if (target.matches('.chosen')){
      target.classList.remove('chosen')
      inputField.classList.add('disappeared')
      typeLabel.classList.remove('disappeared')


    } else {
      var buttons = buttonGroup.querySelectorAll('button')
      buttons.forEach(button => {button.classList.remove('chosen')})
      target.classList.add('chosen')
      inputField.classList.remove('disappeared')
      typeLabel.classList.add('disappeared')
      if (target.textContent = 'Item'){
        autoSuggest('type-query', '#type-query-container', 'items')
      }

    }
  }
  )

  var currencyQueryContainer = document.createElement('span')          //TODO span or div? tbd
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
  currencyQueryContainer.append(label, br(), currencyQuery)




  queryOptions.append(paginationContainer)
  queryOptions.append(currencyQueryContainer)
  queryOptions.append(typeQueryContainer)
  navContainer.append(queryOptions)
  holder.prepend(navContainer)


  pagination.addEventListener('change', function(){
    paginationPacker['limit'] = pagination.value
    selta()
  })

  currencyQuery.addEventListener('change', function(){

    var xhr = new XMLHttpRequest()                                              //TODO global or local
    xhr.open('POST', '/api/user-settings', true)
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")      //TODO recheck if mandatory
    xhr.setRequestHeader("Accept", "application/json;charset=UTF-8")            //TODO recheck if mandatory
    xhr.send(JSON.stringify({'setting_name': 'query currency', 'setting': currencyQuery.value}))

    xhr.onload = function() {
    if (xhr.status == 200){
      queryTypePacker['currency'] = xhr.response
    }
  }





    selta()
  })














}



createQueryOptions('queried-holder')