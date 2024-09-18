$(document).ready(function () {
    function updateKeySizes(algorithmSelector, keySizeSelector) {
        const selectedAlgorithm = $(algorithmSelector).find(':selected');
        const keySizesJson = selectedAlgorithm.attr('data-key-sizes');

        if (keySizesJson) {
            try {
                const keySizesArray = JSON.parse(keySizesJson).map(Number);
                $(keySizeSelector).empty();

                keySizesArray.forEach(function (size) {
                    $(keySizeSelector).append($('<option>', {
                        value: size,
                        text: size.toString()
                    }));
                });
            } catch (error) {
                console.error("Error parsing key sizes:", error);
            }
        } else {
            console.error("No key sizes found for the selected algorithm.");
        }
    }

    $('#zsk-algorithm').on('change', function () {
        updateKeySizes('#zsk-algorithm', '#zsk-key-size');
    });

    $('#ksk-algorithm').on('change', function () {
        updateKeySizes('#ksk-algorithm', '#ksk-key-size');
    });

    updateKeySizes('#zsk-algorithm', '#zsk-key-size');
    updateKeySizes('#ksk-algorithm', '#ksk-key-size');

    function checkInputs() {
        const zskAlgorithm = $('#zsk-algorithm').val();
        const zskKeySize = $('#zsk-key-size').val();
        const zskDomainName = $('#zsk-domain-name').val();
        const kskAlgorithm = $('#ksk-algorithm').val();
        const kskKeySize = $('#ksk-key-size').val();
        const kskDomainName = $('#ksk-domain-name').val();

        if (zskAlgorithm !== '' && zskKeySize !== '' && zskDomainName !== '') {
            $('#generate-zsk-btn').prop('disabled', false);
        } else {
            $('#generate-zsk-btn').prop('disabled', true);
        }

        if (kskAlgorithm !== '' && kskKeySize !== '' && kskDomainName !== '') {
            $('#generate-ksk-btn').prop('disabled', false);
        } else {
            $('#generate-ksk-btn').prop('disabled', true);
        }
    }

    $('#zsk-algorithm, #zsk-key-size, #zsk-domain-name').on('input change', checkInputs);
    $('#ksk-algorithm, #ksk-key-size, #ksk-domain-name').on('input change', checkInputs);

    checkInputs();

    $('#generate-zsk-btn').click(function () {
        const algorithm = $('#zsk-algorithm').val();
        const keySize = $('#zsk-key-size').val();
        const domainName = $('#zsk-domain-name').val();

        $.ajax({
            url: generateZskUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({algorithm: algorithm, key_size: keySize, domain_name: domainName}),
            success: function (response) {
                $('#zsk-key-info')
                    .addClass('success-backup-message')
                    .html(`<i class="fa fa-check-circle"></i> ${response.message + ". Output: " + response.output}`)
                    .show();
            },
            error: function (xhr) {
                const errorResponse = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                $('#zsk-key-info')
                    .addClass('error-backup-message')
                    .html(`<i class="fa fa-exclamation-circle"></i> ${errorResponse}`)
                    .show();
                console.error(errorResponse)
            }
        });
    });

    $('#generate-ksk-btn').click(function () {
        const algorithm = $('#ksk-algorithm').val();
        const keySize = $('#ksk-key-size').val();
        const domainName = $('#ksk-domain-name').val();

        $.ajax({
            url: generateKskUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({algorithm: algorithm, key_size: keySize, domain_name: domainName}),
            success: function (response) {
                console.log(response)
                $('#ksk-key-info')
                    .addClass('success-backup-message')
                    .html(`<i class="fa fa-check-circle"></i> ${response.message + ". Output: " + response.output}`)
                    .show();
            },
            error: function (xhr) {
                const errorResponse = xhr.responseJSON ? xhr.responseJSON.error : 'An error occurred';
                $('#ksk-key-info')
                    .addClass('error-backup-message')
                    .html(`<i class="fa fa-exclamation-circle"></i> ${errorResponse}`)
                    .show();
                console.error(errorResponse)
            }
        });
    });

    $('#next-sign-zone-btn').click(function () {
        window.location.href = signZoneUrl;
    });

})