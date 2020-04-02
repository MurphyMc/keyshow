JsOsaDAS1.001.00bplist00�Vscript_�function writeFile(text, file)
{
  return $.NSString.alloc.initWithUTF8String(text).writeToFileAtomicallyEncodingError(file, true, $.NSUTF8StringEncoding, null);
}


var app = Application.currentApplication();
app.includeStandardAdditions = true;

var keynote = Application("Keynote")
keynote.includeStandardAdditions = true;


var path = keynote.chooseFile();

var doc = keynote.open(path);

if (!path.toString().endsWith(".key")) throw "Not a keynote file?!";


var slides = doc.slides;
var notes = [];
for (var i = 0; i < slides.length; i++)
{
  var slide = slides[i];
  if (slide.skipped()) continue;
  var note = slide.presenterNotes().trim();
  notes.push(note);
}

notes = JSON.stringify(notes);
app.setTheClipboardTo(notes); //XXX

outpath = path.toString().slice(0, -4);

doc.export({"as":"HTML", "to":Path(outpath), "skippedSlides":false});

if (!writeFile(notes, outpath + "/keyshow_notes.json"))
{
  app.displayAlert("Could not save notes");
}                              � jscr  ��ޭ