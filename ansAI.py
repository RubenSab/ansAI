import requests
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime
import google.generativeai as genai


def get_titles_from_url(url):

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        print('Failed to load the url, Status code:', response.status_code)

    titles = soup.find_all('h3', class_='title')
    return titles


def extract_title_text_from_html_title(title):
    return str(title.get_text(strip=True))


def extract_title_url_from_html_title(root_url, title):

    try:
        title_url = title.find('a')['href']
        if title_url[0] == '/':
            title_url = root_url + title_url
            return title_url

    except:
        pass


def md_format_entry(text, url):
    return f'- [{text}]({url})'


def markdown_table_from_dict(dictionary):

    now = datetime.now()
    current_time = now.strftime("%H:%M")

    keys = list(dictionary.keys())
    values = list(dictionary.values())

    markdown_table = [f'| categoria | panoramica ({current_time}) |\n|---|---|\n']
    for (key, value) in zip(keys, values):
        markdown_table.append(f'| {key} | {value} |\n')

    return ''.join(markdown_table)


if __name__ == '__main__':

    # get variables from config
    with open('config.json') as config_file:
        import json
        config = json.load(config_file)

    url = config['url']
    root_url = config['root_url']
    get_only_today_news = config['get_only_today_news']
    news_folder_path = config['news_folder_path']
    ai_model_name = config['ai_model_name']
    api_key = config['api_key']
    add_translation = config['add_translation']
    translation_language = config['translation_language']

    # get news titles from ANSA
    html_titles = get_titles_from_url(url)
    print(f'(1/8): news fetched from {url}')

    # format every news entry as a markdown link
    titles_for_ai = []
    titles_in_markdown = []

    for html_title in html_titles:

        text = extract_title_text_from_html_title(html_title)
        url = extract_title_url_from_html_title(root_url, html_title)

        if type(url) == str:  # checks if the url is valid

            this_was_written_today = str(date.today()).replace('-', '/') in url
            should_add_title = not get_only_today_news or (get_only_today_news and this_was_written_today)

            if should_add_title:
                titles_in_markdown.append(f'{md_format_entry(text, url)}\n')
                titles_for_ai.append(f'- {text}\n')

    print('(2/8): news formatted')

    # remove duplicates
    titles_in_markdown = list(dict.fromkeys(titles_in_markdown))
    titles_number = len(titles_in_markdown)
    titles_in_markdown = ''.join(titles_in_markdown)
    titles_for_ai = ''.join(list(dict.fromkeys(titles_for_ai)))
    print('(3/8): duplicated news removed')

    # import Gemini AI
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(ai_model_name)
    print(f'(4/8): {ai_model_name} imported')

    # give AI the instructions to categorize the news into a dict
    with open('prompts/categorization_prompt.txt', 'r') as f:
        categorization_prompt = f.read()
    categorized_news = model.generate_content(categorization_prompt + titles_for_ai).text
    print('(5/8): news categorized')

    # load summarization prompt
    with open('prompts/summarization_prompt.txt', 'r') as f:
        summarization_prompt = f.read()

    # make the AI summarize news categories into the news dict.
    # if there are syntax errors in the output repeat until AI gets it right.
    # (takes around 3 attempts with weak models in the worst case scenario)
    ai_summary_dict = None
    while ai_summary_dict == None:
        try:
            ai_summary_string = model.generate_content(summarization_prompt + titles_for_ai).text
            ai_summary_string = ai_summary_string.strip('```python\n')
            ai_summary_string = ai_summary_string.strip('```')
            # convert the string representation of the dict into a proper dict
            import ast
            ai_summary_dict = ast.literal_eval(ai_summary_string)
            print('(6/8): news summarized')
        except:
            print('(6/8): invalid news summary format, retrying...')
            pass

    # generate a markdown table from the news dict
    ai_summary_table = markdown_table_from_dict(ai_summary_dict)

    # save the news on a file
    with open(f'{news_folder_path}/{str(date.today())}.md', 'w+') as news_file:

        news_file.write(f'{ai_summary_table}\n')
        news_file.write(f'*sintetizzato da {ai_model_name}*\n\n')
        news_file.write(f'# fonti e altri articoli ({titles_number})\n')
        news_file.write(f'{titles_in_markdown}\n')
        print(f'(7/8): news written in {news_folder_path}')

        # add a translated table if requested by user
        if add_translation:

            # load summarization prompt and add the translated table
            with open('prompts/translation_prompt.txt', 'r') as f:

                translation_prompt = f.read()
                translation_prompt = translation_prompt.replace('{language}', translation_language)
                translated_news_table = model.generate_content(translation_prompt + ai_summary_table).text
                news_file.write(translated_news_table)
                print('(8/8): news translated')
        else:
            print('(8/8): no translation requested')
