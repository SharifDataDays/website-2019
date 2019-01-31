from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import os
from sys import exit
from django.apps import apps


MAX_DOC_ID = 999999
FILE_UPLOAD_QUESTION_GROUP = 93949596


TERMINOLOGY_MAP = {
    "multiple": "multiple_choice",
    "numeric_range": "interval_number",
    "string": "single_answer",
    "multi_string": "multiple_answer",
    "numeric": "single_number",
}

FUNCTION_MAP = {
    "multiple_choice": answer_multiple_choice,
    "single_answer": answer_single_answer,
    "multiple_answer": answer_multiple_answer,
    "single_number": answer_single_number,
    "interval_number": answer_interval_number,
}


def add_questions(questions_file_path):
    questions = pd.read_csv(questions_file_path, index_col='id')

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
        
        save_in_database(question_id, question_type, definition, choices, answer, skill, group_id, difficulty)
        
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

        save_in_database(i, 'file_upload', dataset_hash, '', dataset_answer_path, 'Categorization', FILE_UPLOAD_QUESTION_GROUP, 'Easy')


def save_in_database(question_id, question_type, definition, choices, answer, skill, group_id, difficulty):
    qt = question_type
    if qt == 'multiple_choice':
        model = apps.get_model('game', 'MultipleChoiceQuestion')
        q = model()
        q.stmt = definition
        choice = apps.get_model('game', 'Choice')
        for c in choices:
            c = choice()
            c.text = c
            c.question = q;
            c.save()
        q.correct_answer = answer
        q.group_id = group_id
        q.save()

    elif qt == 'interval_number':
        model = apps.get_model('game', 'IntervalQuestion')
        q = model()
        q.stmt = definition
        q.min_range = choices[0]
        q.max_range = choices[1]
        q.group_id = group_id
        q.save()
        
    elif qt == 'single_answer':
        model = apps.get_model('game', 'Question')
        q = model()
        q.stmt = definition
        q.correct_answer = answer
        q.group_id = group_id
        q.save()

    elif qt == 'multiple_answer':
        model = apps.get_model('game', 'MultipleAnswerQuestion')
        q = model()
        q.stmt = definition
        q.group_id = group_id
        q.answer = answer
        q.save()

    elif qt == 'single_number':
        model = apps.get_model('game', 'MultipleAnswerQuestion')
        q = model()
        q.stmt = definition
        q.correct_answer = answer
        q.group_id = group_id
        q.save()
    
    elif qt == 'file':
        model = apps.get_model('game', 'FileUploadQuestion')
        q = model()
        q.stmt = definition
        q.correct_answer = answer
        q.save()


    # TODO implement in views
    


def answer_multiple_choice(question):
    choices = '$'.join([str(x) for x in [question['choices'], question['Unnamed: 6'], question['Unnamed: 7'], question['Unnamed: 8']]])
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
        csv_file_path = options['csv_file_path']
        ddatasets_folder_path = options['ddatasets_folder_path']
        self.stdout.write(self.style.SUCCESS('Adding questions'))
        add_questions(csv_file_path)
        self.stdout.write(self.style.SUCCESS('Finished adding questions'))
        self.stdout.write(self.style.SUCCESS('Adding datasets'))
        add_datasets(ddatasets_folder_path)
        self.stdout.write(self.style.SUCCESS('Finished adding datasets'))
        self.stdout.write(self.style.SUCCESS('DONE'))        





