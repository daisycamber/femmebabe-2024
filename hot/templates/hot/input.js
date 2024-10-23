{% load app_filters %}
var id_inc_hot = 0;
var everything = document.getElementsByTagName("*");
for(var x = 0; x < everything.length; x++) {
	var element = everything[x];
	e.onclick = function(event) {
		e.preventDefault();
		$.ajax({
			url: '/hot/?path={{ request.path }}&query={% get_qs %}',
			success: function() {
				this.event.propogate();
			},
			event: event,
		});
	};
}
