import json
import pandas as pd
import plotly.graph_objects as go
from medcat.cdb import CDB
from medcat.cat import CAT


class MedcatTrainer_export(object):
    """
    Class to analyse JSON format MedCATtrainer exports
    """

    def __init__(self, mct_export_path, model_pack_path=None):
        """
        :param mct_export_path: List of paths to MedCATtrainer exports
        :param model_pack_path: Path to medcat modelpack
        """

        if model_pack_path:
            self.cat = CAT.load_model_pack(model_pack_path)

        self.mct_export = self._load_mct_exports(mct_export_path)
        self.project_names = [p['name'] for p in self.mct_export['projects']]
        self.document_names = [doc['name'] for doc in p['documents'] for p in self.mct_exports['projects']]
        self.annotations = []
        for proj in self.mct_exports['projects']:
            for doc in proj['documents']:
                for anns in doc['annotations']:
                    output = dict()
                    output['project'] = proj['name']
                    output['document_name'] = doc['name']
                    meta_anns_dict = dict()
                    for meta_ann in anns['meta_anns'].items():
                        meta_anns_dict.update({meta_ann[0]: meta_ann[1]['value']})
                    anns.pop('meta_anns')
                    output.update(anns)
                    output.update(meta_anns_dict)
                    self.annotations.append(output)

    def _load_mct_exports(self, list_of_paths_to_mct_exports):
        """
        Loads a list of multiple MCT exports
        :param list_of_paths_to_mct_exports: list of mct exports
        :return: single json format object
        """
        mct_projects = []
        for mct_project in list_of_paths_to_mct_exports:
            with open(mct_project, 'r') as jsonfile:
                mct_projects.extend(json.load(jsonfile)['projects'])
        mct_proj_exports = {'projects': mct_projects}
        return mct_proj_exports

    def concept_summary(self):
        """
        Summary of only correctly annotated concepts from a mct export
        :return: DataFrame summary of annotations.
        """
        concept_output = pd.DataFrame(self.annotations)
        concept_output['last_modified'] = pd.to_datetime(concept_output['last_modified'])
        concept_output = concept_output[concept_output['validated'] == True]
        concept_output = concept_output[(concept_output['correct'] == True) | (concept_output['alternative'] == True)]
        if self.cat:
            concept_output.insert(5, 'concept_name', concept_output['cui'].map(self.cat.cdb.cui2preferred_name))
            concept_count = concept_output.groupby(['concept_name', 'cui']).agg({'value': set, 'id': 'count'})
        else:
            concept_count = concept_output.groupby(['cui']).agg({'value': set, 'id': 'count'})
        concept_count_df = pd.DataFrame(concept_count).reset_index(drop=False)
        concept_count_df['variations'] = concept_count_df['value'].apply(lambda x: len(x))
        concept_count_df.rename({'id': 'concept_count'}, axis=1, inplace=True)
        concept_count_df = concept_count_df.sort_values(by='concept_count', ascending=False).reset_index(drop=True)
        concept_count_df['count_variations_ratio'] = round(concept_count_df['concept_count']/concept_count_df['variations'], 3)
        return concept_count_df

    def user_stats(self):
        concept_output = pd.DataFrame(self.annotations)



    def get_all_children(self, terminology, pt2ch):
        """
        Get all children concepts from a specified terminology

        :param terminology:
        :param pt2ch:
        :return:
        """
        result = []
        stack = [terminology]
        while len(stack) != 0:
            # remove last element from stack
            current_snomed = stack.pop()
            current_snomed_parent = pt2ch.get(current_snomed, [])
            stack.extend(current_snomed_parent)
            result.append(current_snomed)
        result = list(set(result))
        return result



