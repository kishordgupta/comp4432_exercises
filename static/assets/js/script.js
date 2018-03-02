$(document).ready(function() {
    $('#login').click(function(e) {
        $("#auth_stat").html('');
        set_status("#auth_stat", "");
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
            set_status("#auth_stat", '<b style="color: red;">Login Failed</b>');
          }
    
        }).fail(function(err){
            set_status("#auth_stat", '<b style="color: red;">Login Failed</b>');
        });
        e.preventDefault();
    });

    $('#search').click(function(e){
        set_status("#stat", "");
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
            set_status("#stat", '<b style="color: red;">No items found in search</b>');
        });
    });

    $('#addCourse').click(function(e) {
        set_status("#course_stat", "");
        var cnum = document.getElementById("courseNumber").value;
        var cname = document.getElementById("courseName").value;
        var cdesc = document.getElementById("courseDescription").value;
        var data = {'courseNumber':cnum, 'courseName':cname, 'courseDescription':cdesc};


        $.ajax('/api/addCourse',{
            method: 'POST',
            data: JSON.stringify(data),
            dataType: "json",
            contentType: "application/json; charset=utf-8",
        }).done(function(res){
          if (res['status'] == 'success'){
            set_status("#course_stat", '<b style="color: red;">'+res['message']+'</b>')
          }
          else{
            set_status("#course_stat", '<b style="color: red;">'+res['message']+'</b>')
          }
    
        }).fail(function(err){
            set_status("#course_stat", '<b style="color: red;">Failed to add course</b>');
        });
        e.preventDefault();
    });

    var set_status = (elem, msg) => {
        $(elem).html(msg)
    }
});