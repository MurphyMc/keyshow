Keyshow_SendInfo = function ()
{
  try
  {
    sock.send({"show": Keyshow_ShowName, "slide_info":
               {"current_slide":gShowController.currentSlideIndex,
                "current_build":gShowController.currentSceneIndex
               }
              });
  }
  catch
  {
  }
};

var sock = new Resocket("keyshow/agent/ws");
sock.onmessage = function (msg)
{
  console.log("From POX:", msg)
  /**/ if (msg.cmd == "prev_build") gShowController.goBackToPreviousBuild("onKeyPress");
  else if (msg.cmd == "next_build") gShowController.advanceToNextBuild("onKeyPress");
  else if (msg.cmd == "prev_slide") gShowController.goBackToPreviousSlide("onKeyPress");
  else if (msg.cmd == "next_slide") gShowController.advanceToNextSlide("onKeyPress");
  else console.log("Unknown cmd:", cmd);
};

sock.onopen = function ()
{
  Keyshow_SendInfo();
};

document.observe(kSlideIndexDidChangeEvent, function () {
  Keyshow_SendInfo();
});

console.log("Keyshow agent loaded");
document.title = Keyshow_ShowName + " - Keyshow";
