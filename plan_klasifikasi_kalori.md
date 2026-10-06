# Rencana Proyek UAS: Klasifikasi Defisit Kalori Rumah Tangga Berbasis Angka Kecukupan Gizi di Jawa Barat dengan Regresi Logistik-WOE dan XGBoost

Disusun: 2 Oktober 2026. Diselaraskan dengan `plan_olahdata.md` (acuan utama) pada 6 Oktober 2026.

### Catatan definisi

**Kategori tingkat kecukupan energi berbasis % AKG** (Badan Pangan Nasional, 2025 — *nomor dokumen dan halaman/tabel masih harus dilengkapi*):

| Kode | Kategori | Rasio konsumsi / kebutuhan AKG | Kelas target biner |
|---|---|---|---|
| 3 | Baik | `>= 100%` | cukup |
| 2 | Sedang | `80 – <100%` | cukup |
| 1 | Kurang | `70 – <80%` | defisit |
| 0 | Defisit | `< 70%` | defisit |

- Target biner model: **defisit = rasio `< 80%`** (kategori 0 dan 1), cukup = rasio `>= 80%` (kategori 2 dan 3). Empat kategori dipakai untuk deskripsi; `step_woe` hanya bisa untuk respons biner.
- Literatur juga banyak mengutip Depkes (1996) dengan lima tingkat (`<70`, `70–79`, `80–89`, `90–119`, `>=120%`). Jelaskan di makalah mengapa batas Badan Pangan Nasional yang dipakai.
- Ambang 2.150 kkal/kapita/hari (Permenkes 75/2013) dan 2.100 kkal/kapita/hari hanya dipakai sebagai pembanding deskriptif, bukan target. Verifikasi sumber masing-masing angka sebelum dikutip.
- **WOE (terverifikasi 6 Oktober):** WOE kategori *i* = ln(p_defisit,*i* / p_cukup,*i*), dengan Laplace 0,5. **WOE positif = kategori condong defisit.** Karena `glm` di `parsnip` memodelkan peluang level kedua (`cukup`), koefisien prediktor WOE diharapkan negatif.

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

- Kebutuhan energi rumah tangga dihitung berdasarkan AKG per individu menurut umur (dalam bulan) dan jenis kelamin, ditambah +330 kkal (anak 0–5 bulan) atau +400 kkal (anak 6–11 bulan) untuk ibu menyusui.
- Konsumsi energi rumah tangga dihitung dari `KALORI_KAP * R301`.
- Rasio = konsumsi energi rumah tangga / kebutuhan AKG rumah tangga.
- `defisit_akg = "defisit"` jika rasio < 0,80, dan `"cukup"` jika rasio >= 0,80.
- Hasil (setelah perbaikan 5 Oktober): defisit 4.239 rumah tangga (16,30%; tertimbang `WERT` 21,59%).

Variabel tambahan untuk eksplorasi:
- `kategori_akg` empat tingkat (`<70%` 7,43%; `70–<80%` 8,87%; `80–<100%` 25,50%; `>=100%` 58,21%)
- pembandingan dengan ambang 2.100 kkal per kapita

## 7. Variabel penjelas

### 7.1 Karakteristik rumah tangga
- `R301` = jumlah anggota rumah tangga; `n_balita`, `n_anak_5_17`, `n_lansia_60`, `n_perokok`
- wilayah: kab/kota `R102` (kandidat WOE), perkotaan/perdesaan `R105`
- perumahan: status kepemilikan `R1802`, luas lantai per kapita `luas_lantai_kap` = `R1804 / R301`, sumber air minum `R1810A`, tempat cuci tangan `R1815A`, bahan bakar memasak `R1817`
- aset (blok 20): tabung gas 5,5 kg `R2001A`, kulkas `R2001B`, AC `R2001C`, pemanas air `R2001D`, telepon rumah `R2001E`, komputer/laptop `R2001F`, emas `R2001G`, motor `R2001H`, mobil `R2001K`, TV datar `R2001L`, tanah/lahan `R2001M`
- bantuan sosial (blok 22): KKS `R2202`, PKH `R2203`, BPNT `R2207`, BLT Desa `R2209A`, PKTD `R2209B`, bantuan pangan/beras `R2209C`

### 7.2 Karakteristik kepala rumah tangga
- jenis kelamin `krt_sex` (`R405`), umur `krt_age_yr` (`R407`)
- `krt_pendidikan`: ijazah `R614` dikelompokkan menjadi tidak punya ijazah, SD, SMP, SMA sederajat, dan perguruan tinggi
- `krt_status_kerja`: `R707` dengan kode 0 dilabeli "Tidak bekerja"
- `krt_lapangan_usaha`: `R706` dengan kode 0 dilabeli "Tidak bekerja" (kandidat WOE)

### 7.3 Kesejahteraan dan rokok
- `nonfood_kap` = `NONFOOD / R301` sebagai proksi kesejahteraan
- `ada_rokok`, `rokok_kap` = pengeluaran rokok per kapita per bulan (KP blok 41, `KLP == 192`)
- `porsi_rokok_nonfood` = rokok / (`NONFOOD` + rokok)

### 7.4 Variabel yang tidak boleh digunakan dalam model utama
- `KALORI_KAP`, `PROTE_KAP`, `LEMAK_KAP`, `KARBO_KAP`, serta kebutuhan, konsumsi, rasio, dan kategori AKG
- `FOOD`, `EXPEND`, `KAPITA`: memuat belanja makanan yang sangat dekat dengan konsumsi energi. `KAPITA` hanya untuk stratifikasi deskriptif/uji sensitivitas
- porsi rokok terhadap `EXPEND` (penyebutnya memuat belanja makanan)
- skala rawan pangan FIES `R1701–R1708` (ukuran hasil yang mirip target)
- `R2209D` (bantuan sertifikasi tanah) tidak dipakai karena tidak relevan dengan kecukupan pangan

## 8. Proses pembersihan data

1. Menangani kode khusus sesuai semesta pertanyaan tiap variabel: `0` (tidak berlaku) dijadikan kategori berlabel bila bermakna (misalnya KRT tidak bekerja), sedangkan `8`, `9`, `98` (tidak tahu/menolak) dijadikan `NA`.
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
| Model | Deskripsi | Status |
|---|---|---|
| Regresi logistik baseline | `step_other` (1%) → dummy → `step_zv` → normalisasi; tanpa transformasi log | Selesai (CV + threshold) |
| Regresi logistik-WOE | `step_other` → `step_discretize` (5 bin, `min_unique = 10`) → `step_woe` (Laplace 0,5) → `step_zv` | Selesai (CV, cek WOE/IV/koefisien, threshold) |
| XGBoost | `step_other` → dummy one-hot → `step_zv`; tuning 6 hiperparameter | Workflow dan grid siap; tuning belum |
| Random Forest (opsional) | Pembanding tambahan | Tidak dikerjakan kecuali ada waktu |

### 9.3 Parameter tuning
- XGBoost: `mtry` (proporsi 0,3–1), `min_n` (10–100), `tree_depth` (2–8), `learn_rate` (0,003–0,1), `loss_reduction` (rentang bawaan), `sample_size` (0,5–1); `trees = 1000` dengan *early stopping* 50 iterasi pada 10% validasi internal; grid *space-filling* 20 kombinasi × 15 resampel; pilih dengan ROC AUC
- Random Forest (opsional): `mtry`, `min_n`, `trees`
- Logistic-WOE: jumlah bin ditetapkan 5 (tidak di-tuning)
- Threshold: maksimum indeks Youden dari prediksi CV per resampel (grid 0,05–0,60), bukan dari data uji. Hasil: baseline 0,16; Logistic-WOE 0,15

### 9.4 Metrik evaluasi
- ROC AUC
- PR AUC (kelas defisit hanya sekitar 16%)
- Balanced accuracy
- Sensitivitas
- Spesifisitas
- F1 score
- Brier score (opsional, belum dipakai)

### 9.5 Hasil sementara (CV data latih, 6 Oktober 2026)

| Ukuran | Baseline | Logistic-WOE |
|---|---:|---:|
| ROC AUC | 0,784 ± 0,002 | 0,795 ± 0,002 |
| PR AUC | 0,396 ± 0,005 | 0,426 ± 0,005 |
| Threshold Youden | 0,16 | 0,15 |
| Sensitivitas | 0,771 | 0,775 |
| Spesifisitas | 0,648 | 0,657 |
| Presisi | 0,299 | 0,306 |
| Balanced accuracy | 0,710 | 0,716 |
| F1 score | 0,431 | 0,439 |

Logistic-WOE unggul kecil tetapi konsisten (selisih ROC AUC ≈ 3,7 × SE). Pada threshold 0,5 sensitivitas hanya 0,102 dan 0,159, sehingga perbandingan antarmodel dilakukan pada threshold masing-masing. Rincian ada di `plan_olahdata.md` butir 14–19.

## 10. Interpretasi model

- Regresi logistik-WOE: tabel WOE per kategori, *Information Value*, dan koefisien. Sudah dikerjakan: IV tertinggi `R102` (1,01) dan `R301` (0,485); koefisien terkuat `nonfood_kap` (−1,33) dan `R102` (−0,99). Koefisien `n_balita`, `n_anak_5_17`, `n_lansia_60` positif sebagai efek komposisi (dengan `R301` tetap). Tujuh prediktor bertanda terbalik tidak ditafsirkan.
- XGBoost: *gain importance* (`xgboost::xgb.importance`) diagregasi dari kolom dummy ke variabel asal; PDP/SHAP opsional.
- Perbandingan peringkat IV vs *gain* dengan korelasi Spearman.

## 11. Jadwal kerja

| Tanggal | Kegiatan | Output | Status (6 Okt) |
|---|---|---|---|
| 2 Oktober 2026 | Pengumpulan data dan pembersihan data awal | Dataset rumah tangga siap analisis | Selesai |
| 3 Oktober 2026 | EDA dan presentasi rencana proyek | Grafik dan ringkasan EDA | Selesai |
| 4–8 Oktober 2026 | Preprocessing, recipe, validasi, tuning | Tabel metrik model | Logistik selesai; tuning XGBoost berjalan |
| 9 Oktober 2026 | Evaluasi akhir, interpretasi | Hasil model dan variabel penting | Kode siap |
| 10 Oktober 2026 | Presentasi awal hasil | Slide presentasi awal | Belum |
| 11–16 Oktober 2026 | Penulisan makalah | Draft makalah | Belum |
| 17 Oktober 2026 | Presentasi draft makalah | Draft final | Belum |

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
| Tabel AKG salah | Cocokkan dengan Permenkes 28/2019; batas umur dalam bulan harus mencakup seluruh tahun usia (bug batas umur sudah diperbaiki 5 Oktober) |
| Kebocoran variabel | Hindari penggunaan variabel yang langsung terkait konsumsi kalori |
| Kelas target tidak seimbang (defisit ±16%) | Laporkan PR AUC, pilih threshold di CV, atau gunakan bobot kelas/downsampling di dalam recipe |
| WOE sensitif terhadap kategori jarang | Gunakan Laplace smoothing dan gabungkan kategori yang langka |
| WOE ekstrem pada kategori dengan sedikit kasus (Pangandaran, WOE −3,63) | Sudah dicek ke data lengkap (bukan galat konversi); dinyatakan sebagai estimasi kurang stabil |
| IV `R102` > 0,5 karena 27 kategori | Dinyatakan di narasi; ditafsirkan bersama variasi proporsi antarwilayah |
| Multikolinearitas → koefisien bertanda terbalik | Tidak ditafsirkan; analisis sensitivitas menunjukkan kinerja tidak berubah |
| CV XGBoost optimistis (tuning dan evaluasi pada resampel yang sama) | Perbandingan final di data uji dengan threshold dari CV |
| Tuning XGBoost lama (300 fit) | `cache: true`, *early stopping*, grid 20 kombinasi |

## 15. Catatan penting

- Judul ini sejalan dengan tugas UAS dan fokus utama pada pemodelan klasifikasi.
- Model diimplementasikan dengan R menggunakan paket `tidymodels`, `embed`, `xgboost`, `probably` (pemilihan threshold), `broom`, dan `purrr`; `vip` opsional.
- Urutan kerja rinci dan status progres ada di `plan_olahdata.md`.
- Data yang dipakai adalah data Susenas 2024 Maret untuk Jawa Barat, bukan data September atau data nasional.

## 16. Kesimpulan singkat

Proyek ini bertujuan untuk mengklasifikasikan rumah tangga yang mengalami defisit kalori berdasarkan kebutuhan AKG, lalu membandingkan model interpretatif (logistik-WOE) dengan model yang lebih kompleks (XGBoost). Selain performa, fokus utama juga ada pada interpretasi dan pemahaman praktis terhadap faktor-faktor yang menentukan defisit kalori rumah tangga di Jawa Barat.
