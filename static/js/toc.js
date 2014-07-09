$(function() {
	// Create the table of contents.
	var prevli = null;
	var level = 2;
	$('#markdown').find('h2, h3, h4').each(function() {
		// Determine the level of this header.
		var nlevel = Number(/[0-9]+/.exec($(this).prop('tagName')));

		// Create a new li element for this header.
		var li = $('<li></li>');
		var a = $('<a></a>');
		$(a).attr('href', '#' + $(this).attr('id'));
		$(a).text($(this).text());
		$(li).append(a);

		// If this is the first header, add it to the root and mark it as active.
		var menu = null
		if (prevli == null) {
			menu = $('#toc ul').first();
			$(li).addClass('active');
		}

		// If the new header is nested further than the previous header, we need to create a new ul in the previous li.
		else if (nlevel > level) {
			menu = $('<ul></ul>');
			$(menu).addClass('nav nav-stacked');
			$(prevli).append(menu);
		}

		// If the new header is nested on the same level as the previous one, we want to use the same ul as the previous one.
		else if (nlevel == level) {
			menu = $(prevli).parents('ul').first();
		}

		// If we're nested further up, we want to use the ul of our current parent.
		else {
			menu = $(prevli).parents('li').parents('ul').first();
		}

		// Add ourselves to the menu.
		$(menu).append(li);

		// Store data.
		prevli = li;
		level = nlevel;
	});

	// TOC scrollspy.
	$('body').scrollspy({
		target: '#toc',
		offset: 125,
	});

	// TOC links.
	$('#toc a').click(function(e) {
		$('html, body').animate({
			scrollTop: $($(this).attr('href')).offset().top - 120,
		}, 800);
		e.preventDefault();
	});
});
