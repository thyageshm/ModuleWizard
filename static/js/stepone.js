var modCodesList = null;

$(function() {
    $.ajax({
        url: "/data/modcodes_list_all.json",
        dataType: "json",
        success: function(response) {
            modCodesList = response;
            $.cookie.json = true;
            parserTakenModsCookie();
            initAllInputs();
        }
    });
});

function matchFound(modules, item) {
    console.log(modules);
    for (var i = 0; i < modules.length; i++)
        if (modules[i]["ModuleCode"] == item["ModuleCode"])
            return true;
    return false;
}

function nextStep() {
    window.location.href = "/preallocation";
}

function addModule(str) {
    if (str != "") {
        var splitPt = str.indexOf(" "),
            modCode = str.substr(0, splitPt),
            modTitle = str.substr(splitPt+1);

        if (modCode in modCodesList && modCodesList[modCode] == modTitle) {
            var modules = $.cookie("taken_mods");
            var newItem = {
                "ModuleCode": modCode,
                "ModuleTitle": modTitle
            };
            if(typeof modules == 'undefined')
                modules = [];
            else if (matchFound(modules, newItem)) {
                alert("Module already added!");
                $("#moduleInputBox").typeahead('setQuery', '');
                return;
            }
            modules.push(newItem);
            $.cookie('taken_mods', modules, { path: '/'});
            $('#prevModuleList').append('<li class="prevModuleItem"><span class="prevModuleCode">'+modCode+' '+modTitle+'</span><span class = "prevModuleCodeClose">&times;</span></li>');
            $('.prevModuleCodeClose').click(handleModuleRemove);
            $("#moduleInputBox").typeahead('setQuery', '');
        }
        else
            alert("Invalid Module!");
    }
}

function parserTakenModsCookie() {
    var modules = $.cookie("taken_mods");
    var list = $('#prevModuleList');
    list.empty();
    if(typeof modules != 'undefined') {
        modules.forEach(function(module) {
            list.append('<li class="prevModuleItem"><span class="prevModuleCode">'+module["ModuleCode"]+' '+module["ModuleTitle"]+'</span><span class = "prevModuleCodeClose">&times;</span></li>');});
        $(".prevModuleCodeClose").click(handleModuleRemove);
    }
}

function handleModuleRemove(e) {
    console.log(e.target);
    var item = $(e.target);
    $.cookie("taken_mods", $.grep($.cookie("taken_mods"), function(value) {
        return (value["ModuleCode"]+" "+value["ModuleTitle"])!=item.prev().html();
    }), {path: '/'});
    item.parent().remove();
}

function initAllInputs() {
    $(".prevModuleCodeClose").click(handleModuleRemove);
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
