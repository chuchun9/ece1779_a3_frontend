const file_type_arr = ["rgb", "gif", "pbm", "pgm", "ppm", "tiff", "rast", "xbm", "jpeg", "jpg", "bmp", "png", "webp", "exr"];
function imagePreview(input) {
    if (input.files && input.files[0]) {
        const filerdr = new FileReader();
        console.log(input.files[0])
        const inputArr = input.files[0]['name'].split(".")
        const file_type = inputArr[inputArr.length - 1].toLowerCase()
        if (!file_type_arr.includes(file_type) || input.files[0]['name'].length === 0) {
            $("#Message").attr("hidden",false);
            $("#Message").text('"Input Error"');
            $("#Message").css({"color": "red"});
            $('#displayed_img').attr('hidden', true);
        }
        else {
            filerdr.onload = function(e) {
                $('#displayed_img').attr('src', e.target.result);
                $('#displayed_img').attr('hidden', false);
                $('#displayed_img').attr('imageName', input.files[0]['name']);
                $('#displayed_img').attr('imageType', input.files[0]['type']);
                $('#displayed_img').attr('filterNum', 0);
            };
            filerdr.readAsDataURL(input.files[0]);
            $("#Message").attr("hidden",true);
        }
    }
}

function sendFilterRequest(input) {
    const selected_filter = $('#selectedFilter').find(":selected").val();
    const myFile = $('#file').prop('files');
    if (myFile && myFile[0]) {
        console.log(selected_filter)
        const formData = new FormData();
        formData.append('file', myFile[0]);
        formData.append('filter', selected_filter);
        $.ajax({
            url: '/filter',
            data: formData,
            type: 'POST',
            success: function(response) {
                $("#Message").attr("hidden", true);
                $("#displayed_img").attr("filterNum", selected_filter);

                console.log($('#displayed_img').attr('imageName'));
                console.log($('#displayed_img').attr('filterNum'));
            },
            error: function(error) {
                console.log(error);
                $("#Message").attr("hidden",false);
                $("#Message").text(error['responseText']);
                $("#Message").css({"color": "red"});
            }
            ,
            cache: false,
            contentType: false,
            processData: false,
        });
    }
}

function uploadDisplayedImage(input) {
    const src = $("#displayed_img").attr("src")
    const hidden = $("#displayed_img").attr("hidden")
    if (!hidden) {
        const formData = new FormData();
        formData.append('dataurl', src)
        formData.append('imageName', $('#displayed_img').attr('imageName'))
        formData.append('imageType', $('#displayed_img').attr('imageType'))
        formData.append('filterNum', $('#displayed_img').attr('filterNum'))
        $.ajax({
            url: '/upload',
            data: formData,
            type: 'POST',
            success: function(response) {
                $("#Message").attr("hidden",false);
                $("#Message").text("Success");
                $("#Message").css({"color": "green"});
            },
            error: function(error) {
                console.log(error);
                $("#Message").attr("hidden",false);
                $("#Message").text(error['responseText']);
                $("#Message").css({"color": "red"});
            }
            ,
            cache: false,
            contentType: false,
            processData: false,
        });
    }
}
