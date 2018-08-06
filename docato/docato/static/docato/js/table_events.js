var TableEvents = {};

jQuery(document).ready(function ($) {

TableEvents = function(opts) {
	var default_opts = {
			table : 'table',

			enable_selection : true,
			select_all_cb : 'thead .select input[type="checkbox"]',
			select_cb : 'tbody .select input[type="checkbox"]',
			
			delete_button : 'thead .select input[type="checkbox"]',
			delete_confirm_message : gettext('Are you sure to delete the selected records?'),
			delete_url : 'delete',
			after_delete : function () { location.reload(); },
	
			ignore_click_elements: 'a',
			
			row_as_links : true,
			row_selector : 'tbody tr',
			get_row_link : function (row) { return "#"; },
			csrf_token_selector : '[name="csrfmiddlewaretoken"]',
			
			additional_row_click_handler : null
	};

	opts = $.extend({}, default_opts, opts);

	var table = $(opts.table);
	var delete_button = $(opts.delete_button);
	var select_all_cb = table.find(opts.select_all_cb);
	var select_checkboxes = table.find(opts.select_cb);

	var disable_select_all = false;
	
	var csrf_token = $(opts.csrf_token_selector);

	if (opts.enable_selection) {
		select_checkboxes.click(function () {
			disable_select_all = true;
			if (select_checkboxes.is(':not(:checked)') ^ select_all_cb.is(':not(:checked)'))
				select_all_cb.click();
			disable_select_all = false;
		});

		select_all_cb.click(function () {
			if (disable_select_all)
				return;
			if (this.checked)
				select_checkboxes.not(':checked').click();
			else
				select_checkboxes.click();
		});
		
		delete_button.click(function() {
			var selected_ids = select_checkboxes.filter(':checked').map(function () { return this.value; } ).get()
			if (selected_ids.length > 0 && confirm(opts.delete_confirm_message)) {
				var req_data = {
					ids : selected_ids
				};
				req_data[csrf_token.attr('name')] = csrf_token.attr('value')
				$.ajax({
					url  : opts.delete_url,
					type : 'post',
					data : req_data,
					success : opts.after_delete
				});
			}
		});
	}
	
	if (opts.row_as_links) {
		table.find(opts.row_selector).click(function (e) {
			if ($(e.target).is(opts.select_cb) || $(e.target).is(opts.ignore_click_elements))
				return;
			location.href = opts.get_row_link.apply(this);
			if (opts.additional_row_click_handler)
				opts.additional_row_click_handler.apply(this);
		});
	}
};
	


	
});