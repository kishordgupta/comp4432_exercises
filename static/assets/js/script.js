$(document).ready(function() {
    $('#login').click(function(e) {
        $("#auth_stat").html('');
        var uname = document.getElementById("username").value;
        var passw = document.getElementById("password").value;
        var data = {'username':uname, 'password':passw};


        $.ajax('/api/login',{
            method: 'POST',
            data: JSON.stringify(data),
            dataType: "json",
            contentType: "application/json; charset=utf-8",
        }).done(function(res){
          if (res['status'] == 'success'){
            window.location.replace("/profile");
          }
          else{
            $("#auth_stat").html('<b style="color: red;">Login Failed</b>');
          }
    
        }).fail(function(err){
            $("#auth_stat").html('<b style="color: red;">Login Failed</b>');
        });
        e.preventDefault();
    });

    $('#search').click(function(e){
        $("#stat").html('');
        var item = $("#term").val();
        $.ajax('/api/search/'+item, {
            method: 'GET',
        }).done(function(res){
            $(".res").remove();
            $(res).each(function(){
                var r = "<tr class='res'><td>"+this['name']+"</td></tr>";
            $("#results").append(r);
            });
        }).fail(function(err){
            $("#stat").html('<b style="color: red;">No items found in search</b>');
        });
    });
});