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
    link = '/activity' + link;
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
    link = '/activity' + link;
    cell.editable(function(value, settings) {
            jsonPost(link, {"key":activityRow.attr("id"), "value":value}, function(response) {
                activityRow.replaceWith(makeActivity(response));
                });
            }, {"tooltip":"Click to edit..."});
}

function addActivityRowListeners(activityRow) {
    addTextEditor(activityRow, $("td", activityRow).eq(0), "/rename");
    addTextEditor(activityRow, $("td", activityRow).eq(1), "/tags");
    addTextEditor(activityRow, $("td", activityRow).eq(2), "/start");
    addRowLinkListener(activityRow, "/delete", function() { activityRow.remove(); });
    if ($('a[href="/activity/restart"]', activityRow).length == 0) {
        addRowLinkListener(activityRow, "/stop",
                function(response) { 
                    activityRow.remove();
                    addActivity(response, "inactive");
                });
    } else {
        addTextEditor(activityRow, $("td", activityRow).eq(3), "/duration");
        addRowLinkListener(activityRow, "/restart",
                function(response) { activityRow.remove(); addActivity(response, "active"); });
        addRowLinkListener(activityRow, "/again",
                function(response) { addActivity(response, "active"); });
    }
    for (ii = 0; ii < rowAddListeners.length; ii++) {
        rowAddListeners[ii](activityRow);
    }
}

var rowAddListeners = [];
