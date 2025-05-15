import tkinter as tk
from tkinter import ttk, messagebox
import os
from tkinter.filedialog import asksaveasfilename, askopenfilename


class SEAEncryption:
    def __init__(self):
        self.bit_sizes = [64, 128, 256]
        self.key_rules = {
            64: "64-bit anahtar için 8 karakter veya 8 sayı gerekli (0-255 arası)",
            128: "128-bit anahtar için 16 karakter veya 16 sayı gerekli (0-255 arası)",
            256: "256-bit anahtar için 32 karakter veya 32 sayı gerekli (0-255 arası)"
        }

    def generate_key(self, size):
        import random
        return [random.randint(0, 255) for _ in range(size // 8)]

    def validate_key(self, key_text, bit_size):
        required_length = bit_size // 8

        # Eğer giriş boşsa
        if not key_text:
            return False

        # Sayı listesi olarak girilmiş mi kontrol et
        if key_text.startswith('[') and key_text.endswith(']'):
            try:
                numbers = eval(key_text)
                if not isinstance(numbers, list):
                    return False
                if len(numbers) != required_length:
                    return False
                # Sayıların 0-255 arasında olduğunu kontrol et
                return all(isinstance(x, int) and 0 <= x <= 255 for x in numbers)
            except:
                return False

        # Metin kontrolü
        if len(key_text) != required_length:
            return False

        # Metindeki karakterlerin ASCII değerlerinin 0-255 arasında olduğunu kontrol et
        try:
            ascii_values = [ord(c) for c in key_text]
            return all(0 <= x <= 255 for x in ascii_values)
        except:
            return False

    def text_to_key(self, key_text):
        # Sayı listesi olarak girilmiş mi kontrol et
        if key_text.startswith('[') and key_text.endswith(']'):
            try:
                numbers = eval(key_text)
                if isinstance(numbers, list) and all(isinstance(x, int) and 0 <= x <= 255 for x in numbers):
                    return numbers
            except:
                pass

        # Normal metin olarak işle
        return [ord(c) for c in key_text]

    def encrypt(self, text, key):
        result = []
        key_length = len(key)

        for i, char in enumerate(text):
            encrypted_char = ord(char) ^ key[i % key_length]
            result.append(encrypted_char)

        return bytes(result)

    def decrypt(self, encrypted_data, key):
        result = []
        key_length = len(key)

        for i, byte in enumerate(encrypted_data):
            decrypted_char = byte ^ key[i % key_length]
            result.append(decrypted_char)

        return bytes(result).decode('utf-8')


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SEA Şifreleme/Deşifreleme")
        self.root.geometry("800x600")

        self.sea = SEAEncryption()
        self.current_key = None
        self.setup_ui()

    def setup_ui(self):
        # Bit boyutu seçimi
        frame_bit = ttk.LabelFrame(self.root, text="Bit Boyutu", padding=10)
        frame_bit.pack(fill="x", padx=10, pady=5)

        self.bit_var = tk.StringVar(value="64")
        self.bit_var.trace('w', self.update_key_rules)
        for size in self.sea.bit_sizes:
            ttk.Radiobutton(frame_bit, text=f"{size} bit",
                            variable=self.bit_var, value=str(size)).pack(side="left")

        # Anahtar kuralları
        self.rules_label = ttk.Label(self.root, text="", wraplength=700)
        self.rules_label.pack(fill="x", padx=10, pady=5)
        self.update_key_rules()

        # Anahtar yönetimi
        frame_key = ttk.LabelFrame(self.root, text="Anahtar Yönetimi", padding=10)
        frame_key.pack(fill="x", padx=10, pady=5)

        # Anahtar giriş alanı
        self.key_entry = ttk.Entry(frame_key, width=50)
        self.key_entry.pack(side="left", padx=5)

        ttk.Button(frame_key, text="Otomatik Anahtar Oluştur",
                   command=self.generate_auto_key).pack(side="left", padx=5)
        ttk.Button(frame_key, text="Manuel Anahtarı Kullan",
                   command=self.use_manual_key).pack(side="left", padx=5)

        # İşlem seçimi
        frame_op = ttk.LabelFrame(self.root, text="İşlem", padding=10)
        frame_op.pack(fill="x", padx=10, pady=5)

        self.op_var = tk.StringVar(value="encrypt")
        ttk.Radiobutton(frame_op, text="Şifrele",
                        variable=self.op_var, value="encrypt").pack(side="left")
        ttk.Radiobutton(frame_op, text="Deşifrele",
                        variable=self.op_var, value="decrypt").pack(side="left")

        # Dosya seçim butonu
        frame_file = ttk.LabelFrame(self.root, text="Dosya Seçimi", padding=10)
        frame_file.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Button(frame_file, text="Dosya Seç",
                   command=self.select_file).pack(expand=True)

        # Anahtar gösterimi
        self.key_label = ttk.Label(self.root, text="", wraplength=700)
        self.key_label.pack(pady=5)

        # Durum mesajı
        self.status_label = ttk.Label(self.root, text="", wraplength=700)
        self.status_label.pack(pady=5)

    def update_key_rules(self, *args):
        bit_size = int(self.bit_var.get())
        char_count = bit_size // 8
        example_text = 'A' * char_count
        example_numbers = [65] * char_count  # ASCII değeri 'A' için

        self.rules_label.config(
            text=f"Anahtar Kuralları:\n{self.sea.key_rules[bit_size]}\n"
                 f"Örnek metin anahtar: {example_text}\n"
                 f"Örnek sayı listesi: {example_numbers}\n"
                 f"(Her iki örnek aynı anahtarı temsil eder)"
        )

    def generate_auto_key(self):
        bit_size = int(self.bit_var.get())
        self.current_key = self.sea.generate_key(bit_size)
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, str(self.current_key))
        self.key_label.config(
            text=f"Oluşturulan Anahtar: {self.current_key}\n"
                 "ÖNEMLİ: Bu anahtarı kaydedin! Deşifreleme için gerekli olacak."
        )
        self.status_label.config(text="Otomatik anahtar oluşturuldu.")

    def use_manual_key(self):
        bit_size = int(self.bit_var.get())
        key_text = self.key_entry.get()

        if not self.sea.validate_key(key_text, bit_size):
            messagebox.showerror(
                "Hata",
                f"Geçersiz anahtar! {self.sea.key_rules[bit_size]}\n"
                "Anahtar ya metin ya da sayı listesi [n1,n2,...] formatında olmalıdır.\n"
                "Sayılar 0-255 arasında olmalıdır."
            )
            return

        self.current_key = self.sea.text_to_key(key_text)
        key_as_text = ''.join(chr(x) if 32 <= x <= 126 else f"\\x{x:02x}" for x in self.current_key)
        self.key_label.config(
            text=f"Kullanılan Anahtar:\nSayı olarak: {self.current_key}\n"
                 f"Metin olarak: {key_as_text}\n"
                 "ÖNEMLİ: Bu anahtarı kaydedin! Deşifreleme için gerekli olacak."
        )
        self.status_label.config(text="Manuel anahtar ayarlandı.")

    def select_file(self):
        if not self.current_key:
            messagebox.showerror("Hata",
                                 "Lütfen önce bir anahtar oluşturun veya girin!")
            return

        file_path = askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            return

        self.process_file(file_path)

    def process_file(self, file_path):
        try:
            # Dosyayı oku
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # İşlemi gerçekleştir
            if self.op_var.get() == "encrypt":
                processed_data = self.sea.encrypt(content, self.current_key)
                extension = "_encrypted.txt"
            else:
                processed_data = self.sea.decrypt(eval(content), self.current_key)
                extension = "_decrypted.txt"

            # Yeni dosya için kayıt dialogu
            save_path = asksaveasfilename(
                defaultextension=".txt",
                initialfile=os.path.basename(file_path).replace('.txt', extension),
                filetypes=[("Text files", "*.txt")]
            )

            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    if self.op_var.get() == "encrypt":
                        f.write(str(list(processed_data)))
                    else:
                        f.write(processed_data)

                self.status_label.config(
                    text=f"İşlem tamamlandı!\nDosya kaydedildi: {save_path}\n"
                         f"Kullanılan anahtar: {self.current_key}\n"
                         "ÖNEMLİ: Deşifreleme için bu anahtarı kaydettiğinizden emin olun!"
                )

        except Exception as e:
            messagebox.showerror("Hata", f"İşlem sırasında bir hata oluştu: {str(e)}")


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()