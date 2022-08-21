function createFlashMessage(text, popIn=1.5, pause=1, fadeAway=4) {
  /**
   * Function used to create ephemeral info messages
   * Used mostly for the standard Flask flash messages, but also as an event feedback called from a JS script
   * Messages, if multiple, stack one upon another, or in the place of the recently faded away ones
   */
  let existing = document.getElementsByClassName('flash-message')
  let messages = [...existing]
  let message = document.createElement('div')
  message.classList.add('flash-message')
  message.classList.add('flash-pop')                      //animation - message pops into the window
  message.style['animation-duration']= popIn+'s'          //duration optionally defined via args
  message.textContent = text
  document.body.appendChild(message)
  let msgPositions = []                                   //get the position of all the existing messages in the window

  messages.forEach(msg =>{
    let position = window.getComputedStyle(msg).getPropertyValue('--bottom-flex')
    msgPositions.push((parseInt(position.replace('px', '').trim())))
  })

  for (let x = 0; x < existing.length + 1; x++) {         //loop through positions of existing messages
    if (msgPositions.includes(25 + x*40 ) != true) {      //find the first free slot for the new message to pop into
      let neumax = 25 + x*40
      let bottom = String(neumax) + 'px'
      message.style.setProperty('--bottom-flex', bottom)  //set the position of the new message
      break
    }
  }

  setTimeout(function() {
    message.classList.add('flash-fade')                   //animation - message fades away after being displayed
    message.style['animation-duration']= fadeAway+'s'     // for the amount of time specified in args
  }, (popIn+pause)*1000)

  setTimeout(function() {            //message removed after fading away, opening the slot/position for a new message
    message.remove()
  }, (popIn+pause+fadeAway)*1000)
}


//document.body.addEventListener('click', function() {        //test
//  createFlashMessage('something')
//})