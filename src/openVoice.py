import random
import torch
from openvoice import se_extractor
from openvoice.api import BaseSpeakerTTS, ToneColorConverter
from utils import *

class OpenVoice:

    def __init__(self):
        ckpt_base = SPEAKERS_DIR
        ckpt_converter = CONVERTERS_DIR
        device="cuda:0" if torch.cuda.is_available() else "cpu"
        self.base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)

        self.tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
        self.tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

        self.source_se = torch.load(f'{ckpt_base}/en_default_se.pth').to(device)
    
    def textToSpeech(self, text, voice, outputPath):
        voicePath = voice['path']

        files = [f for f in os.listdir(voicePath) if os.path.isfile(os.path.join(voicePath, f))]

        voicePath = os.path.join(voicePath, random.choice(files))

        target_se, audio_name = se_extractor.get_se(voicePath, self.tone_color_converter, target_dir='processed', vad=True)

        src_path = f'{TEMP_DIR}/{audio_name}.wav'

        self.base_speaker_tts.tts(text, src_path, speaker='default', language='English', speed=1.0)

        # Run the tone color converter
        encode_message = "@MyShell"
        self.tone_color_converter.convert(
            audio_src_path=src_path, 
            src_se=self.source_se, 
            tgt_se=target_se, 
            output_path=outputPath,
            message=encode_message)
        
