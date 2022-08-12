(function () {
	window.onpageshow = function(event) {
		if (event.persisted) {
			window.location.reload();
		}
	};
})()

autoSuggest('item', '.poly', 'items')
autoSuggest('category', '.poly', 'categories')
autoFill('item', 'category', 'category')



