function createModal(event, happening){

	event.preventDefault()
	var frame = document.createElement('div')
  frame.classList.add('modalFrame')
  frame.id = 'modal'
  var content = document.createElement('div')
  content.classList.add('modalContent')
  content.append(happening)
  frame.append(content)
	document.body.appendChild(frame)
}

function createModalContentConfirmation(text, submitButtonId, event){
  var buttonHolder = document.createElement('div')
  var prompt = document.createElement('div')
  var br = document.createElement('br')
  prompt.textContent = text
  buttonHolder.append(prompt, br)
  options = ['yes', 'no']
	options.forEach(option => {
    let button = document.createElement('button')
  	button.id = option
    button.textContent = option
    buttonHolder.append(button)
  })

 buttonHolder.addEventListener('click', function(e){
    switch(e.target.textContent){
      case('yes'):
        var myForm = document.getElementsByTagName("form")[0]
        var submitButton = document.getElementById(submitButtonId)
        var modal = document.getElementsByClassName('modalFrame')[0]
        modal.remove()

      	myForm.requestSubmit(submitButton)
        history.replaceState({}, '', '/entries')
        break
      case('no'):

      	var modal = document.getElementsByClassName('modalFrame')[0]
        modal.remove()
        break
    }
  })
  return buttonHolder
}


function addModal(submitId){
  var ziel = document.getElementById(submitId)
  ziel.addEventListener('click', function(event){

  createModal(event, createModalContentConfirmation('Are you sure you want to delete the element?', submitId, event))
})
}



