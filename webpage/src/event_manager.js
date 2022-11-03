/* eslint-disable import/no-absolute-path */

export class EventManager {

    constructor() {
        this.on_down_listener = []
        this.on_up_listener = []
        this.on_move_listener = []
    }

    loopEvent(event, callback_array) {
        event.consumed = false
        for (let i = 0; i < callback_array.length; i++) {
            let callback = callback_array[i][0]
            callback(event)
            if (event.consumed) {
                break;
            }
        }
    }

    registerOnDownListener(callback, priority) {
        this.on_down_listener.push([callback, priority])
        this.on_down_listener.sort((a, b) => a[1] - b[1])
    }

    registerOnUpListener(callback, priority) {
        this.on_up_listener.push([callback, priority])
        this.on_up_listener.sort((a, b) => a[1] - b[1])
    }

    registerOnMoveListener(callback, priority) {
        this.on_move_listener.push([callback, priority])
        this.on_move_listener.sort((a, b) => a[1] - b[1])
    }

    mouseDownCallback(event) {
        console.log('mouse down')
        this.loopEvent(event, this.on_down_listener)
    }

    mouseUpCallback(event) {
        console.log('mouse up')
        this.loopEvent(event, this.on_up_listener)

    }

    mouseMoveCallback(event) {
        // console.log('mouse up')
        this.loopEvent(event, this.on_move_listener)
    }
}

window.event_manager = new EventManager();

addEventListener('mousedown', (event) => {
    window.event_manager.mouseDownCallback(event)
});
addEventListener('mouseup', (event) => {
    window.event_manager.mouseUpCallback(event)
});
addEventListener('mousemove', (event) => {
    window.event_manager.mouseMoveCallback(event)
});
