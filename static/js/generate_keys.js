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

    // Button disable functionality
    $('#generate-zsk-btn').prop('disabled', true);
    $('#generate-ksk-btn').prop('disabled', true);

})