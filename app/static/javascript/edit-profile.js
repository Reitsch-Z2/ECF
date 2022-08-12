
let options = document.getElementById("options-container")
options.addEventListener('click', function(e){
  let target = e.target
  if (!target.classList.contains('profile-option')){
    return
  }
  if (!target.classList.contains('chosen-option')){
    [...options.children].forEach(option => option.classList.remove('chosen-option'))
    target.classList.add('chosen-option')
  }



  var xhr = new XMLHttpRequest()                                              //TODO global or local
  xhr.open('POST', '/api/edit-profile', true)
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")      //TODO recheck if mandatory
  xhr.setRequestHeader("Accept", "application/json;charset=UTF-8")            //TODO recheck if mandatory
  xhr.send(JSON.stringify({'value': target.textContent}))
  xhr.onload = function() {
    if (xhr.status == 200){
      parsed = JSON.parse(xhr.response)
      value = parsed['data']
      var formHolder = document.getElementById("form-container")
      formHolder.innerHTML=value

      submitButton = document.querySelector("input[type='submit']")
      overrideSubmit(submitButton, formHolder)
    }
  }
})


function overrideSubmit(submitButton, formHolder){
  submitButton.addEventListener('click', function(e){
        e.preventDefault()
        var formData = new FormData(document.getElementsByTagName('form')[0])
        var formDataFinal = JSON.stringify(Object.fromEntries(formData))
        var xhr2 = new XMLHttpRequest()
        xhr2.open('POST', '/profile/Marko', true)
        xhr2.setRequestHeader("Content-Type", "application/json;charset=UTF-8")      //TODO recheck if mandatory
        xhr2.setRequestHeader("Accept", "application/json;charset=UTF-8")            //TODO recheck if mandatory
        xhr2.send(JSON.stringify({'data': formDataFinal, 'submit':submitButton.id}))
        xhr2.onload = function() {
        if (xhr2.status == 200){
          alert(xhr2.response)
          parsed = JSON.parse(xhr2.response)
          value = parsed['data']

          if(value==''){
            createFlashMessage('your profile has been updated ')

          } else if(value=='-'){
            value = ''

          } else{
          var formHolder = document.getElementById("form-container")
          formHolder.innerHTML=value
          submitButton = document.querySelector("input[type='submit']")
          overrideSubmit(submitButton, formHolder)
          return
          }
        }
        var formHolder = document.getElementById("form-container")
        formHolder.innerHTML=value
        }
      })
}









