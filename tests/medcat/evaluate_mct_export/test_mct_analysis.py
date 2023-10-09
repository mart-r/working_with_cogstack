import os
import sys

import pandas as pd

import unittest


_FILE_DIR = os.path.dirname(__file__)

# because this project isn't (at least of of writing this)
# set up as a python project, there are no __init__.py
# files in each folder
# as such, in order to gain access to the relevant module,
# I'll need to add the path manually
_WWC_BASE_FOLDE = os.path.join(_FILE_DIR, "..", "..", "..")
MEDCAT_EVAL_MCT_EXPORT_FOLDER = os.path.abspath(os.path.join(_WWC_BASE_FOLDE, "medcat", "evaluate_mct_export"))
sys.path.append(MEDCAT_EVAL_MCT_EXPORT_FOLDER)
# and now we can import from mct_analysis
from mct_analysis import MedcatTrainer_export

# add path to MCT export
RESOURCE_DIR = os.path.abspath(os.path.join(_FILE_DIR, "..", "resources"))
MCT_EXPORT_JSON_PATH = os.path.join(RESOURCE_DIR, "MCT_export_example.json")


class MCTExportInitTests(unittest.TestCase):

    def test_can_init(self):
        inst = MedcatTrainer_export([MCT_EXPORT_JSON_PATH, ], None)
        self.assertIsInstance(inst, MedcatTrainer_export)


class BaseMCTExportTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.export = MedcatTrainer_export([MCT_EXPORT_JSON_PATH, ], None)

    def assertNonEmptyDataframe(self, df):
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)


class MCTExportBasicTests(BaseMCTExportTests):

    def test_can_get_annotations(self):
        annotation_df = self.export.annotation_df()
        self.assertNonEmptyDataframe(annotation_df)

    def test_can_get_summary(self):
        summary_df = self.export.concept_summary()
        self.assertNonEmptyDataframe(summary_df)

    def test_can_get_user_stats(self):
        users_stats = self.export.user_stats()
        self.assertNonEmptyDataframe(users_stats)

    def test_can_rename_meta_anns_empty_no_change(self):
        ann_df1 = self.export.annotation_df()
        self.export.rename_meta_anns()
        ann_df2 = self.export.annotation_df()
        self.assertTrue(all(ann_df1 == ann_df2))

    # these would need a CAT instance
    # def test_can_full_annotation_df(self):
    #     full_ann_df = self.export.full_annotation_df()
    #     self.assertNonEmptyDataframe(full_ann_df)

    # def test_can_meta_anns_concept_summary(self):
    #     meta_anns_summary_df = self.export.meta_anns_concept_summary()
    #     self.assertNonEmptyDataframe(meta_anns_summary_df)


class MCTExportUsageTests(BaseMCTExportTests):

    def assertDataFrameHasRowsColumns(self, df,
                                      exp_rows: int,
                                      exp_columns: int):
        self.assertEqual(len(df.index), exp_rows)
        self.assertEqual(len(df.columns), exp_columns)

    def test_annotations_has_correct_rows_columns(self,
                                                  exp_rows=362,
                                                  exp_columns=18):
        ann_df = self.export.annotation_df()
        self.assertDataFrameHasRowsColumns(ann_df, exp_rows, exp_columns)

    def test_summary_has_correct_rows_columns(self,
                                              exp_rows=197,
                                              exp_columns=5):
        summary_df = self.export.concept_summary()
        self.assertDataFrameHasRowsColumns(summary_df, exp_rows, exp_columns)

    def test_cuser_stats_has_correct_rows_columns(self,
                                                  exp_rows=1,
                                                  exp_columns=2):
        users_stats = self.export.user_stats()
        self.assertDataFrameHasRowsColumns(users_stats, exp_rows, exp_columns)

    def test_cuser_stats_has_correct_user(self, expected="mart"):
        unique_users = self.export.user_stats()["user"].unique().tolist()
        self.assertEqual(len(unique_users), 1)
        self.assertEqual(unique_users[0], expected)