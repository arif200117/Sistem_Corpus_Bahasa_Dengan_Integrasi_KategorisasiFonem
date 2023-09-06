import os
import tkinter as tk
from tkinter import filedialog, messagebox
import re
from tkinter import ttk
import wave
import pyaudio
import time
import soundfile as sf

# Variabel global untuk menyimpan lokasi file korpus
WORDS_PRON_DICT = ''
# Ukuran buffer atau blok data adalah 1024 byte
CHUNK = 1024

# Fungsi untuk menghapus tanda baca dari teks
def remove_punctuation(text):
    text_with_space = text.replace('-', ' ')
    text_without_punctuation = re.sub(r'[^\w\s]', '', text_with_space)
    return text_without_punctuation

# Fungsi untuk menghitung Longest Prefix Suffix (LPS) dalam algoritma KMP
def compute_lps(pattern):
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

# Fungsi untuk mencari pola dalam teks menggunakan algoritma KMP
def kmp_search(text, pattern, start=0, end=None):
    if end is None:
        end = len(text)

    M = len(pattern)
    N = end

    lps = compute_lps(pattern)
    i = start
    j = 0

    while i < N:
        if pattern[j] == text[i]:
            i += 1
            j += 1

            if j == M:
                return True
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return False

# Fungsi untuk mencari pola dalam sebuah file
def search_in_file(pattern, file_path):
    with open(file_path, 'r') as file:
        text = file.read().replace('\n', '')
        return pattern in text

# Fungsi kategorisasi fonem
def kategorisasi_fonem(missing_words, file_path):
    pattern_tiga = ["kan", "nga", "nya", "sya", "nyi", "nyo", "tya", "syu", "ter", "ber", "per", "pem", "pri", "tur",
                    "tes", "pan", "vei", "sur", "men", "lah"]
    pattern_satu = ["a", "i", "u", "e", "o"]

    for word in missing_words:
        fonem_awal = []
        fonem_akhir = []
        fonem_3 = []

        for fonem in pattern_tiga:
            if kmp_search(word, fonem):
                fonem_3.append(fonem)
        remaining_letters = len(word) - (len(fonem_3) * 3)

        if remaining_letters != 0 and remaining_letters % 2 == 1:  # Ganjil
            if word[0] in pattern_satu and word[0:3] not in pattern_tiga:
                fonem_awal.append(word[0])
            elif word[0] not in pattern_satu and word[0:3] not in pattern_tiga:
                fonem_awal.append(word[0:2])
            else:
                fonem_awal.append(word[0:3])

        elif remaining_letters != 0 and remaining_letters % 2 == 0 and word[0:3] not in pattern_tiga:  # Genap
            fonem_awal.append(word[0:2])

        elif remaining_letters != 0 and remaining_letters % 2 == 0 and word[
                                                                       0:3] in pattern_tiga:  # Genap huruf pertama 3 huruf pertama
            fonem_awal.append(word[0:3])
        elif remaining_letters == 0 and word[0:3] in pattern_tiga:
            fonem_awal.append(word[0:3])

        if fonem_awal:
            first_fonem = len(fonem_awal[0])

        remaining_letters2 = len(word) - first_fonem

        if remaining_letters2 != 0 and remaining_letters2 % 2 == 1:  # karakter tersisa dikurang fonem awal = Ganjil
            if word[-1] in pattern_satu and word[-3:] not in pattern_tiga:
                fonem_akhir.append(word[-1])
            elif word[-1] not in pattern_satu and word[-3:] not in pattern_tiga:
                area_ft = word[first_fonem:len(word) - 1]
                i = 0
                ft3 = []
                for char in area_ft:
                    if area_ft[i:i + 3] in pattern_tiga:
                        ft3.append(area_ft[i:i + 3])
                        i += 3
                if ft3:
                    if len(ft3) % 2 == 1:
                        fonem_akhir.append(word[-2:])
                    else:
                        fonem_akhir.append(word[-1:] + "~")
                elif not ft3:
                    fonem_akhir.append(word[-1:] + "~")
            else:
                fonem_akhir.append(word[-3:])

        elif remaining_letters2 != 0 and remaining_letters2 % 2 == 0:  # karakter tersisa dikurang fonem awal = Genap
            if word[-3:] not in pattern_tiga:  # Genap
                fonem_akhir.append(word[-2:])
            else:
                fonem_akhir.append(word[-3:])

        elif remaining_letters2 % 2 == 0 and word[-3:] in pattern_tiga:  # Genap
            fonem_akhir.append(word[-3:])

        if "~" in fonem_akhir[0]:
            end_fonem = len(fonem_akhir[0]) - 1
        else:
            end_fonem = len(fonem_akhir[0])

        remaining_letters3 = len(word) - first_fonem - end_fonem
        area_ft = word[first_fonem:len(word) - end_fonem]
        fonem_tengah = []
        i = 0

        for char in area_ft:
            if area_ft[i:i + 3] in pattern_tiga:
                fonem_tengah.append(area_ft[i:i + 3])
                i += 3
            else:
                fonem_tengah.append(area_ft[i:i + 2])
                i += 2

        for i, fonem in enumerate(fonem_tengah):
            if len(fonem) == 1 and fonem not in pattern_satu:
                fonem_tengah[i] = fonem + "~"

        fonem_awal = [item for item in fonem_awal if item != ""]
        fonem_tengah = [item for item in fonem_tengah if item != ""]
        fonem_akhir = [item for item in fonem_akhir if item != ""]

        if fonem_akhir and fonem_awal and fonem_tengah:  # fonem akhir ada
            with open(file_path, 'a') as file:
                file.write(word + " " + " " + " ".join(fonem_awal) + " " + " ".join(fonem_tengah) + " " + " ".join(
                    fonem_akhir) + "\n")
        elif fonem_awal and fonem_tengah and not fonem_akhir:
            with open(file_path, 'a') as file:
                file.write(word + " " + " " + " ".join(fonem_awal) + " " + " ".join(fonem_tengah) + "\n")
        elif fonem_awal and fonem_akhir and not fonem_tengah:
            with open(file_path, 'a') as file:
                file.write(word + " " + " " + " ".join(fonem_awal) + " " + " ".join(fonem_akhir) + "\n")
        else:  # fonem akhir habis
            with open(file_path, 'a') as file:
                file.write(word + " " + " " + " ".join(fonem_awal) + "\n")

    return "Kata berhasil ditambahkan ke dalam korpus."

#Fungsi untuk memilih file korpus
def browse_corpus_file():
    global WORDS_PRON_DICT
    file_path = filedialog.askopenfilename(title="Select Corpus File", filetypes=[("Text Files", "*.txt")])
    WORDS_PRON_DICT = file_path
    corpus_file_entry.delete(0, tk.END)
    corpus_file_entry.insert(tk.END, file_path)

# Fungsi untuk menjalankan pencarian dalam korpus
def run_search():
    loaded_words = load_words(WORDS_PRON_DICT)
    kalimat = kalimat_entry.get()
    corpus_file_path = corpus_file_entry.get()

    kalimat = kalimat.lower()
    kalimat_without_punctuation = remove_punctuation(kalimat)
    kata_kata = kalimat_without_punctuation.split()

    file_path = corpus_file_path
    found_words = []
    missing_words = []

    with open(file_path, 'r') as file:
        lines = file.read().split("\n\n")
        for line in lines:
            words = line.split()
            for word in words:
                found_indices = kmp_search(kalimat_without_punctuation, word.lower())
                if found_indices:
                    found_words.append(word)
                else:
                    missing_words.append(word)

    missing_words = list(set(kata_kata) - set(found_words))

    if missing_words:
        result_label.config(text="Kata yang tidak ditemukan dalam korpus: " + ", ".join(missing_words))
        response = messagebox.askquestion("Konfirmasi",
                                          "Apakah Anda yakin kata-kata tersebut merupakan bahasa Indonesia? Apakah Anda ingin menambahkannya ke dalam korpus?")
        if response == 'yes':
            result_message = kategorisasi_fonem(missing_words, file_path)
            result_label.config(text=result_message)
        else:
            print("Kata tidak ditemukan dalam korpus, pastikan kata merupakan bahasa Indonesia.")
    else:
        result_label.config(text="Semua kata ditemukan dalam korpus.")



# Fungsi untuk memuat kata-kata dari file korpus
def load_words(words_pron_dict):
    corpus = {}
    with open(words_pron_dict, 'r') as file:
        for line in file:
            if not (line.startswith(';;;') or line.strip() == ''):
                # Lakukan sesuatu dengan baris yang tidak merupakan komentar atau baris koson
                key, val = line.split('  ', 2)
                corpus[key] = re.findall(r"[\w+~]+", val)
    return corpus

# Fungsi untuk mendapatkan pengucapan kata dalam fonem
def get_pronunciation(corpus, str_input):
    list_pron = []
    # print(str_input) #terbaca
    x = re.sub(r"\s+", ' space ', str_input)
    str_input = x
    for word in re.findall(r"(\w+)+", str_input.lower()):  # ambil tiap kata
        if word in corpus:  # cek kata ada dalam corpus? tidak terdeteksi
            list_pron.extend(corpus[word])
        else:
            print("word tidak terbaca di corpus")

    delay = 0.145
    result = '\nFonem: {}'.format(list_pron)
    tab1_display.insert(tk.END, result)


    for pron in list_pron:
        sound_fonem = play_audio(pron, delay)

# Fungsi untuk memainkan audio berdasarkan fonem
def play_audio(sound, delay):
    try:
        time.sleep(delay)
        wf = wave.open("Fonem/" + sound + ".wav", 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK)

        while data:
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()

        p.terminate()

        return wf
    except:
        pass

# Fungsi untuk mengonversi teks menjadi audio
def convert_audio1():
    loaded_words = load_words(WORDS_PRON_DICT)
    text_info = text.get()
    get_pronunciation(loaded_words, text_info)
# Fungsi untuk menyimpan audio
def save_audio(corpus,str_input):
    list_pron = []
    dir_fon = "E:\AI\Sistem Terbaru fix\Fonem"
    dir_out = "E:\AI\Sistem Terbaru fix\Output"
    #print(corpus) #terbaca
    x = re.sub(r"\s+", ' space ', str_input)
    str_input = x
    for word in re.findall(r"(\w+)+", str_input.lower()):  # ambil tiap kata
        if word in corpus:  # cek kata ada dalam corpus? tidak terdeteksi
            list_pron.extend(corpus[word])
        else:
            print("word tidak terbaca di corpus")

    output_audio = []

    for file in list_pron:
        audio_data, _ = sf.read(os.path.join(dir_fon, f'{file}.wav'))
        output_audio.append(audio_data)

    combined_audio = output_audio[0]
    delay = 0.145

    for audio_data in output_audio[1:]:

        silent_samples = int(delay * 44100)  # Assuming a sample rate of 44100 Hz
        silence = [0.0] * silent_samples
        combined_audio = list(combined_audio) + silence + list(audio_data)
          # Menambahkan penundaan untuk fonem berikutnya

    output_filename = f'{str_input}.wav'  # Tambahkan ekstensi .wav
    output_file = os.path.join(dir_out, output_filename)
    sf.write(output_file, combined_audio, 44100)  # Writing the combined audio data

# Fungsi mengeksekusi penyimpanan audio
def saved():
    loaded_words = load_words(WORDS_PRON_DICT)
    text_info = text.get()
    save_audio(loaded_words,text_info)


# Membuat jendela utama aplikasi
root = tk.Tk()
root.title("Corpus Search GUI")
root.geometry("650x500")

# Membuat tab menggunakan ttk.Notebook
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text="Project")
tab_control.pack(expand=1, fill='both')

# Membuat elemen-elemen GUI
kalimat_label = tk.Label(tab1, text="Masukkan kalimat:")
text = tk.StringVar()
kalimat_entry = tk.Entry(tab1, textvariable=text, width=50)
corpus_file_label = tk.Label(tab1, text="Lokasi Corpus File:")
corpus_file_entry = tk.Entry(tab1, width=50)
corpus_file_entry.insert(tk.END, "Pilih Corpus Dulu ^_*")
corpus_file_button = tk.Button(tab1, text="Browse", command=browse_corpus_file)
search_button = tk.Button(tab1, text="Cek Corpus", command=run_search)
result_label = tk.Label(tab1, text="", wraplength=400)


# Menampilkan elemen-elemen GUI
kalimat_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
kalimat_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W)
corpus_file_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
corpus_file_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
corpus_file_button.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
search_button.grid(row=0, column=2, padx=5, pady=5,sticky=tk.W)
result_label.grid(row=3, column=0, columnspan=4, padx=5, pady=5)
tab1_display = tk.Text(tab1)
tab1_display.grid(row=7, column=0, columnspan=3, padx=5, pady=5)
button = tk.Button(tab1, text="Convert To Audio", command=convert_audio1, width="15", bg="#03A9F4", fg="#FFF")
button.grid(row=2, column=0, padx=5, pady=10,sticky=tk.W)
button = tk.Button(tab1, text="Save Audio", command=saved, width="15", bg="#03A9F4", fg="#FFF")
button.grid(row=2, column=1, padx=5, pady=10,sticky=tk.W)

# Menjalankan loop utama GUI
tab1.mainloop()
