// Establish a WebSocket connection with the server
const chatSocket = new WebSocket('ws://' + window.location.host + '/chatsocket');
const colorSocket = new WebSocket('ws://' + window.location.host + '/colorsocket');

// Call the chatMessage function whenever data is received from the server over the WebSocket
chatSocket.onmessage = chatMessage;
colorSocket.onmessage = changeColor;

// Read the name/comment the user is sending to chat and send it to the server over the WebSocket as a JSON string
// Called whenever the user clicks the Send button or pressed enter
function sendMessage() {
   const chatName = document.getElementById("chat-name").value;
   const chatBox = document.getElementById("chat-comment");
   const comment = chatBox.value;
   chatBox.value = "";
   chatBox.focus();
   if(comment !== "") {
       chatSocket.send(JSON.stringify({'username': chatName, 'comment': comment}));
   }
}

function sendColorChange() {

}

// Called when the server sends a new message over the WebSocket and renders that message so the user can read it
function chatMessage(message) {
   const chatMessage = JSON.parse(message.data);
   let chat = document.getElementById('chat');
   chat.innerHTML += "<b>" + chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>";
}

function changeColor(){

}
