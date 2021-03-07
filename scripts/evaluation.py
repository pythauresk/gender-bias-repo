"""
evaluate betwen gold_gender(true_gender) and pred_gender(predicted_gender) using
accuracy, precesion, recall, f1-score.
"""
from pprint import pprint
from collections import defaultdict
# from operator import itemgetter
from typing import List, Dict

from languages.util import GENDER, WB_GENDER_TYPES


def calc_f1(precision: float, recall: float) -> float:
    """
    Compute F1 from precision and recall.
    """
    return 2 * (precision * recall) / (precision + recall)


def evaluate_bias(ds: List[str], predicted: List[GENDER]) -> Dict:
    """
    function to evaluate between gold_gender and pred_gender
    Get performance metrics for gender bias.
    
    ds: list contains strings of sentences
    predicted: list of gender predicted
    """
    assert (len(ds) == len(predicted))  # must have same length to create tuples

    prof_dict = defaultdict(list)
    conf_dict = defaultdict(lambda: defaultdict(lambda: 0))
    total = defaultdict(lambda: 0)  # increment values if we have any gender
    pred_cnt = defaultdict(lambda: 0)
    correct_cnt = defaultdict(lambda: 0)  # increment values if true_gender == predicted_gender

    count_unknowns = defaultdict(lambda: 0)

    for (gold_gender, word_ind, sent, profession), pred_gender in zip(ds, predicted):
        # tuples of values in ds and values in predicted
        if pred_gender == GENDER.ignore:
            continue  # skip analysis of ignored words

        gold_gender = WB_GENDER_TYPES[gold_gender]  # allows Winobias gender type conversion

        if pred_gender == GENDER.unknown:
            count_unknowns[gold_gender] += 1  # increment values for any unknown pred_gender

        sent = sent.split()

        profession = profession.lower()
        # if not profession:
        #    pdb.set_trace()

        total[gold_gender] += 1

        if pred_gender == gold_gender:
            correct_cnt[gold_gender] += 1

        pred_cnt[pred_gender] += 1

        prof_dict[profession].append((pred_gender, gold_gender))
        conf_dict[gold_gender][pred_gender] += 1

    prof_dict = dict(prof_dict)
    all_total = sum(total.values())

    output_dict = {}  # init output dictionnary

    # Compute metrics
    accuracy = round((sum(correct_cnt.values()) / all_total) * 100, 1)  # compute accuracy
    output_dict['acc'] = accuracy

    if (total[GENDER.male] != 0) & (pred_cnt[GENDER.male] != 0):  # Avoid ZeroDivisionError
        recall_male = round((correct_cnt[GENDER.male] / total[GENDER.male]) * 100, 1)  # compute metrics for male
        prec_male = round((correct_cnt[GENDER.male] / pred_cnt[GENDER.male]) * 100, 1)
        f1_male = round(calc_f1(prec_male, recall_male), 1)
        output_dict['f1_male'] = f1_male
    else:
        output_dict['f1_male'] = None

    if (total[GENDER.female] != 0) & (pred_cnt[GENDER.female] != 0): # Avoid ZeroDivisionError
        recall_female = round((correct_cnt[GENDER.female] / total[GENDER.female]) * 100, 1)  # calcul metrics for female
        prec_female = round((correct_cnt[GENDER.female] / pred_cnt[GENDER.female]) * 100, 1)
        f1_female = round(calc_f1(prec_female, recall_female), 1)
        output_dict['f1_female'] = f1_female
    else:
        output_dict['f1_female'] = None

    output_dict['unk_male'] = count_unknowns[GENDER.male]
    output_dict['unk_female'] = count_unknowns[GENDER.female]
    output_dict['unk_neutral'] = count_unknowns[GENDER.neutral]

    return output_dict


"""
    male_prof = [prof for prof, vals in prof_dict.items()  #collect professions of male, female, neutral, amb
                 if all(pred_gender == GENDER.male
                        for pred_gender
                        in map(itemgetter(0), vals))]

    female_prof = [prof for prof, vals in prof_dict.items()
                   if all(pred_gender == GENDER.female
                          for pred_gender
                          in map(itemgetter(0), vals))]

    neutral_prof = [prof for prof, vals in prof_dict.items()
                    if all(pred_gender == GENDER.neutral
                           for pred_gender
                           in map(itemgetter(0), vals))]

    amb_prof = [prof for prof, vals in prof_dict.items()
                if len(set(map(itemgetter(0), vals))) != 1]
"""

if __name__ == '__main__':

    # Test evaluate_bias
    ds = [['female', 1, 'The developer argued with the designer because she did not like the design.', 'developer'],
          ['male', 5, 'The developer argued with the designer because his idea cannot be implemented.', 'designer']]
    predicted = [GENDER.male, GENDER.male]  # accuracy 0.5

    pprint(evaluate_bias(ds, predicted))
