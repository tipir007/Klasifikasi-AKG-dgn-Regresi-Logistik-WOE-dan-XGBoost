# Rencana Proyek UAS: Klasifikasi Defisit Kalori Rumah Tangga Berbasis Angka Kecukupan Gizi di Jawa Barat dengan Regresi Logistik-WOE dan XGBoost

WOE = Weight of evidence = ln (% bukan kejadian / % Kejadian)
syarat kalori >= 2150 kkal / kapita / hari (menurut Permenkes No 75 Thn 2013)
>= 2100 kkal menurut badan pangan nasional 2025

berdarsarkan % AKG itu ada kategori (Badan pangan nasional 2025)
1. Baik (100% AKG)
2. Sedang (80 - 99%)
3. kurang (70 - 79%) AKG
4. Defisit < 70 % AKG
Disusun: 2 Oktober 2026

no 1 dan 2 dikatakan cukup kalori
no 3 dan 4 dikatakan kurang / defisit kalori

## 1. Judul proyek

Klasifikasi Defisit Kalori Rumah Tangga Berbasis Angka Kecukupan Gizi di Jawa Barat dengan Regresi Logistik-WOE dan XGBoost

## 2. Latar belakang (mba put)

- Ambang konsumsi kalori 2.100 kkal per kapita per hari tidak cukup representatif karena tidak membedakan kebutuhan tiap rumah tangga menurut umur, jenis kelamin, dan komposisi anggota rumah tangga.
- Angka Kecukupan Gizi (AKG) dari Permenkes No. 28 Tahun 2019 memberi kebutuhan energi yang lebih tepat berdasarkan kelompok umur dan jenis kelamin.
- Di Jawa Barat, defisit kalori rumah tangga dapat dipengaruhi oleh karakteristik rumah tangga, kesejahteraan, pendidikan, pekerjaan, perumahan, dan pola pengeluaran, termasuk pengeluaran rokok.
(pendidikan KRT) (Faktor pekerjaan mencakup status bekerja kepala rumah tangga serta ada atau tidaknya anggota rumah tangga yang bekerja)


- Penelitian ini berfokus pada klasifikasi rumah tangga yang mengalami defisit kalori berbasis AKG dengan model yang dapat diinterpretasi dan model yang memiliki akurasi tinggi.

## 3. Rumusan masalah (mba put)

1. Berapa prevalensi rumah tangga yang mengalami defisit kalori berbasis AKG di Jawa Barat?
2. Seberapa baik model regresi logistik-WOE dibandingkan dengan XGBoost dalam mengklasifikasikan defisit kalori rumah tangga?
3. Variabel apa yang paling berpengaruh dalam memprediksi defisit kalori rumah tangga?
4. Apakah model interpretatif dan model berakurasi tinggi memberikan pola yang konsisten dalam hal variabel penting?

## 4. Tujuan penelitian (mba put)

- Mengidentifikasi rumah tangga defisit kalori berbasis kebutuhan AKG.
- Membangun model klasifikasi dengan pendekatan logistik-WOE dan XGBoost.
- Membandingkan performa model berdasarkan metrik evaluasi yang relevan.
- Menafsirkan variabel paling berpengaruh dalam menentukan klasifikasi defisit kalori.

## 5. Data yang digunakan

### 5.1 Sumber data
- KOR Maret 2024, Jawa Barat (link 1)
- KP Maret 2024, Jawa Barat (link 2)
- Data yang dipakai adalah data rumah tangga dan data individu yang dapat digabungkan melalui `URUT` dan `R401`

### 5.2 File utama
| File | Kegunaan |
|---|---|
| `DATA SUSENAS/link 2/32_ssn_202403_kp_blok43.dbf` | Ringkasan konsumsi dan pengeluaran rumah tangga |
| `DATA SUSENAS/link 2/32_ssn_202403_kp_blok41.dbf` | Data pengeluaran rumah tangga per komoditas, termasuk rokok |
| `DATA SUSENAS/link 1/b_34976_2025_05_14_11_05_39_ssn202403_kor_ind1.dbf` | Data individu: umur, jenis kelamin, pendidikan, pekerjaan, merokok |
| `DATA SUSENAS/link 1/b_34976_2025_05_14_11_07_40_ssn202403_kor_ind2.dbf` | Data individu lanjutan: usia balita, menyusui |
| `DATA SUSENAS/link 1/b_34976_2025_05_14_11_09_07_ssn202403_kor_rt.dbf` | Data rumah tangga: perumahan, aset, bantuan sosial, kredit |

### 5.3 Satuan amatan
- Satuan amatan model: rumah tangga
- Jumlah rumah tangga: 26.012

## 6. Variabel respon

Variabel respon utama adalah:

- `defisit_akg`

Definisi:

- Kebutuhan energi rumah tangga dihitung berdasarkan AKG per individu menurut umur dan jenis kelamin.
- Konsumsi energi rumah tangga dihitung dari `KALORI_KAP * R301`.
- Rasio = konsumsi energi rumah tangga / kebutuhan AKG rumah tangga.
- `defisit_akg = 1` jika rasio < 1, dan `0` jika rasio >= 1.

Variabel tambahan untuk eksplorasi:
- `sangat_defisit` dengan ambang < 0.7
- pembandingan dengan ambang 2.100 kkal per kapita

## 7. Variabel penjelas

### 7.1 Karakteristik rumah tangga
- `R301` = jumlah anggota rumah tangga
- jumlah balita, anak 5–17, lansia >= 60
- `R102`, `R105`
- `R1802`, `R1804`, `R1810A`, `R1817`, `R1815A`
- aset rumah tangga dari blok 20
- bantuan sosial dari blok 22

### 7.2 Karakteristik kepala rumah tangga
- jenis kelamin `R405`
- umur `R407`
- pendidikan `R614`
- status pekerjaan `R707`
- lapangan usaha `R706`

### 7.3 Kesejahteraan dan konsumsi
- `NONFOOD / R301` sebagai proksi kesejahteraan
- `KAPITA`
- `FOOD`, `NONFOOD`, `EXPEND`
- pengeluaran rokok sebagai prediktor tambahan dalam analisis lanjutan

### 7.4 Variabel yang tidak boleh digunakan dalam model utama
- `KALORI_KAP`, `PROTE_KAP`, `LEMAK_KAP`, `KARBO_KAP`
- variabel pengeluaran makanan yang secara langsung berhubungan dengan konsumsi kalori
- variabel yang merepresentasikan hasil yang sama dengan target

## 8. Proses pembersihan data

1. Menghilangkan kode yang bukan valid seperti `0`, `8`, `9`, `98` sesuai konteks tiap variabel.
2. Mengubah variabel multi-respons berbentuk huruf menjadi indikator 0/1 jika ada.
3. Menggabungkan data individu ke tingkat rumah tangga dengan `URUT` sebagai kunci utama.
4. Mengecek konsistensi internal data, seperti:
   - `R301` sesuai dengan banyaknya individu per rumah tangga
   - `FOOD + NONFOOD = EXPEND`
5. Membangun agregat rumah tangga seperti jumlah anggota, jumlah balita, jumlah lansia, serta jumlah perokok.
6. Menghitung pengeluaran rokok dari blok 41 dengan memanfaatkan kode komoditas rokok.
7. Menyiapkan dataset akhir rumah tangga untuk modeling.

## 9. Metodologi analisis

### 9.1 Validasi model
- Pembagian data 80% train dan 20% test dengan stratifikasi pada variabel target.
- Validasi silang 5-fold yang diulang 3 kali pada data train.
- Semua preprocessing dilakukan di dalam `recipe` agar tidak terjadi kebocoran data.

### 9.2 Model yang dibandingkan
| Model | Deskripsi |
|---|---|
| Regresi logistik baseline | Model dasar dengan dummy dan transformasi log jika diperlukan |
| Regresi logistik-WOE | Diskritisasi numerik dan WOE untuk peubah kategorik / hasil diskritisasi |
| XGBoost | Model non-linear dengan tuning hyperparameter |
| Random Forest (opsional) | Pembanding tambahan |

### 9.3 Parameter tuning
Untuk XGBoost dan Random Forest:
- `trees`
- `tree_depth`
- `learn_rate`
- `min_n`
- `mtry`
- `loss_reduction`

### 9.4 Metrik evaluasi
- ROC AUC
- Balanced accuracy
- Sensitivitas
- Spesifisitas
- F1 score
- Brier score (opsional)

## 10. Interpretasi model

- Regresi logistik-WOE: interpretasi koefisien dan WOE per bin.
- XGBoost: variable importance, partial dependence plot, dan SHAP jika memungkinkan.
- Perbandingan variabel penting antara model interpretatif dan model tree ensemble.

## 11. Jadwal kerja

| Tanggal | Kegiatan | Output |
|---|---|---|
| 2 Oktober 2026 | Pengumpulan data dan pembersihan data awal | Dataset rumah tangga siap analisis |
| 3 Oktober 2026 | EDA dan presentasi rencana proyek | Grafik dan ringkasan EDA |
| 4–8 Oktober 2026 | Preprocessing, recipe, validasi, tuning | Tabel metrik model |
| 9 Oktober 2026 | Evaluasi akhir, interpretasi | Hasil model dan variabel penting |
| 10 Oktober 2026 | Presentasi awal hasil | Slide presentasi awal |
| 11–16 Oktober 2026 | Penulisan makalah | Draft makalah |
| 17 Oktober 2026 | Presentasi draft makalah | Draft final |

## 12. Struktur makalah

1. Pendahuluan
2. Tinjauan pustaka
3. Metodologi
4. Hasil dan pembahasan
5. Kesimpulan dan saran
6. Lampiran

## 13. Produk yang diharapkan

- Dataset gabungan rumah tangga untuk model klasifikasi
- Hasil EDA yang mencakup prevalensi defisit AKG, distribusi karakteristik rumah tangga, dan pola hubungan dengan target
- Model klasifikasi terbaik dengan evaluasi performa
- Interpretasi variabel penting dan kontribusi utama terhadap klasifikasi defisit kalori 
- Draft makalah sesuai standar jurnal yang dipakai oleh mata kuliah

## 14. Risiko dan mitigasi

| Risiko | Mitigasi |
|---|---|
| Data tidak lengkap | Lakukan cleaning dan cek missing value sebelum model |
| Tabel AKG salah | Cocokkan dengan aturan Permenkes 28/2019 |
| Kebocoran variabel | Hindari penggunaan variabel yang langsung terkait konsumsi kalori |
| Kelas target tidak seimbang | Gunakan balanced accuracy dan tuning class imbalance jika perlu |
| WOE sensitif terhadap kategori jarang | Gunakan Laplace smoothing dan gabungkan kategori yang langka |

## 15. Catatan penting

- Judul ini sejalan dengan tugas UAS dan fokus utama pada pemodelan klasifikasi.
- Model akan diimplementasikan dengan R menggunakan paket `tidymodels`, `embed`, `xgboost`, dan `vip`.
- Data yang dipakai adalah data Susenas 2024 Maret untuk Jawa Barat, bukan data September atau data nasional.

## 16. Kesimpulan singkat

Proyek ini bertujuan untuk mengklasifikasikan rumah tangga yang mengalami defisit kalori berdasarkan kebutuhan AKG, lalu membandingkan model interpretatif (logistik-WOE) dengan model yang lebih kompleks (XGBoost). Selain performa, fokus utama juga ada pada interpretasi dan pemahaman praktis terhadap faktor-faktor yang menentukan defisit kalori rumah tangga di Jawa Barat.
