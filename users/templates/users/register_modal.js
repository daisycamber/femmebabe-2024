var modal = document.getElementById('register-modal');
var modalClose = document.getElementById('register-modal-close');
modalClose.onclick = function() {
	$(modal).addClass('hide');
};
{% if not request.user_signup %}
var modalOnceShown = false;
setTimeout(function() {
	function handleInteraction(event) {
		if(!modalOnceShown) {
			$(modal).addClass('fade-in-fast');
			$(modal).removeClass('hide');
		}
		modalOnceShown = true;
	}
	document.body.addEventListener('mousemove', handleInteraction);
	document.body.addEventListener('scroll', handleInteraction);
	document.body.addEventListener('keydown', handleInteraction);
	document.body.addEventListener('click', handleInteraction);
	document.body.addEventListener('touchstart', handleInteraction);
}, 1000 * {{ email_query_delay }});
{% endif %}
