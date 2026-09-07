from django.urls import path

from . import views

urlpatterns = [
    path("", views.root, name="root"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("kunjungan/", views.kunjungan_list, name="kunjungan_list"),
    path("kunjungan/baru/", views.kunjungan_baru, name="kunjungan_baru"),
    path("kunjungan/cek-instansi/", views.cek_instansi, name="cek_instansi"),
    path("kunjungan/<int:pk>/", views.kunjungan_detail, name="kunjungan_detail"),
    path("kunjungan/<int:pk>/edit/", views.kunjungan_edit, name="kunjungan_edit"),
    path("blast-wa/", views.blast_wa, name="blast_wa"),
    path("blast-wa/<int:pk>/<str:jenis>/", views.klik_wa, name="klik_wa"),
    path("export/excel/", views.export_excel, name="export_excel"),
]
