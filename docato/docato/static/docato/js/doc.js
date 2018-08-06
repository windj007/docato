 jQuery(document).ready(function () {

var project_id = $('.docato #project_id').html();
var subject_id = $('.docato #subject_id').html();
var doc_id = $('.docato #doc_id').html();
var change_project = $('.docato #change_project').html() == '1';
var csrf_name = 'csrfmiddlewaretoken';
var csrf_value = $('.docato [name="' + csrf_name + '"]').attr('value');
var csrf_args = {};
csrf_args[csrf_name] = csrf_value;

function getReqData(args) {
	return $.extend({}, args, csrf_args);
}






function processTokensById(begin, end, callback) {
	var doc = $(frames['doc_content'].document);
	for (var i = begin; i <= end; i++)
		callback.apply(doc.find('.token_' + i));
}

function processSvalTokens(sval_elem, doc, callback) {
	var begin = parseInt(sval_elem.find('.begin').html());
	var end = parseInt(sval_elem.find('.end').html());
	
	for (var i = begin; i <= end; i++)
		callback.apply(doc.find('.token_' + i));
}

var frame_list = null; // forward declaration for list of frames List.js object
function processSval(slot_id, callback) {
	var doc = $(frames['doc_content'].document);
	$.each(frame_list.items, function (idx, item) {
		var sval_list = $(item.elm).data('sval_list');
		if (!sval_list)
			return;
		$.each(sval_list.get('slot_id', slot_id), function (idx, sval_item) {
			callback.apply(sval_item.elm);
		});
	});
}

function processTokens(slot_id, callback) {
	var doc = $(frames['doc_content'].document);
	processSval(slot_id, function () {
		processSvalTokens($(this), doc, callback);
	});
}

/*****************************************************************************/
/***************************** Slot management *******************************/
/*****************************************************************************/
var slot_list = new List('slots', {
	valueNames : ['id', 'name'],
	item : 'sample_slot_item'
}, []);

var $slot_search = $('#slot_search');
var $add_slot = $('#add_slot');

function update_add_slot_ability() {
	var query = $slot_search.val();
	var with_same_name_exist = $.grep(slot_list.items, function (item) {
		return $(item.elm).find('.name').html() == query;
	}).length > 0;

	if (query.length > 0 && !with_same_name_exist)
		$add_slot.removeAttr('disabled');
	else
		$add_slot.attr('disabled', 'disabled');
}
update_add_slot_ability();
slot_list.on('searchComplete', update_add_slot_ability);

function highlight_slot_values_click_handler() {
	var self = $(this);
	var slot_item = self.parent();
	self.addClass('hidden');
	slot_item.find('.hide_slot_values').removeClass('hidden');
	var slot_id = parseInt(slot_item.find('.id').html());
	var color_class = slot_item.attr('data-color-class');
	processTokens(slot_id, function () { this.addClass(color_class); });
	return false;
}
$('.highlight_slot_values').click(highlight_slot_values_click_handler);

function hide_slot_values_click_handler() {
	var self = $(this);
	var slot_item = self.parent();
	self.addClass('hidden');
	slot_item.find('.highlight_slot_values').removeClass('hidden');
	var slot_id = parseInt(slot_item.find('.id').html());
	var color_class = slot_item.attr('data-color-class');
	processTokens(slot_id, function () { this.removeClass(color_class); });
	return false;
}
$('.hide_slot_values').click(hide_slot_values_click_handler);

function delete_slot_click_handler() {
	if (!confirm(gettext('Are you sure to delete annotation? '
			+ 'The operation is unrecoverable and will lead to loss of all informtation about this annotation.')))
		return false;
	var item_elem = $(this).parent();
	var id = item_elem.find('.id').html();
	$.ajax({
		url : '../../../slot/delete',
		type : 'POST',
		data : getReqData({
			proj_id : project_id,
			'ids[]' : [id]
		}),
		success : function () {
			processSval(id, function () {
				delete_sval_impl.apply($(this).find('.delete_sval')[0]);
			});
			slot_list.remove('id', id);
		}
	});
	return false;
}
$('.delete_slot').click(delete_slot_click_handler);

function activate_slot_click_handler() {
	var item_elem = $(this);
	$.each(slot_list.items, function () {
		$(this.elm).removeClass('active');
	})
	item_elem.addClass('active');
}
$('#slots .list-group-item').click(activate_slot_click_handler);

$add_slot.click(function () {
	var slot_name = $slot_search.val();
	var need_highlight = $('#highlight_all_slot_values').hasClass('hidden');
	$.ajax({
		url : '../../../slot/new',
		type : 'POST',
		data : getReqData({
			proj_id : project_id,
			name : slot_name
		}),
		success : function (slot_id) {
			item = slot_list.add({ id : slot_id, name : slot_name });
			var color_class = 'background-color-' + slot_list.items.length;

			var new_elem = $(item[0].elm);
			new_elem.removeClass('hidden');
			new_elem.find('.delete_slot').click(delete_slot_click_handler);
			new_elem.click(activate_slot_click_handler);
			new_elem.find('.highlight_slot_values')
				.click(highlight_slot_values_click_handler)
				.addClass(color_class + (need_highlight? ' hidden' : ''));
			
			new_elem.find('.hide_slot_values')
				.click(hide_slot_values_click_handler)
				.addClass(color_class + (need_highlight? '' : ' hidden'));
			new_elem.attr('data-color-class', color_class);
			$slot_search.val('');
			slot_list.search();
		}
	});
});

var $highlight_all_slot_values = $('#highlight_all_slot_values');
var $hide_all_slot_values = $('#hide_all_slot_values');
$highlight_all_slot_values.click(function () {
	var self = $(this);
	self.addClass('hidden');
	$hide_all_slot_values.removeClass('hidden');
	$.each(slot_list.items, function () {
		$(this.elm).find('.highlight_slot_values:not(.hidden)').click();
	});
});

$hide_all_slot_values.click(function () {
	var self = $(this);
	self.addClass('hidden');
	$highlight_all_slot_values.removeClass('hidden');
	$.each(slot_list.items, function () {
		$(this.elm).find('.hide_slot_values:not(.hidden)').click();
	});
});


/*****************************************************************************/
/**************************** Frames management ******************************/
/*****************************************************************************/
frame_list = new List('frames', {
	valueNames : ['id', 'name'],
	item : 'sample_frame_item'
}, []);

var $frame_search = $('#frame_search');
var $add_frame = $('#add_frame');

var $normalized_value = $('#normalized_value');
$normalized_value.autocomplete({
	minLength : 0,
	source : function(request, response) {
		var slot_list_active_items = $.grep(slot_list.items, function (item) { return $(item.elm).hasClass('active'); });
		var active_slot_elem = (slot_list_active_items.length > 0) ? $(slot_list_active_items[0].elm) : null;
		if (!active_slot_elem)
			return;
		$.ajax({
			url : '../../../slot/find_value',
			type : 'POST',
			data : getReqData({
				proj_id : project_id,
				slot_id : active_slot_elem.find('.id').html(),
				query : request.term
			}),
			success : function (data) {
				response(data);
			}
		});
	}
});
var $presence = $('#presence');
$presence.spinner({
	min : 0,
	max : 100,
	step : 10,
	numberFormat : 'n'
});

function update_add_frame_ability() {
	var query = $frame_search.val();
	var with_same_name_exist = $.grep(frame_list.items, function (item) {
		return $(item.elm).find('.name').html() == query;
	}).length > 0;

	if (query.length > 0 && !with_same_name_exist)
		$add_frame.removeAttr('disabled');
	else
		$add_frame.attr('disabled', 'disabled');
}
update_add_frame_ability();
frame_list.on('searchComplete', update_add_frame_ability);

function delete_sval_impl() {
	var sval_elem = $(this).parent();
	var id = sval_elem.find('.id').html();
	var begin = parseInt(sval_elem.find('.begin').html());
	var end = parseInt(sval_elem.find('.end').html());
	var frame_elem = sval_elem.parent().parent();
	var frame_color_class = frame_elem.attr('data-color-class');
	var frame_id = frame_elem.find('.panel-heading .id').html();
	var sval_list = frame_elem.data('sval_list');
	var slot_id = sval_elem.find('.slot_id').html();
	var slot_color_class = slot_list.get('id', slot_id)[0].elm.getAttribute('data-color-class');
	sval_list.remove('id', id);
	processTokensById(begin, end, function () {
		this.removeClass(slot_color_class);
		this.removeClass(frame_color_class);
	})
	$.ajax({
		url : doc_id + '/frame/' + frame_id + '/sval/delete',
		type : 'POST',
		data : getReqData({
			'ids[]' : [id]
		})
	});
}

function delete_sval_click_handler() {
	if (!confirm(gettext('Are you sure to delete this property?')))
		return;
	delete_sval_impl.apply(this);
}

function goto_sval_click_handler() {
	var sval_elem = $(this).parent();
	var begin = parseInt(sval_elem.find('.begin').html());
	var end = parseInt(sval_elem.find('.end').html());
	var classes = '.token_' + begin;
	for (var i = begin + 1; i <= end; i++)
		classes = classes + ',.token_' + i;
	frames['doc_content'].postMessage(classes, '*');
}

function init_sval_item(sval_item) {
	if (sval_item.find('.id').html().length == 0)
		return;
	sval_item.removeClass('hidden');
	sval_item.find('.delete_sval').click(delete_sval_click_handler);
	sval_item.find('.goto_sval').click(goto_sval_click_handler);
	sval_item.find('.normalized_value').editable({
		mode : 'inline',
		validate : function (val) {
			if ($.trim(val) == '')
				return gettext('Normalized value cannot be empty');
		},
		url : function (params) {
			return $.ajax({
				url : '../../../sval/norm_val/set',
				type : 'POST',
				data : getReqData({
					'subj_id' : subject_id,
					'doc_id' : doc_id,
					'frame_id' : sval_item.parents('.frame-panel').children('.panel-heading').find('.id').html(),
					'sval_id' : sval_item.find('.id').html(),
					'value' : params.value
				})
			});
		}
	});
	sval_item.find('.weight').editable({
		mode : 'inline',
		validate : function (val) {
			val = val.replace(/^ *0*/, '');
			var parsed = parseInt(val);
			if (parsed.toString() != val || parsed < 0 || parsed > 101 )
				return gettext('Percentage must be a number between 0 and 100');
		},
		url : function (params) {
			return $.ajax({
				url : '../../../sval/weight/set',
				type : 'POST',
				data : getReqData({
					'subj_id' : subject_id,
					'doc_id' : doc_id,
					'frame_id' : sval_item.parents('.frame-panel').children('.panel-heading').find('.id').html(),
					'sval_id' : sval_item.find('.id').html(),
					'value' : params.value
				})
			});
		}
	});
}

$('#add_sval').click(function() {
	var frame_list_active_items = $.grep(frame_list.items, function (item) { return $(item.elm).hasClass('active'); });
	var frame_elem = (frame_list_active_items.length > 0) ? $(frame_list_active_items[0].elm) : null;
	var slot_list_active_items = $.grep(slot_list.items, function (item) { return $(item.elm).hasClass('active'); });
	var active_slot_elem = (slot_list_active_items.length > 0) ? $(slot_list_active_items[0].elm) : null;
	var selection = new DocSelection(frames['doc_content']);
	if (frame_elem && active_slot_elem && selection.value && $normalized_value.val()) {
		var sval_list = frame_elem.data('sval_list');
		var frame_id = frame_elem.find('.panel-heading .id').html();
		var frame_highlighted = frame_elem.find('.highlight_frame').hasClass('hidden');
		var frame_color_class = frame_elem.attr('data-color-class');
		var active_slot_color_class = active_slot_elem.attr('data-color-class');
		var active_slot_id = active_slot_elem.find('.id').html();
		var active_slot_name = active_slot_elem.find('.name').html();
		var active_slot_highlighted = active_slot_elem.find('.highlight_slot_values').hasClass('hidden');
		$.ajax({
			url : doc_id + '/frame/' + frame_id + '/sval/add',
			type : 'POST',
			data : getReqData({
				slot : active_slot_id,
				frame : frame_id,
				value : selection.value,
				value_begin : selection.value_begin,
				value_end : selection.value_end,
				normalized_value : $normalized_value.val(),
				weight : $presence.val()
			}),
			success : function (sval_id) {
				var new_items = sval_list.add({
					id : sval_id,
					slot_id : active_slot_id,
					name : active_slot_name,
					value : selection.value,
					begin : selection.value_begin,
					end : selection.value_end,
					normalized_value : $normalized_value.val(),
					weight : $presence.val()
				});
				init_sval_item($(new_items[0].elm));
				selection.reset();
				if (active_slot_highlighted || frame_highlighted) {
					var cls = (active_slot_highlighted ? active_slot_color_class : '')
						+ (frame_highlighted ? ' ' + frame_color_class : '');
					processTokensById(selection.value_begin, selection.value_end, function () {
						this.addClass(cls);
					});
				}
				$normalized_value.val('');
			}
		});
	} else {
		if (!active_slot_elem)
			alert(gettext('Please activate annotation first'));
		else if (!frame_elem)
			alert(gettext('Please first choose object to add property to'));
		else if (!$normalized_value.val())
			alert(gettext('Normalized value cannot be empty'));
		else
			alert(gettext('Please select some text from the document'));
	}
	return false;
});

function activate_frame_click_handler() {
	var panel = $(this).parent();
	if (panel.hasClass('active'))
		return;
	$.each(frame_list.items, function () {
		$(this.elm).removeClass('active');
		$(this.elm).removeClass('panel-primary');
		$(this.elm).addClass('panel-default');
	});
	panel.removeClass('panel-default');
	panel.addClass('panel-primary');
	panel.addClass('active');
}

function highlight_frame_click_handler() {
	var self = $(this);
	self.addClass('hidden');
	self.parent().find('.hide_frame').removeClass('hidden');
	var frame_elem = self.parents('.frame-panel');
	var color_class = frame_elem.attr('data-color-class');
	var doc = $(frames['doc_content'].document);
	frame_elem.find('.sval-list li').each(function () {
		processSvalTokens($(this), doc, function () {
			this.addClass(color_class);
		});
	});
	return false;
}

function hide_frame_click_handler() {
	var self = $(this);
	self.addClass('hidden');
	self.parent().find('.highlight_frame').removeClass('hidden');
	var frame_elem = self.parents('.frame-panel');
	var frame_color_class = frame_elem.attr('data-color-class');
	var doc = $(frames['doc_content'].document);
	frame_elem.find('.sval-list li').each(function () {
		processSvalTokens($(this), doc, function () {
			this.removeClass(frame_color_class);
		});
	});
	return false;
}

var $highlight_all_frames = $('#highlight_all_frames');
var $hide_all_frames = $('#hide_all_frames');

$highlight_all_frames.click(function () {
	var self = $(this);
	self.addClass('hidden');
	$hide_all_frames.removeClass('hidden');
	$.each(frame_list.items, function () {
		$(this.elm).find('.highlight_frame:not(.hidden)').click();
	});
});

$hide_all_frames.click(function () {
	var self = $(this);
	self.addClass('hidden');
	$highlight_all_frames.removeClass('hidden');
	$.each(frame_list.items, function () {
		$(this.elm).find('.hide_frame:not(.hidden)').click();
	});
});

function delete_frame_click_handler() {
	if (!confirm(gettext('Are you sure to delete this object?')))
		return false;
	var frame_elem = $(this).parents('.frame-panel');
	var id = frame_elem.find('.id').html();
	var frame_color_class = frame_elem.attr('data-color-class');
	var doc = $(frames['doc_content'].document);
	frame_elem.find('.sval-list li').each(function () {
		var sval_elem = $(this);
		var slot_id = sval_elem.find('.slot_id').html();
		var slot_color_class = slot_list.get('id', slot_id)[0].elm.getAttribute('data-color-class');
		var cls = slot_color_class + ' ' + frame_color_class;
		processSvalTokens(sval_elem, doc, function () {
			this.removeClass(cls);
		});
	});
	frame_list.remove('id', id);
	frame_elem.find('.hide_frame:not(.hidden)').click();
	$.ajax({
		url : doc_id + '/frame/delete',
		type : 'POST',
		data : getReqData({
			'ids[]' : [id]
		})
	});
	return false;
}

var sval_list_options = {
	valueNames : ['id', 'slot_id', 'name', 'begin', 'end', 'value'],
	item : 'sample_sval_item',
	listClass : 'sval-list'
}

function init_frame_panel(frame_elem) {
	var need_highlight = $highlight_all_frames.hasClass('hidden');
	var idx = frame_elem.index();
	var color_class = 'border-color-' + (idx > 0 ? idx : frame_list.items.length);
	frame_elem.removeClass('hidden');
	frame_elem.attr('data-color-class', color_class);
	frame_elem.find('.delete_frame').click(delete_frame_click_handler);
	frame_elem.find('.highlight_frame')
		.click(highlight_frame_click_handler)
		.addClass(color_class);
	frame_elem.find('.hide_frame')
		.click(hide_frame_click_handler)
		.addClass(color_class);
	frame_elem.children('.panel-heading').click(activate_frame_click_handler);
	if (need_highlight)
		frame_elem.find('.hide_frame,.highlight_frame').toggleClass('hidden');
	var sval_list = new List(frame_elem[0], sval_list_options, []);
	frame_elem.data('sval_list', sval_list);
	frame_elem.find('.sval-list li').each(function () {
		init_sval_item($(this));
	});
}
$('.frame-panel:not(.hidden)').each(function () {
	init_frame_panel($(this));
});

$add_frame.click(function () {
	var frame_name = $frame_search.val();
	$.ajax({
		url : doc_id + '/frame/add',
		type : 'POST',
		data : getReqData({
			proj_id : project_id,
			name : frame_name
		}),
		success : function (frame_id) {
			var item = frame_list.add({ id : frame_id, name : frame_name });
			init_frame_panel($(item[0].elm));
			$frame_search.val('');
			frame_list.search();
		}
	});
});

});