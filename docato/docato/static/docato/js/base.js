jQuery(document).ready(function ($) {
	
//$('.docato input[type=submit]').button();
//$('.docato input[type=button]').button();

	var choose_lang_form = $('#choose_language');
	choose_lang_form.find('a').click(function () {
		cur_lang = /setlang_([\S]+)/.exec($(this).attr('class'))[1];
		choose_lang_form.find('input[name="language"]').val(cur_lang);
		choose_lang_form.submit();
		return false;
	});
	
	$('[data-toggle=tooltip]').tooltip();

});