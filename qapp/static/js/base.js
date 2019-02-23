function ValidateForm() {
      var comtextfield = document.getElementById('id_text').value;
      var comfilefielda = document.getElementById('id_commentfile_set-0-file').value;
      var comfilefieldb = document.getElementById('id_commentfile_set-1-file').value;
      var comfilefieldc = document.getElementById('id_commentfile_set-2-file').value;
      if (comtextfield == '' && (comfilefielda || comfilefieldb || comfilefieldc)) {
        document.getElementById('id_text').value = '[Automatyczny komentarz; użytkownik dodał pliki i nie wprowadził żadnej treści]';
        return true;
      }
      return true;
    }

    function FileListItem(a) {
      a = [].slice.call(Array.isArray(a) ? a : arguments)
      for (var c, b = c = a.length, d = !0; b-- && d;) d = a[b] instanceof File
      if (!d) throw new TypeError("expected argument to FileList is File or array of File objects")
      for (b = (new ClipboardEvent("")).clipboardData || new DataTransfer; c--;) b.items.add(a[c])
      return b.files
    }

    function ResizeImage(obj) {
      const file = obj.files[0]
        if (!file) return

        file.image().then(img => {
        const canvas = document.createElement('canvas')
            const ctx = canvas.getContext('2d')
        const maxWidth = 1600
        const maxHeight = 1200

        // calculate new size
        const ratio = Math.min(maxWidth / img.width, maxHeight / img.height)
        const width = img.width * ratio + .5|0
        const height = img.height * ratio + .5|0

        // resize the canvas to the new dimensions
        canvas.width = width
        canvas.height = height

        // scale & draw the image onto the canvas
        ctx.drawImage(img, 0, 0, width, height)

        // Get the binary (aka blob)
        canvas.toBlob(blob => {
          const resizedFile = new File([blob], file.name, file)
          const fileList = new FileListItem(resizedFile)

          // temporary remove event listener since
          // assigning a new filelist to the input
          // will trigger a new change event...
          obj.onchange = null
          obj.files = fileList
          obj.onchange = ResizeImage
        }, 'image/jpeg', 0.70)
      })
      alert('Plik załadowany');
    }