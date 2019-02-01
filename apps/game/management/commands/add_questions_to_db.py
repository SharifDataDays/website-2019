import os
from sys import exit

import pandas as pd
from django.apps import apps
from django.core.management.base import BaseCommand

MAX_DOC_ID = 999999
FILE_UPLOAD_QUESTION_GROUP = 93949596


TERMINOLOGY_MAP = {
    "multiple": "multiple_choice",
    "numeric_range": "interval_number",
    "string": "single_answer",
    "multi_string": "multiple_answer",
    "numeric": "single_number",
}



def add_questions(questions_file_path):
    print(questions_file_path)
    questions = pd.read_csv(questions_file_path)

    for i in range(len(questions)):
        question = questions.iloc[i].to_dict()
        
        question_type = question['type']
        
        if pd.isna(question_type):
            print('DONE :)')
            break
            
        if question_type not in list(TERMINOLOGY_MAP.keys()):
            print('INVALID TYPE "{}"'.format(question_type))
            print(i)
            exit(0)
        
        choices, answer = FUNCTION_MAP[TERMINOLOGY_MAP[question_type]](question)
        skill = question['skill']
        definition = question['question']
        group_id = question['group_id']
        difficulty = question['level']
        question_id = question['id']

        save_in_database(question_id, question_type, definition, choices, answer, skill, group_id, difficulty)

    print(set(qts))
        
    # TODO
    # in order to add file_upload questions to db we must run generator script and then call save_in_database
    # function with these inputs:
    # 1. question_type = "file_upload"
    # 2. definition = <dataset download file url on server>
    # 3. choices = ""
    # 4. answer = <answer file path on server (not reachable from outside of server)>
    # 5. skill = "categorization"

    # this part can be automated but since the generator is another script, 
    # its better to do these instructions manually.


def add_datasets(datasets_folder_path):
    for i, dataset in enumerate(os.listdir('{}/tds'.format(datasets_folder_path))):
        dataset_hash = dataset[:-4] # drop .csv format
        dataset_file_path = '{}/tds/{}'.format(datasets_folder_path, dataset)
        dataset_answer_path = '{}/tdsa/{}_answer'.format(datasets_folder_path, dataset)

        save_in_database(MAX_DOC_ID - i, 'file_upload', dataset_hash, '', dataset_answer_path, 'Categorization', FILE_UPLOAD_QUESTION_GROUP, 'Easy')


def score_from_level(question_type, difficulty):
    if question_type in ['multiple_choice']:
        return {'Easy': 100, 'Medium': 200, 'Difficult': 300}[difficulty]
    elif question_type in ['file_upload']:
        return 1000
    else:
        return {'Easy': 150, 'Medium': 300, 'Difficult': 600}[difficulty]


diff_map = {'Easy': 'easy', 'Medium': 'medium', 'Difficult': 'difficult'}


x = 0

qts = []


def multiple_add(question_id, question_type, definition, choices, answer, skill, group_id, difficulty):
    question_model = apps.get_model('game', 'MultipleChoiceQuestion')
    question = question_model()
    question.stmt = definition
    question.save()

    choice_model = apps.get_model('game', 'Choice')

    if 'visualization' not in skill:
        for option in choices.split('$'):
            choice = choice_model()
            choice.text = option
            choice.question = question
            choice.save()

    question.type = 'multiple_choice'
    question.ui_type = 'choices'

    question.correct_answer = answer
    question.group_id = group_id
    question.doc_id = question_id
    question.level = diff_map[difficulty]
    question.max_score = score_from_level(question_type, difficulty)

    question.save()


def numeric_range_add(question_id, question_type, definition, choices, answer, skill, group_id, difficulty):
    question_model = apps.get_model('game', 'IntervalQuestion')
    question = question_model()
    question.stmt = definition
    question.min_range = float(answer.split('$')[0])
    question.max_range = float(answer.split('$')[1])
    question.group_id = group_id
    question.type = 'interval_number'
    question.ui_type = 'text_number'
    question.doc_id = question_id
    question.level = diff_map[difficulty]
    question.max_score = score_from_level(question_type, difficulty)
    question.save()


def string_add(question_id, question_type, definition, choices, answer, skill, group_id, difficulty):
    question_model = apps.get_model('game', 'Question')
    question = question_model()
    question.stmt = definition
    question.correct_answer = answer
    question.group_id = group_id
    question.type = 'single_answer'
    question.ui_type = 'text_string'
    question.doc_id = question_id
    question.level = diff_map[difficulty]
    question.max_score = score_from_level(question_type, difficulty)
    question.save()


def multi_string_add(question_id, question_type, definition, choices, answer, skill, group_id, difficulty):
    question_model = apps.get_model('game', 'MultipleAnswerQuestion')
    question = question_model()
    question.stmt = definition
    question.group_id = group_id
    question.correct_answer = answer
    question.type = 'multiple_answer'
    question.ui_type = 'multiple'
    question.doc_id = question_id
    question.level = diff_map[difficulty]
    question.max_score = score_from_level(question_type, difficulty)
    question.save()


def numeric_add(question_id, question_type, definition, choices, answer, skill, group_id, difficulty):
    question_model = apps.get_model('game', 'Question')
    question = question_model()
    question.stmt = definition
    question.correct_answer = answer
    question.group_id = group_id
    question.doc_id = question_id
    question_type.type = 'single_answer'
    question_type.ui_type = 'text_number'

    question.level = diff_map[difficulty]
    question.max_score = score_from_level(question_type, difficulty)
    question.save()


def file_upload_add(question_id, question_type, definition, choices, answer, skill, group_id, difficulty):
    model = apps.get_model('game', 'FileUploadQuestion')
    q = model()
    q.stmt = ' '
    q.correct_answer = definition
    q.type = 'file_upload'
    q.ui_type = 'file'
    q.doc_id = question_id
    q.level = diff_map[difficulty]
    q.max_score = score_from_level(question_type, difficulty)
    q.save()


QUESTION_TYPE_MAP = {'numeric': numeric_add,
                     'multi_string': multi_string_add,
                     'multiple': multiple_add,
                     'numeric_range': numeric_range_add,
                     'string': string_add,
                     'file_upload': file_upload_add}


def save_in_database(question_id, question_type, definition, choices, answer, skill, group_id, difficulty):
    QUESTION_TYPE_MAP[question_type](question_id, question_type, definition, choices, answer, skill, group_id,
                                     difficulty)


def answer_multiple_choice(question):
    choices = []
    if not pd.isna(question['choices']):
        choices.append(question['choices'])
        
    if not pd.isna(question['Unnamed: 6']):
        choices.append(question['Unnamed: 6'])

    if not pd.isna(question['Unnamed: 7']):
        choices.append(question['Unnamed: 7'])

    if not pd.isna(question['Unnamed: 8']):
        choices.append(question['Unnamed: 8'])

    choices = '$'.join(choices)
    answer = question['answer_multiple']
    return choices, answer


def answer_single_answer(question):
    answer = question['answer_string']
    return None, answer


def answer_multiple_answer(question):
    answer = question['answer_string']
    answer = answer.strip()[1:-1].split(',')
    answer = '$'.join(answer)
    
    return None, answer


def answer_single_number(question):
    answer = question['answer_numeric']
    return None, answer


def answer_interval_number(question):
    answer = '{}${}'.format(question['from'], question['to'])
    return None, answer


class Command(BaseCommand):
    help = 'Adds questions specifiied in csv input file to database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', nargs='+', type=str)
        parser.add_argument('ddatasets_folder_path', nargs='+', type=str)

    def handle(self, *args, **options):
        csv_file_path = options['csv_file_path'][0]
        ddatasets_folder_path = options['ddatasets_folder_path'][0]
        self.stdout.write(self.style.SUCCESS('Adding questions'))
        add_questions(csv_file_path)
        self.stdout.write(self.style.SUCCESS('Finished adding questions'))
        self.stdout.write(self.style.SUCCESS('Adding datasets'))
        add_datasets(ddatasets_folder_path)
        self.stdout.write(self.style.SUCCESS('Finished adding datasets'))
        self.stdout.write(self.style.SUCCESS('DONE'))        



FUNCTION_MAP = {
    "multiple_choice": answer_multiple_choice,
    "single_answer": answer_single_answer,
    "multiple_answer": answer_multiple_answer,
    "single_number": answer_single_number,
    "interval_number": answer_interval_number,
}


