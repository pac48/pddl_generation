/* eslint-disable import/no-absolute-path */
import {Draggable} from './draggable'
import {EventManager} from './event_manager'
import {BoxSelect} from './box_select'

window.keypress = keypress


var listener = new window.keypress.Listener();
listener.simple_combo("control c", function () {
    let title_name = ""
    if (window.active_drag != null) {
        title_name = window.active_drag.getTitle()
    }
    let draggable = new Draggable('drag-' + window.draggable_instances.length, title_name)
    window.draggable_instances.push(draggable)
});

listener.simple_combo("delete", function () {
    // document.getElementById("main-group").removeChild(window.active_drag);
    window.active_drag.delete()
    delete window.active_drag
    window.active_drag = null
});

// let draggable = new Draggable('drag-0')
