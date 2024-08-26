function add_buttons(box, instance) {
  let reset = box.querySelector(".panzoom-reset");
  let max = box.querySelector(".panzoom-max");
  let min = box.querySelector(".panzoom-min");

  reset.addEventListener("click", function (e) {
    instance.moveTo(0, 0);
    instance.zoomAbs(0, 0, 1);
  });

  max.addEventListener("click", function (e) {
    box.classList.add("panzoom-fullscreen");
    min.classList.remove("panzoom-hidden");
    max.classList.add("panzoom-hidden");
  });

  min.addEventListener("click", function (e) {
    box.classList.remove("panzoom-fullscreen");
    max.classList.remove("panzoom-hidden");
    min.classList.add("panzoom-hidden");
  });
}

function activate_zoom_pan() {
  boxes = document.querySelectorAll(".panzoom-box");
  console.log(boxes);
  boxes.forEach((box) => {
    elem = box.querySelector(".mermaid");
    //console.log(elem.nodeName);
    if (elem.nodeName == "DIV" && !elem.dataset.zoom) {
      elem.dataset.zoom = true;
      let instance = panzoom(elem, {
        minZoom: 0.9,
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
