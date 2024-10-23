$(document).ready(function(){
        $("#contact-form").submit(function(e){
                e.preventDefault();
                var data = new FormData(document.getElementById('contact-form'));
                $.ajax({
                        url: "/contact/",
                        type: "POST",
                        data: data,
                        cache: false,
                        contentType: false,
                        processData: false,
                        timeout: 1000 * 60,
                        tryCount: 0,
                        retryLimit: 5,
                        error: (xhr, textStatus, errorThrown) => {
                                this.tryCount++;
                                if(this.tryCount >= this.retryLimit) return;
                                $.ajax(this);
                        },
                        success: (data) => {
                                if(data == 'Message sent.') {
                                        $('#contact-submit').prop('disabled', true);
                                        $(this).trigger('reset');
                                }
                                document.getElementById('contact-message').innerHTML = data;
                                $('#contact-message').removeClass('hide');
                        },
                });
        });
});
function copyToClipboard(el) {
        navigator.clipboard.writeText(document.getElementById(el).innerHTML);
}
