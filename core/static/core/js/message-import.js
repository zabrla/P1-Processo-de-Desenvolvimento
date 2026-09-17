// Keep the native file field usable when JavaScript is unavailable.
const importForm = document.getElementById('decrypt-form');
const importButton = document.getElementById('import-button');
const fileInput = document.getElementById('arquivo');

if (importForm && importButton && fileInput) {
    document.getElementById('file-field').hidden = true;
    importButton.addEventListener('click', (event) => {
        event.preventDefault();
        fileInput.click();
    });
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            importForm.requestSubmit(importButton);
        }
    });
}
