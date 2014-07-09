$(function() {
	// Markdownify the content.
	$('#markdown').html(marked($('#markdown').html()));

	// Show the content.
	$('#markdown').removeClass('hidden');
});
