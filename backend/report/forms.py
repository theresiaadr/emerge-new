from captcha.fields import CaptchaField, CaptchaTextInput
from django import forms

from .models import Instansi, Kunjungan
from .wa_templates import normalisasi_nomor


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "input", "placeholder": "Masukkan username", "autofocus": True,
                   "autocomplete": "username", "data-testid": "login-username"}
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "input", "placeholder": "Masukkan password",
                   "autocomplete": "current-password", "data-testid": "login-password"}
        ),
    )
    captcha = CaptchaField(
        label="Kode Keamanan",
        widget=CaptchaTextInput(
            attrs={"class": "input", "placeholder": "Ketik kode", "autocomplete": "off"}
        ),
    )


class KunjunganForm(forms.ModelForm):
    nama_instansi = forms.CharField(
        label="Nama Instansi",
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "input", "list": "daftar-instansi", "autocomplete": "off",
                   "placeholder": "contoh: SMKN 1 Purworejo", "data-testid": "kunjungan-nama-instansi"}
        ),
    )
    pic = forms.CharField(
        label="PIC / Kontak", max_length=100, required=False,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Nama penanggung jawab",
                                      "data-testid": "kunjungan-pic"}),
    )
    no_wa = forms.CharField(
        label="No. WhatsApp", max_length=20, required=False,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "08xxxxxxxxxx",
                                      "inputmode": "tel", "data-testid": "kunjungan-no-wa"}),
    )
    alamat = forms.CharField(
        label="Alamat", required=False,
        widget=forms.Textarea(attrs={"class": "input", "rows": 2, "placeholder": "Alamat instansi",
                                     "data-testid": "kunjungan-alamat"}),
    )

    field_order = ["nama_instansi", "tanggal", "pic", "no_wa", "alamat", "catatan", "status"]

    class Meta:
        model = Kunjungan
        fields = ["tanggal", "status", "catatan"]
        widgets = {
            "tanggal": forms.DateInput(attrs={"type": "date", "class": "input",
                                              "data-testid": "kunjungan-tanggal"}, format="%Y-%m-%d"),
            "status": forms.Select(attrs={"class": "input", "data-testid": "kunjungan-status"}),
            "catatan": forms.Textarea(attrs={"class": "input", "rows": 4,
                                             "placeholder": "Hasil pembicaraan, kebutuhan, dll.",
                                             "data-testid": "kunjungan-catatan"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tanggal"].input_formats = ["%Y-%m-%d"]
        instansi = getattr(self.instance, "instansi", None) if self.instance.pk else None
        if instansi:
            self.initial.update(
                nama_instansi=instansi.nama, pic=instansi.pic,
                no_wa=instansi.no_wa, alamat=instansi.alamat,
            )

    def clean_nama_instansi(self):
        return " ".join(self.cleaned_data["nama_instansi"].split())

    def clean_no_wa(self):
        nomor = self.cleaned_data.get("no_wa", "")
        return normalisasi_nomor(nomor) if nomor else ""

    def simpan(self, sales):
        nama = self.cleaned_data["nama_instansi"]
        instansi = Instansi.objects.filter(nama__iexact=nama).first()
        if instansi is None:
            instansi = Instansi(nama=nama, dibuat_oleh=sales)
        for field in ("alamat", "pic", "no_wa"):
            nilai = self.cleaned_data.get(field, "")
            if nilai:
                setattr(instansi, field, nilai)
        instansi.save()
        kunjungan = self.instance
        kunjungan.instansi = instansi
        if kunjungan.pk is None:
            kunjungan.sales = sales
        kunjungan.save()
        return kunjungan
