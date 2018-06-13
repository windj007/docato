function make_fill_height($elem, $bottom, min_height, bottom_offset) {
	var $window = $(window)
	function update_height() {
		var height = $window.height() - $bottom.outerHeight() - $elem.offset().top - bottom_offset;
		if (height < min_height)
			height = min_height;
		$elem.css('height', height + 'px');
	}
	update_height();
	$window.resize(update_height);
}