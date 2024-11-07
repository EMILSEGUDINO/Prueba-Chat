import openai
import tkinter as tk
from tkinter import filedialog, messagebox
from fpdf import FPDF
from datetime import datetime

# Configuración de la API de Azure OpenAI
openai.api_type = "azure"
openai.api_base = "https://TU_ENDPOINT.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = "TU_CLAVE_DE_API"

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat con Copilot - Cuenta Empresa")
        self.root.geometry("500x600")

        # Área de chat
        self.chat_box = tk.Text(root, wrap="word", state="disabled", bg="#f0f0f0", font=("Arial", 12))
        self.chat_box.pack(padx=10, pady=10, fill="both", expand=True)

        # Entrada de texto
        self.message_entry = tk.Entry(root, font=("Arial", 12))
        self.message_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)

        # Frame de botones
        button_frame = tk.Frame(root)
        button_frame.pack(fill="x", padx=10, pady=10)

        # Botón para adjuntar PDF
        attach_pdf_button = tk.Button(button_frame, text="Adjuntar PDF", command=self.attach_pdf, bg="#4caf50", fg="white")
        attach_pdf_button.grid(row=0, column=0, padx=5, pady=5)

        # Botón para borrar chat
        clear_button = tk.Button(button_frame, text="Borrar", command=self.clear_chat, bg="#f44336", fg="white")
        clear_button.grid(row=0, column=1, padx=5, pady=5)

        # Botón para guardar en PDF con fecha
        save_pdf_button = tk.Button(button_frame, text="Descargar en PDF", command=self.save_pdf, bg="#2196f3", fg="white")
        save_pdf_button.grid(row=0, column=2, padx=5, pady=5)

        # Botón para guardar historial de chats
        save_history_button = tk.Button(button_frame, text="Guardar Histórico", command=self.save_history, bg="#ff9800", fg="white")
        save_history_button.grid(row=0, column=3, padx=5, pady=5)

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message:
            self.append_to_chat("Tú", message)
            
            # Llamada a la API de Azure OpenAI
            try:
                response = openai.ChatCompletion.create(
                    engine="gpt-35-turbo",  # O el nombre del motor de Azure que hayas configurado
                    messages=[{"role": "user", "content": message}]
                )
                assistant_message = response['choices'][0]['message']['content']
                self.append_to_chat("Copilot", assistant_message)
            except Exception as e:
                self.append_to_chat("Error", f"No se pudo obtener respuesta: {e}")

            # Limpiar la entrada de mensaje
            self.message_entry.delete(0, tk.END)

    def append_to_chat(self, sender, message):
        self.chat_box.config(state="normal")
        self.chat_box.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_box.config(state="disabled")
        self.chat_box.yview(tk.END)

    def attach_pdf(self):
        pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            self.append_to_chat("Sistema", f"Se ha adjuntado el archivo PDF: {pdf_path}")

    def clear_chat(self):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres borrar el chat?"):
            self.chat_box.config(state="normal")
            self.chat_box.delete("1.0", tk.END)
            self.chat_box.config(state="disabled")

    def save_pdf(self):
        chat_content = self.chat_box.get("1.0", tk.END).strip()
        if not chat_content:
            messagebox.showwarning("Advertencia", "No hay conversación para guardar.")
            return

        # Generar el nombre de archivo basado en la fecha actual
        fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"chat_{fecha_actual}.pdf"

        # Guardar el PDF con la fecha actual como nombre predeterminado
        save_path = filedialog.asksaveasfilename(initialfile=default_filename, defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if save_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            
            for line in chat_content.split("\n"):
                pdf.cell(0, 10, line, ln=True)
            
            pdf.output(save_path)
            messagebox.showinfo("Éxito", "Conversación guardada como PDF.")

    def save_history(self):
        # Obtener el contenido actual del chat
        chat_content = self.chat_box.get("1.0", tk.END).strip()
        if not chat_content:
            messagebox.showwarning("Advertencia", "No hay conversación para guardar en el histórico.")
            return

        # Guardar en un archivo de texto
        try:
            with open("historico_chat.txt", "a", encoding="utf-8") as file:
                file.write(f"\n\n=== Conversación del {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                file.write(chat_content)
            messagebox.showinfo("Éxito", "Conversación guardada en el histórico.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el histórico: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
