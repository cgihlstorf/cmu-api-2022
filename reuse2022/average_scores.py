def is_same_file(pres_line, abs_line):
    pres = pres_line.split("->")[0]
    abs = abs_line.split("->")[0]
    return abs == pres


def average_scores(present_scores:str, absent_scores:str):
    present_file = open(present_scores, 'r')
    present_lines = present_file.readlines()
    absent_file = open(absent_scores, 'r')
    absent_lines = absent_file.readlines()
    scores_sum_pres = 0
    scores_sum_abs = 0
    number_of_scores = 0

    for pres_line, abs_line in zip(present_lines[0:12000], absent_lines[0:12000]):
        if abs_line.strip() == "SKIP":
            continue
        else:
            number_of_scores = number_of_scores + 1
            assert is_same_file(pres_line, abs_line)
            score_pres = float(pres_line.split("->")[1])
            score_abs = float(abs_line.split("->")[1])
            # if abs(score_pres - score_abs) >= 0.01 and abs(score_pres - score_abs) <= 0.1:
            #     print("Present:", pres_line, "Absent:", abs_line)
            scores_sum_pres = scores_sum_pres + score_pres
            scores_sum_abs = scores_sum_abs + score_abs

    return "Docstring present: " + str('%.2f' %(scores_sum_pres/number_of_scores)) + '\n' + "Docstring absent: " + str('%.2f' %(scores_sum_abs/number_of_scores) + '\n' + "Total functions scored: " + str(number_of_scores))

pres_scores = "../results_codegen_ALL_with_context/docstring_present_scores.txt"
abs_scores = "../results_codegen_ALL_with_context/docstring_absent_scores.txt"
print(average_scores(pres_scores, abs_scores))
# print("Docstring included:", '%.2f' % average_scores("../results_codegen/docstring_present_scores.txt"))
# print("Docstring not included:", '%.2f' % average_scores("../results_codegen/docstring_absent_scores.txt"))


