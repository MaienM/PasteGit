$(function() {
	// Markdownify the content.
	$('#markdown').html(marked($('#markdown').html()));

	// Show the content.
	$('#markdown').removeClass('hidden');

	// Anchor links.
	$('body').delegate('a[href^="#"]', 'click', function(e) {
		$('html, body').animate({
			scrollTop: $($(this).attr('href')).offset().top - 120,
		}, 800);
		window.location.href = window.location.href.split('#')[0] + $(this).attr('href');
		e.preventDefault();
	});
});
