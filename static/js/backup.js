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

        $.ajax({
            url: checkZoneFileAvailabilityUrl,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({zone_path: zonePath, file_name: fileName}),
            success: function (response) {
                if (response.available) {
                    $('#confirm-backup-btn').prop('disabled', false);
                    $('#backup-availability-info').text('File is available. Ready for backup.');
                } else {
                    alert('File not available. Please check the path and try again.');
                }
            }
        });
    });

    $('#confirm-backup-btn').on('click', function () {
        const zonePath = $('#zone-path').val();
        const fileName = $('#file-name').val();

        $.ajax({
            url: confirmBackupZoneFileUrl,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({zone_path: zonePath, file_name: fileName}),
            success: function (response) {
                alert('Backup successful: ' + response.backup_path);
            }
        });
    });
});