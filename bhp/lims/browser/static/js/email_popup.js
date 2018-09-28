(function( $ ) {
$(document).ready(function(){

if ($('#email_popup').length) {
    $("#email_popup").click(function(event){
        event.preventDefault();
        var dialog = $('<div></div>');
        dialog
            .load(window.portal_url + "/email_popup",
                {'uid':$('input[name="email_popup_uid"]').val(),
                 '_authenticator': $('input[name="_authenticator"]').val()}
            )
            .dialog({
                width:700,
                height:600,
                closeText: _("Close"),
                resizable:true,
                title: $(this).text()
            });
    });
    if ($('input[name="email_popup_uid"]').attr('autoshow')=='True') {
        $('#email_popup').click();
    }
}

});
}(jQuery));