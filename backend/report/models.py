import datetime as dt

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from .crypto_fields import EncryptedCharField, EncryptedTextField


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERUSER = "SUPERUSER", "Superuser"
        ADMIN = "ADMIN", "Admin / SPV"
        SALES = "SALES", "Sales"
        TEKNISI = "TEKNISI", "Teknisi"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SALES)
    no_hp = models.CharField("No. HP", max_length=20, blank=True)

    @property
    def is_spv(self):
        return self.is_superuser or self.role in (self.Role.SUPERUSER, self.Role.ADMIN)

    @property
    def is_sales(self):
        return self.role == self.Role.SALES

    @property
    def nama(self):
        return self.get_full_name() or self.username


class Instansi(models.Model):
    nama = models.CharField(max_length=150)
    alamat = EncryptedTextField(blank=True)
    pic = EncryptedCharField("PIC", max_length=100, blank=True)
    no_wa = EncryptedCharField("No. WhatsApp", max_length=20, blank=True)
    dibuat_oleh = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="instansi_dibuat"
    )
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Instansi"
        ordering = ["nama"]
        constraints = [
            models.UniqueConstraint(Lower("nama"), name="instansi_nama_unik_ci"),
        ]

    def save(self, *args, **kwargs):
        self.nama = self.nama.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama


class Kunjungan(models.Model):
    class Status(models.TextChoices):
        BARU = "BARU", "Baru"
        PEMBICARAAN = "PEMBICARAAN", "Pembicaraan"
        PENAWARAN = "PENAWARAN", "Penawaran"
        CLOSING = "CLOSING", "Closing"
        TIDAK_RESPON = "TIDAK_RESPON", "Tidak Respon"
        BATAL = "BATAL", "Batal"

    class Tahap(models.TextChoices):
        AWAL = "AWAL", "Kunjungan Awal"
        FOLLOW_UP = "FOLLOW_UP", "Follow Up"
        PROGRESS = "PROGRESS", "Progress"

    instansi = models.ForeignKey(Instansi, on_delete=models.CASCADE, related_name="kunjungan")
    sales = models.ForeignKey(User, on_delete=models.PROTECT, related_name="kunjungan")
    tanggal = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BARU)
    tahap = models.CharField(max_length=20, choices=Tahap.choices, default=Tahap.AWAL)
    catatan = EncryptedTextField(blank=True)
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diubah_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Kunjungan"
        ordering = ["-tanggal", "-id"]

    def __str__(self):
        return f"{self.instansi} - {self.tanggal:%d/%m/%Y}"

    def jenis_terkirim(self):
        return {f.jenis for f in self.followup.all()}

    def reminder_hari_ini(self):
        if self.status == self.Status.BATAL:
            return None
        selisih = (timezone.localdate() - self.tanggal).days
        jenis = {2: FollowUpWA.Jenis.H2, 5: FollowUpWA.Jenis.H5}.get(selisih)
        if jenis and jenis not in self.jenis_terkirim():
            return jenis
        return None

    @staticmethod
    def tanggal_reminder(today=None):
        today = today or timezone.localdate()
        return [today - dt.timedelta(days=2), today - dt.timedelta(days=5)]


class FollowUpWA(models.Model):
    class Jenis(models.TextChoices):
        H0 = "H0", "H0 - Terima kasih"
        H2 = "H2", "H2 - Follow up"
        H5 = "H5", "H5 - Penawaran"

    kunjungan = models.ForeignKey(Kunjungan, on_delete=models.CASCADE, related_name="followup")
    jenis = models.CharField(max_length=2, choices=Jenis.choices)
    oleh = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="followup_wa")
    waktu = models.DateTimeField(auto_now_add=True)
    pesan = models.TextField(blank=True)

    class Meta:
        verbose_name = "Follow Up WA"
        verbose_name_plural = "Follow Up WA"
        ordering = ["waktu"]

    def __str__(self):
        return f"{self.jenis} {self.kunjungan}"
