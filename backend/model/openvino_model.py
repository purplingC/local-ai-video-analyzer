from pathlib import Path
from typing import Dict
import numpy as np
import cv2
import imageio_ffmpeg as iio_ffmpeg
import subprocess


try:
    from openvino.runtime import Core
except Exception as e:
    raise ImportError("OpenVINO runtime not found. Install openvino-dev[onnx] or openvino. Error: " + str(e))


class OVModel:
    def __init__(self, model_path: str, device: str = "CPU"):
        model_path = str(model_path)
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.core = Core()
        self.model = self.core.read_model(model_path)
        self.input_map = {i.get_any_name(): i for i in self.model.inputs}
        self.output_map = {o.get_any_name(): o for o in self.model.outputs}
        self.compiled = self.core.compile_model(self.model, device)
        self.req = self.compiled.create_infer_request()

    def input_info(self) -> Dict[str, Dict]:
        return {k: {"shape": tuple(v.shape)} for k, v in self.input_map.items()}

    def output_info(self) -> Dict[str, Dict]:
        return {k: {"shape": tuple(v.shape)} for k, v in self.output_map.items()}

    def infer(self, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        return self.req.infer(inputs)


def detect_objects_in_video(model_path: str, video_path: str, device: str = "CPU"):
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    core = Core()
    model = core.read_model(model_path)
    compiled_model = core.compile_model(model, device)
    output_layer = compiled_model.outputs[0]

    cap = cv2.VideoCapture(str(video_path))
    counts = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_resized = cv2.resize(frame, (544, 320))
        input_data = frame_resized.transpose(2, 0, 1)[None, ...]  # NCHW
        result = compiled_model([input_data])[output_layer]
        for det in result[0][0]:
            conf = det[2]
            if conf > 0.5:
                label_id = int(det[1])
                counts[label_id] = counts.get(label_id, 0) + 1
    cap.release()
    return {"object_counts": counts}


def extract_audio_to_wav(video_path: str, out_wav_path: str = None, sample_rate: int = 16000):
    video_path = str(video_path)
    if out_wav_path is None:
        out_wav_path = str(Path(video_path).with_suffix(".wav"))

    ffmpeg_exe = iio_ffmpeg.get_ffmpeg_exe()

    cmd = [
        ffmpeg_exe, "-y", "-i", video_path,
        "-ac", "1",
        "-ar", str(sample_rate),
        "-vn", out_wav_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_wav_path

