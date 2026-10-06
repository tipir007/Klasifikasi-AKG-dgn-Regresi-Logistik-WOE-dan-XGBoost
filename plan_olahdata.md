# Rencana Pengolahan Data dan Penyusunan `Kelompok_4_AKG.qmd`

**Proyek:** Klasifikasi Defisit Kalori Rumah Tangga Berbasis Angka Kecukupan Gizi di Jawa Barat dengan Regresi Logistik-WOE dan XGBoost  
**Data:** Susenas Maret 2024, Jawa Barat (KOR rumah tangga, KOR individu, Modul KP)  
**Unit analisis:** rumah tangga  
**Tujuan dokumen:** menjadi urutan kerja yang dapat diikuti saat memperbaiki dataset, melakukan analisis di RStudio, dan menyusun laporan Quarto `Kelompok_4_AKG.qmd`.  
**Status dokumen:** acuan utama kelompok. `plan_klasifikasi_kalori.md` (rencana proyek) dan `plan.md` (rencana awal dua judul) sudah diselaraskan dengan dokumen ini.

## Keputusan yang sudah dibekukan

| Aspek | Keputusan |
|---|---|
| Unit analisis | Rumah tangga, n = 26.012 |
| Kebutuhan energi | Jumlah AKG energi seluruh ART menurut umur (bulan) dan jenis kelamin, Permenkes 28/2019, ditambah +330/+400 kkal untuk ibu menyusui anak 0–5/6–11 bulan. Status hamil tidak tersedia |
| Konsumsi energi | `KALORI_KAP * R301` |
| Rasio | Konsumsi / kebutuhan AKG rumah tangga |
| Kategori deskriptif | `<70%`, `70–<80%`, `80–<100%`, `>=100%` AKG |
| Target biner model | `defisit` jika rasio `< 0,80`; `cukup` jika `>= 0,80`. Kelas `defisit` = *event* (level pertama) |
| Prevalensi populasi | Tertimbang `WERT`; model tanpa bobot |
| Sumber ambang 80% | Badan Pangan Nasional (2025) — **nomor dokumen dan halaman masih harus dilengkapi** |
| Arah WOE | WOE = ln(p_defisit / p_cukup); **WOE positif = condong defisit** (terverifikasi pada 140 kategori). `glm` parsnip memodelkan level kedua (`cukup`), sehingga koefisien WOE diharapkan negatif |
| Kriteria threshold | Maksimum indeks Youden (J) dari prediksi CV per resampel, grid 0,05–0,60; threshold tidak diubah saat evaluasi data uji |
| Himpunan prediktor | 38 prediktor yang sama untuk baseline, Logistic-WOE, dan XGBoost |

## 0. Progress kerja terbaru

Status diperbarui pada 6 Oktober 2026. Butir 1–13 berasal dari run QMD 4–5 Oktober. Butir 14–20 berasal dari run QMD 5–6 Oktober oleh kelompok (output R sudah dicek). Sebagian angka di narasi bagian G–I kini diketik langsung dari output, sehingga harus dicocokkan ulang jika data atau kode berubah.

### 0.1 Bagian yang sudah selesai/divalidasi

1. Dataset awal `Klasifikasi_Kalori_RT.csv` sudah dibaca di QMD.
2. Struktur awal dataset sudah dikonfirmasi pada level rumah tangga:
   - jumlah baris: 26.012 rumah tangga;
   - `URUT` unik: 26.012;
   - tidak ada duplikasi rumah tangga yang terdeteksi pada pemeriksaan kunci.
3. Kolom identitas/wilayah duplikat hasil join (`R101_x`/`R101_y`, `R102_x`/`R102_y`, `R105_x`/`R105_y`, `WI1_x`/`WI1_y`, dan `WI2_x`/`WI2_y`) sudah diperiksa. Nilai dan pola missing sama, sehingga satu salinan dipertahankan dan suffix duplikat dihapus.
4. Audit umur individu sudah dilakukan dengan aturan sementara:
   - individu usia 0-4 tahun memakai `R1401` sebagai umur bulan jika berada pada rentang 0-59;
   - individu usia 5 tahun ke atas memakai `R407 * 12`;
   - tidak ditemukan kasus tidak sesuai pada filter validasi umur (`nrow(kasus_umur_tidak_sesuai) = 0`).
5. Agregat komposisi rumah tangga sudah dihitung ulang dari data individu dan tervalidasi terhadap `R301`:
   - `jumlah_rt = 26012`;
   - `urut_unik = 26012`;
   - `r301_tidak_sama_n_art = 0`;
   - `total_balita = 5579`;
   - `total_anak_5_17 = 19327`;
   - `total_lansia_60 = 10402`;
   - `total_perokok = 20958`.
6. Hasil agregat lama yang bermasalah sudah diganti di objek `data_clean`:
   - `n_balita` tidak lagi sama dengan seluruh ART;
   - `n_anak_5_17` dan `n_lansia_60` tidak lagi nol semua;
   - `n_art` konsisten dengan `R301` pada seluruh rumah tangga.
7. Variabel rokok sudah diaudit dari KP blok 41:
   - missing lama pada `rokok_bln` dan `ada_rokok`: 8.483 rumah tangga;
   - setelah audit, missing baru pada `rokok_bln` dan `ada_rokok`: 0;
   - rumah tangga dengan pengeluaran rokok: 17.529;
   - rumah tangga tanpa pengeluaran rokok: 8.483.
8. Keputusan sementara untuk rokok: rumah tangga tanpa baris komoditas rokok di KP41 dikodekan sebagai `rokok_bln = 0` dan `ada_rokok = 0`, karena tidak munculnya baris komoditas pada blok konsumsi menunjukkan tidak adanya konsumsi/pengeluaran komoditas tersebut pada periode pencatatan.
9. Validasi pengeluaran dan konsumsi dari KP blok 43 sudah lulus:
   - tidak ada missing pada `FOOD`, `NONFOOD`, `EXPEND`, `KAPITA`, dan `KALORI_KAP`;
   - `FOOD + NONFOOD = EXPEND` konsisten untuk seluruh rumah tangga;
   - `EXPEND / R301 = KAPITA` konsisten untuk seluruh rumah tangga;
   - selisih maksimum hanya pada skala pembulatan numerik (`max_abs_selisih_expend` sekitar `7.45e-08` dan `max_abs_selisih_kapita` sekitar `2.24e-08`).
10. Target berbasis AKG sudah dibentuk sesuai tabel "Keputusan yang sudah dibekukan", termasuk tambahan ibu menyusui (688 ibu teridentifikasi).
11. Distribusi target setelah perbaikan 5 Oktober (sebelumnya 16,92% karena bug batas umur):
   - `<70% AKG`: 7,43%;
   - `70-<80% AKG`: 8,87%;
   - `80-<100% AKG`: 25,50%;
   - `>=100% AKG`: 58,21%;
   - target biner `defisit`: 4.239 rumah tangga (16,30%); tertimbang `WERT`: 21,59%;
   - target biner `cukup`: 21.773 rumah tangga (83,70%).
12. EDA awal (arah pola tidak berubah setelah perbaikan; angka di narasi QMD kini inline R):
   - perkotaan 19,1% vs perdesaan 10,9%;
   - ukuran rumah tangga: 5,8% (1-2 ART), 17,9% (3-4), 30,4% (5-6), 41,3% (>=7);
   - ada balita 22,1% vs tanpa balita 14,9%;
   - ada lansia 10,3% vs tanpa lansia 18,9%;
   - ada pengeluaran rokok 18,0% vs tanpa 12,7%;
   - kuintil `nonfood_kap`: 29,4% → 18,1% → 13,7% → 11,5% → 8,7%;
   - dalam setiap kuintil, rumah tangga dengan rokok lebih tinggi (K1: 30,8% vs 24,5%; K2: 18,5% vs 16,6%; K3: 14,5% vs 11,8%; K4: 12,3% vs 10,1%; K5: 9,2% vs 8,3%);
   - proporsi rumah tangga dengan pengeluaran rokok menurun menurut kuintil (78,3% → 75,5% → 71,0% → 63,4% → 48,8%; dihitung dari tabel output), sehingga selisih bivariat 5,3 poin sebagian mencerminkan kesejahteraan;
   - pendidikan KRT: SD 37,7%, SMA 25,7%, SMP 17,0%, tidak berijazah 10,5%, PT 9,1%. Status kerja KRT: buruh/karyawan 33,9%, berusaha sendiri 23,8%, tidak bekerja 13,1%, pekerja keluarga hanya 0,7% (189 RT).
13. Modeling tahap awal tersedia di QMD: split 80:20 berstrata, repeated 5-fold CV × 3, baseline logistik (dummy + normalisasi), dan Logistic-WOE (diskritisasi 5 bin + `step_woe`, Laplace 0,5). Hasil CV: ROC AUC 0,7949 ± 0,0018 (WOE) vs 0,7840 ± 0,0024 (baseline), selisih ≈ 3,7 × SE gabungan; PR AUC 0,426 vs 0,396. Hasil 4 Oktober (0,803 vs 0,797) tidak dipakai lagi.
14. Split dan resampling: data latih 20.809 RT (3.391 defisit; 16,30%), data uji 5.203 RT (848 defisit; 16,30%). Fold: 15 resampel (±16.647 analisis / ±4.162 penilaian); prediksi CV gabungan = 62.427.
15. Matriks konfusi CV pada threshold 0,5:
   - baseline: TP 1.034, FN 9.139, FP 873, TN 51.381 (sens 0,102; spes 0,983; presisi 0,542; BA 0,542; F1 0,171);
   - Logistic-WOE: TP 1.622, FN 8.551, FP 1.249, TN 51.005 (sens 0,159; spes 0,976; presisi 0,565; BA 0,568; F1 0,248).
   - Kurva ROC kedua model hampir berimpit; pada FPR 25% sensitivitas 0,669 (WOE) vs 0,659 (baseline). Selisih besar di threshold 0,5 terutama karena pergeseran titik operasi.
16. Pemeriksaan WOE (I.4):
   - 140 kategori, semua WOE berhingga; 68 kategori condong defisit seluruhnya WOE positif, 72 condong cukup seluruhnya negatif;
   - `R102 = 18` (Pangandaran) WOE −3,63 (3 dari 584 RT latih defisit). Dicek di data lengkap: n = 740, median kalori 2.293 kkal (peringkat 6 dari 27; tertinggi Indramayu 2.442), median rasio 1,15, p10 0,95, minimum 0,61 → bukan galat konversi, melainkan ekor bawah yang sempit.
17. *Information Value* (38 prediktor; 5 prediktor hitungan dihitung terpisah dengan top-coding):
   - kuat: `R102` 1,01 (perlu dicermati; Pangandaran menyumbang ±0,12), `R301` 0,485;
   - sedang: `luas_lantai_kap` 0,290, `nonfood_kap` 0,268, `krt_age_yr` 0,170, `n_anak_5_17` 0,165, `rokok_kap` 0,107, `krt_lapangan_usaha` 0,104;
   - lemah (14): antara lain `n_lansia_60` 0,097, `R105` 0,094, `krt_sex` 0,087, `n_perokok` 0,083, `krt_pendidikan` 0,070, `krt_status_kerja` 0,070, `n_balita` 0,040, `ada_rokok`, `porsi_rokok_nonfood`;
   - tidak prediktif (16; IV < 0,02): sebagian besar aset (`R2001A–F`, `H`, `K`, `L`), `R1815A`, dan seluruh bansos.
18. Koefisien Logistic-WOE (fit seluruh data latih): 28 negatif, 10 positif.
   - Positif pada 3 prediktor numerik (`n_balita` 0,53; `n_anak_5_17` 0,41; `n_lansia_60` 0,22) bukan pembalikan: dengan `R301` (−0,46) di model, ketiganya adalah efek komposisi (AKG anak/lansia lebih rendah).
   - 7 prediktor WOE bertanda terbalik (`R2203`, `R2001A`, `R2001K`, `R2001C`, `R2001E`, `ada_rokok`, `porsi_rokok_nonfood`): IV sangat rendah/multikolinear, tidak ditafsirkan.
   - Analisis sensitivitas tanpa ketujuhnya: ROC AUC 0,7943 vs 0,7949; PR AUC 0,4235 vs 0,4255 (selisih ≈ 0,25 SE) → tetap 38 prediktor.
19. Threshold (I.5), indeks Youden dari CV:
   - baseline: threshold 0,16; sens 0,771; spes 0,648; presisi 0,299; BA 0,710; J 0,419; F1 0,431;
   - Logistic-WOE: threshold 0,15; sens 0,775; spes 0,657; presisi 0,306; BA 0,716; J 0,433; F1 0,439;
   - puncak F1 di threshold 0,24 (0,454 baseline; 0,463 WOE) sebagai alternatif bila menekankan ketepatan sasaran.
20. XGBoost (I.6): recipe dummy one-hot, `trees = 1000` + `stop_iter = 50` (validasi internal 10%), `counts = FALSE`; grid *space-filling* 20 kombinasi (`mtry` 0,3–1; `min_n` 10–100; `tree_depth` 2–8; `learn_rate` 0,003–0,1; `loss_reduction` bawaan; `sample_size` 0,5–1). **Tuning belum dijalankan.**

### 0.2 Langkah berikutnya (hands-on)

1. **Jalankan `xgb-tuning`** (300 fit, ±15–40 menit; chunk memakai `cache: true`). Cek `show_best()` dan `autoplot()`. Jika `learn_rate` terbaik < 0,01, naikkan `trees` menjadi 2.000 dan ulangi.
2. **`xgb-best`:** finalisasi workflow, ambil prediksi CV konfigurasi terbaik, pilih threshold Youden XGBoost dengan fungsi yang sama.
3. **Perbandingan tiga model (I.7):** tabel ROC AUC/PR AUC ± SE, metrik pada threshold masing-masing, kurva ROC dan PR gabungan. Catat bahwa CV XGBoost sedikit optimistis karena tuning dan evaluasi memakai resampel yang sama.
4. **Evaluasi data uji (I.8):** `last_fit()` ketiga model; metrik dan matriks konfusi memakai threshold dari CV (0,16 / 0,15 / threshold XGBoost).
5. **Interpretasi (I.9):** *gain importance* XGBoost diagregasi ke variabel asal; bandingkan peringkatnya dengan IV (korelasi Spearman). Opsional: PDP/SHAP untuk `nonfood_kap`, `R301`, `rokok_kap`.
6. **Analisis rokok (opsional, Judul 1):** model dengan vs tanpa peubah rokok (ΔAUC).
7. **Rapikan QMD:**
   - hapus paragraf ganda ("Tabel perbandingan hasil … dibaca sebagai berikut" dan paragraf matriks konfusi WOE yang muncul dua kali);
   - beri label pada chunk tanpa label (`roc-sensitivity-fpr25`, `roc-overlay-baseline-woe`, `threshold-f1-peak`, analisis sensitivitas 31 prediktor);
   - tambahkan `#| warning: false` pada chunk CV yang memunculkan peringatan `step_discretize`.
8. **Verifikasi klaim narasi yang belum dicek:** `mean(data_train$n_balita > 0)`; rata-rata `R301` menurut ada/tidaknya balita dan lansia; nilai `median_nonfood_kap` dan `median_rokok_kap_rt_perokok`; proporsi defisit tertinggi antar-`R102` (batas atas 24,2%).
9. **Penutup:** diskusi, keterbatasan (status hamil dan aktivitas fisik tidak tersedia, `KALORI_KAP` dibatasi BPS, desain survei tidak dipakai di model, sumber ambang 80%, IV `R102` dipengaruhi jumlah kategori), kesimpulan, daftar pustaka, `sessionInfo()`.

### 0.3 Perbaikan yang diterapkan pada QMD (5 Oktober 2026)

| Bagian QMD | Perubahan |
|---|---|
| F.1 `akg-reference-table` | Batas umur diperbaiki (1–3 th = 12–47 bln, 4–6 = 48–83, 7–9 = 84–119, 10–12 = 120–155, 13–15 = 156–191, 16–18 = 192–227, 19–29 = 228–359, 65–80 = 780–971, >80 = 972+). Sebelumnya anak umur 3, 6, 9, 12, 15, 18 tahun dan lansia 80 tahun (7.845 orang) masuk kelompok umur berikutnya |
| F.1 `breastfeeding-mothers` (baru) | Tambahan +330/+400 kkal untuk ibu menyusui; `R503` ditambahkan ke `ind1_full` |
| G.1 `akg-weighted-prevalence` (baru) | Prevalensi tertimbang `WERT` |
| D.6 | Filter rokok menjadi `KLP == 192` |
| D.7 `add-asset-variables` (baru) | Tambah aset emas `R2001G`, motor `R2001H`, mobil `R2001K`, TV datar `R2001L`, lahan `R2001M`, dan bahan bakar memasak `R1817` dari KOR RT |
| G.3 `derive-eda-predictors` | `porsi_rokok_expend` diganti `porsi_rokok_nonfood` = rokok / (NONFOOD + rokok); tambah `luas_lantai_kap`; label `krt_pendidikan` (5 jenjang), `krt_status_kerja` (0 = tidak bekerja), `krt_lapangan_usaha` |
| H.1 | Prediktor diperbarui; `R1804` total, `R2209D` (sertifikasi tanah), dan kode mentah KRT dikeluarkan; `FOOD`, `EXPEND`, `KAPITA` masuk daftar leakage; `stopifnot()` cek leakage |
| I.1 | Tambah `pr_auc` |
| Narasi | Angka pada narasi G, H, I memakai inline R; klaim berlebihan di I.3 (WOE "lebih unggul", "monoton") diganti pembacaan netral; rumusan masalah 5W1H diganti 4 RQ; pembacaan CSV ganda di bagian C dihapus |

### 0.4 Tambahan QMD (5–6 Oktober 2026)

| Bagian QMD | Isi |
|---|---|
| G.2–G.3 | Narasi EDA ditulis ulang dengan angka dari output (tipe daerah, ukuran RT, balita/lansia, rokok, kuintil × rokok, proporsi perokok per kuintil, pendidikan dan status kerja KRT) |
| H.1–H.3 | Narasi dataset final (38 prediktor dalam 7 kelompok, tanpa missing, 1 : 5,1), split, dan fold |
| I.2–I.3 | Narasi matriks konfusi dan ROC baseline serta WOE; tabel perbandingan; overlay ROC; sensitivitas pada FPR 25% |
| I.4 (baru) | `woe-sign-check`, cek Pangandaran, `woe-information-value`, IV 5 prediktor numerik, `woe-coefficient-check`, analisis sensitivitas 31 prediktor (recipe disusun ulang dengan `step_rm` di awal) |
| I.5 (baru) | `threshold-functions`, `threshold-logistic`, puncak F1 |
| I.6 (baru) | `xgb-workflow` (grid sudah dibangkitkan); `xgb-tuning` dan `xgb-best` siap dijalankan |
| I.7–I.9, J | Kode perbandingan tiga model, `last_fit`, *gain importance*, perbandingan IV vs gain, dan `sessionInfo()` sudah disiapkan, belum dijalankan |

## 1. Prinsip kerja yang diselaraskan

Rencana ini menggabungkan tujuan dan variabel pada `plan_klasifikasi_kalori.md` dengan pola penyajian yang direkomendasikan dalam `review_electricalvehicle.md`:

- **Yang diadopsi dari notebook contoh:** alur cerita dari konteks → tujuan → data → analisis → visualisasi → insight → ringkasan; setiap analisis diikuti interpretasi singkat yang menjawab pertanyaan.
- **Yang tidak disalin:** tanggal buatan untuk time series, klaim forecast tanpa waktu observasi yang benar, target leakage, kesimpulan kausal dari analisis prediktif, dan pernyataan bahwa XGBoost pasti lebih unggul sebelum hasil test tersedia.
- **Aturan penulisan QMD:** satu bagian harus menjelaskan tujuan/pertanyaan, metode, kode yang dapat dijalankan, output yang relevan, dan insight dengan batas interpretasi. Semua angka hasil harus berasal dari run QMD terbaru.
- **Reproducibility:** QMD dijalankan dari awal sampai akhir (Render atau Restart & Run All). Tetapkan `set.seed()` dan catat versi R serta package yang digunakan.

## 2. Gerbang wajib sebelum modeling

Jangan mulai pembentukan label final atau model sampai butir berikut selesai.

### 2.1 Putuskan definisi target

> **Status: selesai** — lihat tabel "Keputusan yang sudah dibekukan". Yang tersisa hanya melengkapi rujukan sumber ambang 80% (nomor dokumen, halaman/tabel).

Catatan awal (arsip): rencana yang ada belum konsisten. Ada definisi biner `rasio < 1` sebagai defisit, tetapi juga ada kategori AKG yang menyebut kategori 80–99% sebagai cukup, lalu kategori 70–79% kurang dan <70% defisit. Selain itu terdapat ambang 2.100 dan 2.150 kkal/kapita/hari yang berbeda sumber dan bukan hal yang sama dengan rasio kebutuhan AKG.

**Keputusan yang harus dicatat dalam QMD sebelum analisis:**
1. Formula rasio kecukupan energi rumah tangga.
2. Tabel/sumber AKG dan cara memetakan setiap anggota ke kelompok umur dan jenis kelamin (termasuk aturan nilai umur tidak diketahui dan kelompok fisiologis bila masuk cakupan).
3. Kategori deskriptif yang saling eksklusif dan mencakup semua nilai, misalnya `<70%`, `70–<80%`, `80–<100%`, dan `>=100%`—hanya jika batas tersebut sesuai sumber resmi yang sudah diverifikasi.
4. Label biner utama yang digunakan kedua model. Jika definisinya `defisit = rasio < 100%`, kategori 80–<100% masuk kelas defisit. Jika tim memilih batas lain, rumusan masalah, tujuan, label, dan interpretasi harus disesuaikan.
5. Definisi *event* untuk WOE (kelas mana dianggap event) dan nilai pada batas tepat, seperti rasio sama dengan 70%, 80%, atau 100%.
6. Sumber resmi, tahun, halaman/tabel, dan interpretasi ambang 2.100/2.150 sebagai analisis pembanding terpisah jika tetap digunakan.

**Keluaran gerbang:** keputusan target tertulis dan disetujui kelompok/dosen sebelum label dibuat. Jangan memilih cut-off setelah melihat model mana yang tampak lebih baik.

### 2.2 Perbaiki dan validasi agregat individu

> **Status: selesai** (QMD D.5). Agregat dihitung ulang dari DBF individu dan cocok dengan `R301`. Karakteristik KRT (`krt_edu`, `krt_job`, `krt_sector`) di CSV lama juga salah—misalnya 76% KRT tercatat tidak bekerja, padahal data mentah hanya 13%—dan sudah diganti dari DBF.

Catatan awal (arsip) dari pemeriksaan CSV:
- `n_balita` sama dengan `n_art` di seluruh 26.012 rumah tangga;
- `n_anak_5_17` dan `n_lansia_60` seluruhnya nol;
- pada file KOR individu lanjutan, `R1401` tercatat 0 untuk sebagian besar individu dan positif pada 5.522 individu; metadata mengidentifikasi `R1401` sebagai umur balita dalam bulan. Kode yang memperlakukan setiap nilai non-missing sebagai umur bulan menggunakan kode skip `0` seolah umur valid. Selain itu, umur `R407` (tahun) perlu diperiksa konsistensinya.

Karena itu, **jangan gunakan agregat umur dari CSV sekarang** sampai definisi nilai skip `R1401` diverifikasi dari metadata/kuesioner dan aturan umur dibetulkan. Bentuk indikator balita hanya dari umur yang benar-benar valid dan berada pada rentang yang sesuai; untuk anggota lain gunakan `R407` setelah memeriksa kode umur tidak valid. Setelah agregasi ulang, verifikasi jumlah anak dan lansia secara manual pada beberapa rumah tangga serta pastikan `n_art = R301`.

### 2.3 Periksa nilai hilang rokok dan kolom duplikat

> **Status: selesai** (QMD D.2–D.3 dan D.6). Rumah tangga tanpa baris rokok di KP41 dikodekan 0; kolom `_x`/`_y` terbukti identik dan sudah dirapikan.

Catatan awal (arsip): di CSV, `rokok_bln` dan `ada_rokok` masing-masing kosong pada 8.483 rumah tangga. Telusuri apakah rumah tangga yang tidak memiliki baris komoditas rokok pada KP41 memang harus dikodekan sebagai pengeluaran nol atau apakah terjadi kegagalan join/kelengkapan sumber. Isi nol hanya jika definisi/kuesioner mendukungnya; jika tidak, simpan sebagai missing dan jelaskan perlakuannya.

Kolom wilayah/identitas berpasangan seperti `R101_x`/`R101_y`, `R102_x`/`R102_y`, `R105_x`/`R105_y`, `WI1_x`/`WI1_y`, dan `WI2_x`/`WI2_y` telah diperiksa dan nilainya sama pada CSV ini. Saat memperbaiki skrip, pilih satu sumber yang konsisten dan hapus suffix duplikat setelah validasi. Jangan hapus kolom hanya berdasarkan nama sebelum memastikan kesamaan nilainya.

## 3. Susunan kerja di `Kelompok_4_AKG.qmd`

Susunan di bawah memakai heading laporan yang mudah diikuti. Nomor/format heading boleh disesuaikan dengan template jurnal final, tetapi urutan narasinya dijaga.

### 0. Data Explanation & Import Library

**Isi narasi:** sumber data Susenas Maret 2024 Jawa Barat, komponen KOR rumah tangga/KOR individu/KP Maret, unit rumah tangga, kunci `URUT` dan `URUT`+`R401`, serta tujuan umum dataset gabungan. Sebutkan bahwa angka ukuran dataset adalah hasil pemeriksaan, bukan asumsi.

**Setup chunk:** opsi Quarto, seed, dan package yang memang digunakan. Hindari memanggil `library(tidyverse)` berulang kali. Package tambahan (misalnya `survey`, `tidymodels`, `embed`, `xgboost`, `vip`) dapat dijelaskan/dimuat pada bagian analisis terkait agar bagian awal ringkas. `tidymodels_prefer()` hanya perlu dipanggil setelah `tidymodels` dimuat.

**Output yang diharapkan:** dokumen dapat dirender dan package inti dimuat tanpa error. Warning versi build atau konflik namespace perlu dibedakan dari error; gunakan `dplyr::filter()`/`stats::filter()` bila fungsi ambigu.

### A.1. Identitas / pengantar analisis

Tulis ringkas apa yang dianalisis, wilayah dan periode, unit rumah tangga, serta dua pendekatan yang dibandingkan. Jangan menyebut hasil, prevalensi, model terbaik, atau variabel terpenting sebelum analisis dijalankan. Hindari mengulang rincian file dan semua variabel yang akan diterangkan pada bagian data.

### A.2. Business Understanding

Gunakan SMART bila format tugas menghendaki, namun setiap sasaran harus terukur dan benar-benar dapat dijawab oleh dataset:
- Specific: klasifikasi status kecukupan/defisit energi rumah tangga berdasarkan definisi AKG yang diputuskan.
- Measurable: prevalensi/proporsi dengan penjelasan pembobotan; performa model pada data test; variabel penting.
- Achievable: batasi pada data tersedia dan akui target perlu dibentuk dari AKG anggota.
- Relevant: jelaskan kegunaan sebagai informasi/pemetaan prediksi, bukan bukti sebab-akibat.
- Time-bound: jadwal penyelesaian sesuai jadwal proyek UAS.

### A.3. Gambaran Dataset

Tampilkan pemeriksaan struktural dan kelengkapan data saja; rata-rata, median, distribusi konsumsi, dan interpretasi pola hasil ditempatkan nanti pada Statistik Deskriptif/EDA.

**Kode dan pemeriksaan minimum:**
- baca CSV final yang sudah diperbarui;
- `dim()`/`glimpse()`;
- contoh 5–6 baris;
- jumlah duplikasi dan keunikan `URUT`;
- missing value per kolom dan persentasenya;
- cek konsistensi penggabungan dan `R301` vs jumlah ART;
- identifikasi kolom placeholder target yang masih NA.

**Narasi boleh melaporkan fakta struktural yang terverifikasi:** CSV saat ini berukuran 26.012 × 94; 26.012 `URUT` unik, tidak ada baris duplikat; terdapat 78 kolom integer dan 16 numeric pada pembacaan Python. Laporkan tipe R sesuai output R QMD. Sebutkan bahwa tiga placeholder target (`defisit_akg`, `kebutuhan_akg_rumahtangga`, `konsumsi_akg_rumahtangga`) masih kosong sebelum target dihitung. Nyatakan nilai missing rokok dengan penjelasan bahwa penyebabnya sedang ditelusuri.

### B. Data Validation dan Data Preparation

Pisahkan langkah validasi dari ringkasan dataset, agar pembaca memahami bagaimana data siap analisis.

1. Verifikasi nama kolom dan satuan dari metadata/kuesioner.
2. Audit kunci: `URUT` unik pada level rumah tangga; pasangan `URUT`+`R401` unik pada individu; hasil join tidak menambah/menggandakan baris.
3. Tangani duplikasi `*_x`/`*_y` setelah memastikan nilainya sama.
4. Atur kode skip/tidak berlaku/tidak tahu/menolak menurut semesta pertanyaan masing-masing variabel. Jangan menyamakan seluruh nilai 0 dengan missing; `0` bisa valid pada variabel lain.
5. Perbaiki agregat umur, merokok, bekerja, dan komposisi rumah tangga dengan aturan yang telah divalidasi.
6. Tinjau 8.483 missing pada `rokok_bln`/`ada_rokok`; dokumentasikan jika menjadi nol atau tetap NA dan alasannya.
7. Verifikasi `FOOD + NONFOOD = EXPEND`, `EXPEND / R301 = KAPITA`, unit periode, dan bobot/desain.
8. Simpan dataset bersih sebagai objek analisis di memori atau file turunan yang jelas; jangan menimpa raw DBF.

**Keluaran:** tabel alur data (jumlah baris sebelum/sesudah, alasan eksklusi), ringkasan cleaning, serta assertion/check yang lulus.

### C. Pembentukan Target AKG

1. Gunakan tabel AKG resmi yang sudah diverifikasi dan dikutip.
2. Petakan umur serta jenis kelamin setiap anggota pada kelompok AKG yang sesuai. Umur balita dalam bulan (`R1401`) harus memperlakukan kode skip `0` dengan benar; jangan mengasumsikan non-missing berarti valid.
3. Jumlahkan kebutuhan energi seluruh anggota menjadi kebutuhan rumah tangga.
4. Pastikan konsumsi rumah tangga dan kebutuhan AKG memakai periode/unit yang selaras. Rencana saat ini mengusulkan total konsumsi = `KALORI_KAP * R301`; verifikasi arti dan satuan `KALORI_KAP` serta `R301` terhadap metadata sebelum memakai formula ini.
5. Hitung rasio kecukupan = konsumsi energi rumah tangga / total kebutuhan AKG.
6. Bentuk kategori deskriptif dan target biner setelah gerbang definisi target pada Bagian 2.1 disetujui.
7. Laporkan jumlah target yang berhasil dihitung, jumlah kasus tidak dapat diklasifikasikan, alasan missing, dan distribusi kelas.

**Keluaran:** tabel aturan kategori, flow/ringkasan target, dan prevalensi awal. Bedakan prevalensi berbobot dari proporsi sampel tanpa bobot.

### D. Exploratory Data Analysis / Statistik Deskriptif

Ikuti gaya notebook contoh: pertanyaan kecil → kode → tabel/grafik → paragraf insight. Jangan menulis “faktor memengaruhi” dari grafik deskriptif.

Urutan yang disarankan:
1. Distribusi kelas target (jumlah dan proporsi; beri keterangan bobot yang digunakan).
2. Karakteristik rumah tangga: ukuran rumah tangga, komposisi umur yang sudah dibetulkan, wilayah urban/rural.
3. Pendidikan dan pekerjaan KRT serta indikator pekerjaan ART.
4. Kondisi perumahan/aset/bantuan sosial.
5. Pengeluaran/pengeluaran rokok setelah penanganan missing diputuskan.
6. Hubungan bivariat deskriptif terhadap kelas target (plot/tabel yang relevan), dengan catatan asosiasi bukan kausalitas.

Setiap grafik harus memiliki judul, label, satuan, sumber, dan dirujuk dalam teks. Rata-rata/median dan statistik distribusi dilaporkan di bagian ini, bukan dalam A.3.

### E. Modeling: Logistic-WOE dan XGBoost

- Sebelum split, bekukan definisi target dan daftar kandidat prediktor. Keluarkan variabel yang secara langsung menentukan target, terutama `KALORI_KAP`, `PROTE_KAP`, `LEMAK_KAP`, `KARBO_KAP` dan turunan langsung konsumsi energi. Evaluasi juga risiko leakage dari FOOD/pengeluaran makanan.
- Split stratified 80:20 dengan seed tetap; test set disimpan untuk evaluasi akhir.
- Gunakan repeated stratified 5-fold CV × 3 repeat di training set untuk seleksi/tuning, sesuai rencana, bila kelas dan ukuran sampel tiap kelas memungkinkan.
- Semua imputasi, penggabungan kategori langka, diskretisasi, encoding, dan estimasi WOE dipelajari ulang hanya di training fold melalui `recipe`/workflow. Tidak boleh menghitung WOE seluruh data sebelum CV.
- Logistic-WOE: pastikan event/non-event dan arah WOE eksplisit; gunakan smoothing serta periksa bin dengan nilai nol/kecil.
- XGBoost: tuning hanya dengan CV training; catat parameter dan grid/range yang digunakan.
- Baseline logistik boleh disertakan sebagai pembanding sederhana. Random Forest hanya opsional bila ada alasan dan waktu; jangan menambah model tanpa tujuan.
- Tetapkan metrik utama sebelum melihat hasil. Laporkan ROC AUC, PR AUC, balanced accuracy, sensitivity, specificity, dan F1. Sajikan confusion matrix serta prevalensi kelas.
- Threshold klasifikasi dipilih di dalam training/CV dengan indeks Youden (sudah diterapkan untuk kedua model logistik), bukan berdasarkan test. Puncak F1 dilaporkan sebagai alternatif.

### F. Interpretasi Model

- Logistic-WOE: jelaskan bin, distribusi event/non-event, WOE, koefisien, dan pengaruh perubahan definisi event terhadap tanda interpretasi.
- XGBoost: tampilkan variable importance dan, bila mampu, SHAP/PDP; nyatakan interpretasi prediktif, bukan kausal.
- Bandingkan apakah pola fitur penting konsisten antar model dan beri konteks variabel.
- Jangan menyatakan XGBoost unggul dari training score/feature importance; keunggulan performa ditentukan berdasarkan metrik test yang disepakati dan hasil validasi silang.

### G. Diskusi, kesimpulan, dan keterbatasan

Diskusi menghubungkan hasil dengan pertanyaan dan literatur, menjelaskan kemungkinan mekanisme secara hati-hati, serta menyebut keterbatasan pengukuran konsumsi, pemetaan AKG, desain survei, target/class cut-off, missing, dan generalisasi. Kesimpulan menjawab setiap tujuan menggunakan angka yang benar-benar dihasilkan QMD; jangan klaim sebab-akibat.

## 4. Struktur chunk yang disarankan untuk QMD

Gunakan label chunk yang stabil dan hindari mengulang import package:

1. `setup` — opsi render dan seed; `include: false`.
2. `packages` — package yang dipakai, dimuat sekali.
3. `load-data` — baca dataset gabungan.
4. `dataset-overview` — dimensi, struktur, contoh baris, missing, duplikat.
5. `validate-keys` — keunikan kunci dan pemeriksaan gabungan/agregat.
6. `clean-variables` — kode invalid/skip dan duplikasi kolom.
7. `fix-household-composition` — perbaikan umur/agregat individu dan validasi hasil.
8. `define-akg-target` — kebutuhan, konsumsi, rasio, kategori/label setelah keputusan cut-off.
9. `eda-*` — satu atau beberapa chunk ringkas per pertanyaan EDA.
10. `data-split` — split stratified dan resampling pada training.
11. `recipe-logistic-woe`, `tune-logistic-woe`, `tune-xgboost` — semua transformasi berada dalam fold.
12. `final-test-evaluation` — evaluasi test akhir.
13. `model-interpretation` — WOE, importance, SHAP/PDP bila tersedia.
14. `session-info` — versi R/package untuk reproduksibilitas.

Jangan gunakan `include: false` pada chunk analisis yang metodenya perlu terlihat oleh pembaca; bila output perlu disembunyikan, atur opsi chunk terpisah dan jelaskan metode dalam teks.

## 5. Paket R yang direncanakan

Muat hanya paket yang benar-benar dipakai dan install paket sekali di Console, bukan setiap render:

- `tidyverse` / `readr`: impor, transformasi, dan visualisasi;
- `janitor`: `clean_names()` atau pembersihan nama kolom (opsional jika diperlukan);
- `skimr`: ringkasan struktur (opsional);
- `survey`: ringkasan berbobot/desain survei bila diterapkan;
- `tidymodels`: split, recipe, workflow, CV, tuning, metrik;
- `embed`: transformasi WOE yang kompatibel dengan versi/package yang dipakai;
- `xgboost`: engine boosting dan `xgb.importance()` untuk *gain importance*;
- `dials` (≥ 1.3 untuk `grid_space_filling()`), `hardhat`: ruang dan grid hiperparameter;
- `probably`: pemilihan threshold dari prediksi CV (`threshold_perf()`);
- `broom`, `purrr`: tabel koefisien dan agregasi importance;
- `vip`: opsional (importance sudah dihitung dengan `xgboost`);
- `themis`: downsampling/SMOTE di dalam recipe, hanya bila dipakai (saat ini tidak dipakai; imbalance ditangani dengan pemilihan threshold).

Hindari `library(tidyverse)` berulang kali. Pesan konflik fungsi dari tidyverse biasanya informasi; gunakan namespace, misalnya `dplyr::filter()`, bila ada ambiguitas. `janitor` belum wajib jika tidak memakai fungsi dari package tersebut.

## 6. Checklist penerimaan tahap olahdata

- [ ] `Kelompok_4_AKG.qmd` dapat di-render dari awal pada project folder dengan path relatif.
- [x] Dimensi CSV hasil baca sama dengan angka yang dilaporkan; seluruh `URUT` unik dan tidak ada duplikasi tidak terjelaskan.
- [x] Kolom `*_x`/`*_y` diperiksa dan dibersihkan dengan validasi nilai.
- [x] Konsistensi `R301` vs `n_art` lulus.
- [x] Agregat `n_balita`, `n_anak_5_17`, `n_lansia_60` sudah benar; kode `R1401 = 0` diperlakukan sesuai metadata, bukan umur balita yang valid.
- [x] Makna 8.483 missing pada variabel rokok telah dipastikan sebelum recoding.
- [x] `FOOD + NONFOOD = EXPEND` dan `EXPEND / R301 = KAPITA` konsisten dalam toleransi numerik.
- [x] Pemetaan umur/jenis kelamin ke tabel AKG benar di semua batas kelompok umur (diperbaiki 5 Oktober) dan tambahan ibu menyusui diterapkan.
- [ ] Rujukan sumber ambang 80% (Badan Pangan Nasional 2025: nomor dokumen, halaman/tabel) dilengkapi.
- [x] Cut-off/kategori target tidak kontradiktif dan ditetapkan sebelum modeling.
- [x] Prediktor tidak membocorkan target (daftar leakage + `stopifnot`); preprocessing/WOE diletakkan dalam recipe dan dipelajari per fold.
- [x] Arah tanda WOE diperiksa dengan `tidy()` dan ditulis di metodologi (WOE positif = condong defisit).
- [x] IV dan tanda koefisien Logistic-WOE diperiksa; analisis sensitivitas prediktor bertanda terbalik dilakukan.
- [ ] Threshold klasifikasi dipilih di CV training, bukan di test (logistik selesai: 0,16 / 0,15; XGBoost menyusul).
- [ ] XGBoost di-tuning dengan CV training dan hiperparameter terbaik dicatat.
- [ ] Test set tidak digunakan untuk tuning/seleksi threshold; semua model diuji pada test set yang sama.
- [ ] Narasi tidak mengklaim kausalitas, dan angka yang diketik langsung di narasi G–I sudah dicocokkan dengan render final.
- [x] Prevalensi populasi memakai bobot `WERT`; model tanpa bobot (dinyatakan di G.1).
- [ ] `PSU`/`STRATA` dipakai (paket `survey`) bila diperlukan *standard error* prevalensi.

## 7. Urutan deliverable

1. Dataset hasil perbaikan agregat/kolom dengan dokumentasi perubahan.
2. Keputusan definisi target AKG dengan sumber.
3. QMD tahap data overview, cleaning, target, dan EDA yang dapat di-render.
4. QMD tahap model, validasi, evaluasi test, dan interpretasi.
5. QMD final dengan kesimpulan, keterbatasan, referensi, serta catatan reproducibility.
6. Review internal dosen/asisten dan bukti submission SINTA sesuai aturan UAS.
