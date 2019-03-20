function ValidateForm() {
    // If files was added to comment-form and there is no text,
    // automatic phrase will be added

    var comTextField = document.getElementById('id_text').value;
    var comFileField0 = document.getElementById('id_commentfile_set-0-file').value;
    var comFileField1 = document.getElementById('id_commentfile_set-1-file').value;
    var comFileField2 = document.getElementById('id_commentfile_set-2-file').value;

    if (comTextField == '' && (comFileField0 || comFileField1 || comFileField2)) {
    document.getElementById('id_text').value = '[AUTOMAT: użytkownik dodał pliki i nie wprowadził żadnej treści]';
        return true;
    }
    return true;
}

function FileListItem(a) {
    // Necesary to proper-work of CatchFile function (especially image-resizing).
    // Code by Jimmy Wärting (https://github.com/jimmywarting)
    a = [].slice.call(Array.isArray(a) ? a : arguments)
    for (var c, b = c = a.length, d = !0; b-- && d;) d = a[b] instanceof File
    if (!d) throw new TypeError('expected argument to FileList is File or array of File objects')
    for (b = (new ClipboardEvent('')).clipboardData || new DataTransfer; c--;) b.items.add(a[c])
    return b.files
}

function CatchFile(obj) {
    // Based on ResizeImage function.
    // Original code by Jimmy Wärting (https://github.com/jimmywarting)

    var file = obj.files[0];
    // Check that file is image (regex)
    var imageReg = /[\/.](gif|jpg|jpeg|tiff|png|bmp)$/i;
    if (!file) return

    var uploadButtonsDiv = document.getElementById('upload_buttons_area');
    // Check, that it is first uploaded file, or not
    // If first, draw a div for showing status
    var uploadStatusDiv = document.getElementById('upload_status_area');

    if (!uploadStatusDiv && uploadButtonsDiv) {
        var uploadStatusDiv = document.createElement('div');
        uploadStatusDiv.setAttribute('class', 'upload-status-area');
        uploadStatusDiv.setAttribute('id', 'upload_status_area');
        uploadButtonsDiv.parentNode.insertBefore(uploadStatusDiv, uploadButtonsDiv.nextSibling);
        // Draw sub-div for each input field
        var i;
        for (i = 0; i < 3; i++) {
          var uploadStatus = document.createElement('div');
          uploadStatus.setAttribute('class', 'upload-status');
          uploadStatus.setAttribute('id', ('upload_status_id_commentfile_set-' + i + '-file'));
          uploadStatusDiv.append(uploadStatus);
        }
    }

    var canvasDiv = document.getElementById('canvas-area');
    // var currField = document.getElementById(obj.id);
    // var currFieldLabel = document.getElementById(('label_' + obj.id));

    // Main image-converting procedure
    if (imageReg.test(file.name)) {
        file.image().then(img => {
            const canvas = document.createElement('canvas')
            canvas.setAttribute('id', ('canvas_' + obj.id));
            const ctx = canvas.getContext('2d')
            const maxWidth = 1600
            const maxHeight = 1200

            document.getElementById(('upload_status_' + obj.id)).innerHTML =
            '<font color="#F44336">Konwertowanie pliku ' + file.name + ' w trakcie...</font>';
            console.log('Conversion in-progress');

            // Calculate new size
            const ratio = Math.min(maxWidth / img.width, maxHeight / img.height)
            const width = img.width * ratio + .5|0
            const height = img.height * ratio + .5|0

            // Resize the canvas to the new dimensions
            canvas.width = width
            canvas.height = height

            // Drawing canvas-object is necessary to proper-work
            // on mobile browsers.
            // In this case, canvas is inserted to hidden div (display: none)
            ctx.drawImage(img, 0, 0, width, height)
            canvasDiv.appendChild(canvas)

            // Get the binary (aka blob)
            canvas.toBlob(blob => {
                const resizedFile = new File([blob], file.name, file)
                const fileList = new FileListItem(resizedFile)

                // Temporary remove event listener since
                // assigning a new filelist to the input
                // will trigger a new change event...
                obj.onchange = null
                obj.files = fileList
                obj.onchange = CatchFile
            }, 'image/jpeg', 0.70)

            // If file is image, during conversion show status
            function ShowConvertConfirmation() {
                if (document.getElementById('canvas_' + obj.id)) {
                    document.getElementById(('upload_status_' + obj.id)).innerHTML =
                    '<font color="#4CAF50">Konwertowanie pliku ' + file.name + ' zakończone!</font>';
                    console.log('Conversion finished');
                    return true;
                }
                else {
                    return false;
                }
            }
            // Loop ShowConvertConfirmation function untill return true (file is converted)
            var convertConfirmationLoop = setInterval(function() {
                var isConfirmed = ShowConvertConfirmation();
                if (!isConfirmed) {
                    ShowConvertConfirmation();
                }
                else {
                    // Break loop
                    clearInterval(convertConfirmationLoop);
                }
            }, 1000); // Check every 1000ms
            })
        }
    // If file is not an image, show status with filename
    else {
        document.getElementById(('upload_status_' + obj.id)).innerHTML =
        '<font color="#4CAF50">Dodano plik ' + file.name + '</font>';
        //uploadStatusDiv.append(uploadStatus);
        console.log('Upload of file finished, not an image')
    }
}
