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
    // Necesary to proper-work of ResizeImage function.
    // Code by Jimmy Wärting (https://github.com/jimmywarting)
    a = [].slice.call(Array.isArray(a) ? a : arguments)
    for (var c, b = c = a.length, d = !0; b-- && d;) d = a[b] instanceof File
    if (!d) throw new TypeError('expected argument to FileList is File or array of File objects')
    for (b = (new ClipboardEvent('')).clipboardData || new DataTransfer; c--;) b.items.add(a[c])
    return b.files
}

function ResizeImage(obj) {
    // Modified ResizeImage function.
    // Original code by Jimmy Wärting (https://github.com/jimmywarting)
    var divCanvas = document.getElementById('divcanvas');
    var currFieldId = document.getElementById(obj.id);
    var divStatus = document.createElement('div');
    divStatus.setAttribute('class', 'uploadstatus');
    const file = obj.files[0]
    if (!file) return

    file.image().then(img => {
        const canvas = document.createElement('canvas')
        canvas.setAttribute('id', ('canvas_' + obj.id));
        const ctx = canvas.getContext('2d')
        const maxWidth = 1600
        const maxHeight = 1200

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
        divcanvas.appendChild(canvas)

        // Get the binary (aka blob)
        canvas.toBlob(blob => {
            const resizedFile = new File([blob], file.name, file)
            const fileList = new FileListItem(resizedFile)

            // Temporary remove event listener since
            // assigning a new filelist to the input
            // will trigger a new change event...
            obj.onchange = null
            obj.files = fileList
            obj.onchange = ResizeImage
        }, 'image/jpeg', 0.70)
    }
    )
    function ShowConfirmation() {
        if (document.getElementById('canvas_' + obj.id)) {
            // console.log('Uploaded canvas_' + obj.id)
            divStatus.innerHTML = '<font color="#12b70c">Konwertowanie zakończone!</font>';
            currFieldId.parentNode.insertBefore(divStatus, currFieldId.nextSibling);
            return true;
        }
        else {
            divStatus.innerHTML = '<font color="red">W trakcie konwertowania...</font>';
            currFieldId.parentNode.insertBefore(divStatus, currFieldId.nextSibling);
        }
    }
    setInterval(function() {
        ShowConfirmation();
    }, 2000); // Counter in miliseconds
}