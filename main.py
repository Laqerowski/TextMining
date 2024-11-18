import tkinter as tk
from tkinter import scrolledtext
import requests
from bs4 import BeautifulSoup
import spacy
import string
from collections import Counter
from stopwordy import custom_polish_stopwords
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Adres URL artykułu
url = "https://wiadomosci.gazeta.pl/wiadomosci/7,114883,26545092,bortniczuk-o-uczestnikach-strajku-kobiet-prymitywne-osoby.html"

# Pobierz zawartość strony
response = requests.get(url)
html_content = response.content

soup = BeautifulSoup(html_content, 'html.parser')

content = ''

elements = soup.find_all(["h1", "h2", "div", "blockquote", "p"])

for element in elements:
    if element.name == "h1":
        content += element.text + '\n'
    elif element.name == "h2":
        content += element.text + '\n'
    elif element.name == "div" and element.get("id") == "gazeta_article_lead":
        content += element.text + '\n'
    elif element.name == "blockquote":
        content += element.text + '\n'
    elif element.name == "p":
        content += element.text + '\n'

# Usunięcie znaków interpunkcyjnych
translator = str.maketrans('', '', string.punctuation)
content_normalized = content.translate(translator).lower()

# Załadowanie modelu języka polskiego w spaCy
nlp = spacy.load("pl_core_news_sm")

# Lematyzacja i usunięcie stopwords
def process_text(text):
    doc = nlp(text)
    lemmatized_tokens = [token.lemma_ for token in doc if token.text.lower() not in custom_polish_stopwords and token.text.strip()]
    return lemmatized_tokens

# Przetworzenie tekstu artykułu
processed_tokens = process_text(content_normalized)

# Słownik tokenów
corrections = {
    "wiejski":"Wiejska",
    "analizą":"analiza",
    "bortniczuk":"Bortniczuk",
    "dziemianowiczbąk":"Dziemianowicz-Bąk",
    "głoszą":"głosić",
    "jarosław":"Jarosław",
    "kaczyński":"Kaczyński",
    "koalicja":"Koalicja",
    "lewica":"Lewica",
    "lewik":"Lewica",
    "news":"News",
    "niezadowolyć":"niezadowalać",
    "obywatelski":"Obywatelska",
    "polityczko":"polityczka",
    "porozumienie":"Porozumienie",
    "praew":"prawa",
    "przyłębsko":"Przyłębska",
    "sanitarn":"sanitarny",
    "Polak":"polak",
    "wyrachowaen":"wyrachowany"
}

# Podmiana/poprawa tokenów
def correct_tokens(tokens, corrections):
    correct_tokens = [corrections.get(token, token) for token in tokens]
    return correct_tokens
 
# Poprawione tokeny
corrected_tokens = correct_tokens(processed_tokens, corrections)

# Słownik połączeń
tokens_to_merge = {
    ("Koalicja", "Obywatelska"):"Koalicja Obywatelska",
    ("Kamil", "Bortniczuk"):"Kamil Bortniczuk",
    ("Polsat", "News"):"Polsat News",
    ("strajk", "kobieta"):"strajk kobiet",
    ("Agnieszka", "Dziemianowicz-Bąk"):"Agnieszka Dziemianowicz-Bąk",
    ("reżim", "sanitarny"):"reżim sanitarny",
    ("Jarosław", "Kaczyński"):"Jarosław Kaczyński",
    ("Julia", "Przyłębska"):"Julia Przyłęska"
}

# Funkcja łączenia tokenów
def merge_token_pairs(tokens, token_pairs):
    merged_tokens = []
    skip_next = False

    for i in range(len(tokens) - 1):
        if skip_next:
            skip_next = False
            continue

        pair = (tokens[i], tokens[i + 1])
        if pair in token_pairs:
            merged_tokens.append(token_pairs[pair])
            skip_next = True
        else:
            merged_tokens.append(tokens[i])

    if not skip_next:  # Dodaj ostatni token, jeśli nie został połączony
        merged_tokens.append(tokens[-1])

    return merged_tokens

# Łączenie tokenów
merged_tokens = merge_token_pairs(corrected_tokens, tokens_to_merge)

#Przypisane sentymencji tokenów
positive_tokens = ["bronić","deeskalować", "pokojowy", "pomagać", "pomóc", "zdrowie"]
negative_tokens = ["barykadować", "koronawirus", "manifestacja", "niezadowalać", "niezadowolenie",
                   "pandemia", "prymitywny", "protest", "protestujący", "reżim sanitarny", "skrajny", 
                   "strajk kobiet", "zatrzymany", "zarzucić", "zaprotestować"]

# Liczenie ilości tokenów
word_counts = Counter(merged_tokens)

# Top 10 tokenów
top_words = word_counts.most_common(10)
top_words_dict = dict(top_words)

# Generator wykresu
def plot_top_words(top_words):
    plt.figure(figsize=(10,6))
    plt.bar(top_words.keys(), top_words.values(), color='skyblue')
    plt.title('Top 10 wystąpień słów')
    plt.xlabel('Słowa')
    plt.ylabel('Liczba wystąpień')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Posortowanie tokenów alfabetycznie
sorted_word_counts = sorted(word_counts.items())

# Funkcja do wyświetlenia tokenów w nowym oknie
def display_tokens():
    # Tworzenie okna
    window = tk.Tk()
    window.title("Tokeny z artykułu")

    # Pole tekstowe do wyświetlenia tokenów
    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=20)
    text_area.pack(padx=10, pady=10)

    # Dodawanie tokenów do pola tekstowego w porządku alfabetycznym
    for token, count in sorted_word_counts:
        if token.strip():  # Sprawdzenie, czy token nie jest pusty
            text_area.insert(tk.END, f"{token}: {count}\n")

    # Uruchomienie pętli głównej tkinter
    window.mainloop()

# Top 20 tokenów
top_words = dict(word_counts.most_common(20))

# Generowanie chmury słów
def generate_word_cloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(text)

    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Chmura słów')
    plt.show()

# Wywołanie funkcji do wyświetlenia tokenów
display_tokens()

# Wywołanie funkcji do wyświetlania wykresu
plot_top_words(top_words_dict)

# Wywołanie funkcji do chmury słów
generate_word_cloud(top_words)

# Analiza emocji dla całego tekstu
def analyze_sentiment(tokens, positive_tokens, negative_tokens):
    positive_count = sum([tokens.count(word) for word in positive_tokens])
    negative_count = sum([tokens.count(word) for word in negative_tokens])
    total_count = len(tokens)
    sentiment_score = (positive_count - negative_count) / total_count
    return positive_count, negative_count, sentiment_score

positive_count, negative_count, sentiment_score = analyze_sentiment(merged_tokens, positive_tokens, negative_tokens)

# Wyświetlenie wyników analizy emocji
def display_sentiment_analysis():
    # Tworzenie okna
    window = tk.Tk()
    window.title("Analiza emocji")

    # Pole tekstowe do wyświetlenia analizy emocji
    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=20)
    text_area.pack(padx=10, pady=10)

    # Dodanie wyników analizy emocji do pola tekstowego
    text_area.insert(tk.END, f"Liczba pozytywnych słów: {positive_count}\n")
    text_area.insert(tk.END, f"Liczba negatywnych słów: {negative_count}\n")
    text_area.insert(tk.END, f"Wynik sentymentu: {sentiment_score:.2f}\n")
    text_area.insert(tk.END, f"Ogólny sentyment: {'Pozytywny' if sentiment_score > 0 else 'Negatywny' if sentiment_score < 0 else 'Neutralny'}\n")

    # Uruchomienie pętli głównej tkinter
    window.mainloop()

# Wywołanie funkcji do wyświetlenia analizy emocji
display_sentiment_analysis()
# Tematyczne słowniki
themes = {
    "polityka": ["polityka", "Koalicja Obywatelska", "Kamil Bortniczuk", "Jarosław Kaczyński", "Lewica", "Porozumienie"],
    "zdrowie": ["koronawirus", "pandemia", "reżim sanitarny", "zdrowie"],
    "protesty": ["strajk kobiet", "protest", "manifestacja", "zaprotestować", "barykadować"]
}

# Funkcja licząca wystąpienia słów tematycznych
def count_theme_words(tokens, themes):
    theme_counts = {theme: 0 for theme in themes}
    for token in tokens:
        for theme, words in themes.items():
            if token in words:
                theme_counts[theme] += 1
    return theme_counts

# Liczenie słów tematycznych
theme_counts = count_theme_words(merged_tokens, themes)

# Generowanie wykresu tematów
def plot_theme_counts(theme_counts):
    plt.figure(figsize=(10, 6))
    plt.bar(theme_counts.keys(), theme_counts.values(), color='skyblue')
    plt.title('Liczba wystąpień słów związanych z tematami')
    plt.xlabel('')
    plt.ylabel('Liczba wystąpień')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Wywołanie funkcji do wyświetlenia wykresu tematów
plot_theme_counts(theme_counts)
