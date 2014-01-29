var modCodesList = null;

$(function() {
    $("#semValue").change(function() {
        changeSem($(this).val());
    });
    $.cookie.json = true;
    //parserTakenModsCookie();
    changeSem(currentSem);
});

function changeSem(sem) {
    $("#moduleSelector").css("display", "none");
    $("#loadingGif").css("display", "");
    $.ajax({
        url: "http://api.nusmods.com/2013-2014/"+sem+"/moduleList.json",
        dataType: "json",
        success: function(response) {
            modCodesList = response;
            initAllInputs(sem);
        }
    });
}

function initAllInputs(sem) {
    $("#moduleSelector").css("display", "");
    $("#loadingGif").css("display", "none");
    var inputBox = $("#modulerInputBox");
    inputBox.typeahead('destroy');
    inputBox.typeahead({
        name: 'module-lookup-sem'+sem,
        prefetch: '/data/mod_list_sem'+sem+'.json',
        limit: 8
    });
    inputBox.keyup(function (e) {
        if (e.keyCode == 13) addModule($(e.target).val());
    });
    inputBox.on('typeahead:selected', function (object, datum) {
        addModule(datum["value"]);
    });
}