function liveRemote() {
    let btns = document.querySelectorAll('#liveRemote');
    for (i of btns) {
        $(i).on('submit', function(e) {
            e.preventDefault();
            $(this).find(':submit').html('<i class="bi bi-cloud-snow-fill"></i>');
            $.ajax({
                url: $(this).attr('action') || window.location.pathname,
                type: "POST",
                button: $(this).find(':submit'),
                data: $(this).serialize(),
                success: function(data) {
		    this.button.html(data);
		},
                error: function(xhr, response, error) {
                    alert("Please connect to the internet to interact.");
                }
            });
        });
   }
}
liveRemote();