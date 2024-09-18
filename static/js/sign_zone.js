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

    $('#sign-zone-btn').click(function () {
        const origin = $('#sign-zone-origin').val();
        const keysDirectory = $('#sign-zone-keys-directory').val();
        const zoneFilePath = $('#sign-zone-file-path').val();

        $.ajax({
            url: signZoneFile,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                origin: origin,
                keys_directory: keysDirectory,
                zone_file_path: zoneFilePath
            }),
            success: function (response) {
                $('#sign-zone-info')
                    .addClass('success-backup-message')
                    .html(`<i class="fa fa-check-circle"></i> ${response.message + ". Output: " + response.output}`)
                    .show();
            },
            error: function (xhr) {
                const errorResponse = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                $('#sign-zone-info')
                    .addClass('error-backup-message')
                    .html(`<i class="fa fa-exclamation-circle"></i> ${errorResponse}`)
                    .show();
                console.error(errorResponse);
            }
        });
    });
})