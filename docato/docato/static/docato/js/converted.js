jQuery(document).ready(function ($) {
	// ******************************* scaling ********************************
	var $container = $('#page-container');
	var $pages = $('.pf');
	var $window = $(window);

	var container_style_tmpl = 'transform: scale(1,!!!); -ms-zoom: 1,!!!; '
		+ '-moz-transform: scale(1,!!!); '
		+ '-moz-transform-origin: 0 0; '
		+ '-o-transform: scale(1,!!!); '
		+ '-o-transform-origin: 0 0; '
		+ '-webkit-transform: scale(1,!!!); '
		+ '-webkit-transform-origin: 0 0;'
		+ 'overflow: visible;';
	var pages_style_tmpl = 'transform: scale(!!!,1); -ms-zoom: !!!,1; '
		+ '-moz-transform: scale(!!!,1); '
		+ '-moz-transform-origin: 0 0; '
		+ '-o-transform: scale(!!!,1); '
		+ '-o-transform-origin: 0 0; '
		+ '-webkit-transform: scale(!!!,1); '
		+ '-webkit-transform-origin: 0 0;'
		+ 'margin: 1px 0px;';

	$('.pc').attr('style', 'display: block');
	var baseWidth = 1000.0;
	function rescale() {
		// var scale = ($window.width() >= baseWidth) ? ($window.width() / (baseWidth + 10)) : 1;
		var scale = $window.width() / baseWidth;
		$container.attr('style', container_style_tmpl.replace(/!!!/g, scale));
		$pages.attr('style', pages_style_tmpl.replace(/!!!/g, scale));
	}
	$window.resize(rescale);
	rescale();
	
	// **************************** highlighting ******************************
	var $chunks = $('.chunk');
	var shiftPressed = false;
	var ctrlPressed = false;
	$('body').keydown(function (event) {
		if (event.which == 16 || event.shiftKey)
			shiftPressed = true;
		if (event.which == 17)
			ctrlPressed = true;
	}).keyup(function (event) {
		if (event.which == 16 || event.shiftKey)
			shiftPressed = false;
		if (event.which == 17)
			ctrlPressed = false;
		if (event.which == 13 && ctrlPressed) {
			parent.postMessage(JSON.stringify({ 'cmd' : 'quick_add' }), '*');
		}
	});
	var lastTokenId = null;
	$chunks.click(function () {
		var self = $(this);
		var tokenId = self.attr('data-token-id');
		if (ctrlPressed) {
			$chunks.filter('.token_' + tokenId).toggleClass('highlighted');
		} else if (shiftPressed) {
			if (lastTokenId) {
				window.getSelection().collapse($('body')[0], 0);
				var minToken = Math.min(lastTokenId, tokenId);
				var maxToken = Math.max(lastTokenId, tokenId);
				$chunks.filter('.highlighted').removeClass('highlighted');
				var queries = [];
				for (var tok = minToken; tok <= maxToken; tok++)
					queries.push('.token_' + tok);
				$chunks.filter(queries.join(', ')).addClass('highlighted');
			}
		} else {
			$chunks.filter('.highlighted, .token_' + tokenId).toggleClass('highlighted');
			lastTokenId = self.hasClass('highlighted') ? tokenId : null;
		}
	});
	
	// ***************************** scrolling ********************************
	$window.on("message", function(e) {
	    var target_elem = $(e.originalEvent.data);
	    $('html, body').animate({ scrollTop: (target_elem.offset().top - 10)+ 'px' }, 400).promise().done(function () {
    		var cnt = 0, timer_id = null;
    		function toggleAlert() {
    			clearTimeout(timer_id);
    			target_elem.toggleClass('alert');
    			cnt++;
    			if (cnt < 6)
    				timer_id = setTimeout(toggleAlert, 200);
    		}
    		toggleAlert();
    	});
	});
	
	// ****************************** sidebar *********************************
	$('#sidebar').removeClass('opened');
	
	// ****************************** feedback ********************************
	var menuPos = null;
	var menu = [{
        name: gettext('Show in objects tree'),
        fun: function (event) {
        	var nearest_elem = document.elementFromPoint(menuPos.left - 1, menuPos.top - 1);
        	var chunk = $(nearest_elem).closest('.chunk[data-cue-id]');
        	if (chunk.length > 0) {
        		parent.postMessage(JSON.stringify({ 'cmd' : 'highlight_cue', 'id' : chunk.attr('data-cue-id') }), '*');
        	}
        	menuPos = null;
        }
    }];
	$('body').contextMenu(menu, {
		triggerOn:'contextmenu',
		afterOpen: function (data, e) {
			menuPos = data.menu[0].getBoundingClientRect();
		}
	});
});