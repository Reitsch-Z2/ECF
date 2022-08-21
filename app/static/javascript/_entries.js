(function () {                              //TODO maybe superfluous?
	window.onpageshow = function(event) {
		if (event.persisted) {
			window.location.reload();
		}
	};
})()

//adding autofill and autosuggest functionalities for the referent nodes in the item entry page view
autoSuggest('item', 'items')
autoSuggest('category', 'categories')
autoFill('item', 'category', 'category')



