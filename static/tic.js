function addActivity(response, group) {
    newRow = $(response.activity);
    addRowLinkListeners(newRow, group);
    $("#" + group).prepend($(newRow));
}

function addRowLinkListener(activityRow, link, callback) {
    $('a[href="'+ link + '"]', activityRow).click(function() {
            $.post(link, {"key":activityRow.attr("id")}, function(response) {
                if (response.success) {
                    callback(response);
                } else {
                   alert(response.reason);
                }
                }, "json");
            return false;
            });
}

function addRowLinkListeners(activityRow, group) {
    addRowLinkListener(activityRow, "/delete", function() { activityRow.remove(); });
    if (group == "active") {
        addRowLinkListener(activityRow, "/stop",
                function(response) { 
                    activityRow.remove();
                    addActivity(response, "inactive");
                });
    } else {
        addRowLinkListener(activityRow, "/restart",
                function(response) { activityRow.remove(); addActivity(response, "active"); });
        addRowLinkListener(activityRow, "/again",
                function(response) { addActivity(response, "active"); });
    }
}
