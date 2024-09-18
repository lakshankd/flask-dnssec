$(document).ready(function () {
    console.log("apply_changes.js file loaded")

    $('#next-view-statistics-btn').click(function () {
        window.location.href = viewStatisticsUrl;
    });
})