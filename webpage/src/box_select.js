/* eslint-disable import/no-absolute-path */

export class BoxSelect {

    constructor(x_start, y_start) {
        this.x_start = x_start
        this.y_start = y_start
        this.x_end = x_start
        this.y_end = y_start
        console.log("make box " + x_start + "  " + y_start)

        let clone = box_select_template.content.cloneNode(true);
        this.html_element = clone.children[0]
        document.getElementById("main-group").appendChild(this.html_element);
    }

    set_end(x_end, y_end) {
        this.x_end = x_end
        this.y_end = y_end
        console.log("box end " + x_end + " " + y_end)

        this.html_element.style.height = Math.abs(this.y_end - this.y_start) + 'px'
        this.html_element.style.width = Math.abs(this.x_end - this.x_start) + 'px'

        this.html_element.style.transform = 'translate(' + Math.min(this.x_start, this.x_end) + 'px, ' + Math.min(this.y_start, this.y_end) + 'px)'
    }

    delete() {
        document.getElementById("main-group").removeChild(this.html_element);

    }
}

window.event_manager.registerOnDownListener(function (event) {
    event.consumed = true
    window.box_select = new BoxSelect(event.clientX, event.clientY)
}, 1)

window.event_manager.registerOnUpListener(function (event) {
    if (window.box_select != null) {
        event.consumed = true
        window.box_select.delete()
        window.box_select = null
    }
}, 0)

window.event_manager.registerOnMoveListener(function (event) {
    if (window.box_select != null) {
        event.consumed = true
        window.box_select.set_end(event.clientX, event.clientY)
    }
}, 0)


