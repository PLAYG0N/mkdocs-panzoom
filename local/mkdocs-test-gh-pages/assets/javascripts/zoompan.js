function activate_zoom_pan() {
  boxes = document.querySelectorAll(".mermaid");
  console.log(boxes);
  boxes.forEach((elem) => {
    //console.log(elem.nodeName);
    if (elem.nodeName == "DIV" && !elem.dataset.zoom) {
      console.log("Added");
      elem.dataset.zoom = true;
      panzoom(elem);
    }
    //console.log(elem);
  });
}

const interval = setInterval(activate_zoom_pan, 1000);

setTimeout(function () {
  clearInterval(interval);
  //console.log("Cleared");
}, 5000);
