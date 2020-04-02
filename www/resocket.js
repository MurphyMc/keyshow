class Resocket
{
  constructor (sockname)
  {
    this.socket = null;
    this.onmessage = null;
    this.onopen = null;
    this.sockname = sockname;
    setInterval(this.connect.bind(this), 2500);
    setTimeout(this.connect.bind(this), 500);
  }
  connect ()
  {
    if (this.socket)
    {
      switch (this.socket.readyState)
      {
        case 0:
        case 1:
          return;
      }
    }
    if (this.socket)
    {
      this.socket.onclose = this.socket.onmessage = null;
      this.socket.close();
    }

    this.socket = new WebSocket("ws://" + location.host + "/" + this.sockname);
    this.socket.onclose = function () {
      console.log("Reconnect momentarily...");
      try
      {
        this.socket.close();
      }
      catch
      {
      }
      this.socket = null;
    }
    this.socket.onerror = this.socket.onclose;

    var parent = this;
    this.socket.onmessage = function (event) {
      var data = JSON.parse(event.data);
      //console.log(data);
      if (parent.onmessage) parent.onmessage(data);
    };
    this.socket.onopen = function (event) {
      this.connecting = false;
      this.reconnecting = false;
      console.log("Connected");
      if (parent.onopen) parent.onopen(event)
    };
  }
  send (o)
  {
    var o = JSON.stringify(o);
    try
    {
      this.socket.send(o);
      console.log(o);
    }
    catch
    {
      this.socket.onerror();
    }
  }
}
