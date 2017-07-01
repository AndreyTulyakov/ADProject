#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class MConverter:

    def __process_lines(lines):
        started_content = False
        result = []

        for line in lines:
            if started_content == False and line.startswith('kp'):
                started_content = True
                start_data_index = line.find('[')
                if start_data_index > -1:
                    line = line[start_data_index + 1:]

            if started_content:

                rrr_index = line.rfind('%')
                if rrr_index > -1:
                    line = line[:rrr_index]

                rrr_index = line.rfind(']')
                if rrr_index > -1:
                    line = line[:rrr_index]

                line = line.strip()

                line = line.replace('     ', ' ')
                line = line.replace('    ', ' ')
                line = line.replace('   ', ' ')
                line = line.replace('  ', ' ')
                line = line.replace(' ', ',\t')

                result.append(line)
        return result

    def convert_m_to_csv(input_filename, output_filename):
        with open(input_filename) as current_file:
            with open(output_filename, 'w') as output_file:
                table_header = 'CH1,CH2,CH3,CH4,CH5,CH6,CH7,CH8,CH9,Time\n'
                output_file.write(table_header)

                lines = current_file.readlines()
                lines = MConverter.__process_lines(lines)

                for line in lines:
                    output_file.write(line + '\n')