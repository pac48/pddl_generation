/* eslint-disable import/no-absolute-path */
import interact from '@interactjs/interactjs'

window.interact = interact

export class Draggable {
// target element
    element_id = "";
    html_element = "";
    body_selected = false
    title = ""
    x = 0;
    y = 0;

    constructor(id, title) {
        this.element_id = id
        this.title = title

        let clone = draggable_template.content.cloneNode(true);
        this.html_element = clone.children[0]
        if (title.length > 0) {
            this.setTitle(title)
        }

        this.html_element.setAttribute('id', this.element_id);
        document.getElementById("main-group").appendChild(this.html_element);


        let tmp = this
        let down_listener = function (event) {
            tmp.onDownListener(event)
        }
        window.event_manager.registerOnDownListener(down_listener, 0)
        let up_listener = function (event) {
            tmp.onUpListener(event)
        }
        let drag_move_listener = function (event) {
            tmp.dragMoveListener(event)
        }

        interact('#' + this.element_id)
            .draggable({
                // enable inertial throwing
                inertia: true,
                // keep the element within the area of it's parent
                modifiers: [
                    interact.modifiers.restrictRect({
                        restriction: 'parent',
                        endOnly: true
                    })
                ],
                // enable autoScroll
                autoScroll: true,

                listeners: {
                    // call this function on every dragmove event
                    move: drag_move_listener,
                    // // call this function on every dragend event
                    // end: this.dragMoveListener,
                }
            }).on('up', function (event) {
            up_listener(event)
        })
        //     .on('down', function (event) {
        //     down_listener(event)
        // })
    }

    delete() {
        document.getElementById("main-group").removeChild(this.html_element);
    }

    onDownListener(event) {
        if (this.checkBodyClick(event)) {
            window.active_drag = this
            this.html_element.style.outline = '2px dashed blue'
            this.body_selected = true
            document.getElementById(this.element_id).style.cursor = "pointer";
            event.consumed =  true
        }

    }

    onUpListener(event) {
        this.html_element.style.outline = ''
        this.body_selected = false
    }

    dragMoveListener(event) {
        // if (this.body_selected) {
        var target = event.target
        // keep the dragged position in the data-x/data-y attributes
        var x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx
        var y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy

        // translate the element
        target.style.transform = 'translate(' + x + 'px, ' + y + 'px)'

        // update the posiion attributes
        target.setAttribute('data-x', x)
        target.setAttribute('data-y', y)

        console.log("move")
        // }

    }

    checkBodyClick(event) {
        console.log(event)
        let id = this.element_id
        return event.path.find(function (element) {
                return (typeof element.getAttribute === "function") && element.getAttribute('id') === id
            }
        )
    }

    setTitle(title) {
        this.html_element.children[0].children[0].children[0].children[0].innerText = title
    }

    getTitle() {
        return this.html_element.children[0].children[0].children[0].children[0].innerText
    }
}

// Static variable shared by all instances
window.draggable_instances = [];