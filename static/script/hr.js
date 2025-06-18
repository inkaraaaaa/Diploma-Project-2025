document.addEventListener('DOMContentLoaded', function () {
    const logoInput = document.getElementById('companyLogo');
    const fileUploadBtn = document.getElementById('fileUploadBtn');
    const fileUploadText = document.getElementById('fileUploadText');
    const fileUploadPreview = document.getElementById('fileUploadPreview');
    const logoPreview = document.getElementById('logoPreview');
    const removeLogoBtn = document.getElementById('removeLogoBtn');
  
    logoInput.addEventListener('change', function (e) {
      if (e.target.files.length > 0) {
        const file = e.target.files[0];
        const reader = new FileReader();
  
        reader.onload = function (event) {
          logoPreview.src = event.target.result;
          fileUploadPreview.style.display = 'block';
          fileUploadText.textContent = file.name;
        };
  
        reader.readAsDataURL(file);
      }
    });
  
    removeLogoBtn.addEventListener('click', function () {
      logoInput.value = '';
      logoPreview.src = '#';
      fileUploadPreview.style.display = 'none';
      fileUploadText.textContent = 'Choose file or drag it here';
    });
  
    fileUploadBtn.addEventListener('dragover', function (e) {
      e.preventDefault();
      this.classList.add('dragover');
    });
  
    fileUploadBtn.addEventListener('dragleave', function (e) {
      e.preventDefault();
      this.classList.remove('dragover');
    });
  
    fileUploadBtn.addEventListener('drop', function (e) {
      e.preventDefault();
      this.classList.remove('dragover');
  
      if (e.dataTransfer.files.length) {
        logoInput.files = e.dataTransfer.files;
        const event = new Event('change');
        logoInput.dispatchEvent(event);
      }
    });
  });
  