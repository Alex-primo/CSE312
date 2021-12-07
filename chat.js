// Establish a WebSocket connection with the server
const chatSocket = new WebSocket('ws://' + window.location.host + '/chatsocket');

// Call the chatMessage function whenever data is received from the server over the WebSocket
chatSocket.onmessage = chatMessage;


// Read the name/comment the user is sending to chat and send it to the server over the WebSocket as a JSON string
// Called whenever the user clicks the Send button or pressed enter
function sendMessage() {
   const chatName = document.getElementById("chat-dm").value;
   const chatBox = document.getElementById("chat-comment");
   const comment = chatBox.value;
   chatBox.value = "";
   chatBox.focus();
   if(comment !== "") {
      if(chatName !== "") {
         chatSocket.send(JSON.stringify({'recipient': chatName, 'comment': comment}));
      }
      else{
      chatSocket.send(JSON.stringify({'comment': comment}));
      }
   }
}


// Called when the server sends a new message over the WebSocket and renders that message so the user can read it
function chatMessage(message) {
   const chatMessage = JSON.parse(message.data);
   let chat = document.getElementById('chat');
   if(chatMessage['dm'] !== undefined){
      if(chatMessage['dm'] == 'To'){
      chat.innerHTML += "<b>" +chatMessage['dm']+' '+ chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>";
      }
      if(chatMessage['dm'] == 'From'){
      chat.innerHTML += "<b>" +chatMessage['dm']+' '+ chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>";
      }
   }
   else{
   chat.innerHTML += "<b>" + chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>";
   }
}

