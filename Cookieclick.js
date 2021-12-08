const cookieSocket = new WebSocket('ws://' + window.location.host + '/cookieclick');
cookieSocket.onmessage = chatMessage;

function sendClick(){
    // alert("sending",JSON.stringify({'click': "hi"}))
    cookieSocket.send(JSON.stringify({'click': "hi"}));
}

function chatMessage(message) {
    const chatMessage = JSON.parse(message.data);
    let cookie = document.getElementById('cookie');
    if(chatMessage['clicks'] !== undefined){
       cookie.innerHTML = undefined;
       cookie.innerHTML = "Cookie Clicks:" + chatMessage['clicks'];
    }
    // else{
    // chat.innerHTML += "<b>" + chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>";
    // }
 }