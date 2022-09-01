function autoSuggest(id, property){
  /**
   * Function used to query for previous results based on the user data and offer suggestions while the user is typing
   * It sends an ajax request (on input event) to an api route, which then returns the existing/previous results
   * For the arguments, it takes the id of the input field to be monitored, and the property to be checked for
   * Based on the characters entered, the api route finds the matching existing results starting with those characters,
   *  using the property argument value to determine which database data to check for
   */
  let inputField = document.getElementById(id)
  let inputSuggestions = document.createElement('div')
  let name = id+'-'+'suggestions'

  inputSuggestions.classList.add('suggestions')                       //create a dropdown list with suggestions
  inputSuggestions.id = name
  inputSuggestions.addEventListener('mousedown', function(e) {        // Populate the input field with the chosen
    target = e.target                                                 // result from the database
    choice = target.textContent
    inputField.value = choice
    inputSuggestions.innerHTML=''                   // Empty the dropdown menu if the user clicked a suggested option
    }
  )
  inputField.addEventListener('input', function() { // On input send ajax request to check for matching existing results
    if (inputField.value.length != 0){
      let xhr = new XMLHttpRequest()
      xhr.open('POST', '/api/auto-suggest', true)
      xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
      xhr.setRequestHeader('Accept', 'application/json;charset=UTF-8')
      xhr.send(JSON.stringify({'value': inputField.value, 'property': property}))

      xhr.onload = function() {
        if (xhr.status == 200) {
          if (inputField.matches(':focus')) {             // Conditional that prevents the potentially delayed ajax
            inputSuggestions.innerHTML=''                 // responses from forming a dropdown menu if the user already
            parsed = JSON.parse(xhr.response)             // clicked outside of the input field
            values = parsed['data']
            if (values.length != 0) {                     // If there are matching results in the ajax response
              for (let i = 0; i < values.length; i++) {   // generate suggestions in a dropdown element
                temp = document.createElement('div')
                temp.classList.add('choice')
                temp.textContent = values[i]
                inputSuggestions.append(temp)
                inputField.after(inputSuggestions)
              }
            }
          }
        }
      }
    } else {
      inputSuggestions.remove()       // If the user deleted the typed characters down to none, remove the suggestions,
    }                                 // so that they do not remain for an empty input field
  })
  inputField.addEventListener('blur', function(e) {                   // On blur event, remove the current suggestions
    inputSuggestions.remove()
  })
}

function autoFill(eventNodeId, targetId, property){
  /**
   * Function used to populate one input field based on what the user typed in another input field - if there are
   * existing results for that relationship pattern
   * For the arguments, it takes the id of the input field to be monitored for typing, the id for the input field to be
   * populated, and the name of the property to be checked for, in order to determine if the previous data exists
   * Currently used to check if there is already a defined category for the item/article that the user is entering in
   * the first input field - the function sends an ajax request, and if there is a match, the category input field gets
   * automatically populated
   */
  eventNode = document.getElementById(eventNodeId)
  eventNode.addEventListener('blur', function(){
    if (eventNode.value != 0){
      let xhr = new XMLHttpRequest()
      xhr.open('POST', '/api/auto-fill', true)
      xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
      xhr.setRequestHeader('Accept', 'application/json;charset=UTF-8')
      xhr.send(JSON.stringify({'value': eventNode.value, 'property': property}))

      xhr.onload = function() {
        if (xhr.status == 200){
          parsed = JSON.parse(xhr.response)
          value = parsed['data']
          if (value.length!=0){
            let inputField = document.getElementById(targetId)
            inputField.value = value
          }
        } else {
          // pass
        }
      }
    }
  })
}




