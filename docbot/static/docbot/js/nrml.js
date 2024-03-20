function checkMsgBox(){

  if($('#msg').val()=="")
    {
      $("#sendBtn").attr("disabled", true);
    }
    else
    {
      $("#sendBtn").attr("disabled", false);
    }
}

function sendMsg(){
var count=0;

if (count == 0) {

$('#msg').val("This is a first method")
}
else if (count >0 ){

alert($('#msg').val() + " message has been sent");

$('#msg').val("")


}

count++
}