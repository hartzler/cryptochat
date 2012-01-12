var lastDate = "";
//var urlbase = 'http://localhost:8080';
//var urlbase = 'http://cryptochat.appspot.com';
var urlbase = '';

function say(s) {
  var user = $('#user-text').val();
  var room = $('#room-text').val();
  var pass = $('#pass-text').val();
  var text = s;
  var enc = AESEncryptCtr(text,pass,256);
  $.post(urlbase+'/chat/'+room,{text: enc, alias: user})
}

function go() {
  if( $('#pass-text').val() == '' ) {
    alert("You must set a passphrase!");
    $('#pass').focus();
  }
  else {
    var st = $('#say-text');
    say(st.val());
    st.val('');
  }
}

function update() {
  //alert("Something Else!");
  document.title = "foo";
  var room = $('#room-text').val();
  var user = $('#user-text').val();
  var pass = $('#pass-text').val();

  if( pass == '' ) {
    setTimeout(update,1000);  // try again later...
    return;
  }

  $.getJSON(urlbase+'/chat/'+room, {'alias': user, date: lastDate, noCache: Date() },
    function (json) {
      $.each(json.chats.reverse(), function(i,row) {
        try {
          var text = row.text;
          var alias = row.alias;
          var plain = AESDecryptCtr(text,pass,256);
          var c = $('#content');
          c.append('<br/>'+'<span class="alias">'+ alias + ':</span> ' + plain);
          var obj = document.getElementById('content');
          obj.scrollTop = obj.scrollHeight;
          lastDate = row.date;
        }
        catch(e) { alert(e.message); }
      });
      var mhtml = '';
      $.each(json.members, function(i,member) {
        try {
          mhtml += member.alias + '<br/>'
        }
        catch(e) { alert(e.message); }
      });
      $('#members-content').html(mhtml);
      setTimeout(update,1000);
    }
  );
}
  
$(document).ready(function() {
  update();
  if(NiftyCheck()) {
    Rounded("div#info","tl","#C7BDA1","#577270","smooth");
    Rounded("div#chat","bottom","#C7BDA1","#580E0C","smooth");
    Rounded("div#members","all","#580E0C","#C7BDA1","smooth");
    Rounded("div#history","all","#580E0C","#C7BDA1","smooth");
    Rounded("div#links","all","#C7BDA1","#ffffff","smooth");
  }
});

