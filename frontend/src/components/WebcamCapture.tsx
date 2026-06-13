import { useEffect, useRef, useState } from 'react';
import { apiWebSocketUrl } from '../api';

export default function WebcamCapture({ onGestureTriggered }: { onGestureTriggered?: (gesture: string, power: number, curve: number) => void }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [gesture, setGesture] = useState<string | null>(null);
  const [wsStatus, setWsStatus] = useState<string>('Disconnected');
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // 1. Setup WebSocket
    ws.current = new WebSocket(apiWebSocketUrl('/ws/video'));
    
    ws.current.onopen = () => setWsStatus('Connected');
    ws.current.onclose = () => setWsStatus('Disconnected');
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'GESTURE_DETECTED') {
        const displayGesture = data.gesture === "Charging" 
            ? `Charging Power... ${(data.power * 100).toFixed(0)}%`
            : `${data.gesture} (${(data.confidence * 100).toFixed(0)}%)`;
            
        setGesture(displayGesture);
        
        if (data.gesture !== "Charging" && onGestureTriggered) {
             onGestureTriggered(data.gesture, data.power, data.curve);
        }
        
        // Reset gesture display after 1 second if not charging
        if (data.gesture !== "Charging") {
            setTimeout(() => setGesture(null), 1000);
        }
      }
    };

    // 2. Setup Webcam
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        })
        .catch((err) => console.error("Error accessing webcam:", err));
    }

    const videoElement = videoRef.current;
    
    return () => {
      if (ws.current) ws.current.close();
      if (videoElement && videoElement.srcObject) {
        const stream = videoElement.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    // 3. Send frames to WebSocket interval
    const interval = setInterval(() => {
      if (ws.current?.readyState === WebSocket.OPEN && videoRef.current && canvasRef.current) {
        const canvas = canvasRef.current;
        const video = videoRef.current;
        
        // Ensure video is playing
        if (video.videoWidth === 0) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          
          // Convert to JPEG blob (lower quality for speed)
          canvas.toBlob((blob) => {
            if (blob) {
              ws.current?.send(blob);
            }
          }, 'image/jpeg', 0.5);
        }
      }
    }, 100); // 10 FPS to keep latency low

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ position: 'relative', width: '640px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
        <h2>Camera Feed</h2>
        <span style={{ color: wsStatus === 'Connected' ? 'green' : 'red' }}>
          Server: {wsStatus}
        </span>
      </div>
      
      <video 
        ref={videoRef} 
        autoPlay 
        playsInline 
        muted 
        style={{ width: '100%', borderRadius: '8px', transform: 'scaleX(-1)' }} 
      />
      
      {/* Hidden canvas used for extracting frames */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {gesture && (
        <div style={{
          position: 'absolute',
          bottom: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          color: '#39d7ff',
          padding: '10px 20px',
          borderRadius: '20px',
          fontSize: '24px',
          fontWeight: 'bold',
          zIndex: 10
        }}>
          Detected: {gesture}
        </div>
      )}
    </div>
  );
}
