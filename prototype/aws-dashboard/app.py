import asyncio, io, wave
import boto3, numpy as np, streamlit as st
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler

REGION = "us-east-1"
MODEL_ID = "amazon.nova-lite-v1:0"


# Speech -> text with Amazon Transcribe
class Handler(TranscriptResultStreamHandler):
    text = ""
    async def handle_transcript_event(self, event):
        for r in event.transcript.results:
            if not r.is_partial:
                self.text += r.alternatives[0].transcript + " "

async def transcribe_async(pcm):
    client = TranscribeStreamingClient(region=REGION)
    stream = await client.start_stream_transcription(
        language_code="en-US", media_sample_rate_hz=16000, media_encoding="pcm")
    async def send():
        for i in range(0, len(pcm), 8192):
            await stream.input_stream.send_audio_event(audio_chunk=pcm[i:i + 8192])
        await stream.input_stream.end_stream()
    handler = Handler(stream.output_stream)
    await asyncio.gather(send(), handler.handle_events())
    return handler.text.strip()

def speech_to_text(wav_bytes):
    with wave.open(io.BytesIO(wav_bytes)) as w:
        rate, ch = w.getframerate(), w.getnchannels()
        audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    audio = audio.reshape(-1, ch).mean(axis=1)                       # to mono
    audio = np.interp(np.arange(0, len(audio), rate / 16000), np.arange(len(audio)), audio)  # to 16 kHz
    return asyncio.run(transcribe_async(audio.astype(np.int16).tobytes()))


# Question -> answer with Amazon Bedrock
def ask_bedrock(question):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)
    resp = bedrock.converse(modelId=MODEL_ID,
                            messages=[{"role": "user", "content": [{"text": question}]}])
    return resp["output"]["message"]["content"][0]["text"]


# Dashboard
st.title("Ask a Question")

question = st.text_input("Type your question")
audio = st.audio_input("Or record your question")

if audio and st.button("Transcribe"):
    st.session_state.spoken = speech_to_text(audio.getvalue())
if st.session_state.get("spoken"):
    st.write("**You said:**", st.session_state.spoken)
    question = question or st.session_state.spoken

if st.button("Ask") and question:
    st.write("**Answer:**")
    st.write(ask_bedrock(question))
