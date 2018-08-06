jQuery(document).ready(function ($) {

var events = new TableEvents({
	table: '.docato #subjects',
	delete_button : '#delete_subjects',
	delete_url : 'subject/delete',
	get_row_link : function () {
		return 'subject/' + $(this).find('.select input').attr('value');
	}
});

	
});