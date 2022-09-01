(function () {                              // Prevent the page from loading from cache - TODO maybe superfluous?
	window.onpageshow = function(event) {
		if (event.persisted) {
			window.location.reload();
		}
	};
})()

// Adding autofill and autosuggest functionalities for the referent nodes in the item entry page view
autoSuggest('item', 'items')
autoSuggest('category', 'categories')
autoFill('item', 'category', 'category')



