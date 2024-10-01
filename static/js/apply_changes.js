$(document).ready(function () {

    function checkInputs() {
        const zoneFile = $('#zone-file').val();

        if (zoneFile !== '') {
            $('#apply-changes-btn').prop('disabled', false);
        } else {
            $('#apply-changes-btn').prop('disabled', true);
        }
    }

    $('#zone-file').on('input change', checkInputs);

    checkInputs();

    $('#apply-changes-btn').click(function () {
        const domainName = $('#domain-name').val();

        $.ajax({
            url: applyChangesRequestUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({domain_name: domainName}),

            beforeSend: function () {
                $('#apply-changes-loader').show();
            },

            success: function (response) {
                console.log("success function called")
                $('.apply-changes-info')
                    .addClass('success-backup-message')
                    .html(`<i class="fa fa-check-circle"></i> ${response.message}`)
                    .show();
                $('#apply-changes-command-output').text(response.rndc_output);
                $('#apply-changes-dsset-output-section').show();
            },
            error: function (xhr) {
                console.log("error function called")
                const errorResponse = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                $('.apply-changes-info')
                    .addClass('error-backup-message')
                    .html(`<i class="fa fa-exclamation-circle"></i> ${errorResponse}`)
                    .show();
                console.error(errorResponse);
            },

            complete: function () {
                $('#apply-changes-loader').hide();
            }
        });
    });

    $('#next-view-statistics-btn').click(function () {
        window.location.href = viewStatisticsUrl;
    });
})