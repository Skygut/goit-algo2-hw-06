import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching text: {e}")
        return None


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word.lower(), 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text, search_words=None):
    text = remove_punctuation(text)
    words = text.split()

    if search_words:
        words = [word.lower() for word in words if word.lower() in search_words]

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def visualize_top_words(word_counts, top_n=10):
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[
        :top_n
    ]
    words, counts = zip(*sorted_word_counts)

    plt.barh(words, counts, color="skyblue")
    plt.xlabel("Frequency")
    plt.ylabel("Words")
    plt.title("Top 10 Most Frequent Words")
    plt.gca().invert_yaxis()
    plt.show()


if __name__ == "__main__":
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"
    text = get_text(url)

    if text:
        word_counts = map_reduce(text)

        print("Top 10 most frequent words:")
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for word, count in top_words:
            print(f"{word}: {count}")

        visualize_top_words(word_counts, top_n=10)
    else:
        print("Failed to fetch the text.")
