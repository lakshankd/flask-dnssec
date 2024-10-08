$(document).ready(function () {
    console.log("update_zone_file.js file loaded")

    $('#next-generate-keys-btn').click(function () {
        window.location.href = generateKeysUrl;
    });
})