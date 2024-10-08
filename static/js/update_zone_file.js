$(document).ready(function () {
    console.log("update_zone_file.js file loaded")

    $('#update-zone-file-add-a-record-form').hide();
    $('#update-zone-file-update-a-record-form').hide();
    $('#update-zone-file-delete-a-record-form').hide();

    $('#update-zone-file-show-add-form').click(function () {
        $('#update-zone-file-add-a-record-form').show();
        $('#update-zone-file-update-a-record-form').hide();
        $('#update-zone-file-delete-a-record-form').hide();
    });

    $('#update-zone-file-show-update-form').click(function () {
        $('#update-zone-file-add-a-record-form').hide();
        $('#update-zone-file-update-a-record-form').show();
        $('#update-zone-file-delete-a-record-form').hide();
    });

    $('#update-zone-file-show-delete-form').click(function () {
        $('#update-zone-file-add-a-record-form').hide();
        $('#update-zone-file-update-a-record-form').hide();
        $('#update-zone-file-delete-a-record-form').show();
    });

    // Optional: If you want to reset the forms when they are hidden
    function resetForms() {
        $('#update-zone-file-add-a-record-form')[0].reset();
        $('#update-zone-file-update-a-record-form')[0].reset();
        $('#update-zone-file-delete-a-record-form')[0].reset();
    }

    function checkInputs() {
        // add a record inputs
        const addNameServerIP = $('#add-nameserver-ip').val()
        const addZoneName = $('#add-zone-name').val()
        const addDomainName = $('#add-domain-name').val()
        const addTTL = $('#add-ttl').val()
        const addIP = $('#add-ip').val()

        // update a record inputs
        const updateNameServerIP = $('#update-nameserver-ip').val()
        const updateZoneName = $('#update-zone-name').val()
        const updateDomainName = $('#update-domain-name').val()
        const updateTTL = $('#update-ttl').val()
        const updateIP = $('#update-new-ip').val()

        // delete a record inputs
        const deleteNameServerIP = $('#delete-nameserver-ip').val()
        const deleteZoneName = $('#delete-zone-name').val()
        const deleteDomainName = $('#delete-domain-name').val()

        if (addNameServerIP !== '' && addZoneName !== '' && addDomainName !== '' && addTTL !== '' && addIP !== '') {
            $('#add-a-record-btn').prop('disabled', false)
        } else {
            $('#add-a-record-btn').prop('disabled', true)
        }

        if (updateNameServerIP !== '' && updateZoneName !== '' && updateDomainName !== '' && updateTTL !== '' && updateIP !== '') {
            $('#update-a-record-btn').prop('disabled', false)
        } else {
            $('#update-a-record-btn').prop('disabled', true)
        }

        if (deleteNameServerIP !== '' && deleteZoneName !== '' && deleteDomainName !== '') {
            $('#delete-a-record-btn').prop('disabled', false)
        } else {
            $('#delete-a-record-btn').prop('disabled', true)
        }
    }

    $('#add-nameserver-ip, #add-zone-name, #add-domain-name, #add-ttl, #add-ip').on('input change', checkInputs);
    $('#update-nameserver-ip, #update-zone-name, #update-domain-name, #update-ttl, #update-new-ip').on('input change', checkInputs);
    $('#delete-nameserver-ip, #delete-zone-name, #delete-domain-name').on('input change', checkInputs);

    checkInputs()


    $('#next-generate-keys-btn').click(function () {
        window.location.href = generateKeysUrl;
    });
})