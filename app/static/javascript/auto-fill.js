

function autoSuggest(id, containerSelector, property){
  var inputField = document.getElementById(id)
  var inputSuggestions = document.createElement('div')
  var name = id+'-'+'suggestions'
  inputSuggestions.classList.add('suggestions')
  inputSuggestions.id = name
  var container = inputField.closest(containerSelector)   //superfluous

  inputSuggestions.addEventListener('mousedown', function(e){
    target = e.target
    choice = target.textContent
    inputField.value = choice
    }
  )

  inputField.addEventListener('input', function(){
      if (inputField.value.length != 0){
      inputSuggestions.innerHTML=''
      var xhr = new XMLHttpRequest()                                              //TODO global or local
      xhr.open('POST', '/api/auto-suggest', true)
      xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")      //TODO recheck if mandatory
      xhr.setRequestHeader("Accept", "application/json;charset=UTF-8")            //TODO recheck if mandatory
      xhr.send(JSON.stringify({'value': inputField.value, 'property': property}))

      xhr.onload = function() {
        if (xhr.status == 200){


          parsed = JSON.parse(xhr.response)
          values = parsed['data']

          if (values.lenght != 0){
            for (let i = 0; i < values.length; i++){
              temp = document.createElement('div')
              temp.classList.add('choice')
              temp.textContent = values[i]
              inputSuggestions.append(temp)
            }
          }
        inputField.after(inputSuggestions)
        }
      }
    } else {
      inputSuggestions.innerHTML=''
    }
  })
  inputField.addEventListener('blur', function(e){
    inputSuggestions.remove()
  })
}










//
function autoFill(eventNodeId, targetId, property){
  eventNode = document.getElementById(eventNodeId)

  eventNode.addEventListener('blur', function(){

    if (eventNode.value != 0){

      var xhr = new XMLHttpRequest()                                              //TODO global or local
      xhr.open('POST', '/api/auto-fill', true)
      xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")      //TODO recheck if mandatory
      xhr.setRequestHeader("Accept", "application/json;charset=UTF-8")            //TODO recheck if mandatory
      xhr.send(JSON.stringify({'value': eventNode.value, 'property': property}))

      xhr.onload = function() {
        if (xhr.status == 200){

          parsed = JSON.parse(xhr.response)
          value = parsed['data']

          var inputField = document.getElementById(targetId)
          inputField.value = value

        }
      }
    }
  })
}




