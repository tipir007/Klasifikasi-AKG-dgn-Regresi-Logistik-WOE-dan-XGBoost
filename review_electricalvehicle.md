# Review Model Penyampaian Notebook Electrical Vehicle untuk Analisis Susenas di RStudio

**Bahan yang ditinjau:** notebook `P1M2_Christopher_Roberto.ipynb`  
**Rencana penggunaan:** mengambil pola penyampaian dan struktur ceritanya sebagai inspirasi untuk analisis klasifikasi defisit kalori rumah tangga Susenas 2024 menggunakan RStudio.  
**Batasan:** yang diadopsi adalah cara mengatur narasi dan menampilkan hasil, bukan menyalin topik, formula, hasil, atau semua metode notebook Electrical Vehicle.

## 1. Kesimpulan utama

Notebook Electrical Vehicle berguna sebagai **contoh alur komunikasi analisis**: mulai dari konteks bisnis, tujuan, data, eksplorasi, analisis, visualisasi, insight per bagian, hingga ringkasan akhir. Pola ini cocok diadaptasi ke laporan RStudio agar pembaca memahami alasan setiap analisis dan arti hasilnya.

Namun, notebook tersebut **tidak sebaiknya dijadikan acuan metodologi tanpa perbaikan**. Beberapa bagian analisis aslinya bermasalah: tanggal time series dibuat secara acak, prediktor model mengandung komponen yang digunakan untuk menghitung target rasio, asumsi ANOVA belum dibuktikan, dan hasil/simulasi ditafsirkan terlalu jauh. Untuk proyek Susenas, gunakan pola penyajian yang sama secara hati-hati, tetapi bangun metode dari pertanyaan penelitian, definisi target AKG, struktur survei, dan rancangan validasi klasifikasi yang benar.

## 2. Pola penyampaian yang layak diadopsi

### 2.1 Cerita bergerak dari masalah ke bukti lalu ke keputusan

Urutan notebook cukup mudah diikuti:
1. mengenalkan topik dan manfaat analisis;
2. menjelaskan masalah bisnis;
3. menetapkan tujuan;
4. mengenalkan data;
5. menunjukkan analisis secara bertahap;
6. memberi insight setelah tabel/grafik/hasil;
7. merangkum temuan dan implikasi.

**Adaptasi untuk Susenas:** ceritakan mengapa kecukupan energi rumah tangga penting, mengapa kebutuhan anggota tidak selalu sama, apa pertanyaan klasifikasinya, data apa yang tersedia, bagaimana target dibentuk, bagaimana dua model dibandingkan, lalu apa arti hasilnya bagi konteks Jawa Barat.

### 2.2 Setiap bagian analisis diikuti interpretasi

Notebook berusaha menyertakan “insight” setelah keluaran. Ini baik sebagai pola komunikasi. Dalam laporan Susenas, setiap tabel atau grafik sebaiknya diikuti paragraf singkat yang menjawab:
- apa pola utama yang terlihat;
- seberapa besar atau seberapa konsisten pola itu;
- bagaimana pola tersebut menjawab pertanyaan penelitian;
- apa batasan interpretasinya.

Hindari hanya menuliskan “terlihat perbedaan” atau membaca ulang semua angka. Insight harus merangkum bukti terpenting dan tetap berhati-hati: *feature importance* dan asosiasi bukan bukti sebab-akibat.

### 2.3 Gunakan visual untuk mendukung, bukan menggantikan, penjelasan

Boxplot, grafik distribusi, grafik performa model, dan tabel ringkasan membantu pembaca memahami hasil dengan cepat. Untuk Susenas, setiap visual perlu memiliki judul informatif, label/satuan, keterangan jumlah observasi atau bobot bila relevan, sumber data, dan disebutkan di dalam teks. Pilih visual yang menjawab tujuan; jangan menambahkan grafik hanya agar laporan tampak panjang.

### 2.4 Tutup dengan ringkasan yang kembali ke tujuan

Bagian *summary* pada notebook membuat pembaca melihat kembali hasil utama. Di laporan Susenas, ringkasan akhir sebaiknya menjawab tiap tujuan secara berurutan, menyebut model terbaik hanya menurut kriteria evaluasi yang telah ditetapkan, lalu mencatat implikasi dan keterbatasan.

## 3. Hal dari notebook yang jangan disalin

| Bagian notebook sumber | Mengapa tidak layak disalin langsung | Prinsip untuk analisis Susenas |
|---|---|---|
| Bulan acak dibuat untuk membangun tanggal dan deret bulanan | Tanggal buatan tidak merepresentasikan kronologi; seasonal decomposition, ADF, ARIMA, dan forecast tidak memiliki dasar temporal yang sahih. | Jangan menambah analisis time series kecuali variabel waktu benar-benar merekam pengamatan berurutan. Susenas Maret 2024 yang dipakai di sini pada dasarnya satu gelombang/cross-section. |
| Target `CO2_Saved_per_TCO_dollar` diprediksi memakai pembilang/penyebut atau komponennya | Informasi target bocor ke prediktor, sehingga nilai $R^2$ yang sangat tinggi tidak menunjukkan generalisasi. | Hindari `KALORI_KAP`, makronutrien, atau fitur lain yang langsung menghitung/mengungkap label defisit AKG sebagai prediktor. Lakukan audit leakage sebelum modeling. |
| $R^2$ disebut “akurasi” atau “tingkat kepercayaan” | $R^2$ adalah ukuran kecocokan regresi, bukan probabilitas kepercayaan atau akurasi klasifikasi. | Untuk klasifikasi, laporkan metrik yang sesuai: ROC AUC, balanced accuracy, sensitivitas, spesifisitas, F1, serta Brier score bila relevan. |
| ANOVA ditafsirkan “H0 diterima” dan rata-rata pasti sama | $p > \alpha$ berarti bukti belum cukup untuk menolak H0; bukan bukti bahwa kelompok pasti sama. Asumsi dan uji lanjut juga perlu diperiksa. | Tulis “gagal menolak H0”, cek asumsi dan desain data, sertakan ukuran efek/ketidakpastian, serta jangan mengklaim beda pasangan hanya dari uji omnibus. |
| Hipotesis menyebut interaksi, formula hanya berisi efek utama | Pertanyaan, model, dan interpretasi tidak konsisten. | Samakan tujuan, rumus model, dan interpretasi; masukkan interaksi hanya bila ada alasan substantif. |
| Simulasi masa depan dibangun dari korelasi dan asumsi kenaikan/penurunan buatan | Itu skenario asumsi, bukan prediksi empiris yang tervalidasi. | Jika ada skenario, beri label “simulasi asumsi” dan jelaskan seluruh asumsi. Jangan menyebutnya hasil forecasting. |
| Kesimpulan memberi rekomendasi kebijakan kuat dari model asosiasi/prediksi | Klaim melebihi bukti, terutama jika ada data leakage atau data buatan. | Sampaikan implikasi secara proporsional; model prediksi tidak membuktikan hubungan sebab-akibat atau efektivitas kebijakan. |

Notebook sumber juga berisi masalah teknis seperti penggunaan objek `sales` yang tidak didefinisikan, ringkasan missing value yang tidak memanggil `sum()`, dan impor yang tidak konsisten dengan fungsi ANOVA yang dipakai. Ini menguatkan bahwa notebook lebih aman ditiru **pola presentasinya** saja, bukan menyalin kode maupun outputnya.

## 4. Rancangan alur penyampaian untuk analisis Susenas di RStudio

Berikut struktur yang disarankan agar mempertahankan gaya penyampaian notebook sumber sambil cocok dengan proyek klasifikasi defisit kalori rumah tangga.

### Bagian 1 — Sampul dan ringkasan proyek

- Judul proyek, nama anggota, mata kuliah, dan tanggal.
- Ringkasan 3–5 kalimat: masalah, data, target, model pembanding, serta temuan utama setelah hasil tersedia.
- Jangan mengisi ringkasan hasil sebelum model benar-benar dijalankan dan dievaluasi.

### Bagian 2 — Latar belakang dan pemahaman masalah

Jelaskan secara ringkas bahwa kebutuhan energi bergantung pada karakteristik anggota rumah tangga. Terangkan alasan menggunakan AKG per individu sebagai dasar kebutuhan rumah tangga, bukan menganggap satu ambang per kapita mewakili semua susunan rumah tangga.

Akhiri dengan pertanyaan yang terukur, misalnya:
1. Berapa proporsi rumah tangga yang masuk kategori defisit menurut definisi yang dipilih?
2. Bagaimana performa Logistic-WOE dibanding XGBoost pada data test yang sama?
3. Prediktor apa yang berkontribusi pada prediksi, dan apakah pola interpretasinya konsisten?

Nyatakan bahwa proyek ini memprediksi/ mengklasifikasikan status menurut definisi operasional, bukan mengestimasi dampak kausal faktor sosial-ekonomi.

### Bagian 3 — Data, unit analisis, dan definisi target

- Sebutkan Susenas Maret 2024, sumber KOR rumah tangga/individu dan KP Maret 2024, cakupan Jawa Barat, unit analisis rumah tangga, serta jumlah data sumber dan sampel akhir.
- Terangkan penggabungan dengan `URUT` untuk rumah tangga dan `URUT` + `R401` untuk individu sebelum agregasi.
- Berikan tabel definisi variabel: target, prediktor, satuan, kode sumber, tingkat data, dan aturan cleaning.
- Jelaskan rasio kecukupan sebagai konsumsi energi rumah tangga dibagi jumlah kebutuhan AKG anggota rumah tangga.
- **Selesaikan terlebih dahulu definisi target.** Rencana saat ini belum konsisten antara target biner rasio <100% dan kategori kecukupan lain. Nyatakan ambang, penanganan nilai tepat di batas, kelompok umur/jenis kelamin AKG, sumber standar, dan kelas event. Jika empat kategori hanya untuk deskripsi sedangkan model memakai target biner, tuliskan pemetaan kategorinya secara eksplisit.
- Ambang 2.100/2.150 kkal per kapita harus dipisahkan sebagai pembanding bila digunakan; jangan disamakan dengan rasio kebutuhan AKG.

### Bagian 4 — Data cleaning dan EDA

Pakai urutan presentasi notebook sumber: pemeriksaan data, tabel/grafik, lalu interpretasi singkat. Untuk Susenas, tunjukkan:
- jumlah observasi, missing, kode skip/tidak tahu/menolak yang diperlakukan menurut konteks variabel;
- konsistensi join dan kesesuaian `R301` dengan jumlah individu;
- distribusi target dan komposisi rumah tangga;
- ringkasan variabel prediktor utama serta perbandingan deskriptif antar kelas.

Pisahkan estimasi tertimbang dan tidak tertimbang dengan jelas. Data Susenas memiliki bobot/desain survei; nyatakan penggunaan `FWT` atau bobot KP yang sesuai untuk statistik populasi dan keputusan pemakaian bobot pada pemodelan. Jangan menafsirkan proporsi sampel tanpa bobot sebagai estimasi prevalensi penduduk jika desain survei tidak dipertimbangkan.

### Bagian 5 — Metode klasifikasi

Susun metode menjadi satu bagan alir dan uraian singkat per tahap:
1. Tetapkan target dan arah kelas event.
2. Pisahkan train/test secara stratifikasi.
3. Lakukan preprocessing di dalam resampling/training, bukan pada seluruh data sebelum split.
4. **Logistic-WOE:** bentuk bin/kategori pada data analysis fold, hitung WOE dengan smoothing yang dinyatakan, transformasi data assessment, lalu fit regresi logistik.
5. **XGBoost:** gunakan fold/pembagian yang sama, tuning parameter berdasarkan cross-validation pada train saja, lalu refit pada seluruh train.
6. Pilih threshold klasifikasi berdasarkan training/CV bila diperlukan; jangan memilihnya dengan melihat test.
7. Evaluasi kedua model satu kali pada test set yang sama.

Jelaskan WOE secara verbal dan matematis, termasuk definisi event/non-event dan arah tandanya. Bin dengan nol atau sangat sedikit observasi/event perlu penanganan dan dilaporkan. Laplace smoothing saja tidak menggantikan pemeriksaan stabilitas bin.

### Bagian 6 — Hasil model, interpretasi, dan insight

Tampilkan tabel performa Logistic-WOE dan XGBoost berdampingan. Sertakan jumlah kelas test dan metrik yang relevan. Tentukan sebelum evaluasi metrik utama sesuai tujuan (misalnya sensitivitas bila kesalahan melewatkan rumah tangga defisit paling merugikan); jangan memilih metrik setelah melihat model mana yang menang.

Setelah tabel, jelaskan:
- model mana yang unggul menurut metrik utama dan bagaimana metrik pendukungnya;
- apakah selisihnya konsisten dalam cross-validation atau kecil/tidak stabil;
- trade-off interpretabilitas Logistic-WOE dengan fleksibilitas XGBoost;
- faktor penting WOE/koefisien serta importance/SHAP, dengan catatan bahwa importance bukan pengaruh kausal.

Jangan menyatakan XGBoost lebih baik hanya karena modelnya kompleks atau nilai training lebih tinggi. Klaim keunggulan harus didasarkan pada hasil test set dan validasi yang fair.

### Bagian 7 — Diskusi, keterbatasan, dan kesimpulan

- Bandingkan temuan dengan literatur yang relevan.
- Bahas potensi pengukuran konsumsi, definisi target, kategori umur AKG, missing, ketidakseimbangan kelas, desain/bobot survei, dan generalisasi.
- Batasi implikasi pada rumah tangga/cakupan data yang dianalisis.
- Kesimpulan menjawab tujuan dengan angka hasil terverifikasi, bukan klaim kausal atau prediksi di luar data.

## 5. Cara meniru gaya penyajian di RStudio

R Markdown (`.Rmd`) atau Quarto (`.qmd`) dapat menggabungkan narasi dan kode dalam satu laporan. Setiap bagian analisis idealnya memakai pola tetap:

1. **Pertanyaan/tujuan kecil** — apa yang hendak diperiksa?
2. **Metode** — bagaimana ukuran atau model dihitung?
3. **Kode R** — singkat, modular, dan dapat dijalankan ulang.
4. **Output** — tabel/grafik yang relevan saja.
5. **Insight** — satu paragraf interpretasi yang menjawab pertanyaan dan memberi batasan.

Gunakan heading yang konsisten, nomor tabel/gambar otomatis, sumber data, serta setup chunk yang mengatur package dan seed. Simpan langkah import, cleaning, pembentukan target, split, preprocessing, modeling, dan evaluasi secara eksplisit supaya laporan dapat dirender dari awal.

Paket yang mungkin sesuai: `tidyverse`/`readr` untuk data, `ggplot2` untuk grafik, `survey` untuk analisis berbobot/desain, `tidymodels` (`rsample`, `recipes`, `workflows`, `tune`, `yardstick`) untuk workflow dan validasi, `embed` untuk langkah WOE sesuai implementasi yang digunakan, `xgboost` sebagai engine, serta `vip` atau alat interpretasi lain untuk importance. Pastikan semua preprocessing dan WOE dipelajari hanya dari training fold agar tidak bocor.

## 6. Checklist sebelum mulai menulis laporan RStudio

- [ ] Pertanyaan penelitian, unit analisis, dan populasi sasaran sudah jelas.
- [ ] Definisi rasio AKG, cut-off defisit, empat kategori deskriptif, dan kelas event sudah konsisten.
- [ ] Tabel AKG dan pemetaan umur/jenis kelamin memiliki sumber yang dapat dikutip.
- [ ] Konsumsi energi, periode, dan satuan telah diverifikasi terhadap dokumentasi Susenas.
- [ ] Prediktor tidak memuat variabel yang langsung membentuk atau mengungkap target.
- [ ] Bobot dan desain survei dipertimbangkan; keputusan pemakaian bobot dinyatakan.
- [ ] Train/test dan resampling sama untuk kedua model; preprocessing dilakukan hanya di dalam train/fold.
- [ ] Metrik utama ditetapkan sebelum membandingkan model.
- [ ] Semua insight merujuk pada output aktual dan tidak menyatakan kausalitas dari model prediksi.
- [ ] R Markdown/Quarto dapat dirender dari awal tanpa bergantung pada state tersembunyi.

## 7. Penilaian akhir

**Yang ditiru:** alur komunikasi dari konteks → tujuan → data → analisis → visualisasi → insight → ringkasan, serta kebiasaan memberi penjelasan setelah hasil.

**Yang tidak ditiru:** tanggal sintetis untuk time series, penggunaan prediktor pembentuk target, klaim akurasi/forecast yang belum tervalidasi, kesimpulan “H0 diterima”, dan rekomendasi kebijakan yang melampaui bukti.

Dengan batas tersebut, notebook Electrical Vehicle dapat membantu membentuk **gaya penyampaian** laporan RStudio. Validitas hasil proyek Susenas tetap harus ditentukan oleh definisi AKG yang konsisten, preprocessing tanpa leakage, pertimbangan desain survei, dan perbandingan model pada data yang benar-benar belum digunakan selama training.