import pandas as pd
from zipfile import ZipFile
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer


class DataPreparation():
    """
        A class to represent data preparation for active learning

        Attributes
        ----------
        dataframe: DataFrame
            DataFrame before the preparation operations
        transformed_dataframe: DataFrame
            dataframe after transformation operations are applied
        X: DataFrame
            DataFrame contains all features except target column
        y: Series
            series that contain target data

        Methods
        ----------
        load_data()
            loads the data
        transform_dataframe()
            transforms the dataframe
        scaler(df)
            applies standard scaler
        ohe(df)
            applies one hot encoding
        prepare_data(data)
            splits data as features(X) and label(y)
        """

    def __init__(self) -> None:
        """
        Parameters
        ----------
        dataframe: DataFrame
            DataFrame before the preparation operations
        transformed_dataframe: DataFrame
            dataframe after transformation operations are applied
        X: DataFrame
            DataFrame contains all features except target column
        y: Series
            series that contain target data
        """
        self.dataframe = None
        self.transformed_dataframe = None
        self.X = None
        self.y = None

    def unzip_file(self):
        file_name = "preprossed.zip"
        with ZipFile(file_name, 'r') as zip_:
            zip_.extractall()

    def load_data(self):
        """ Gets data """
        #self.unzip_file()
        self.dataframe = pd.read_csv("preprossed_data.csv")
    
    def transform_dataframe(self, data):
        """ Preprocesses and transforms data using Scaler and One Hot Encoding """

        new_df = data.copy()

        # Drops directions columns
        new_df = new_df.iloc[:,9:].drop("directions", axis=1)

        if len(new_df[new_df.index == 30048]) == 1:
            new_df.drop(index=30048, inplace=True)

        # Adds labels column
        new_df["labels"] = 0

        original_index = new_df.index

        def scaler(df):
            """ Applies Standard Scaler to necessary columns returns scaled df"""
            need_scale = list(df.columns[:22])
            sc = StandardScaler()
            df[need_scale] = sc.fit_transform(df[need_scale])

            return df
        
        def ohe(df):
            """ Applies One Hot Encoding returns transformed df"""
            categorical_features = list(df.columns[-7:-1])
            one_hot = OneHotEncoder()
            transformer_ohe = ColumnTransformer([("one_hot", 
                                            one_hot, 
                                            categorical_features)], 
                                            remainder= "passthrough"
                                            )
            return transformer_ohe.fit_transform(df)
        
        scaled_df = scaler(new_df)
        transformed_X = ohe(scaled_df)
        res_df = pd.DataFrame(transformed_X)
        res_df.index = original_index
        return res_df

    def prepare_data(self, data):
        """ Split dataframe as Features(X) and Label(y) """
        #self.load_data()
        self.transformed_dataframe = self.transform_dataframe(data)
        self.X = self.transformed_dataframe.iloc[:,:-1]
        self.y = self.transformed_dataframe.iloc[:,-1]
        return self.X, self.y

    def get_transformed_data(self, data):
        return self.transform_dataframe(data)


