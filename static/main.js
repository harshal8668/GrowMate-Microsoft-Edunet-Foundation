$(document).ready(function () {
    // Init
    $('.image-section').show();
    $('.loader').hide();
    $('#result').hide();
    $('#result2').hide();
    $('#result3').hide();
    $('#result-section h6').hide();

    // Upload Preview
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#imagePreview').css('background-image', 'url(' + e.target.result + ')');
                $('.img-preview').css('border', '5px solid #f8f8f8');
                $('#imagePreview').hide();
                $('#imagePreview').fadeIn(650);
            }
            reader.readAsDataURL(input.files[0]);
            
        }
    }
    $("#imageUpload").change(function () {
        $('.image-section').show();
        $('#btn-predict').show();
        $('#result').text('');
        $('#result').hide();
        $('#result2').text('');
        $('#result3').text('');
        $('#result2').hide();
        $('#result3').hide();
        $('#result-section h6').hide();
        readURL(this);
    });

    // Predict
    $('#btn-predict').click(function () {
        var form_data = new FormData($('#upload-file')[0]);
       
        // Show loading animation
        $(this).hide();
        $('.loader').show();
        

     
        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/predictDisease',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                // Get and display the result
                $('#result-section').css('border-left','5px solid yellow')
                $('.loader').hide();
                $('#result-section h6').show();
                $('#result').fadeIn(600);
                $('#result3').fadeIn(600);
                $('#result2').fadeIn(600);
                $('#result').text(data[0]);                
                $('#result3').text(data[2]);                
                $('#result2').text(data[1]);                
            },
            error: function(xhr){
                $('#result-section').css('border-left','5px solid yellow')
                $('.loader').hide();
                $('#result').fadeIn(600);
                $('#result').text('Error while fetching image....'); 
            },
      });
    });

});




function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
  }
  
  function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
  }