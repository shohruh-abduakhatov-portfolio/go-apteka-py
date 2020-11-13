var connections = 0;     // count active connections  
var updateDelay = 1000; // = 1 sec delay
var ports = [];
var token;
var resultData = null;
var isopen = false;
var started = false;
function sendToAll(data){
   for(var i=0; i< ports.length; i++) {
      w = ports[i];
      w.postMessage(data);
   }
}
function start(){
   socket = new WebSocket("ws:///34.244.12.104:9001?token=asda");
   socket.binaryType = "arraybuffer";
   socket.onopen = function() {
      console.log("Connected!");
      sendToAll({ type: "connection", status: "open" });
      isopen = true;
   }
   socket.onmessage = function(e) {
      if (typeof e.data == "string") {
         console.log("Text message received: " + e.data);
         sendToAll({"type":"message", "data": e.data});
      } else {
         var arr = new Uint8Array(e.data);
         var hex = '';
         for (var i = 0; i < arr.length; i++) {
            hex += ('00' + arr[i].toString(16)).substr(-2);
         }
         console.log("Binary message received: " + hex);
      }
   }
   socket.onclose = function(e) {
      sendToAll({ type: "connection", status: "closed" });
      console.log("Connection closed.");
      socket = null;
      isopen = false;
      start();
   }
}
//
// The controller that manage the actions/commands/connections
//
self.addEventListener("connect", function (e) {
   var port = e.ports[0];
   connections++;

   port.addEventListener("message", function (e) {
      var data = e.data;
      switch (data.cmd) {
         case 'start':
         token = data.token;
         if (isopen) {
            sendToAll({ type: "connection", status: "open" });
            } else {
            sendToAll({ type: "connection", status: "closed" });
            }
         if (!started) {
               started = true;
               start();
         }
         break;
         case 'stop':
         self.close();
         break;
      }
   }, false);
   ports[ports.length] = port;
   port.start();
}, false);
self.addEventListener("error", function (e) {
   this.close();
   console.log(e);
});