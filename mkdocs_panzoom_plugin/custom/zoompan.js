function minimize(e, box, max, min) {
  box.classList.remove("panzoom-fullscreen");
  max.classList.remove("panzoom-hidden");
  min.classList.add("panzoom-hidden");
}

function escapeFullScreen(e, box, max, min) {
  // console.log(e,box,);

  if (e.keyCode == 27) {
    minimize(e, box, max, min);
  }
}

function showModal(boxid) {
  let box = document.getElementById(boxid);
  let modal = document.getElementById("panzoom-fullscreen-modal");
  let content = document.getElementById("panzoom-fullscreen-modal-content");
  children = box.children;

  for (let i = 0; i < children.length; i++) {
    console.log(children[i]);
    
    if (children[i].dataset.zoom == "true") {
      if (children[i].classList.contains("mermaid")) {
        let mermaid = children[i].cloneNode(true);
        const shadowRoot = children[i].shadowRoot;

        console.log("shadowRoot",shadowRoot, children[i]);
        
        // content.appendChild(mermaid);
        content.innerHTML = children[i].outerHTML;
        const newRoot = mermaid.attachShadow({ mode: "closed" });
        // newRoot.innerHTML = shadowRoot.innerHTML;

      } else {
        content.appendChild(children[i].cloneNode(true));
      }
      break;
    }
  }
  
  modal.style.display = "block";

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
  if (info != undefined) {
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
      showModal(box.id);
      // box.classList.add("panzoom-fullscreen");
      // min.classList.remove("panzoom-hidden");
      // max.classList.add("panzoom-hidden");
      // box.focus();
    });
  }
  if (min != undefined) {
    min.addEventListener("click", function (e) {
      box.classList.remove("panzoom-fullscreen");
      max.classList.remove("panzoom-hidden");
      min.classList.add("panzoom-hidden");
    });
  }
  box.addEventListener("keydown", function (e) {
    escapeFullScreen(e, box, max, min);
  });
}

function activate_zoom_pan() {
  boxes = document.querySelectorAll(".panzoom-box");

  meta_tag = document.querySelector('meta[name="panzoom-data"]').content;
  selectors = JSON.parse(meta_tag).selectors;

  // console.log(boxes);
  boxes.forEach((box) => {
    key = box.dataset.key;

    selectors.every((selector) => {
      elem = box.querySelector(selector);

      if (elem != undefined) {
        return false;
      }
      return true;
    });

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
        minZoom: 0.5,
        beforeWheel: function (e) {
          switch (key) {
            case "ctrl":
              return !e.ctrlKey;
            case "shift":
              return !e.shiftKey;
            case "alt":
              return !e.altKey;
            default:
              return false && !e.button == 1;
          }
        },
        beforeMouseDown: function (e) {
          // console.log(e);
          switch (key) {
            case "ctrl":
              return !e.ctrlKey && !e.button == 1;
            case "shift":
              return !e.shiftKey && !e.button == 1;
            case "alt":
              return !e.altKey && !e.button == 1;
            default:
              return false && !e.button == 1;
          }
        },
        zoomDoubleClickSpeed: 1,
      });
      add_buttons(box, instance);
    }
    //console.log(elem);
  });

  // configure modal
  let modalContent = document.getElementById("panzoom-fullscreen-modal-content");
  let modal_instance = panzoom(modalContent, {
    minZoom: 0.5,
        beforeWheel: function (e) {
          switch (key) {
            case "ctrl":
              return !e.ctrlKey;
            case "shift":
              return !e.shiftKey;
            case "alt":
              return !e.altKey;
            default:
              return false && !e.button == 1;
          }
        },
        beforeMouseDown: function (e) {
          switch (key) {
            case "ctrl":
              return !e.ctrlKey && !e.button == 1;
            case "shift":
              return !e.shiftKey && !e.button == 1;
            case "alt":
              return !e.altKey && !e.button == 1;
            default:
              return false && !e.button == 1;
          }
        },
        zoomDoubleClickSpeed: 1,
      });

}

const interval = setInterval(activate_zoom_pan, 1000);

setTimeout(function () {
  clearInterval(interval);
  //console.log("Cleared");
}, 5000);
