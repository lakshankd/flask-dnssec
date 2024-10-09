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

    $('#add-a-record-btn').click(function (event) {
        event.preventDefault();

        const nameServerIP = $('#add-nameserver-ip').val();
        const zoneName = $('#add-zone-name').val();
        const domainName = $('#add-domain-name').val();
        const ttl = $('#add-ttl').val();
        const ip = $('#add-ip').val();

        $.ajax({
            url: addRecordUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                nameserver_ip: nameServerIP,
                zone_name: zoneName,
                domain_name: domainName,
                ttl: ttl,
                ip: ip
            }),
            beforeSend: function () {
                $('#add-a-record-loader').show();
            },
            success: function (response) {
                $('#add-a-record-info')
                    .addClass('success-backup-message')
                    .html(`<i class="fa fa-check-circle"></i> ${response.message}`)
                    .show();
            },
            error: function (xhr) {
                const errorResponse = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                $('#add-a-record-info')
                    .addClass('error-backup-message')
                    .html(`<i class="fa fa-exclamation-circle"></i> ${errorResponse}`)
                    .show();
                console.error(errorResponse);
            },
            complete: function () {
                $('#add-a-record-loader').hide();
            }
        });
    });

    $('#update-a-record-btn').click(function (event) {
        event.preventDefault();

        const nameServerIP = $('#update-nameserver-ip').val();
        const zoneName = $('#update-zone-name').val();
        const domainName = $('#update-domain-name').val();
        const ttl = $('#update-ttl').val();
        const newIP = $('#update-new-ip').val();

        $.ajax({
            url: updateRecordUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                nameserver_ip: nameServerIP,
                zone_name: zoneName,
                domain_name: domainName,
                ttl: ttl,
                new_ip: newIP
            }),
            beforeSend: function () {
                $('#update-a-record-loader').show();
            },
            success: function (response) {
                $('#update-a-record-info')
                    .addClass('success-backup-message')
                    .html(`<i class="fa fa-check-circle"></i> ${response.message}`)
                    .show();
            },
            error: function (xhr) {
                const errorResponse = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                $('#update-a-record-info')
                    .addClass('error-backup-message')
                    .html(`<i class="fa fa-exclamation-circle"></i> ${errorResponse}`)
                    .show();
                console.error(errorResponse);
            }, complete: function () {
                $('#update-a-record-loader').hide();
            }
        });
    });

    $('#delete-a-record-btn').click(function (event) {
        event.preventDefault();

        const nameServerIP = $('#delete-nameserver-ip').val();
        const zoneName = $('#delete-zone-name').val();
        const domainName = $('#delete-domain-name').val();

        $.ajax({
            url: deleteRecordUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                nameserver_ip: nameServerIP,
                zone_name: zoneName,
                domain_name: domainName
            }),
            beforeSend: function () {
                $('#delete-a-record-loader').show();
            },
            success: function (response) {
                $('#delete-a-record-info')
                    .addClass('success-backup-message')
                    .html(`<i class="fa fa-check-circle"></i> ${response.message}`)
                    .show();
            },
            error: function (xhr) {
                const errorResponse = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                $('#delete-a-record-info')
                    .addClass('error-backup-message')
                    .html(`<i class="fa fa-exclamation-circle"></i> ${errorResponse}`)
                    .show();
                console.error(errorResponse);
            },
            complete: function () {
                $('#delete-a-record-loader').hide();
            }
        });
    });

    $('#next-generate-keys-btn').click(function () {
        window.location.href = generateKeysUrl;
    });
})