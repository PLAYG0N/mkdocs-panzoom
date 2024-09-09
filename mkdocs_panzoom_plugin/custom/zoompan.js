
function minimize(e,box,max,min){
  box.classList.remove("panzoom-fullscreen");
  max.classList.remove("panzoom-hidden");
  min.classList.add("panzoom-hidden");
}

function escapeFullScreen(e,box,max,min) {
  console.log(e,box,);
  
  if (e.keyCode == 27){
    minimize(e,box,max,min);
  }
}

function add_buttons(box, instance) {
  let reset = box.querySelector(".panzoom-reset");
  let max = box.querySelector(".panzoom-max");
  let min = box.querySelector(".panzoom-min");
  let info = box.querySelector(".panzoom-info");
  let info_box = box.querySelector(".panzoom-info-box");

  reset.addEventListener("click", function (e) {
    instance.moveTo(0, 0);
    instance.zoomAbs(0, 0, 1);
  });
  if (info!=undefined){
    info.addEventListener("click", function (e) {
      // console.log(box);
      if (box.dataset.info == "true") {
        box.dataset.info = false;
        info_box.classList.add("panzoom-hidden");
      } else {
        box.dataset.info = true;
        info_box.classList.remove("panzoom-hidden");
      }
    });
  }
  if (max != undefined) {
    max.addEventListener("click", function (e) {
      //instance.setTransformOrigin({ x: 0.25, y: 0.25 });
      // box.addEventListener("keydown", escapeFullScreen(e,box,max,min))
      box.classList.add("panzoom-fullscreen");
      min.classList.remove("panzoom-hidden");
      max.classList.add("panzoom-hidden");
      box.focus();
    });
  }
  if (min != undefined) {
    min.addEventListener("click", function (e) {
      box.classList.remove("panzoom-fullscreen");
      max.classList.remove("panzoom-hidden");
      min.classList.add("panzoom-hidden");
    });
  }
  box.addEventListener("keydown",function(e){
    escapeFullScreen(e,box,max,min);
  });
}

function activate_zoom_pan() {
  boxes = document.querySelectorAll(".panzoom-box");
  // console.log(boxes);
  boxes.forEach((box) => {
    elem = box.querySelector(".mermaid");

    // check if it is an image
    if (elem == undefined) {
      elem = box.querySelector("img");
    }

    if (elem == undefined) {
      return;
    }

    //console.log(elem.nodeName);
    if (
      (elem.nodeName == "DIV" || elem.nodeName == "IMG") &&
      !elem.dataset.zoom
    ) {
      elem.dataset.zoom = true;
      let instance = panzoom(elem, {
        minZoom: 0.9,
        beforeWheel: function (e) {
          var shouldIgnore = !e.altKey;
          return shouldIgnore;
        },
        beforeMouseDown: function (e) {
          // console.log(e);
          var shouldIgnore = !e.altKey && !e.button == 1;
          return shouldIgnore;
        },
        zoomDoubleClickSpeed: 1,
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
