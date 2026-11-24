import tkinter as tk
from tkinter import messagebox
from functools import lru_cache
import secrets
import string

ALPHABET = string.ascii_uppercase + '0123456789'
WEIGHTS = {character: index + 1 for index, character in enumerate(ALPHABET)}
BLOCK_LENGTH = 4
BLOCK_COUNT = 3


@lru_cache(maxsize=None)
def count_completions(remaining, total):
    if remaining == 0:
        return int(total == 0)
    return sum(
        count_completions(remaining - 1, total - weight)
        for weight in WEIGHTS.values()
    )


def weighted_choice(options):
    total_weight = sum(weight for _, weight in options)
    selected = secrets.randbelow(total_weight)
    for value, weight in options:
        if selected < weight:
            return value
        selected -= weight
    raise RuntimeError('Не удалось выбрать символ для ключа')


def generate_block(minimum, maximum):
    possible_totals = [
        (total, count_completions(BLOCK_LENGTH, total))
        for total in range(max(minimum, BLOCK_LENGTH), min(maximum, BLOCK_LENGTH * len(ALPHABET)) + 1)
    ]
    possible_totals = [(total, count) for total, count in possible_totals if count]
    if not possible_totals:
        raise ValueError('Для этого интервала невозможно сгенерировать блок')

    target = weighted_choice(possible_totals)
    remaining_total = target
    characters = []
    for remaining in range(BLOCK_LENGTH - 1, -1, -1):
        options = [
            (
                character,
                count_completions(remaining, remaining_total - WEIGHTS[character]),
            )
            for character in ALPHABET
        ]
        options = [(character, count) for character, count in options if count]
        character = weighted_choice(options)
        characters.append(character)
        remaining_total -= WEIGHTS[character]
    return ''.join(characters), target


def generate_key(minimum, maximum):
    blocks = [generate_block(minimum, maximum) for _ in range(BLOCK_COUNT)]
    key = '-'.join(block for block, _ in blocks)
    totals = '-'.join(str(total) for _, total in blocks)
    return key, totals


def main():
    window = tk.Tk()
    window.title('Генератор ключа')
    window.geometry('800x400')
    window.resizable(0,0)

    bg_img = tk.PhotoImage(file='i.png')
    label_bg = tk.Label(window, image=bg_img)
    label_bg.place(x=0, y=0, relwidth=1, relheight=1)

    tk.Label(
        window,
        text='Диапазон суммы одного блока:',
        font=('Consolas', '14')
    ).pack(pady=(36, 6))

    interval_frame = tk.Frame(window)
    interval_frame.pack()
    tk.Label(interval_frame,text='От',font = ('Consolas', '12')).grid(row=0, column=0, padx=(0, 10))
    minimum_entry = tk.Entry(interval_frame, width=8, font = ('Consolas', '12'))
    minimum_entry.grid(row=0, column=1)
    tk.Label(interval_frame,text='До', font = ('Consolas', '12')).grid(row=0, column=2, padx=(12, 10))
    maximum_entry = tk.Entry(interval_frame, width=8, font = ('Consolas', '12'))
    maximum_entry.grid(row=0, column=3)

    key_value = tk.StringVar()
    tk.Label(window, text='Сгенерированный ключ:').pack(pady=(18, 10))
    tk.Entry(
        window,
        textvariable=key_value,
        justify='center',
        font=('Consolas', 14),
        width=30,
        state = 'readonly'
    ).pack()

    sums_value = tk.StringVar()
    tk.Label(window, textvariable=sums_value).pack(pady=5)

    def on_generate():
        try:
            minimum = int(minimum_entry.get())
            maximum = int(maximum_entry.get())
            if minimum > maximum:
                raise ValueError('Начало диапазона не может быть больше конца')
            key, totals = generate_key(minimum, maximum)
        except ValueError as error:
            messagebox.showerror('Некорректный диапазон', str(error), parent=window)
            return

        key_value.set(key)
        sums_value.set(f'Суммы блоков: {totals}')

    tk.Button(window, text='Сгенерировать', command=on_generate).pack(pady=12)
    window.mainloop()


if __name__ == '__main__':
    main()
