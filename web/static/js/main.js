var worker;
function startWorker() {
  worker = new SharedWorker(WORKER_URL);
  worker.port.addEventListener("message", function (e) {
    var type = e.data["type"];
    if (type == "message") {
      toastr.info(e.data);
    }
    if (type == "connection") {
      if (e.data["status"] == "open") {
        if (!Notification) {
          alert('Desktop notifications not available in your browser. Try Chromium.'); 
          return;
        }
      
        if (Notification.permission !== "granted"){
          Notification.requestPermission();
        } else {
          console.log("???");
           // notifyMe();
        }
      
        $('#websocket-status').addClass('active');
      } else {
        $('#websocket-status').removeClass('active');
      }
    }
  }, false);

  var started = worker.port.start();

  worker.port.postMessage({
    cmd: "start",
    token: jQuery('meta[name="csrf-token"]').attr("content")
  });
}
function stopWorker() {
  if (worker != undefined) {
    worker.port.postMessage({ cmd: "stop" });
  }
}

function notifyMe() {
  if (Notification.permission !== "granted")
    Notification.requestPermission();
  else {
    var notification = new Notification('Notification title', {
      icon: 'http://cdn.sstatic.net/stackexchange/img/logos/so/so-icon.png',
      body: "???",
    });

    notification.onclick = function () {
      window.open("http://stackoverflow.com/a/13328397/1269037");      
    };

  }

}