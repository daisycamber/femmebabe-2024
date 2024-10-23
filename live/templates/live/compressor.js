var zip = new JSZip();
function en(text, callback){
        var thefile = zip.file("frame.b64", text);
        var reader = new FileReader();
        reader.onload=callback;
        thefile.generateAsync({ type: "blob" }).then(function (content) {
		reader.readAsDataURL(content);
	});
}

const b64toBlob = (text, contentType='', sliceSize=512) => {
  var b64Data = text.split(',')[1];
  var byteCharacters = null;
  var base64;
  try{
    byteCharacters = atob(b64Data); //b64Data);
  } catch(e) {
    console.log(e.stack);
    console.log(new Error().stack);
    console.log(text);
    console.log("Error");
//    byteCharacters = atob(b64Data);
  }
  const byteArrays = [];
  for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    const slice = byteCharacters.slice(offset, offset + sliceSize);
    const byteNumbers = new Array(slice.length);
    for (let i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    byteArrays.push(byteArray);
  }
  const blob = new Blob(byteArrays, {type: contentType});
  return blob;
}
function de(text, callback){
	console.log(text);
	console.log("Length is - " + text.length);
	if(!text.startsWith('data:application/zip;base64,')){
		text = 'data:application/zip;base64,' + text;
	}
//	const blob = new Blob([text.split(",")[1]], {type:"text/plain"});
//	var blob = new Blob([text], {type: "blob"});
	var blob = b64toBlob(text, "application/zip");
       	zip.loadAsync(blob, {type: "blob"}).then(function (zip) {
               	Object.keys(zip.files).forEach(function (filename) {
                       	zip.files[filename].async('string').then(function (fileData) {
                               	callback(fileData);
                       	})
               	})
        })
}
