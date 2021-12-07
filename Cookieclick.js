const cookieSocket = new WebSocket('ws://' + window.location.host + '/cookieclick');

function sendClick(){
    cookieSocket.send(JSON.stringify({'click': "hi"}));
}