console.log("load VideoPage js");

//minimum streaming return dimension, else error
const mediaConstraint = {
    video: {
        width: {
            min: 800,
            ideal: 800,
            max: 2560,
        },
        height: {
            min: 600,
            ideal: 600,
            max: 1440
        },
//        facingMode: {
//            exact: 'environment'
//        }
         facingMode: 'user'
        // facingMode: {
        //     exact: 'environment'
        // }
    }
}

let video = document.getElementById('video_element');
let canvas = document.getElementById("canvas");
// let radioAPI = document.formAPI.radioAPI;
// let radiowrapper = document.getElementById("radioform_wrapper");

let onloadtestbt = document.getElementById("onloadtestbutton");
let statustracker = document.getElementById("statustracker");

let videostarted = false;
let API_PREFIX = "/dev";

//check api usability
if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices){
    console.log("mediaDevices API usable");
    onloadtestbt.onclick = doEverything;
}else{
    console.log("mediaDevices API not usable")
    alert("browser is not supported, mediaDevices API not usable");
}

//choose forms
// radiowrapper.style.display="none";
// for (i=0; i<radioAPI.length; i++){
//     radioAPI[i].addEventListener('change', function () {
//         API_PREFIX= this.value;
//         console.log(API_PREFIX);
//     })
// }

function do_screenshot(){
    console.log("Video Started: "+ videostarted);
    if (!videostarted){
        console.log("no video");
        alert("no video");
        return ;
    }
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    //before draw, hide video
    video.style.display = "none";
    canvas.style.display = "initial"
    canvas.getContext('2d').drawImage(video, 0, 0);

    let image64 = canvas.toDataURL('image/screenshot');
    image64 = image64.replace('data:image/png;base64,', '');

//    make ajax
    $.ajax({
        type: 'POST',
        url: API_PREFIX+'/api/process_screenshot',
        data: {  Image64 : image64 },
    }).done(
        function (data){
            console.log("S3 upload: "+data.result);
            if (data.result === "success"){
                callAnalyze(data.s3path);
            }else{
                console.log("S3 upload failed");
                statustracker.innerHTML = "S3 Upload Failed"
            }
        }
    )
}

function handlestream(stream){
    video.srcObject = stream;
    videostarted = true;
}

async function doEverything(){
    if (videostarted){
        alert("video Already Started");
        return
    }
    statustracker.innerHTML = "Starting Video"
    const stream = await navigator.mediaDevices.getUserMedia(mediaConstraint);
    handlestream(stream);
    statustracker.innerHTML="Entering Countdown";

    let time = 5;
    let counter = setInterval(()=>{
        time--;
        if (time>=0){
            statustracker.innerHTML = time.toString();
        }else{
            clearInterval(counter);
            statustracker.innerHTML = "ScreenShot and Upload";
            do_screenshot();
            stream.getTracks().forEach(function (track){
                track.stop();
            })
            videostarted=false
            console.log("Video Is Now: "+videostarted);
        }
    }, 1000);
}

function callAnalyze(s3path){
    statustracker.innerHTML = "Analyzing With Model";
    $.ajax({
        type: 'POST',
        url: API_PREFIX+'/api/analyze_s3',
        data: {  S3_Image : s3path },
    }).done(
        function (data){
            if (data.succeed){
                console.log("Call Analyze Successful");
                console.log("Label: "+data.Label);
                console.log("Label: "+data.Confidence);
                HiddenFormPost(data, s3path);
            }else{
                console.log("Call analyze failed");
                statustracker.innerHTML = "Analyze Call Failed";

                // alert("using fake data")
                // fakedata = {
                // 'Label': 'rock'
                // }
                // HiddenFormPost(fakedata, s3path)
            }
        }
    )
}

function HiddenFormPost(data, s3path){
    let url = API_PREFIX+'/redirect_GamePage';
    let form = $('<form action="' + url + '" method="post">' +
        '<input type="hidden" name="Label" value="' + data.Label + '" />' +
        '<input type="hidden" name="s3path" value="' + s3path + '" />' +
        '</form>');
    $('body').append(form);
    form.submit();
}


