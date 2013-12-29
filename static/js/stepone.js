$(function() {
    $.cookie.json = true;
    parserTakenModsCookie();
    initAllInputs();
});

function parserTakenModsCookie() {
    var modules = $.cookie("taken_mods");
    var list = $('#prevModuleList');
    list.empty();
    modules.forEach(function(module) {
        list.append('<li class="prevModuleItem"><span class="prevModuleCode">'+module["ModuleCode"]+'</span><span class = "prevModuleCodeClose">&times;</span></li>');
    });
    $(".prevModuleCodeClose").click(handleModuleRemove);
}

function handleModuleRemove(e) {
    var item = $(e.target);
    $.cookie("taken_mods", $.grep($.cookie("taken_mods"), function(value) {
        return value["ModuleCode"]!=item.prev().html();
    }), {path: '/'});
    item.parent().remove();
}

function initAllInputs() {
    $(".prevModuleCodeClose").click(handleModuleRemove);
}
