import re
from urllib.parse import quote

TEMPLATES = {
    "H0": (
        "Halo Bapak/Ibu {pic}, terima kasih atas waktunya menerima kunjungan saya hari ini "
        "di {instansi}. Saya {sales} dari Srikaton. Jika ada kebutuhan atau pertanyaan, "
        "silakan hubungi saya kapan saja di nomor ini. Salam hangat."
    ),
    "H2": (
        "Selamat pagi Bapak/Ibu {pic}, saya {sales} dari Srikaton. Menindaklanjuti kunjungan "
        "saya ke {instansi} beberapa hari lalu, apakah ada hal yang bisa kami bantu lebih lanjut? "
        "Kami siap membantu kebutuhan {instansi}."
    ),
    "H5": (
        "Halo Bapak/Ibu {pic}, saya {sales} dari Srikaton. Kami ingin menawarkan solusi terbaik "
        "untuk {instansi} sesuai kebutuhan yang telah didiskusikan. Mohon informasinya kapan waktu "
        "yang tepat untuk kami sampaikan penawaran lengkapnya. Terima kasih."
    ),
}

TAHAP_SETELAH = {"H0": None, "H2": "FOLLOW_UP", "H5": "PROGRESS"}


def normalisasi_nomor(nomor: str) -> str:
    digits = re.sub(r"\D", "", nomor or "")
    if digits.startswith("0"):
        return "62" + digits[1:]
    if digits.startswith("8"):
        return "62" + digits
    return digits


def buat_pesan(jenis: str, kunjungan) -> str:
    return TEMPLATES[jenis].format(
        pic=kunjungan.instansi.pic or "",
        instansi=kunjungan.instansi.nama,
        sales=kunjungan.sales.nama,
    ).replace("Bapak/Ibu ,", "Bapak/Ibu,")


def link_wa(no_wa: str, pesan: str) -> str:
    return f"https://wa.me/{normalisasi_nomor(no_wa)}?text={quote(pesan)}"
