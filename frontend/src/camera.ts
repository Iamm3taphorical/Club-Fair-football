export type CameraState = 'idle' | 'requesting' | 'ready' | 'blocked' | 'unavailable';

type CameraOptions = {
  width: number;
  height: number;
};

export function cameraUnavailableMessage() {
  if (!window.isSecureContext) {
    return 'Camera access requires localhost or HTTPS.';
  }
  if (!navigator.mediaDevices?.getUserMedia) {
    return 'This browser does not expose camera permissions here.';
  }
  return '';
}

export async function requestFrontCamera({ width, height }: CameraOptions) {
  const unavailable = cameraUnavailableMessage();
  if (unavailable) {
    throw new Error(unavailable);
  }

  return navigator.mediaDevices.getUserMedia({
    audio: false,
    video: {
      facingMode: { ideal: 'user' },
      width: { ideal: width },
      height: { ideal: height },
    },
  });
}

export function attachStreamToVideo(video: HTMLVideoElement | null, stream: MediaStream | null) {
  if (!video || !stream) return;
  if (video.srcObject !== stream) {
    video.srcObject = stream;
  }
  void video.play().catch(() => {
    // Some browsers wait for autoplay even on muted video; the retry button can attach again.
  });
}

export function stopStream(stream: MediaStream | null) {
  stream?.getTracks().forEach((track) => track.stop());
}

export function cameraStateFromError(error: unknown): CameraState {
  const name = error instanceof Error ? error.name : '';
  if (name === 'NotAllowedError' || name === 'SecurityError') return 'blocked';
  return 'unavailable';
}

export function cameraErrorMessage(error: unknown) {
  const name = error instanceof Error ? error.name : '';
  if (name === 'NotAllowedError' || name === 'SecurityError') {
    return 'Camera permission was blocked. Allow camera access in the browser, then retry.';
  }
  if (name === 'NotFoundError' || name === 'DevicesNotFoundError') {
    return 'No front camera was found on this device.';
  }
  if (name === 'NotReadableError' || name === 'TrackStartError') {
    return 'The camera is already in use by another app or tab.';
  }
  if (name === 'OverconstrainedError' || name === 'ConstraintNotSatisfiedError') {
    return 'The requested front camera settings are not available.';
  }
  if (error instanceof Error && error.message) return error.message;
  return 'Camera could not start. Check browser permissions and retry.';
}
