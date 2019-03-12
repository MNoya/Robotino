from datetime import datetime


def parse_phrases():
    filepath = 'phrases.txt'
    phrases = []
    errors = []
    with open(filepath) as fp:
        currently_reading_phrase = False
        date = None
        phrase_lines = []
        for cnt, line in enumerate(fp):
            line = line.strip(' ')
            try:
                if line != '\n':
                    try:
                        date = parse_date(line)
                        currently_reading_phrase = True
                        phrase_lines = []
                    except:
                        phrase_lines.append(line.strip())
                else:
                    # Phrases should be separated by a break line
                    if currently_reading_phrase:
                        phrase_data = {'text': '\n'.join(phrase_lines), 'date': date}
                        phrases.append(phrase_data)
                        currently_reading_phrase = False
                        print("Saved phrase: {}".format(phrase_data))
            except Exception as e:
                print("Problem parsing line {}: {}".format(cnt, line))
                errors.append(cnt)
                print("Exception:", e)

    print("=" * 40)
    print("Parsed {} phrases, with {} errors".format(len(phrases), len(errors)))
    return phrases

def parse_date(line):
    return datetime.strptime(line.strip(), '%d/%m/%y')

if __name__ == '__main__':
    parse_phrases()
