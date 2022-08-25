from ..models.ActiveLearning.active_learning import ActiveLearning
from sklearn.ensemble import RandomForestClassifier


class RecommendationModel():
    """
    This class represents the used model in recommendation step

    Attributes
    ----------
    technique: str
        name of technique which is used for recommendation
    instance: object
        an object that represent used technique
    dataframe: DataFrame
        DataFrame contains all features except target column
    X: DataFrame
        DataFrame contains all features except target column
    y: Series
        series that contain target data
    model: ML model
        used model for the used technique
    n_cluster: int
        creates n_cluster times cluster
    n: int
        takes n element for each clusters

    Methods
    ----------
    create_object(technique="active-learning", model=RandomForestClassifier(), n_cluster=5, n=4)
        method that prepare the used technique/model for the recommendation processes
    """
    def __init__(self):
        """
        Parameters
        ----------
        technique: str
            name of technique which is used for recommendation
        instance: object
            an object that represent used technique
        dataframe: DataFrame
            DataFrame contains all features except target column
        X: DataFrame
            DataFrame contains all features except target column
        y: Series
            series that contain target data
        model: ML model
            used model for the used technique
        n_cluster: int
            creates n_cluster times cluster
        n: int
            takes n element for each clusters
        """
        self.technique = None
        self.instance  = None
        self.dataframe = None
        self.X         = None
        self.y         = None
        self.model     = None
        self.n_cluster = None
        self.n         = None

    def create_object(self, technique="active-learning", model=RandomForestClassifier(), n_cluster=5, n=4):
        """
        Method that prepares the used technique/model for the recommendation processes

         Parameters
        ----------
        technique: str
            name of technique which is used for recommendation
        model: ML model
            used model for the used technique
        n_cluster: int
            creates n_cluster times cluster
        n: int
            takes n element for each clusters
        """
        self.technique = technique
        if technique == "active-learning":
            self.instance = ActiveLearning()
            self.dataframe = self.instance.main_dataframe
            self.X, self.y = self.instance.get_data(self.instance.main_dataframe)
            self.model = model
            self.n_cluster = n_cluster
            self.n = n