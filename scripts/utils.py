# -*- coding: utf-8 -*-
import os
from collections import OrderedDict

from git import Repo

# Languages with insufficient translation data are excluded
# TODO: Automate with exclusion criteria.
AVOID_LANGUAGES = {'cu', 'kkj', 'nds', 'prg', 'tk', 'vai', 'vai-Latn', 'vai-Vaii', 'vo'}


def get_raw_data():
    cldr_dates_full_url = "https://github.com/unicode-cldr/cldr-dates-full.git"
    cldr_core_url = "https://github.com/unicode-cldr/cldr-core.git"
    cldr_rbnf_url = "https://github.com/unicode-cldr/cldr-rbnf.git"
    raw_data_directory = "../raw_data"
    cldr_dates_full_dir = "../raw_data/cldr_dates_full/"
    cldr_core_dir = "../raw_data/cldr_core/"
    cldr_rbnf_dir = "../raw_data/cldr_rbnf/"
    if not os.path.isdir(raw_data_directory):
        os.mkdir(raw_data_directory)
        Repo.clone_from(cldr_dates_full_url, cldr_dates_full_dir, branch='master')
        Repo.clone_from(cldr_core_url, cldr_core_dir, branch='master')
        Repo.clone_from(cldr_rbnf_url, cldr_rbnf_dir, branch='master')


def get_dict_difference(parent_dict, child_dict):
    difference_dict = OrderedDict()
    for key, child_value in child_dict.items():
        parent_value = parent_dict.get(key)
        child_specific_value = None
        if not parent_value:
            child_specific_value = child_value
        elif isinstance(child_value, list):
            child_specific_value = list(
                set(map(str.lower, map(str, child_value))) -
                set(map(str.lower, map(str, parent_value)))
            )
        elif isinstance(child_value, dict):
            child_specific_value = get_dict_difference(parent_value, child_value)
        elif child_value.lower() != parent_value.lower():
            child_specific_value = child_value
        if child_specific_value:
            difference_dict[key] = child_specific_value
    return difference_dict


def combine_dicts(primary_dict, supplementary_dict):
    if not primary_dict:
        return supplementary_dict
    elif not supplementary_dict:
        return primary_dict
    combined_dict = OrderedDict()
    filter_locales(primary_dict, supplementary_dict)
    for key, value in primary_dict.items():
        if key in supplementary_dict:
            if isinstance(value, list):
                combined_dict[key] = value + supplementary_dict[key]
            elif isinstance(value, dict):
                combined_dict[key] = combine_dicts(value, supplementary_dict[key])
            else:
                combined_dict[key] = supplementary_dict[key]
        else:
            combined_dict[key] = primary_dict[key]
    remaining_keys = [key for key in supplementary_dict.keys() if key not in primary_dict.keys()]
    for key in remaining_keys:
        combined_dict[key] = supplementary_dict[key]
    return combined_dict


def filter_locales(primary_dict, supplementary_dict):
    if not primary_dict.get('locale_specific'):
        return
    for locale, locale_data in primary_dict['locale_specific'].items():
        diff = get_dict_difference(supplementary_dict, locale_data)
        primary_dict['locale_specific'][locale] = diff
        if diff.keys() == ['name']:
            del primary_dict['locale_specific'][locale]


def language_from_filename(filename):
    return filename.split('.')[0]
