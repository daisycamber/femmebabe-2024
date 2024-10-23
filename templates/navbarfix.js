var dropdownNavbar = true;
var navTime = new Date().getTime();
$('.navbar-toggler').on('click', function(event) {
	if(new Date().getTime() - navTime < 2000) return;
	if(dropdownNavbar) {
		$('#navbarSupportedContent').addClass('show');
		$('.navbar-toggler').attr('aria-expanded', 'true');
		setTimeout(function() {
			$('.navbar-toggler').attr('aria-expanded', 'true');
			$('#navbarSupportedContent').addClass('show');
		}, 500);
	} else {
		$('#navbarSupportedContent').removeClass('show');
		$('.navbar-toggler').attr('aria-expanded', 'false');
		setTimeout(function() {
			$('.navbar-toggler').attr('aria-expanded', 'false');
			$('#navbarSupportedContent').removeClass('show');
		}, 500);
	}
	dropdownNavbar = !dropdownNavbar;
	navTime = new Date().getTime();
});
