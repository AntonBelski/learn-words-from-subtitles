import csv
import os
import random
import re
from collections import Counter, deque

from config import c, setup_webbrowser


colorful = {
    'g': c.GREEN,
    'y': c.YELLOW,
    'r': c.RED,
    '|': c.VIOLET,
    '-': c.VIOLET,
    'info_cyan': c.CYAN,
    'info_blue': c.BLUE
}


def add_colors_to_text(line):
    words_with_freq = line.split('|')
    if not words_with_freq:
        return ''
    elif words_with_freq[0] and words_with_freq[0][0] == '-':
        return colorful['-'] + words_with_freq[0]
    colorful_line = [colorful['|'] + '|']
    for word_block in words_with_freq:
        if not word_block:
            continue
        text_color = word_block[1]
        vertical_line = colorful['|'] + '|'
        colorful_block = colorful[text_color] + ' ' + word_block[2:] + vertical_line
        colorful_line.append(colorful_block)

    return ''.join(colorful_line)


def calculate_percentages_of_words(words_freq, learned_words):
    known_words = 0
    known_unique_words = 0
    for word, freq in words_freq.items():
        if word in learned_words:
            known_words += freq
            known_unique_words += 1
    known_words_percentage = round(100 * known_words / sum(words_freq.values()), 2)
    known_unique_words_percentage = round(100 * known_unique_words / len(words_freq), 2)
    return known_words_percentage, known_unique_words_percentage


def get_words_from_file(file_path):
    counter = Counter()
    with open(file_path, 'r') as file:
        for line in file:
            filtered_line = re.sub('[^a-zA-Z]', ' ', line).lower()
            line_counter = Counter(filtered_line.split())
            counter.update(line_counter)
    return counter


def count_words():
    words_freq = get_words_from_file('words_source')
    unlearned_words = get_words_from_file('vocabulary/unlearned')
    learned_words = get_words_from_file('vocabulary/learned')
    percentages = calculate_percentages_of_words(words_freq, learned_words)
    known_words_percentage, known_unique_words_percentage = percentages

    print(c.BLUE + f'Total words: {str(sum(words_freq.values()))}')
    print(c.BLUE + f'Total unique words: {str(len(words_freq))}')
    print(c.CYAN + f'Percentage of known words: {str(known_words_percentage)}')
    print(c.CYAN + f'Percentage of known unique words: {str(known_unique_words_percentage)}')

    words_freq_list = []
    for word, freq in words_freq.most_common():
        if len(word) > 17:
            print('-------------------------------------------')
        text_color = 'r'
        if word in learned_words:
            text_color = 'g'
        elif word in unlearned_words:
            text_color = 'y'
        # length of the line below is 24
        words_freq_list.append(' ' + text_color + word.ljust(17) + str(freq).ljust(4) + '|')

    cols = 7
    # word_block_size length is 23,
    # 24 -> 23, we decrease 1 because of text_color which we'll remove later
    word_block_length = len(words_freq_list[0]) - 1
    # we increase 1 because we add '|' on the line 34
    underline_size = word_block_length * cols + 1
    underline = '-' * underline_size
    table = []
    for col in range(cols):
        nth_row_words = words_freq_list[col::cols]
        line = []
        for row in range(cols, len(nth_row_words) + cols, cols):
            text_row = ''.join(nth_row_words[row-cols:row])
            line.append(text_row)
        table.append(line)
    table.insert(0, [underline] * min([len(row) for row in table]))
    for sub_table in zip(*table):
        for row in sub_table:
            print(add_colors_to_text(row))
    print(add_colors_to_text(underline))


def refresh_unlearned_words():
    unlearned_words = get_words_from_file('vocabulary/unlearned')
    learned_words = get_words_from_file('vocabulary/learned')
    new_words = []
    with open('vocabulary/unlearned', 'a') as unlearned:
        for source in os.listdir('vocabulary/source'):
            source_words = get_words_from_file(f'vocabulary/source/{source}')
            for word in source_words:
                if word not in unlearned_words and word not in learned_words:
                    unlearned.write(word.ljust(25) + '0\n')
                    unlearned_words[word] = 1
                    new_words.append(word)
    colon = ":" if len(new_words) else ''
    print(c.BLUE + f'Refresh unlearned words was successful, {len(new_words)} new words were added {colon}')
    for word in new_words:
        print(c.CYAN + f' - {word}')


def get_unlearned_words():
    words_freq = dict()
    with open('vocabulary/unlearned', 'r') as file:
        for line in file:
            word, reps = line.split()
            words_freq[word] = int(reps)
    return words_freq


def learn_words():
    unlearned_words = get_unlearned_words()
    k_words = min(5, len(unlearned_words))
    words_to_learn = random.sample(list(unlearned_words.keys()), k=k_words)

    if len(words_to_learn) == 0:
        print(c.GREEN + 'Co Co Congratulations! You don\'t have unlearned words.')
        return

    open_browser = True
    browser = setup_webbrowser()

    with open('vocabulary/learned', 'a') as learned_file:
        while words_to_learn:
            word = words_to_learn[-1]
            print(c.CYAN + 'Do you know the word ' + c.VIOLET + word + c.CYAN + '?')
            print(c.GREEN + 'Y - Yes,' + c.RED + ' N - No')
            answer = input()
            if answer in 'nNтТ':
                if open_browser:
                    browser.open(f'https://translate.yandex.ru/?source_lang=en&target_lang=ru&text={word}')
                words_to_learn.pop()
            elif answer in 'yYнН':
                print(c.GREEN + 'Co Co Congratulations!')
                unlearned_words[word] += 1
                if unlearned_words[word] == 5:
                    learned_file.write(word + '\n')
                words_to_learn.pop()
            print()

    with open('vocabulary/unlearned', 'w') as unlearned_file:
        for word, reps in unlearned_words.items():
            if reps != 5:
                unlearned_file.write(word.ljust(25) + str(reps) + '\n')


def get_word_rating_from_csv(word):
    before_after_10_words = deque()
    is_word_found = False
    with open('unigram_freq_v2.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for i, row in enumerate(csv_reader):
            curr_word_rating = [i, row[0]]
            before_after_10_words.append(curr_word_rating)
            if len(before_after_10_words) == 21:
                break
            if is_word_found:
                continue
            elif word == row[0]:
                is_word_found = True
            elif len(before_after_10_words) > 10:
                before_after_10_words.popleft()
    return before_after_10_words


def find_word_rating():
    print(c.VIOLET + 'Enter the word you want to find the rating for:')
    word = input().lower()
    print()

    unlearned_words = get_words_from_file('vocabulary/unlearned')
    learned_words = get_words_from_file('vocabulary/learned')
    words_around = get_word_rating_from_csv(word)

    if len(words_around) < 21:
        return print(c.GREEN + 'Your word doesn\'t exist in the rating.')

    print(c.CYAN + 'Your word in the rating:')
    for i, word_pair in enumerate(words_around):
        rating, word = word_pair
        color = c.GREY
        if i == 10:
            color = c.BLUE
        elif word in learned_words:
            color = c.GREEN
        elif word in unlearned_words:
            color = c.YELLOW
        elif rating < 10000:
            color = c.RED
        print(color + str(rating).rjust(6) + word.rjust(15))


if __name__ == '__main__':
    print(c.VIOLET + 'What do you want to do today, my great learner?')
    print(c.BLUE + 'R - Refresh words from vocabulary sources, ' +
          c.CYAN + 'L - Learn unlearned words, ' +
          c.YELLOW + 'C - Count words from text source, ' +
          c.GREEN + 'F - Find word rating slice.')

    answer = input()
    print()
    if answer in 'rRкК':
        refresh_unlearned_words()
    elif answer in 'lLдД':
        learn_words()
    elif answer in 'cCсС':
        count_words()
    elif answer in 'fFаА':
        find_word_rating()
