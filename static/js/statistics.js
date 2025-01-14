$(document).ready(function () {
    console.log("statistics.js file loaded")

    function checkInputs() {
        const domain = $('#statistics-domain').val();
        const hostname = $('#statistics-hostname').val();
        const command = $('#statistics-command').val();

        if (domain !== '' && hostname !== '' && command !== '') {
            $('#get-statistics-btn').prop('disabled', false);
        } else {
            $('#get-statistics-btn').prop('disabled', true);
        }

    }

    $('#statistics-domain, #statistics-hostname, #statistics-command').on('input change', checkInputs);

    checkInputs();

    $('#statistics-info-content').hide();
    $('#statistics-info-content-dates').hide();

    $('#get-statistics-btn').click(function () {
        const hostname = $('#statistics-hostname').val();
        const domain = $('#statistics-domain').val();
        const command = $('#statistics-command').val();

        $.ajax({
            url: getStatisticsUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                hostname: hostname,
                domain: domain,
                command: command
            }),
            beforeSend: function () {
                $('#statistics-loader').show();
            },
            success: function (response) {
                $('#statistics-info')
                    .addClass('success-backup-message')
                    .html(`<i class="fa fa-check-circle"></i> ${response.message}`)
                    .show();

                $('#statistics-info-content')
                    .html(response.output)
                    .show()

                $('#statistics-info-content-dates')
                    .html(`
                         <div class="statistics-date-message">
                             <span class="statistics-date-highlight">RRSIG Expiration Date:</span> ${response.expiration_date}
                         </div>
                         <div class="statistics-date-message">
                              <span class="statistics-date-highlight">Days Until Expiration:</span> ${response.days_to_expire} days
                         </div>
                    `)
                    .show();
            },
            error: function (xhr) {
                const errorResponse = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                $('#statistics-info')
                    .addClass('error-backup-message')
                    .html(`<i class="fa fa-exclamation-circle"></i> ${errorResponse}`)
                    .show();
                console.error(errorResponse);
            },
            complete: function () {
                $('#statistics-loader').hide();
            }
        });
    });

    $('#prev-backup-zone-file-btn').click(function () {
        window.location.href = backupZoneFileUrl;
    });
})