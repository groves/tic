function jsonPost(url, values, callback){ $.post(url, values, callback, "json"); }

function makeActivity(response) {
    newRow = $(response.activity);
    addActivityRowListeners(newRow);
    return newRow;
}
function addActivity(response, group) {
    $("#" + group).prepend(makeActivity(response));
}

function addRowLinkListener(activityRow, link, callback) {
    $('a[href="'+ link + '"]', activityRow).click(function() {
            jsonPost(link, {"key":activityRow.attr("id")}, function(response) {
                if (response.success) {
                    callback(response);
                } else {
                   alert(response.reason);
                }
                });
            return false;
            });
}

function addTextEditor(activityRow, cell, link) {
    cell.editable(function(value, settings) {
            jsonPost(link, {"key":activityRow.attr("id"), "value":value}, function(response) {
                activityRow.replaceWith(makeActivity(response));
                });
            }, {"tooltip":"Click to edit..."});
}

function addActivityRowListeners(activityRow) {
    addTextEditor(activityRow, $("td", activityRow).eq(0), "/rename");
    addTextEditor(activityRow, $("td", activityRow).eq(1), "/editstart");
    addRowLinkListener(activityRow, "/delete", function() { activityRow.remove(); });
    if ($('a[href="/restart"]', activityRow).length == 0) {
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
