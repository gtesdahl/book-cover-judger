var el = x => document.getElementById(x);

function showPicker() {
  el("file-input").click();
}

function showPicked(input) {
  el("upload-label").innerHTML = input.files[0].name;
  var reader = new FileReader();
  reader.onload = function(e) {
    el("image-picked").src = e.target.result;
    el("image-picked").className = "";
  };
  reader.readAsDataURL(input.files[0]);
}

function analyze() {
  var uploadFiles = el("file-input").files;
  if (uploadFiles.length !== 1) {
    alert("Please select a file to analyze!");
    return;
  }

  el("analyze-button").innerHTML = "Analyzing...";
  el("result-label").innerHTML = "";

  var xhr = new XMLHttpRequest();
  var loc = window.location;
  var port = loc.port ? `:${loc.port}` : "";
  xhr.open("POST", `${loc.protocol}//${loc.hostname}${port}/analyze`, true);
  xhr.timeout = 120000;

  xhr.onerror = function() {
    el("result-label").innerHTML = "Request failed. The server may be waking up — try again in a minute.";
    el("analyze-button").innerHTML = "Analyze";
  };

  xhr.ontimeout = function() {
    el("result-label").innerHTML = "Request timed out. First analysis after idle can take up to 2 minutes on the free tier.";
    el("analyze-button").innerHTML = "Analyze";
  };

  xhr.onload = function(e) {
    el("analyze-button").innerHTML = "Analyze";
    if (this.status !== 200) {
      var message = "Analysis failed. Please try again.";
      try {
        var err = JSON.parse(e.target.responseText);
        if (err.error) message = err.error;
      } catch (_) {}
      el("result-label").innerHTML = message;
      return;
    }
    try {
      var response = JSON.parse(e.target.responseText);
      el("result-label").innerHTML = `Prediction = ${response.result} Popularity (${response.confidence}% confident)`;
    } catch (_) {
      el("result-label").innerHTML = "Unexpected response from server.";
    }
  };

  var fileData = new FormData();
  fileData.append("file", uploadFiles[0]);
  xhr.send(fileData);
}
