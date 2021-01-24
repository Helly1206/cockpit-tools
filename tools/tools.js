/*********************************************************
 * SCRIPT : syncwatch.js                                 *
 *          Javascript for syncwatch Cockpit web-gui     *
 *                                                       *
 *          I. Helwegen 2020                             *
 *********************************************************/

////////////////////
// Common classes //
////////////////////

class tools {
    constructor(el) {
        this.el = el;
        this.name = "tools";
        this.pane = new gridPane(this, el, this.name);
    }

    displayContent(el) {
        this.getTools();

    }

    getTools() {
        var cb = function(data) {
            var tData = JSON.parse(data);
            this.pane.disposeSpinner();
            if (Object.keys(tData).length == 0) {
                this.pane.emptyMessage("The toolbox is empty ...");
            } else {
                this.pane.build(tData);
            }
        }
        this.pane.showSpinner();
        runCmd.call(this, cb);
    }
}

class gridPane {
    constructor(caller, el, id) {
        this.caller = caller;
        this.el = el;
        this.id = id;
        this.container = null;
        this.container = document.createElement("div");
        this.el.appendChild(this.container);
        this.loadingSpinner = new spinnerLoading();
    }

    dispose() {
        while (this.el.firstChild) {
            this.el.firstChild.remove();
        }
    }

    showSpinner(spinnerText = "") {
        if (this.container) {
            if (this.container.firstChild) {
                this.container.insertBefore(this.loadingSpinner.build(spinnerText), this.container.firstChild.nextSibling);
            } else {
                this.container.appendChild(this.loadingSpinner.build(spinnerText));
            }
        }
    }

    disposeSpinner() {
        this.loadingSpinner.dispose();
    }

    emptyMessage(message) {
        var dataField = document.createElement("h4");
        dataField.classList.add("panel-title");
        dataField.classList.add("grid-message");
        dataField.innerHTML = message;
        this.container.appendChild(dataField);
    }

    build(data) {
        var grid = document.createElement("div");
        grid.classList.add("grid-container");
        Object.keys(data).forEach(function(item) {
            var hLink = document.createElement("a");
            hLink.setAttribute("href", data[item].ref);
            hLink.setAttribute("target", "_blank");
            var img = document.createElement("img");
            img.setAttribute("src", data[item].icon);
            var hTxt = document.createElement("span");
            hTxt.innerHTML = item;
            hLink.appendChild(img);
            hLink.appendChild(hTxt);
            grid.appendChild(hLink);
        });
        this.container.appendChild(grid);
    }
}

/////////////////////
// Common functions //
//////////////////////

function runCmd(callback, args = [], json = null, cmd = "/opt/tools/tools-cli.py") {
    var cbDone = function(data) {
        callback.call(this, data);
    };
    var cbFail = function(message, data) {
        callback.call(this, "[]");
        new msgBox(this, "Syncwatch command failed", "Command error: " + (data ? data : message + "<br>Please check the log file"));
    };
    var command = [cmd];
    command = command.concat(args);
    if (json) {
        command = command.concat(JSON.stringify(json));
    }
    return cockpit.spawn(command, { err: "out", superuser: "require" })
        .done(cbDone.bind(this))
        .fail(cbFail.bind(this));
}

function buildOpts(data, refData = {}, exclude = []) {
    var opts = {};

    for (let key in data) {
        let addKey = true;
        if (exclude.includes(key)) {
            addKey = false;
        } else if (key in refData) {
            if (data2str(data[key]) == data2str(refData[key])) {
                addKey = false;
            }
        }
        if (addKey) {
            opts[key] = data[key];
        }
    }
    return opts;
}

function data2str(data) {
    var str = "";
    if (Array.isArray(data)) {
        str = data.map(s => s.trim()).join(",");
    } else {
        str = data.toString();
    }
    return str;
}

function cs2arr(data, force = true) {
    var arr = [];
    if ((force) || (data.includes(","))) {
        arr = data.split(",").map(s => s.trim());
    } else {
        arr = data;
    }

    return arr;
}

function generateUniqueName(list, source = "", destination = "") {
    var name = "sync";
    var pname = "";
    var i = 1;

    if (source) {
        name += "_" + decodeName(source);
    }

    if (destination) {
        name += "_" + decodeName(destination);
    }

    if (!name) {
        name = randomString();
    }

    pname = name;

    while (list.includes(name)) {
        name = pname + i.toString();
        i++;
    }

    return name;
}

function decodeName(value) {
    var name = "";

    if (value == "/") {
        name = "_root_";
    } else {
        name = value.substring(value.lastIndexOf('/') + 1);
    }

    return name;
}

function randomString(stringLength = 8) {
    var result           = '';
    var characters       = 'abcdefghijklmnopqrstuvwxyz';
    var charactersLength = characters.length;
    for ( var i = 0; i < stringLength; i++ ) {
       result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

///////////////////////////
// Tab display functions //
///////////////////////////

function displayContent(el) {
    var Tools = new tools(el);
    Tools.displayContent();
}

function displayFirstPane() {
    displayContent(document.querySelectorAll('[id="tools-grid"]')[0]);
}

displayFirstPane();

// Send a 'init' message.  This tells integration tests that we are ready to go
cockpit.transport.wait(function() { });
