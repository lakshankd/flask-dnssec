$(document).ready(function () {
    console.log("statistics.js file loaded")

    $('#prev-backup-zone-file-btn').click(function () {
        window.location.href = backupZoneFileUrl;
    });
})