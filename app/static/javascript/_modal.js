function addModal(prompt, submitButtonId, formId) {
  /**
   * Function used to create a modal window
   * Uses nested functions for the creation of a modal window/frame its content
   * Currently used for prompting/confirmation
   */
  let ziel = document.getElementById(submitButtonId)
  ziel.addEventListener('click', function(event) {
    createModal(event, createModalContent(prompt, submitButtonId, formId))
  })
}

function createModal(event, prompt) {
  /**
   * Function that creates the modal frame/window; first argument is the event to listen for,
   *  second is the content of the modal window
   */
	event.preventDefault()                                    //prevent instant following of the link

	let frame = document.createElement('div')
  frame.classList.add('modalFrame')
  frame.id = 'modal'

  let content = document.createElement('div')
  content.classList.add('modalContent')
  content.append(prompt)

  frame.append(content)
	document.body.appendChild(frame)
}

function createModalContent(question, submitButtonId, formId) {
  /**
   * Function that defines the modal content; first arg is the prompt/question,
   *  second is the ID of the submit button which triggers the appearance of the modal window,
   *  third the ID of the form to be submitted
   */
  let buttonHolder = document.createElement('div')
  let prompt = document.createElement('div')
  let br = document.createElement('br')

  prompt.textContent = question
  buttonHolder.append(prompt, br)
  let options = ['yes', 'no']                           //prompt buttons - check if the default action is to go through

	options.forEach(option => {
    let button = document.createElement('button')
  	button.id = option
    button.textContent = option
    buttonHolder.append(button)
  })

 buttonHolder.addEventListener('click', function(e) {
    let modal
    switch(e.target.textContent) {
      case('yes'):                                                      //follow the link, i.e. confirm the submission
        let myForm = document.getElementById(formId)
        let submitButton = document.getElementById(submitButtonId)
        document.getElementById('modal').remove()
      	myForm.requestSubmit(submitButton)
        history.replaceState({}, '', '/entries')                        //prevent user from going back to the page view
        break                                                           // of a deleted item
      case('no'):                                                       //cancel/not go through with the submission
        document.getElementById('modal').remove()
        break
    }
  })
  return buttonHolder
}






