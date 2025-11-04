import tkinter as tk
from tkinter import messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import random
import os

# -----------------------------
# Data Handling
# -----------------------------

DATA_FILE = "vocab_data.json"

# Initial vocabulary: English → German
INITIAL_VOCAB = {
    "hello": ["hallo", 0],
    "goodbye": ["auf wiedersehen", 0],
    "thank you": ["danke", 0],
    "please": ["bitte", 0],
    "water": ["wasser", 0],
    "house": ["haus", 0],
    "dog": ["hund", 0],
    "cat": ["katze", 0],
    "book": ["buch", 0],
    "pen": ["stift", 0],
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showwarning("Data Error", "Corrupted data file, starting fresh.")
            return INITIAL_VOCAB
    return INITIAL_VOCAB

def save_data(vocab_data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(vocab_data, f, indent=4)
    except IOError:
        messagebox.showerror("Error", "Could not save data.")

# -----------------------------
# Core Functions
# -----------------------------

def select_word_to_quiz(vocab_data):
    if not vocab_data:
        return None, None
    scores = [v[1] for v in vocab_data.values()]
    max_score = max(scores)
    weighted_words = []
    for eng, (target, score) in vocab_data.items():
        weight = max_score - score + 1
        weighted_words.extend([eng] * weight)
    chosen = random.choice(weighted_words)
    return chosen, vocab_data[chosen][0]

def update_mastery(vocab_data, word, correct):
    if word not in vocab_data:
        return
    score = vocab_data[word][1]
    vocab_data[word][1] = min(score + 1, 5) if correct else max(score - 1, 0)
    save_data(vocab_data)

# -----------------------------
# GUI Components
# -----------------------------

class VocabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VocabMaster: Dynamic German Trainer")
        self.root.geometry("600x420")
        self.vocab_data = load_data()

        self.title_label = tk.Label(root, text="VocabMaster 🇩🇪", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=10)

        self.quiz_btn = tk.Button(root, text="Start Quiz", command=self.start_quiz, width=25)
        self.quiz_btn.pack(pady=5)

        self.stats_btn = tk.Button(root, text="View Progress Chart", command=self.display_chart, width=25)
        self.stats_btn.pack(pady=5)

        self.add_btn = tk.Button(root, text="Add New Word", command=self.add_word, width=25)
        self.add_btn.pack(pady=5)

        self.reset_btn = tk.Button(root, text="Reset Data", command=self.reset_data, width=25)
        self.reset_btn.pack(pady=5)

        self.exit_btn = tk.Button(root, text="Exit", command=self.exit_app, width=25)
        self.exit_btn.pack(pady=10)

    # ---------- QUIZ ----------
    def start_quiz(self):
        if not self.vocab_data:
            messagebox.showinfo("Info", "No vocabulary available. Add words first.")
            return

        # Select 5 words dynamically based on mastery
        quiz_words = []
        for _ in range(5):
            eng, correct_ans = select_word_to_quiz(self.vocab_data)
            if eng and eng not in quiz_words:
                quiz_words.append(eng)

        # Display preview window
        preview_text = "\n".join([f"• {w} → {self.vocab_data[w][0]}" for w in quiz_words])
        confirm = messagebox.askyesno("Quiz Preview",
                                      f"Today's quiz will include these words:\n\n{preview_text}\n\nStart quiz?")
        if not confirm:
            return

        # Start quiz loop
        correct = 0
        for eng in quiz_words:
            correct_ans = self.vocab_data[eng][0]
            user_ans = simpledialog.askstring("Quiz", f"What is the German word for '{eng}'?")
            if user_ans is None:
                break
            if user_ans.lower().strip() == correct_ans.lower():
                correct += 1
                update_mastery(self.vocab_data, eng, True)
                messagebox.showinfo("Correct!", f"✅ Correct! '{eng}' → '{correct_ans}'")
            else:
                update_mastery(self.vocab_data, eng, False)
                messagebox.showwarning("Incorrect", f"❌ Wrong! Correct: '{correct_ans}'")

        messagebox.showinfo("Quiz Result", f"You got {correct}/{len(quiz_words)} correct!")
        save_data(self.vocab_data)

    # ---------- ADD WORD ----------
    def add_word(self):
        eng = simpledialog.askstring("Add Word", "Enter English word:")
        trans = simpledialog.askstring("Add Word", "Enter German translation:")
        if not eng or not trans:
            messagebox.showwarning("Error", "Both fields required.")
            return
        self.vocab_data[eng.lower()] = [trans.lower(), 0]
        save_data(self.vocab_data)
        messagebox.showinfo("Success", f"Added '{eng}' → '{trans}'")

    # ---------- RESET DATA ----------
    def reset_data(self):
        confirm = messagebox.askyesno("Confirm", "Reset all vocabulary data?")
        if confirm:
            self.vocab_data = INITIAL_VOCAB.copy()
            save_data(self.vocab_data)
            messagebox.showinfo("Reset", "All data has been reset!")

    # ---------- CHART ----------
    def display_chart(self):
        if not self.vocab_data:
            messagebox.showinfo("Info", "No data to display.")
            return

        words = list(self.vocab_data.keys())
        scores = [v[1] for v in self.vocab_data.values()]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(words, scores, color="skyblue")
        ax.set_title("Vocabulary Mastery Progress (German)")
        ax.set_ylabel("Mastery Score (0–5)")
        ax.set_xlabel("Words")
        plt.xticks(rotation=45, ha='right')

        chart_win = tk.Toplevel(self.root)
        chart_win.title("Progress Chart")
        canvas = FigureCanvasTkAgg(fig, master=chart_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ---------- EXIT ----------
    def exit_app(self):
        save_data(self.vocab_data)
        confirm = messagebox.askyesno("Exit", "Do you want to save and exit?")
        if confirm:
            self.root.destroy()

# -----------------------------
# Run App
# -----------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = VocabApp(root)
    root.mainloop()
