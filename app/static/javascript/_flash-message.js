

function createFlashMessage(text, popIn=1.5, pause=1, fadeAway=4){

  var existing = document.getElementsByClassName('flash-message')
  messages = [...existing]

  var message = document.createElement('div')
  message.classList.add('flash-message')
  message.classList.add('flash-pop')
  message.style["animation-duration"]= popIn+'s'
  message.textContent = text
  document.body.appendChild(message)
  if (existing.length>=0){

    for (let i=0; i<existing.length; i++){
      var max = []
      messages.forEach(mess =>{
        var temp = window.getComputedStyle(mess).getPropertyValue("--bottom-flex")
        max.push((parseInt(temp.replace('px', '').trim())))
      })
    }
    for (let x=0; x<existing.length+1; x++){
      if (max.includes(25+x*40 )!=true){
        var neumax = 25+x*40
        break
      }
    }
    ext=message
    if (ext.classList.contains('positioned')!=true){
      ext.classList.add('positioned')
      var style = window.getComputedStyle(ext).getPropertyValue("--bottom-flex")
      var bottom = String(neumax) + 'px'
      ext.style.setProperty("--bottom-flex", bottom)
    }
  }


  setTimeout(function(){
    message.classList.add('flash-fade')
    message.style["animation-duration"]= fadeAway+'s'
  }, (popIn+pause)*1000)

  setTimeout(function(){
    message.remove()
  }, (popIn+pause+fadeAway)*1000)
}

//createFlashMessage('evo ga prvi')
//
//createFlashMessage('evo ga drugi')
//createFlashMessage('evo ga treci')
//createFlashMessage('evo ga cetvrti')
//
//
//
//document.body.addEventListener("click", function(){createFlashMessage('testy')})