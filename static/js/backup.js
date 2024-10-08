$(document).ready(function () {
    $('#check-availability-btn').prop('disabled', true);

    function checkInputs() {
        const zonePath = $('#zone-path').val();
        const fileName = $('#file-name').val();

        if (zonePath !== '' && fileName !== '') {
            $('#check-availability-btn').prop('disabled', false);
        } else {
            $('#check-availability-btn').prop('disabled', true);
        }
    }

    $('#zone-path, #file-name').on('input', function () {
        checkInputs();
    });

    $('#check-availability-btn').on('click', function () {
        const zonePath = $('#zone-path').val();
        const fileName = $('#file-name').val();

        $('#backup-availability-info').removeClass('success-backup-availability error-backup-availability').text('');

        $.ajax({
            url: checkZoneFileAvailabilityUrl,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({zone_path: zonePath, file_name: fileName}),
            success: function (response) {
                if (response.available) {
                    $('#backup-availability-info')
                        .addClass('success-backup-availability')
                        .html(`<i class="fa fa-check-circle"></i> ${response.message}`)
                        .show();
                    $('#confirm-backup-btn').prop('disabled', false);
                } else {
                    $('#backup-availability-info')
                        .addClass('error-backup-availability')
                        .html(`<i class="fa fa-times-circle"></i> Error: ${response.error || 'File not available.'}`)
                        .show();
                    $('#confirm-backup-btn').prop('disabled', true);
                }
            },
            error: function () {
                $('#backup-availability-info')
                    .addClass('error-backup-availability')
                    .html(`<i class="fa fa-times-circle"></i> An unexpected error occurred.`)
                    .show();
                $('#confirm-backup-btn').prop('disabled', true);
            }
        });
    });


    $('#confirm-backup-btn').click(function () {
        const zonePath = $('#zone-path').val();
        const fileName = $('#file-name').val();

        $.ajax({
            url: confirmBackupZoneFileUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({zone_path: zonePath, file_name: fileName}),
            success: function (response) {
                $('#backup-message')
                    .addClass('success-backup-message')
                    .html(
                        `<i class="fa fa-check-circle"></i> ${response.message}`
                    )
                    .show();
            },
            error: function (xhr) {
                const errorResponse = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                $('#backup-message')
                    .addClass('error-backup-message')
                    .html(
                        `<i class="fa fa-exclamation-circle"></i> ${errorResponse}`
                    )
                    .show();
            }
        });
    });

    $('#next-update-zone-file-btn').click(function () {
        window.location.href = updateZoneFileUrl;
    });
});