import datetime as dt

from django.core.management.base import BaseCommand
from django.utils import timezone

from report.models import FollowUpWA, Instansi, Kunjungan, User


class Command(BaseCommand):
    help = "Isi data contoh untuk demo (idempotent)."

    def handle(self, *args, **options):
        utoro = User.objects.get(username="utoro")
        maryadi = User.objects.get(username="maryadi")
        today = timezone.localdate()
        contoh = [
            ("SMKN 1 Purworejo", "Pak Budi", "081234567890", "Jl. Tentara Pelajar 1", utoro, 12, "CLOSING"),
            ("SMAN 2 Kutoarjo", "Bu Sari", "0899000111", "Jl. Diponegoro 5", utoro, 2, "PEMBICARAAN"),
            ("Dinas Pendidikan Purworejo", "Pak Hadi", "0812999888", "Jl. Mayjen Sutoyo", maryadi, 5, "PENAWARAN"),
            ("Puskesmas Bayan", "Bu Rina", "085700112233", "Jl. Raya Bayan", maryadi, 0, "BARU"),
            ("MTs Negeri Loano", "Pak Anwar", "081355667788", "Loano, Purworejo", utoro, 40, "TIDAK_RESPON"),
        ]
        for nama, pic, wa, alamat, sales, hari, status in contoh:
            inst, _ = Instansi.objects.get_or_create(nama=nama, defaults={"pic": pic, "no_wa": wa, "alamat": alamat, "dibuat_oleh": sales})
            k, created = Kunjungan.objects.get_or_create(
                instansi=inst, sales=sales, tanggal=today - dt.timedelta(days=hari),
                defaults={"status": status, "catatan": f"Kunjungan ke {nama}, PIC {pic}."},
            )
            if created and hari >= 12:
                FollowUpWA.objects.create(kunjungan=k, jenis="H0", oleh=sales)
                FollowUpWA.objects.create(kunjungan=k, jenis="H2", oleh=sales)
                k.tahap = "FOLLOW_UP"
                k.save()
        self.stdout.write(self.style.SUCCESS("Data contoh siap."))
