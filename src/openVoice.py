import os
import torch
from openvoice import se_extractor
from openvoice.api import BaseSpeakerTTS, ToneColorConverter

class OpenVoice:

    def __init__(self):
        ckpt_base = '../checkpoints/base_speakers/EN'
        ckpt_converter = '../checkpoints/converter'
        device="cuda:0" if torch.cuda.is_available() else "cpu"
        base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)

        tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
        tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

        source_se = torch.load(f'{ckpt_base}/en_default_se.pth').to(device)
