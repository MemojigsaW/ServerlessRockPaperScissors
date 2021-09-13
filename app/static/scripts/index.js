console.log("Running index.js")
API_PREFIX = "/dev";
let status = document.getElementById("model_status");
let startbt = document.getElementById("start_bt");
let stopbt = document.getElementById("stop_bt");

if (status!==null){
    $.ajax({
        type: 'GET',
        url: API_PREFIX+'/api/get_model_status',
        error: function(xmlhttprequest, textstatus, message) {
            if(textstatus==="timeout") {
                console.log("get status call timedout");
            } else {
                console.log(textstatus);
            }}
    }).done(
        function (data){
            if (data.succeed){
                console.log("Call get status succeeded");
                status.innerText = 'Status: '+ data.status;
            }else{
                console.log("Call get status failed");
                status.innerText = "Call get status failed"
            }
        }
    )
    let interval_looper = setInterval(()=>{
        $.ajax({
            type: 'GET',
            url: API_PREFIX+'/api/get_model_status',
        }).done(
            function (data){
                if (data.succeed){
                    console.log("Call get status succeeded");
                    status.innerText = 'Status: '+ data.status;
                }else{
                    console.log("Call get status failed");
                    status.innerText = "Call get status failed"
                }
            }
        )
    }, 5*1000)
}

if (startbt !== null && stopbt !==null){
    startbt.onclick = startmodelapi;
    stopbt.onclick = stopmodelapi;

    function startmodelapi(){
        console.log("Make start model call")
        $.ajax({
            type: 'GET',
            url: API_PREFIX+'/api/Startmodel',
            error: function(xmlhttprequest, textstatus, message) {
                if(textstatus==="timeout") {
                    console.log("start call timedout");
                } else {
                    console.log(textstatus);
                }}
        }).done(
            function (data){
                console.log("Start call: "+ data.succeed);
            }
        )
    }
    function stopmodelapi(){
        console.log("Make stop model call")
        $.ajax({
            type: 'GET',
            url: API_PREFIX+'/api/Stopmodel',
            error: function(xmlhttprequest, textstatus, message) {
                if(textstatus==="timeout") {
                    console.log("stop call timedout");
                } else {
                    console.log(textstatus);
                }}
        }).done(
            function (data){
                console.log("Start call: "+ data.succeed);
            }
        )
    }
}
