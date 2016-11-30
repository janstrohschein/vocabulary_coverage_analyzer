# -*- coding: utf-8 -*-
import codecs
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
            self.raw_txt[list_nr]['count_raw_txt_tokens'] = 0
            with open(path, 'r') as in_file:
                self.raw_txt[list_nr]['data'] = []
                for line in in_file:
                    for word in re.findall(r"[\w]+", line):
                        self.raw_txt[list_nr]['data'].append(word.lower())
                        self.raw_txt[list_nr]['count_raw_txt_tokens'] += 1
            self.raw_txt[list_nr]['data'] = sorted(self.raw_txt[list_nr]['data'], key=str.lower)


    def read_base_word_list(self):
        for list_nr, path in self.config['Input Base Word List Paths'].items():
            self.base_word_list[list_nr] = {}
            self.base_word_list[list_nr]['data'] = []
            self.base_word_list[list_nr]['base_word_list_path'] = path
            self.base_word_list[list_nr]['count_base_word_list_families'] = 0
            self.base_word_list[list_nr]['count_base_word_list_tokens'] = 0

            try:
                with open(path, 'r') as in_file:
                    for line in in_file:
                        try:
                            if not line.startswith('\t'):
                                self.base_word_list[list_nr]['data'].append([line.strip()])
                                self.base_word_list[list_nr]['count_base_word_list_families'] += 1
                            else:
                                self.base_word_list[list_nr]['data'][len(self.base_word_list[list_nr]['data'])-1].append(line.strip())

                            self.base_word_list[list_nr]['count_base_word_list_tokens'] += 1
                        except:
                            print('Base Word List ' + str(list_nr) + ': Not all Lines could be processed')
            except:
                print('Base Word List ' + str(list_nr) + ': File could not be opened')


    def get_raw_txt_in_word_list(self):

        for rtl_nr in self.raw_txt:
            self.raw_txt_to_base_list[rtl_nr] = {}

            for bwl_nr in self.base_word_list:
                self.raw_txt_to_base_list[rtl_nr][bwl_nr] = {}
                self.raw_txt_to_base_list[rtl_nr][bwl_nr]['count_txt_in_word_list'] = 0
                self.raw_txt_to_base_list[rtl_nr][bwl_nr]['count_txt_not_in_word_list'] = 0
                self.raw_txt_to_base_list[rtl_nr][bwl_nr]['raw_txt_in_word_list'] = []
                self.raw_txt_to_base_list[rtl_nr][bwl_nr]['raw_txt_not_in_word_list']  = []

            for word in self.raw_txt[rtl_nr]['data']:
                word_found = False
                for bwl_nr in self.base_word_list:
                    if word_found == False:
                        for family in self.base_word_list[bwl_nr]['data']:
                            if word.upper() in family:
                                word_found = True
                                self.raw_txt_to_base_list[rtl_nr][bwl_nr]['count_txt_in_word_list'] += 1
                                self.raw_txt_to_base_list[rtl_nr][bwl_nr]['raw_txt_in_word_list'].append(word)
                                break
                        if not word_found:
                            self.raw_txt_to_base_list[rtl_nr][bwl_nr]['count_txt_not_in_word_list'] += 1
                            self.raw_txt_to_base_list[rtl_nr][bwl_nr]['raw_txt_not_in_word_list'].append(word)


    def get_word_list_in_raw_text(self):
        for bwl_nr in self.base_word_list:
            self.base_list_to_raw_txt[bwl_nr] = {}

            for rtl_nr in self.raw_txt:
                self.base_list_to_raw_txt[bwl_nr][rtl_nr] = {}
                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['count_word_list_in_txt'] = 0
                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['count_word_list_not_in_txt'] = 0
                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['word_list_in_raw_txt'] = []
                self.base_list_to_raw_txt[bwl_nr][rtl_nr]['word_list_not_in_raw_txt'] = []

                for family in self.base_word_list[bwl_nr]['data']:
                    family_found = False
                    for token in self.raw_txt[rtl_nr]['distinct_types']:
                        if token.upper() in family:
                            family_found = True
                            self.base_list_to_raw_txt[bwl_nr][rtl_nr]['count_word_list_in_txt'] += 1
                            self.base_list_to_raw_txt[bwl_nr][rtl_nr]['word_list_in_raw_txt'].append(family)
                            break
                    if not family_found:
                        self.base_list_to_raw_txt[bwl_nr][rtl_nr]['count_word_list_not_in_txt'] += 1
                        self.base_list_to_raw_txt[bwl_nr][rtl_nr]['word_list_not_in_raw_txt'].append(family)


    def get_raw_txt_distinct_types(self):
        for list_nr in self.raw_txt:
            self.raw_txt[list_nr]['distinct_types'] = []
            distinct_types = 0
            old_word = ''
            for word in self.raw_txt[list_nr]['data']:
                if word != old_word:
                    old_word = word
                    self.raw_txt[list_nr]['distinct_types'].append(word)
                    distinct_types += 1
            self.raw_txt[list_nr]['count_raw_txt_types'] = distinct_types


    def get_stats(self):
        for rtl_nr in self.raw_txt:
            cum_percent = 0
            self.stats[rtl_nr] = OrderedDict()

            for bwl_nr in self.base_word_list:
                self.stats[rtl_nr][bwl_nr] = {}
                self.stats[rtl_nr][bwl_nr]['percent_raw_txt_in_base_list'] = self.raw_txt_to_base_list[rtl_nr][bwl_nr]['count_txt_in_word_list'] / self.raw_txt[rtl_nr]['count_raw_txt_tokens']
                cum_percent += self.stats[rtl_nr][bwl_nr]['percent_raw_txt_in_base_list']
                self.stats[rtl_nr][bwl_nr]['cum_percent_raw_txt_in_base_list'] = cum_percent
                self.stats[rtl_nr][bwl_nr]['percent_base_list_in_raw_txt'] = self.base_list_to_raw_txt[bwl_nr][rtl_nr]['count_word_list_in_txt'] / self.base_word_list[bwl_nr]['count_base_word_list_families']


    def prepare_raw_txt_print(self, input):
        for bwl_nr in self.base_word_list:
            if bwl_nr not in self.print_output:
                self.print_output[bwl_nr] = {}

            for rtl_nr in self.raw_txt_to_base_list:
                if rtl_nr not in self.print_output[bwl_nr]:
                    self.print_output[bwl_nr][rtl_nr] = {}

        # for rtl_nr in self.raw_txt_to_base_list:
        #     if rtl_nr not in self.print_output:
        #         self.print_output[rtl_nr] = {}
        #
        #     for bwl_nr in self.raw_txt_to_base_list[rtl_nr]:
        #         if bwl_nr not in self.print_output[rtl_nr]:
        #             self.print_output[rtl_nr][bwl_nr] = {}

                self.print_output[bwl_nr][rtl_nr][input] = []
                old_word = ''
                word_count = 0
                for i, word in enumerate(self.raw_txt_to_base_list[rtl_nr][bwl_nr][input]):
                    if word != old_word:
                        if word_count > 0:
                            self.print_output[bwl_nr][rtl_nr][input].append((str(word_count) + 'x ' + old_word + '\n'))
                        old_word = word
                        word_count = 1
                    else:
                        word_count += 1

                    if len(self.raw_txt_to_base_list[rtl_nr][bwl_nr][input]) -1 == i:
                        self.print_output[bwl_nr][rtl_nr][input].append((str(word_count) + 'x ' + old_word + '\n'))


    def prepare_base_list_print(self, input, complete_families = False):

        for bwl_nr in self.base_list_to_raw_txt:
            if bwl_nr not in self.print_output:
                self.print_output[bwl_nr] = {}

            for ltr_nr in self.base_list_to_raw_txt[bwl_nr]:
                if ltr_nr not in self.print_output[bwl_nr]:
                    self.print_output[bwl_nr][ltr_nr] = {}

                self.print_output[bwl_nr][ltr_nr][input] = []

                if complete_families == True:
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


    def write_excel_file(self, path):

        wb = ExcelWriter(path)

        ws = wb.add_worksheet('Overview')
        ws.set_column(0,0,20)

        # Input File Paths
        ws.write(0, 0, 'Input File Paths', wb.bold)
        wb.curr_row = 1

        for rtl_nr in self.raw_txt:
            ws.write_row(wb.curr_row, 0, ('Raw Text File ' + str(rtl_nr), self.raw_txt[rtl_nr]['raw_txt_path']))
            wb.curr_row += 1

        for bwl_nr in self.base_word_list:
            ws.write_row(wb.curr_row, 0, ('Base Word List ' + str(bwl_nr),\
                           self.base_word_list[bwl_nr]['base_word_list_path'] )
                         )
            wb.curr_row += 1

        # Input File Overview
        for ltr_nr in self.raw_txt:
            ws.write(wb.curr_row + 1,0, 'Overview', wb.bold)
            ws.write_row(wb.curr_row + 2, 0, ('Count Raw Text', 'Tokens:', self.raw_txt[ltr_nr]['count_raw_txt_tokens'],\
                                           'Types:', self.raw_txt[ltr_nr]['count_raw_txt_types']))
            wb.curr_row +=2

        for bwl_nr in self.base_word_list:
            ws.write_row(wb.curr_row,0, ('Count Base Word List'  + str(bwl_nr), 'Families:', \
                                      self.base_word_list[bwl_nr]['count_base_word_list_families'], 'Tokens:',\
                                      self.base_word_list[bwl_nr]['count_base_word_list_tokens']))
            wb.curr_row += 1

        # Analysis
        ws.write(wb.curr_row + 1, 0, 'Analysis', wb.bold)
        ws.write(wb.curr_row + 2, 0, 'Raw Text Token Count in Base Word List')
        ws.write_row(wb.curr_row + 3, 1, ('in', 'not in', '%in', '%in cum'), wb.align_mid)
        wb.curr_row += 4

        for ltr_nr in self.raw_txt_to_base_list:
            for bwl_nr in self.raw_txt_to_base_list[ltr_nr]:
                ws.write_row(wb.curr_row, 0, ('Word List ' + str(bwl_nr) + ' Tokens', \
                                           self.raw_txt_to_base_list[ltr_nr][bwl_nr]['count_txt_in_word_list'],\
                                           self.raw_txt_to_base_list[ltr_nr][bwl_nr]['count_txt_not_in_word_list']))
                ws.write(wb.curr_row, 3, self.stats[ltr_nr][bwl_nr]['percent_raw_txt_in_base_list'] * 100, wb.percent)
                ws.write(wb.curr_row, 4, self.stats[ltr_nr][bwl_nr]['cum_percent_raw_txt_in_base_list'] * 100, wb.percent)

                wb.curr_row += 1

        ws.write(wb.curr_row + 1, 0, 'Base Word List Families Count in Raw Text')
        ws.write_row(wb.curr_row + 2, 1, ('in', 'not in', '%in'), wb.align_mid)

        wb.curr_row += 3
        for bwl_nr in self.base_list_to_raw_txt:
            for ltr_nr in self.base_list_to_raw_txt[bwl_nr]:
                ws.write_row(wb.curr_row, 0, ('Word List ' + str(bwl_nr) + ' Families',\
                                           self.base_list_to_raw_txt[bwl_nr][ltr_nr]['count_word_list_in_txt'],\
                                           self.base_list_to_raw_txt[bwl_nr][ltr_nr]['count_word_list_not_in_txt']))
                ws.write(wb.curr_row, 3, self.stats[ltr_nr][bwl_nr]['percent_base_list_in_raw_txt'] * 100, wb.percent)
                wb.curr_row += 1

        for bwl_nr in self.print_output:
            ws_name = 'BWL' + str(bwl_nr)

            wb.write_print_output(ws_name, bwl_nr, 'Raw Text Tokens in Base Word List ' + str(bwl_nr),\
                                  'raw_txt_in_word_list', self.print_output)

            wb.write_print_output(ws_name, bwl_nr, 'Raw Text Tokens not in Base Word List ' + str(bwl_nr),\
                                  'raw_txt_not_in_word_list', self.print_output)

            wb.write_print_output(ws_name, bwl_nr, 'Base Word List ' + str(bwl_nr) + ' in Raw Text',\
                                  'word_list_in_raw_txt', self.print_output)

            wb.write_print_output(ws_name, bwl_nr, 'Base Word List ' + str(bwl_nr) + ' not in Raw Text',\
                                  'word_list_not_in_raw_txt', self.print_output)

        wb.close()




new_language_stats = LanguageStats()

new_language_stats.read_config()
new_language_stats.read_raw_txt()
new_language_stats.read_base_word_list()


new_language_stats.get_raw_txt_distinct_types()
new_language_stats.get_raw_txt_in_word_list()
new_language_stats.get_word_list_in_raw_text()
new_language_stats.get_stats()

new_language_stats.prepare_raw_txt_print('raw_txt_in_word_list')
new_language_stats.prepare_raw_txt_print('raw_txt_not_in_word_list')
new_language_stats.prepare_base_list_print('word_list_in_raw_txt')
new_language_stats.prepare_base_list_print('word_list_not_in_raw_txt')

#new_language_stats.write_txt_file(r"C:\Users\jan\Downloads\Matze Output.txt")
new_language_stats.write_excel_file(r"C:\Users\jan\Downloads\Matze Output.xlsx")

# Raw text -> Base word list noch um Types ergänzen
# Ausgabe in Zeile 25 hinzufügen