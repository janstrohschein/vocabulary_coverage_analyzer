# -*- coding: utf-8 -*-
import re
import sys
from configparser import ConfigParser
from ExcelWriter import ExcelWriter
from collections import OrderedDict


class LanguageStats:
    def __init__(self):
        self.config = OrderedDict()
        self.raw_txt = OrderedDict()
        self.base_word_list = OrderedDict()
        self.stats = OrderedDict()
        self.print_output = OrderedDict()
        self.raw_txt_to_base_list = OrderedDict()
        self.base_list_to_raw_txt = OrderedDict()

    def read_config(self):

        if len(sys.argv) > 1:
            config_path = sys.argv[1]
            config = ConfigParser()
            config.read(config_path, encoding='utf-8')

            try:
                sections = config.sections()
                if len(sections) == 0:
                    sys.exit()
                for section in sections:

                    self.config[section] = OrderedDict()
                    for option in config.options(section):
                        self.config[section][option] = config.get(section, option)
            except:
                print("The config file path is not valid")
                sys.exit()
        else:
            print("No config file path provided")
            sys.exit()

    def read_raw_txt(self):
        for list_nr, path in self.config['Input Raw Text File Paths'].items():
            self.raw_txt[list_nr] = {}
            self.raw_txt[list_nr]['raw_txt_path'] = path
            self.raw_txt[list_nr]['count_raw_txt'] = 0
            with open(path, 'r') as in_file:
                self.raw_txt[list_nr]['raw_txt'] = []
                for line in in_file:
                    for word in re.findall(r"[\w]+", line):
                        self.raw_txt[list_nr]['raw_txt'].append(word.upper())
                        self.raw_txt[list_nr]['count_raw_txt'] += 1
            self.raw_txt[list_nr]['raw_txt'] = sorted(self.raw_txt[list_nr]['raw_txt'], key=str.lower)

    def read_base_word_list(self):
        for list_nr, path in self.config['Input Base Word List Paths'].items():
            self.base_word_list[list_nr] = {}
            self.base_word_list[list_nr]['data'] = []
            self.base_word_list[list_nr]['base_word_list_path'] = path
            self.base_word_list[list_nr]['count_base_word_list_families'] = 0
            self.base_word_list[list_nr]['count_base_word_list_tokens'] = 0

            try:
                with open(path, 'r') as in_file:
                    family = []
                    for line in in_file:
                        try:
                            if not line.startswith('\t'):
                                if len(family) > 0:
                                    self.base_word_list[list_nr]['data'].append(tuple(family))
                                    family = []
                                family.append(line.strip())
                                self.base_word_list[list_nr]['count_base_word_list_families'] += 1
                            else:
                                family.append(line.strip())

                            self.base_word_list[list_nr]['count_base_word_list_tokens'] += 1
                        except:
                            print('Base Word List ' + str(list_nr) + ': Not all Lines could be processed')
                    # appends the last family
                    self.base_word_list[list_nr]['data'].append(tuple(family))
            except:
                print('Base Word List ' + str(list_nr) + ': File could not be opened')

    def get_sorted_bwl(self):
        for bwl in self.base_word_list:
            self.base_word_list[bwl]['sorted'] = {}
            for i, family in enumerate(self.base_word_list[bwl]['data']):
                for item in family:
                    if item[0] not in self.base_word_list[bwl]['sorted']:
                        self.base_word_list[bwl]['sorted'][item[0]] = []
                    self.base_word_list[bwl]['sorted'][item[0]].append((item, i))

    def get_raw_txt_in_word_list(self, input):

        for rtl_nr in self.raw_txt:
            if rtl_nr not in self.raw_txt_to_base_list:
                self.raw_txt_to_base_list[rtl_nr] = OrderedDict()

            for bwl_nr in self.base_word_list:
                if bwl_nr not in self.raw_txt_to_base_list[rtl_nr]:
                    self.raw_txt_to_base_list[rtl_nr][bwl_nr] = {}
                self.raw_txt_to_base_list[rtl_nr][bwl_nr][input] = {}
                self.raw_txt_to_base_list[rtl_nr][bwl_nr][input]['count_txt_in_word_list'] = 0
                self.raw_txt_to_base_list[rtl_nr][bwl_nr][input]['count_txt_not_in_word_list'] = 0
                self.raw_txt_to_base_list[rtl_nr][bwl_nr][input]['raw_txt_in_word_list'] = []
                self.raw_txt_to_base_list[rtl_nr][bwl_nr][input]['raw_txt_not_in_word_list'] = []

            for word in self.raw_txt[rtl_nr][input]:
                word_found = False
                for bwl_nr in self.base_word_list:
                    if word_found is False:
                        if word[0] in self.base_word_list[bwl_nr]['sorted']:
                            for entry in self.base_word_list[bwl_nr]['sorted'][word[0]]:
                                if word == entry[0]:
                                    word_found = True
                                    self.raw_txt_to_base_list[rtl_nr][bwl_nr][input]['count_txt_in_word_list'] += 1
                                    self.raw_txt_to_base_list[rtl_nr][bwl_nr][input]['raw_txt_in_word_list'].append(word)
                                    break
                        if not word_found:
                            self.raw_txt_to_base_list[rtl_nr][bwl_nr][input]['count_txt_not_in_word_list'] += 1
                            self.raw_txt_to_base_list[rtl_nr][bwl_nr][input]['raw_txt_not_in_word_list'].append(word)

    def get_word_list_in_raw_text(self):
        for bwl_nr in self.base_word_list:
            self.base_list_to_raw_txt[bwl_nr] = {}

            for rtl_nr in self.raw_txt:
                word_list_in_raw_txt = set()

                self.base_list_to_raw_txt[bwl_nr][rtl_nr] = {}
                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['count_word_list_in_txt'] = 0
                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['count_word_list_not_in_txt'] = 0
                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['word_list_in_raw_txt'] = []
                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['word_list_not_in_raw_txt'] = []

                for token in self.raw_txt[rtl_nr]['distinct_types']:
                    if token[0] in self.base_word_list[bwl_nr]['sorted']:
                        for entry in self.base_word_list[bwl_nr]['sorted'][token[0]]:
                            if token == entry[0]:
                                word_list_in_raw_txt.add(tuple(self.base_word_list[bwl_nr]['data'][entry[1]]))
                                break

                word_list_in_raw_txt = sorted(word_list_in_raw_txt)
                word_list_not_in_raw_txt = [item for item in self.base_word_list[bwl_nr]['data'] \
                                            if item not in word_list_in_raw_txt]

                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['word_list_in_raw_txt'] = word_list_in_raw_txt
                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['word_list_not_in_raw_txt'] = word_list_not_in_raw_txt

                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['count_word_list_in_txt'] = len(word_list_in_raw_txt)
                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['count_word_list_not_in_txt'] = len(word_list_not_in_raw_txt)

    def get_raw_txt_distinct_types(self):
        for list_nr in self.raw_txt:
            self.raw_txt[list_nr]['distinct_types'] = []
            distinct_types = 0
            old_word = ''
            for word in self.raw_txt[list_nr]['raw_txt']:
                if word != old_word:
                    old_word = word
                    self.raw_txt[list_nr]['distinct_types'].append(word)
                    distinct_types += 1
            self.raw_txt[list_nr]['count_distinct_types'] = distinct_types

    def get_stats(self):
        for rtl_nr in self.raw_txt:
            self.stats[rtl_nr] = OrderedDict()

            for input_type in ('raw_txt', 'distinct_types'):
                cum_percent = 0
                count_input = 'count_' + input_type
                for bwl_nr in self.base_word_list:
                    if bwl_nr not in self.stats[rtl_nr]:
                        self.stats[rtl_nr][bwl_nr] = OrderedDict()
                    self.stats[rtl_nr][bwl_nr][input_type] = OrderedDict()

                    self.stats[rtl_nr][bwl_nr][input_type]['percent_raw_txt_in_base_list'] = self.raw_txt_to_base_list \
                                                                                                 [rtl_nr][bwl_nr][
                                                                                                 input_type][
                                                                                                 'count_txt_in_word_list'] / \
                                                                                             self.raw_txt[rtl_nr][
                                                                                                 count_input]
                    cum_percent += self.stats[rtl_nr][bwl_nr][input_type]['percent_raw_txt_in_base_list']
                    self.stats[rtl_nr][bwl_nr][input_type]['cum_percent_raw_txt_in_base_list'] = cum_percent

                    self.stats[rtl_nr][bwl_nr]['raw_txt']['percent_base_list_in_raw_txt'] = \
                        self.base_list_to_raw_txt[bwl_nr] \
                            [rtl_nr]['count_word_list_in_txt'] / self.base_word_list[bwl_nr][
                            'count_base_word_list_families']

    def prepare_raw_txt_print(self, input):
        for bwl_nr in self.base_word_list:
            if bwl_nr not in self.print_output:
                self.print_output[bwl_nr] = {}

            for rtl_nr in self.raw_txt_to_base_list:
                if rtl_nr not in self.print_output[bwl_nr]:
                    self.print_output[bwl_nr][rtl_nr] = {}

                self.print_output[bwl_nr][rtl_nr][input] = []
                old_word = ''
                word_count = 0
                for i, word in enumerate(self.raw_txt_to_base_list[rtl_nr][bwl_nr]['raw_txt'][input]):
                    if word != old_word:
                        if word_count > 0:
                            self.print_output[bwl_nr][rtl_nr][input].append((str(word_count) + 'x ' + old_word + '\n'))
                        old_word = word
                        word_count = 1
                    else:
                        word_count += 1

                    if len(self.raw_txt_to_base_list[rtl_nr][bwl_nr]['raw_txt'][input]) - 1 == i:
                        self.print_output[bwl_nr][rtl_nr][input].append((str(word_count) + 'x ' + old_word + '\n'))

    def prepare_base_list_print(self, input):

        complete_families = self.config['Parameter']['print_complete_families']

        for bwl_nr in self.base_list_to_raw_txt:
            if bwl_nr not in self.print_output:
                self.print_output[bwl_nr] = {}

            for ltr_nr in self.base_list_to_raw_txt[bwl_nr]:
                if ltr_nr not in self.print_output[bwl_nr]:
                    self.print_output[bwl_nr][ltr_nr] = {}

                self.print_output[bwl_nr][ltr_nr][input] = []

                if complete_families == 'True':
                    for family in self.base_list_to_raw_txt[bwl_nr][ltr_nr][input]:
                        self.print_output[bwl_nr][ltr_nr][input].append(str(family) + '\n \n')
                else:
                    for family in self.base_list_to_raw_txt[bwl_nr][ltr_nr][input]:
                        self.print_output[bwl_nr][ltr_nr][input].append(str(family[0]) + '\n')

    # def write_txt_file(self, path):
    #     out_file = codecs.open(path, 'w', 'utf-8')
    #     out_file.write('Input File Paths \n')
    #     out_file.write('Raw Text File \t \t' + self.raw_txt['raw_txt_path']  + '\n' )
    #
    #     for list_nr in self.base_word_list:
    #         out_file.write('Base Word List ' + str(list_nr) + '\t' + \
    #                        self.base_word_list[list_nr]['base_word_list_path'] + '\n' )
    #     out_file.write('\n')
    #
    #     out_file.write('Overview \n')
    #     out_file.write('Count Raw Text \t \t \t Tokens: ' + str(self.raw_txt['count_raw_txt_tokens']) + '\t \t')
    #     out_file.write('Types: ' + str(self.raw_txt['count_raw_txt_types']) + '\n')
    #
    #     for list_nr in self.base_word_list:
    #         out_file.write('Count Base Word List ' + str(list_nr) + '\t Families: ' + \
    #                        str(self.base_word_list[list_nr]['count_base_word_list_families']) + '\t \t')
    #         out_file.write('Tokens: ' + \
    #                        str(self.base_word_list[list_nr]['count_base_word_list_tokens']) + '\n')
    #     out_file.write('\n')
    #
    #     out_file.write('Analysis\n')
    #     out_file.write('Raw Text Token Count in Base Word List \n')
    #     out_file.write('\t\t\t\t\t   in \t not in\t  %in\t %in cum\n')
    #     for list_nr in self.raw_txt_to_base_list:
    #         out_file.write('Word List ' + str(list_nr) + ' Tokens \t' + \
    #                        str('{num:{width}}'.format(num=self.raw_txt_to_base_list[list_nr]['count_txt_in_word_list'], width=6)) + ' ' + \
    #                        str('{num:{width}}'.format(num=self.raw_txt_to_base_list[list_nr]['count_txt_not_in_word_list'], width=6)) + '\t ' + \
    #                        str('{percent:6.2%}'.format(percent=self.stats[list_nr]['percent_raw_txt_in_base_list'])) +'\t  ' + \
    #                        str('{percent:6.2%}'.format(percent=self.stats[list_nr]['cum_percent_raw_txt_in_base_list'])) +'\n')
    #     out_file.write('\n')
    #
    #     out_file.write('Base Word List Families Count in Raw Text \n')
    #     for list_nr in self.base_list_to_raw_txt:
    #         out_file.write('Word List ' + str(list_nr) + ' Families \t in: ' + \
    #                        str(self.base_list_to_raw_txt[list_nr]['count_word_list_in_txt']) + ' \t ')
    #         out_file.write('not in: ' + str(self.base_list_to_raw_txt[list_nr]['count_word_list_not_in_txt']) + '\n')
    #     out_file.write('\n')
    #
    #
    #     for list_nr in self.print_output:
    #         out_file.write('Raw Text Tokens in Base Word List ' + str(list_nr) + ': \n')
    #         out_file.writelines(self.print_output[list_nr]['raw_txt_in_word_list'])
    #         out_file.write('\n')
    #         out_file.write('\n')
    #         out_file.write('\n')
    #
    #         out_file.write('Raw Text Tokens not in Base Word List ' + str(list_nr) + ': \n')
    #         out_file.writelines(self.print_output[list_nr]['raw_txt_not_in_word_list'])
    #         out_file.write('\n')
    #         out_file.write('\n')
    #         out_file.write('\n')
    #
    #         out_file.write('Base Word List ' + str(list_nr) + ' in Raw Text: \n')
    #         out_file.writelines(self.print_output[list_nr]['word_list_in_raw_txt'])
    #         out_file.write('\n')
    #         out_file.write('\n')
    #         out_file.write('\n')
    #
    #         out_file.write('Base Word List ' + str(list_nr) + ' not in Raw Text: \n')
    #         out_file.writelines(self.print_output[list_nr]['word_list_not_in_raw_txt'])
    #         out_file.write('\n')
    #         out_file.write('\n')
    #         out_file.write('\n')
    #
    #
    #     out_file.close()
    #     print("Liste ausgegeben in " + path)


    def write_excel_file(self):

        path = self.config['Output File Path']['output_path']

        if len(path) == 0:
            print('No output path provided')
            sys.exit()

        wb = ExcelWriter(path)

        ws = wb.add_worksheet('Overview')
        ws.set_column(0, 0, 30)

        # Input File Paths
        ws.write(0, 0, 'Input File Paths', wb.bold)
        wb.curr_row = 1

        for rtl_nr in self.raw_txt:
            ws.write_row(wb.curr_row, 0, ('Raw Text File ' + str(rtl_nr), self.raw_txt[rtl_nr]['raw_txt_path']))
            wb.curr_row += 1

        for bwl_nr in self.base_word_list:
            ws.write_row(wb.curr_row, 0, ('Base Word List ' + str(bwl_nr),
                                          self.base_word_list[bwl_nr]['base_word_list_path'])
                         )
            wb.curr_row += 1

        # Input File Overview
        wb.curr_row += 1
        ws.write(wb.curr_row, 0, 'Overview', wb.bold)
        wb.curr_row += 1
        for ltr_nr in self.raw_txt:
            ws.write_row(wb.curr_row, 0, ('Count Raw Text ' + str(ltr_nr),
                                          'Tokens:', self.raw_txt[ltr_nr]['count_raw_txt'],
                                          'Types:', self.raw_txt[ltr_nr]['count_distinct_types']))
            wb.curr_row += 1

        for bwl_nr in self.base_word_list:
            ws.write_row(wb.curr_row, 0, ('Count Base Word List ' + str(bwl_nr),
                                          'Tokens:', self.base_word_list[bwl_nr]['count_base_word_list_tokens'],
                                          'Families:', self.base_word_list[bwl_nr]['count_base_word_list_families']))
            wb.curr_row += 1

        # Analysis
        ws.write(wb.curr_row + 1, 0, 'Analysis', wb.bold)
        ws.write(wb.curr_row + 2, 0, 'Raw Text Token Count in Base Word List')
        wb.curr_row += 3

        for ltr_nr in self.raw_txt_to_base_list:
            ws.write(wb.curr_row, 0,
                     'Raw Text ' + str(ltr_nr) + ' (' + str(self.raw_txt[ltr_nr]['count_raw_txt']) + ' Tokens)')
            ws.write_row(wb.curr_row, 1, ('in', 'not in', '%in', '%in cum'), wb.align_mid)
            wb.curr_row += 1

            for bwl_nr in self.raw_txt_to_base_list[ltr_nr]:
                ws.write_row(wb.curr_row, 0, ('Word List ' + str(bwl_nr),
                                              self.raw_txt_to_base_list[ltr_nr][bwl_nr]['raw_txt'][
                                                  'count_txt_in_word_list'],
                                              self.raw_txt_to_base_list[ltr_nr][bwl_nr]['raw_txt'][
                                                  'count_txt_not_in_word_list']))
                ws.write(wb.curr_row, 3, self.stats[ltr_nr][bwl_nr]['raw_txt']['percent_raw_txt_in_base_list'] * 100,
                         wb.percent)
                ws.write(wb.curr_row, 4,
                         self.stats[ltr_nr][bwl_nr]['raw_txt']['cum_percent_raw_txt_in_base_list'] * 100, wb.percent)

                wb.curr_row += 1
            ws.write_row(wb.curr_row, 1, (
                'missed:', self.raw_txt_to_base_list[ltr_nr][bwl_nr]['raw_txt']['count_txt_not_in_word_list']))
            wb.curr_row += 2
        #
        ws.write(wb.curr_row + 1, 0, 'Raw Text Type Count in Base Word List')
        wb.curr_row += 2

        for ltr_nr in self.raw_txt_to_base_list:
            ws.write(wb.curr_row, 0,
                     'Raw Text ' + str(ltr_nr) + ' (' + str(self.raw_txt[ltr_nr]['count_distinct_types']) + ' Types)')
            ws.write_row(wb.curr_row, 1, ('in', 'not in', '%in', '%in cum'), wb.align_mid)
            wb.curr_row += 1

            for bwl_nr in self.raw_txt_to_base_list[ltr_nr]:
                ws.write_row(wb.curr_row, 0, ('Word List ' + str(bwl_nr),
                                              self.raw_txt_to_base_list[ltr_nr][bwl_nr]['distinct_types'][
                                                  'count_txt_in_word_list'],
                                              self.raw_txt_to_base_list[ltr_nr][bwl_nr]['distinct_types'][
                                                  'count_txt_not_in_word_list']))
                ws.write(wb.curr_row, 3,
                         self.stats[ltr_nr][bwl_nr]['distinct_types']['percent_raw_txt_in_base_list'] * 100, wb.percent)
                ws.write(wb.curr_row, 4,
                         self.stats[ltr_nr][bwl_nr]['distinct_types']['cum_percent_raw_txt_in_base_list'] * 100,
                         wb.percent)

                wb.curr_row += 1
            ws.write_row(wb.curr_row, 1, (
                'missed:', self.raw_txt_to_base_list[ltr_nr][bwl_nr]['distinct_types']['count_txt_not_in_word_list']))
            wb.curr_row += 2
        wb.curr_row += 1

        #
        ws.write(wb.curr_row, 0, 'Base Word List Families Count in Raw Text')

        wb.curr_row += 1
        for ltr_nr in self.raw_txt:
            ws.write(wb.curr_row, 0, 'Raw Text ' + str(ltr_nr))
            ws.write_row(wb.curr_row, 1, ('in', 'not in', '%in'), wb.align_mid)
            wb.curr_row += 1
            for bwl_nr in self.base_list_to_raw_txt:
                ws.write_row(wb.curr_row, 0, ('Word List ' + str(bwl_nr) + ' Families',
                                              self.base_list_to_raw_txt[bwl_nr][ltr_nr]['count_word_list_in_txt'],
                                              self.base_list_to_raw_txt[bwl_nr][ltr_nr]['count_word_list_not_in_txt']))
                ws.write(wb.curr_row, 3, self.stats[ltr_nr][bwl_nr]['raw_txt']['percent_base_list_in_raw_txt'] * 100,
                         wb.percent)
                wb.curr_row += 1
            wb.curr_row += 1

        # create worksheets for tokens in/not in bwl and families in/not in raw text
        for rtl_nr in self.raw_txt:
            for bwl_nr in self.print_output:
                ws_name = str(rtl_nr) + '_' + str(bwl_nr)

                wb.write_print_output(ws_name, rtl_nr, bwl_nr, 'Raw Text Tokens in Base Word List ' + str(bwl_nr),
                                      'raw_txt_in_word_list', self.print_output)

                wb.write_print_output(ws_name, rtl_nr, bwl_nr, 'Raw Text Tokens not in Base Word List ' + str(bwl_nr),
                                      'raw_txt_not_in_word_list', self.print_output)

                wb.write_print_output(ws_name, rtl_nr, bwl_nr, 'Base Word List ' + str(bwl_nr) + ' in Raw Text',
                                      'word_list_in_raw_txt', self.print_output)

                wb.write_print_output(ws_name, rtl_nr, bwl_nr, 'Base Word List ' + str(bwl_nr) + ' not in Raw Text',
                                      'word_list_not_in_raw_txt', self.print_output)

        wb.close()


new_language_stats = LanguageStats()

new_language_stats.read_config()
new_language_stats.read_raw_txt()
new_language_stats.read_base_word_list()
new_language_stats.get_sorted_bwl()

new_language_stats.get_raw_txt_distinct_types()
new_language_stats.get_raw_txt_in_word_list('raw_txt')
new_language_stats.get_raw_txt_in_word_list('distinct_types')
new_language_stats.get_word_list_in_raw_text()

new_language_stats.get_stats()

new_language_stats.prepare_raw_txt_print('raw_txt_in_word_list')
new_language_stats.prepare_raw_txt_print('raw_txt_not_in_word_list')
new_language_stats.prepare_base_list_print('word_list_in_raw_txt')
new_language_stats.prepare_base_list_print('word_list_not_in_raw_txt')

new_language_stats.write_excel_file()

# Ausgabe in Zeile 25 hinzufügen
