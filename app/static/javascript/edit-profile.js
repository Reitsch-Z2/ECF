
function editProfile() {
  /**
   * Function used to create an interface for users to edit their profile data
   * It was conceptualized as an accordion-type element, because there are three different types of user data/info
   *  that should available to the user to make changes to, and it did not make sense for them to overlap
   * Each of the three different groups is created as a separate form element, and when the user clicks on the group
   *  title/option, an ajax request is made to a specific api route, which serves back the chosen form
   * This function displays the requested form, and a nested function overrides the default form logic by preventing
   *  the default submission of the form, and restructuring it as a custom post request to the same page the user is on
   * The view function parses the data and sends back the appropriate response as an ajax response, based on the form
   *  which was submitted, without re-rendering the whole page. If there are errors, i.e. validation did not pass, the
   *  ajax response contains the received WTForm with all the triggered error messages, which are served back and
   *  rendered in place of an empty form, allowing the user to make the necessary changes.
   */
  let options = document.getElementById('options-container')

  options.addEventListener('click', function(e) {               //click event on the option tabs, triggering a relevant
    let target = e.target                                       // ajax request, which serves back the appropriate form
    if (!target.classList.contains('profile-option')) {
      return
    }
    if (!target.classList.contains('chosen-option')) {
      [...options.children].forEach(option => option.classList.remove('chosen-option'))
      target.classList.add('chosen-option')
    }

    var xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/edit-profile', true)
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
    xhr.setRequestHeader('Accept', 'application/json;charset=UTF-8')
    xhr.send(JSON.stringify({'value': target.textContent}))

    xhr.onload = function() {
      if (xhr.status == 200) {                                   //on successful response, display the requested form
        parsed = JSON.parse(xhr.response)
        value = parsed['data']
        var formHolder = document.getElementById('form-container')
        formHolder.innerHTML=value
        submitButton = document.querySelector('input[type="submit"]')
        overrideSubmit(submitButton, formHolder)                //nested function which restructures the submit request
      }                                                         // into a custom ajax request, allowing for a tailored
      else {                                                    // response and thus avoiding the re-rendering of the
        //pass atm                                              // whole page
      }
    }
  })
}

function overrideSubmit(submitButton, formHolder) {
  /**
   * Function that acts as a nested function withing "editProfile" function, overriding the submit button behaviour,
   *  and sending the form data in the body of the ajax request.
   * On successful response, and if the form is validated in the view function, it empties the form, and renders the
   *  option tabs not-clicked. On successful response but when the form was not validated, it renders the response
   *  containing the form with validation errors back into the page.
   *
   */
  submitButton.addEventListener('click', function(e) {
    e.preventDefault()
    var formData = new FormData(document.getElementsByTagName('form')[0])   //get the form data to be passed into the
    var formDataFinal = JSON.stringify(Object.fromEntries(formData))        // body of the ajax request
    var xhr2 = new XMLHttpRequest()
    xhr2.open('POST', '/profile/Marko', true)
    xhr2.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
    xhr2.setRequestHeader('Accept', 'application/json;charset=UTF-8')
    xhr2.send(JSON.stringify({'data': formDataFinal, 'submit':submitButton.id}))
    xhr2.onload = function() {
    if (xhr2.status == 200) {                               //three possible successful responses:
      alert(xhr2.response)                                  // •'updated' = changes made > reset accordion + flash info
      parsed = JSON.parse(xhr2.response)                    // •'no change' > reset accordion
      value = parsed['data']                                // • other = response is a form with rendered errors, sent
      if(value=='updated') {                                //   as html code, rendered back into the form container
        createFlashMessage('your profile has been updated ')
      }
      if((value == 'updated') || (value == 'no change')) {
        let options = document.getElementById('options-container')      //reset the accordion appearance if there were
        options = [...options.children]                                 // no changes or the updates were made
        options.forEach(opt => opt.classList.remove('chosen-option'))
        value = ''
      } else {
      var formHolder = document.getElementById('form-container')        //serve back the form with rendered errors
      formHolder.innerHTML=value                                        // if the validation did not pass
      submitButton = document.querySelector('input[type="submit"]')
      overrideSubmit(submitButton, formHolder)                          //function calls itself, in order to add the
      return                                                            // necessary functionality back to the newly
      }                                                                 // rendered form containing validation errors
    } else {
      //pass atm
    }
    var formHolder = document.getElementById('form-container')
    formHolder.innerHTML=value
    }
  })
}

editProfile()                                                           //call the function when the script is imported







