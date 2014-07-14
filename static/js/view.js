$(function() {
	// Anchor links.
	$('body').delegate('a[href^="#"]', 'click', function(e) {
		$('html, body').animate({
			scrollTop: $($(this).attr('href')).offset().top - 10,
		}, 800);
		window.location.href = window.location.href.split('#')[0] + $(this).attr('href');
		e.preventDefault();
	});
	
	// Editable elements.
	$('.editable').editable();
});
