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
    
    $('#next-view-statistics-btn').click(function () {
        window.location.href = viewStatisticsUrl;
    });
})