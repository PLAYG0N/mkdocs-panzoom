function add_buttons(box, instance) {
  let max = box.querySelector(".panzoom-max");
  max.addEventListener("click", function (e) {
    instance.zoomTo(0, 0, 1);
    console.log("clicked");
  });
  console.log(max);
}

function activate_zoom_pan() {
  boxes = document.querySelectorAll(".panzoom-box");
  console.log(boxes);
  boxes.forEach((box) => {
    elem = box.querySelector(".mermaid");
    //console.log(elem.nodeName);
    if (elem.nodeName == "DIV" && !elem.dataset.zoom) {
      console.log("Added");
      elem.dataset.zoom = true;
      let instance = panzoom(elem, {
        minZoom: 1,
        beforeWheel: function (e) {
          var shouldIgnore = !e.altKey;
          return shouldIgnore;
        },
        beforeMouseDown: function (e) {
          var shouldIgnore = !e.altKey;
          return shouldIgnore;
        },
      });
      add_buttons(box, instance);
    }
    //console.log(elem);
  });
}

const interval = setInterval(activate_zoom_pan, 1000);

setTimeout(function () {
  clearInterval(interval);
  //console.log("Cleared");
}, 5000);
