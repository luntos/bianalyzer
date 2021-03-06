# -*- coding: utf-8 -*-

from .biclustering import AbstractBiclustering
from ..errors import InvalidArgumentError
from .bicluster_analysis import find_biclusters
from ..helpers import calculate_row_density


class KeywordTextBicluster:
    def __init__(self, keyword_rows, text_columns, relevance_matrix, density, g_value):
        self.keyword_rows = keyword_rows
        self.text_columns = text_columns
        self.relevance_matrix = relevance_matrix
        self.density = density
        self.texts_number = len(text_columns)
        self.g_value = g_value


def get_keyword_text_biclusters(relevance_matrix, biclustering_algorithm,
                                biclusters_number=50, lambda0=0.0):
    if not issubclass(biclustering_algorithm, AbstractBiclustering):
        raise InvalidArgumentError("biclustering_algorithm", biclustering_algorithm,
                                   "Must be a subclass of AbstractBiclustering")

    texts = relevance_matrix.texts
    keywords = relevance_matrix.keywords
    matrix = relevance_matrix.matrix
    biclustering_result = find_biclusters(matrix, biclustering_algorithm, lambda0, biclusters_number)

    keyword_text_biclusters = []
    for bicluster in biclustering_result.biclusters:
        # print '----------------------------'
        # print 'new bicluster'

        keyword_rows = []
        first_set = ''
        for row in bicluster.row_set:
            first_set += '%s, ' % keywords[row]
            keyword_rows.append(keywords[row])
        # print first_set

        text_columns = []
        # second_set = ''
        for col in bicluster.column_set:
            # second_set += '%s, ' % texts[col].title
            # text_columns.append(texts[col].title)
            text_columns.append(col)
        # print second_set

        # print 'density: %s' % bicluster.density
        # print 'row set len: %s' % len(bicluster.row_set)
        # print 'column set len: %s' % len(bicluster.column_set)
        # print 'g-value: %s' % round(bicluster.g_value, 2)

        bicluster_matrix = []
        for (i, row) in enumerate(bicluster.row_set):
            bicluster_matrix.append([])
            s = ''
            for col in bicluster.column_set:
                s += '%6s' % round(matrix[row][col], 2)
                bicluster_matrix[i].append(round(matrix[row][col], 2))
            # print s

        relative_density = bicluster.density / relevance_matrix.max_relevance_score
        keyword_text_biclusters.append(KeywordTextBicluster(keyword_rows, text_columns, bicluster_matrix,
                                                            round(relative_density, 2), round(bicluster.g_value, 2)))

    biclustering_result.biclusters = keyword_text_biclusters
    return biclustering_result


def save_keyword_text_biclusters(biclustering_result, file, min_density=0.0):
    file.write('Residuals: %s\n\n' % biclustering_result.residuals_portion)
    for keyword_text_bicluster in biclustering_result.biclusters:
        if keyword_text_bicluster.density <= min_density:
            continue
        matrix = keyword_text_bicluster.relevance_matrix
        header = '%30s\tDensity' % 'Keyword'
        file.write(header + '\n')
        for i, row in enumerate(matrix):
            s = '%30s\t%.2f' % (keyword_text_bicluster.keyword_rows[i], calculate_row_density(i,matrix))
            file.write(s + '\n')
        file.write('number of texts in the bicluster: %s' % len(keyword_text_bicluster.text_columns))
        file.write('bicluster density: %.2f\n' % keyword_text_bicluster.density)
        file.write('bicluster g-value: %.2f\n' % keyword_text_bicluster.g_value)
        file.write('-------------------------------------------\n\n')