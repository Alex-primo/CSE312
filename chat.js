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

function thumbsUpMessage(strofid){
   // console.log(JSON.stringify({"emoji":"thumbsUp","id":strofid}))
   chatSocket.send(JSON.stringify({"emoji":"thumbsUp","id":strofid}))
}
function thumbsDownMessage(strofid){
   // console.log(JSON.stringify({"emoji":"thumbsDown","id":strofid}))
   chatSocket.send(JSON.stringify({"emoji":"thumbsDown","id":strofid}))
}

// Called when the server sends a new message over the WebSocket and renders that message so the user can read it
function chatMessage(message) {
   console.log(message.data)
   if (message.data.includes("emoji")){
      receivedEmoji(message);
      return;
   }
   const chatMessage = JSON.parse(message.data);
   let chat = document.getElementById('chat');
   let emojis = "&nbsp&nbsp&nbsp<i onclick='thumbsUpMessage(\""+chatMessage["id"]+"\")' class='far fa-thumbs-up'></i>&nbsp&nbsp&nbsp<b id='"+chatMessage["id"]+"thumbsUp"+"'>0</b>&nbsp&nbsp&nbsp<i onclick='thumbsDownMessage(\""+chatMessage['id']+"\")' class='far fa-thumbs-down'></i>&nbsp&nbsp&nbsp<b id='"+chatMessage["id"]+"thumbsDown"+"'>0</b>";
   if(chatMessage['dm'] !== undefined){
      if(chatMessage['dm'] == 'To'){
      chat.innerHTML += "<div id='"+ chatMessage['id'] +"'><b class='DM'>" + "<b>" +chatMessage['dm']+' '+ chatMessage['username'] + "</b>: " + chatMessage["comment"] + "</b> <div>" + emojis+"</div> </div><br/>";
      }
      if(chatMessage['dm'] == 'From'){
      chat.innerHTML += "<div id='"+ chatMessage['id'] +"'><b class='DM'>" + "<b>" +chatMessage['dm']+' '+ chatMessage['username'] + "</b>: " + chatMessage["comment"] + "</b> <div>" + emojis+"</div> </div><br/>";
      }
   }
   else{
   chat.innerHTML += "<div id='"+ chatMessage['id'] +"'><b>" + chatMessage['username'] + "  </b>: " + chatMessage["comment"]+ "<div>" + emojis+"</div></div><br/>";
   }
}

function receivedEmoji(message){
   let dic = JSON.parse(message.data);
   let id = dic["id"]+dic["emoji"];
   // console.log(id);
   let val = document.getElementById(id).innerText;
   document.getElementById(id).innerText = String(Number(val)+1);
}
