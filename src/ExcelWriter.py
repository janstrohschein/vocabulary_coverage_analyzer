from xlsxwriter import Workbook, worksheet


class ExcelWriter(Workbook):

    def __init__(self, path):

        super().__init__(path)
        self.curr_row = 0
        self.bold = self.add_format({'bold': True})
        self.percent = self.add_format({'num_format': '0.00"%"'})
        self.align_mid = self.add_format({'align': 'center'})

    def write_print_output(self, ws_name, ltr_nr, bwl_nr, text, key, print_output):
        if self.get_worksheet_by_name(ws_name) == None:
            ws = self.add_worksheet(ws_name)
            self.curr_row = 0
        else:
            ws = self.get_worksheet_by_name(ws_name)

        ws.write(self.curr_row, 0, text, self.bold)
        self.curr_row += 1
        for row in print_output[bwl_nr][ltr_nr][key]:
            ws.write(self.curr_row, 0, row)
            self.curr_row += 1
        self.curr_row += 3
