var currentReader = 0;
function toggleReader(id) {
	currentReader = id;
	$('#reader-modal' + id).toggleClass('hide');
	$('#reader-modal' + id).toggleClass('fade-in-fast');
	$('#bnav' + id).toggleClass('hide');
	$('#bnav' + id).toggleClass('fade-in-fast');
	setTimeout(function() {
		$('#reader-modal' + id).toggleClass('fade-in-fast');
		$('#bnav' + id).toggleClass('fade-in-fast');
	}, 1000);
}
function jumpbookto(page) {
	document.getElementById('reader-modal' + currentReader).scrollTo(0, (parseInt(document.getElementById('jumpto' + page).value)-1) * parseInt(window.innerHeight));
	document.getElementById('pagecount' + page).innerHTML = parseInt(document.getElementById('jumpto' + page).value);
}
