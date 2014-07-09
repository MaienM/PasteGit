// From http://stackoverflow.com/a/7124052
function htmlEscape(str) {
    return String(str)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
}

$(function() {
	// Init the editor.
	var editor = new EpicEditor({
		basePath: '/static/bower_components/epiceditor/epiceditor/',
		clientSideStorage: false,
	}).load();

	// Give the editor a sensible size.
	var element = $('#epiceditor');
	var container = $(element).parents('.container');
	var lastitem = $(container).find('*:last-child');
	var height = $(container).height() - $(container).offset().top - $(lastitem).offset().top - $(lastitem).innerHeight() - $(element).innerHeight();
	$(element).height(height);
	editor.reflow('height');

	// Save/load.
	editor.importFile('epiceditor', htmlEscape($('#content').val()));
	$('#submit').click(function() {
		$('#content').val(editor.exportFile());
	});
});
