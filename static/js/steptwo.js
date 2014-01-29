var modCodesList = null;

$(function() {
    $.ajax({
        url: "/data/modcodes_list_all.json",
        dataType: "json",
        success: function(response) {
            modCodesList = response;
            $.cookie.json = true;
            //parserTakenModsCookie();
            initAllInputs();
        }
    });
});


function initAllInputs() {
    var inputBox = $("#moduleInputBox");
    inputBox.typeahead({
        name: 'module-lookup',
        prefetch: '/data/mod_list_all.json',
        limit: 8
    });
    inputBox.keyup(function (e) {
        if (e.keyCode == 13) addModule($(e.target).val());
    });
    inputBox.on('typeahead:selected', function (object, datum) {
        addModule(datum["value"]);
    });
}