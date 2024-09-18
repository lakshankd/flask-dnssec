$(document).ready(function () {
    function checkInputs() {
        const origin = $('#sign-zone-origin').val();
        const keysDirectory = $('#sign-zone-keys-directory').val();
        const zoneFilePath = $('#sign-zone-file-path').val();

        if (origin !== '' && keysDirectory !== '' && zoneFilePath !== '') {
            $('#sign-zone-btn').prop('disabled', false);
        } else {
            $('#sign-zone-btn').prop('disabled', true);
        }

    }

    $('#sign-zone-origin, #sign-zone-keys-directory, #sign-zone-file-path').on('input change', checkInputs);

    checkInputs();
})