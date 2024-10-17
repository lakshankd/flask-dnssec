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

    $('#sing-zone-info-content').hide();

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
            beforeSend: function () {
                $('#sign-zone-loader').show();
            },
            success: function (response) {
                $('#sign-zone-info')
                    .addClass('success-backup-message')
                    .html(`<i class="fa fa-check-circle"></i> ${response.message}`)
                    .show();

                $('#sing-zone-info-content')
                    .html(response.output)
                    .show()
            },
            error: function (xhr) {
                const errorResponse = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                $('#sign-zone-info')
                    .addClass('error-backup-message')
                    .html(`<i class="fa fa-exclamation-circle"></i> ${errorResponse}`)
                    .show();
                console.error(errorResponse);
            },
            complete: function () {
                $('#sign-zone-loader').hide();
            }
        });
    });

    $('#next-apply-changes-btn').click(function () {
        window.location.href = applyChangesUrl;
    });
})