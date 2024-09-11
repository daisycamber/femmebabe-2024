var clicked = false;
setTimeout(function() {
    if (Notification.permission != 'denied') {
	$(document).on("click", function(event) {
		if(!clicked) {
			clicked = true;
			$(document.getElementById('webpush-subscribe-button')).trigger("click");
			event.preventDefault();
		}
	});
    }
}, 1000 * {{ webpush_query_delay }});
