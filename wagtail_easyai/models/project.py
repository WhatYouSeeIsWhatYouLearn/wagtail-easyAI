import pandas as pd
import datetime as dt
import time
import os
import shutil
import joblib

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.documents.models import Document

from generic_chooser.widgets import AdminChooser

from wagtail_easyai.blocks import ml as ml_blocks

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from tpot import TPOTClassifier, TPOTRegressor


def validate_proportion(value):
    if value >= 1 or value <= 0:
        raise ValidationError(
                f"{value} is not a proportion (between 0 and 1)",
                params={"value": value}
                )


class MLProject(models.Model):
    title = models.CharField(max_length=255)

    # the data
    train_x_data = models.ForeignKey(
            "wagtaildocs.Document",
            null=True,
            on_delete=models.SET_NULL,
            related_name="mltrainydata",
            )
    train_y_data = models.ForeignKey(
            "wagtaildocs.Document",
            null=True,
            on_delete=models.SET_NULL,
            related_name="mltrainxdata",
            )
    predict_data = models.ForeignKey(
            "wagtaildocs.Document",
            null=True, blank=True,
            on_delete=models.SET_NULL,
            related_name="mlpredictdata",
            )

    # the pipeline
    preprocessing = StreamField((
        ("knn_imputer", ml_blocks.KNNImputerBlock()),
        ), null=True, blank=True)

    training = StreamField((
        ("tpot_classifier", ml_blocks.TPOTClassifierBlock()),
        ), null=True)

    # train/test split
    train_proportion = models.FloatField(help_text="Proportion of training data that should be used for training (complement will be used for testing)",
            default=0.8, validators=[validate_proportion])

    # model scorer
    model_scoring_metric_choices = (
            ("accuracy", "Accuracy"),
            ("balanced_accuracy", "Balanced Accuracy"),
            )
    model_scoring_metric = models.CharField(max_length=100,
            choices=model_scoring_metric_choices,
            default="accuracy")

    # random seed (for reproducibility)
    random_seed = models.IntegerField(help_text="The random seed to use when training. Enter a value for reproducibility, or leave blank for a truly random seed",
            blank=True, null=True)

    # non-editable project fields
    is_fitted = models.BooleanField(default=False)
    # train_results = GenericField(val={})
    # latest_prediction = GenericField(val=None) 


    panels = (
        FieldPanel('title'),
        DocumentChooserPanel('train_x_data'),
        DocumentChooserPanel('train_y_data'),
        DocumentChooserPanel('predict_data'),
        StreamFieldPanel("preprocessing"),
        StreamFieldPanel("training"),
        FieldPanel("train_proportion"),
        FieldPanel("model_scoring_metric"),
        FieldPanel("random_seed")
    )

    # overrides save function to ensure that there is a directory for this
    # projects models
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        try:
            os.mkdir(self.output_dir)
        except FileExistsError:
            pass

    # overrides delete function to delete the ml models directory
    def delete(self, *args, **kwargs):
        try:
            shutil.rmtree(self.output_dir)
        except FileNotFoundError:
            pass

        super().delete(*args, **kwargs)

    @property
    def output_dir(cls):
        return os.path.join(settings.ML_MODEL_ROOT, str(cls.id))
    
    @staticmethod
    def _get_df(data, data_id, **kwargs):
        return Document.objects.get(pk=data_id).file

    @property
    def x_train_df(cls):
        return cls._get_df(cls.train_x_data, cls.train_x_data_id)

    @property
    def y_train_df(cls):
        return cls._get_df(cls.train_y_data, cls.train_y_data_id)

    @property
    def x_train_df_as_csv(cls):
        return pd.read_csv(cls.x_train_df)

    @property
    def y_train_df_as_csv(cls):
        return pd.read_csv(cls.y_train_df)

    @property
    def predict_df(cls):
        return cls._get_df(cls.predict_data, cls.predict_data_id)

    @property
    def predict_df_as_csv(cls):
        return pd.read_csv(cls.predict_df)

    @classmethod
    def _get_column_types(cls, data, data_id):
        first_row = pd.read_csv(cls._get_df(data, data_id), nrows=1)
        categorical_cols = first_row.select_dtypes(include=["object", "bool"]).columns
        numeric_cols = first_row.select_dtypes(include=["int64", "float64"]).columns
        return categorical_cols, numeric_cols

    @property
    def x_types(cls):
        return cls._get_column_types(cls.train_x_data, cls.train_x_data_id)

    @property
    def y_types(cls):
        return cls._get_column_types(cls.train_y_data, cls.train_y_data_id)

    @property
    def column_statistics(cls):
        data = pd.concat([cls.x_train_df_as_csv,
                          cls.y_train_df_as_csv,],
                          axis=1)
        return_dict = {}
        categorical_cols = data.select_dtypes(include=["object", "bool"])
        for col_name in data:
            col_data = data[col_name]
            # categorical stats
            if col_name in categorical_cols:
                mode = col_data.mode()
                col_stats = {"mode": mode}
                col_stats["type"] = "categorical" 
            # numeric stats
            else:
                mean = col_data.mean()
                median = col_data.mean()
                col_stats = {"mean": mean,
                             "median": median}
                col_stats["type"] = "continuous" 
            return_dict.update({col_name:col_stats})
        return return_dict

    @property
    def pipeline(cls):
        # the initial pipeline steps
        pipe_steps = []

        categorical_columns, numeric_columns = cls.x_types

        # each pipe stage 
        pipe_streams = (
                cls.pipeline_object.data_cleaning,
                cls.pipeline_object.preprocessing,
                cls.pipeline_object.training,
                )

        # project-specific args that relate to each step of the ML process
        data_cleaning_args = {}
        preprocessing_args = {}
        training_args = {"scoring": cls.model_scoring_metric}
        pipe_stream_args = (
                data_cleaning_args,
                preprocessing_args,
                training_args,
                )

        for pipe_stream, extra_args in zip(pipe_streams, pipe_stream_args):
            # the blocks in this pipeline
            for block in pipe_stream:
                # gets the object name (largely symbolic)
                obj_name = block.block.name

                # gets the object class, its args, and renders it
                obj_template = block.block._object
                obj_args = dict(block.value)

                obj = obj_template(**obj_args, **extra_args)

                # the basic pipeline item
                pipeline_arg = (obj_name, obj)

                # block specific values for which data types to operate on
                for_categorical = block.block._for_categorical_data
                for_numeric = block.block._for_numeric_data

                # if for all types of data, no column transform is needed
                if for_categorical and for_numeric:
                    pipe_steps.append(pipeline_arg)
                # else if it is for atleast one type of data, it uses a column
                # transformer to only operate on that data
                elif for_categorical or for_numeric:
                    cols_to_transform = categorical_columns if for_categorical else numeric_columns
                    transformer = [pipeline_arg + tuple([cols_to_transform])]
                    column_transformer = ColumnTransformer(transformers=transformer,
                                                           remainder="passthrough")
                    pipe_steps.append(("column_transformer_" + obj_name, column_transformer))

        # creates a scikit-learn pipeline and returns it
        return Pipeline(pipe_steps)

    def train_model(self):
        return_dict = {"errors":[], "warnings":[], "pipelines":{}}

        # loading the input data
        try:
            x_data = self.x_train_df_as_csv
            y_data = self.y_train_df_as_csv
        except Exception as e:
            error_msg = "Error loading input data, please ensure that the data is properly formatted:" + str(e)
            return_dict["errors"].append(error_msg)
            return return_dict

        # getting the pipeline
        try:
            base_pipe = self.pipeline
        except Exception as e:
            error_msg = "Error loading the pipeline. This is most likely a server fault, so please let the server admin know!" + str(e)
            return_dict["errors"].append(error_msg)
            return return_dict

        # iterates over each target feature
        for y_feature in y_data:
            # records train time for analysis
            start_time = time.time()

            # gets the y feature data
            # y_feature_data = pd.DataFrame(y_data[y_feature])
            y_feature_data = y_data[y_feature]

            # copies the pipeline
            pipe = base_pipe

            # gets the train/test split
            try:
                x_train, x_test, y_train, y_test = train_test_split(x_data,
                        y_feature_data, train_size=self.train_proportion)
            except Exception as e:
                error_msg = "Error completing the train/test split. Please check your input and target features are correct." + str(e)
                return_dict["errors"].append(error_msg)
                return return_dict

            # fits the pipeline
            try:
                pipe.fit(x_train, y_train)
            except Exception as e:
                error_msg = "Error fitting the pipeline. Please check your input and your workflow" + str(e)
                return_dict["errors"].append(error_msg)
                return return_dict

            # gets the model score
            try:
                score = pipe.score(x_test, y_test)

            except Exception as e:
                error_msg = "Error scoring the pipeline. This can often happen if the model you're using does not support this function" + str(e)
                return_dict["errors"].append(error_msg)
                return return_dict

            # saves the pipeline
            try:
                # checks if the last object in the pipeline was a tpot object to
                # see whether to expand the fitted pipeline and save it
                last_obj = pipe.steps[-1][1]
                if isinstance(last_obj, TPOTClassifier) or isinstance(last_obj, TPOTRegressor):
                    new_steps = pipe.steps[:-1] + last_obj.fitted_pipeline_.steps 
                    pipe = Pipeline(steps=new_steps)
            except Exception as e:
                error_msg = "This is most likely an issue with a custom algorithm you forgot to make picklable or that you deleted the ml/ml_models directory" + str(e)
                return_dict["errors"].append(error_msg)
                return return_dict

            # returns the model
            try:
                # gets train length
                end_time = time.time()
                time_difference = str(dt.timedelta(seconds=round(end_time - start_time)))

                # the pipe with newlines removed so it isnt a bad header
                formatted_pipe = str(pipe).replace("\n", "")

                feature_results = {"pipeline":pipe, "formatted_pipeline": formatted_pipe, "score": score, "train_time": time_difference}
                return_dict["pipelines"][y_feature] = feature_results
            except Exception as e:
                error_msg = "Error saving the pipeline internally. If this happened, there's probably something pretty wrong!" + str(e)
                return_dict["errors"].append(error_msg)
                return return_dict

        # saves the latest model in the model itself
        self.is_fitted = True
        self.train_results = return_dict["pipelines"]

        # dumps the model
        joblib.dump(return_dict["pipelines"], os.path.join(self.output_dir, str(dt.datetime.now())))
        return return_dict, self

    @property
    def load_pipelines(cls):
        def load_str_as_datetime(item):
            return dt.datetime.strptime(item, "%Y-%m-%d %H:%M:%S.%f")

        # lists all ml algorithms and gets most recent
        latest_algorithm = max(os.listdir(cls.output_dir),
                               key=load_str_as_datetime)

        # loads pipeline
        pipe = joblib.load(os.path.join(cls.output_dir, latest_algorithm))

        return pipe

    def predict(self):
        return_dict = {"errors":[], "warnings":[], "predictions":None}

        # checks that the model is fitted
        if not self.is_fitted:
            error_msg = "This model is not yet fitted. Please train it first!"
            return_dict["errors"].append(error_msg)
            return return_dict

        # loads the data
        try:
            input_data = self.predict_df_as_csv
        except Exception as e:
            error_msg = "Unable to load data. This is probably because of improperly formatted data" + str(e)
            return_dict["errors"].append(error_msg)
            return return_dict

        # the df object that y features will be added to
        return_df = pd.DataFrame()

        # iterates over every feature model
        for y_feature, y_vals in self.load_pipelines.items():
            # predicts
            try:
                pipe = y_vals["pipeline"]
                predicted_vals = pd.Series(pipe.predict(input_data))
                predicted_vals.name = y_feature
                return_df = pd.concat([return_df, predicted_vals], axis=1)
            except Exception as e:
                error_msg = "Unable to predict on the new data. Is it in the same format that you used to train this model?" + str(e)
                return_dict["errors"].append(error_msg)
                return return_dict
            print(return_df)

        return_dict["predictions"] = return_df
        self.latest_prediction = return_df
        self.save()
        return return_dict

    def __str__(cls):
        return cls.title + f" ({cls.pk})"

    class Meta:
        verbose_name_plural = "Projects (models)"
